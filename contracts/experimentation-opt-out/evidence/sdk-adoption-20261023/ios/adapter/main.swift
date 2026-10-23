import Foundation

struct SerializationFailureControl: Encodable {
    func encode(to encoder: Encoder) throws {
        throw EncodingError.invalidValue("negative-control", .init(codingPath: encoder.codingPath, debugDescription: "Injected serialization failure"))
    }
}

let bundle = try JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1]))) as! [String: Any]
let cases = bundle["cases"] as! [[String: Any]]
var rows: [[String: Any]] = []
for item in cases {
    let identifier = item["id"] as! String
    if item["kind"] as! String == "timestamp" {
        let normalized = (item["input"] as? String).flatMap { try? ExperimentationOptOut.normalizedTimestamp($0) }
        rows.append(["id": identifier, "accepted": normalized != nil, "normalized": normalized.map { $0 as Any } ?? NSNull()])
    } else if item["kind"] as! String == "ack" {
        let args = item["args"] as! [String: String]
        let reference = "2026-10-19T12:00:00.123456789Z"
        let policy: ExperimentationOptOut?
        switch args["policy"]! {
        case "none": policy = nil
        case "immediate": policy = .immediate
        default: policy = .futureExperimentsOnly(cutoff: reference)
        }
        var options: [String: Any] = [:]
        if args["acknowledged"] != "missing" { options["experimentation_opt_out"] = args["acknowledged"] == "true" }
        if args["mode"] != "missing" { options["experimentation_opt_out_mode"] = args["mode"] == "immediate" ? "immediate" : "future_experiments_only" }
        switch args["cutoff"]! {
        case "equal": options["dd_experimentation_opt_out_at"] = reference
        case "equivalent": options["dd_experimentation_opt_out_at"] = "2026-10-19T08:00:00.123456789-04:00"
        case "different": options["dd_experimentation_opt_out_at"] = "2026-10-19T12:00:00.123456788Z"
        case "invalid": options["dd_experimentation_opt_out_at"] = "invalid"
        default: break
        }
        let bytes = try JSONSerialization.data(withJSONObject: ["data": ["attributes": ["flags": [:], "evaluation_options": options]]])
        let fetcher = FlagAssignmentsFetcher(customEndpoint: nil, customHeaders: nil, featureScope: ProbeFeatureScope(), fetch: { _, complete in complete(.success(bytes)) })
        var outcome: Bool? = nil
        let completed = DispatchSemaphore(value: 0)
        fetcher.flagAssignments(for: FlagsEvaluationContext(targetingKey: "contract-subject"), experimentationOptOut: policy) { result in
            switch result {
            case .success: outcome = true
            case .failure(.invalidResponse): outcome = false
            case .failure: preconditionFailure("Unexpected fetcher failure outside acknowledgement domain")
            }
            completed.signal()
        }
        precondition(completed.wait(timeout: .now() + 5) == .success, "Fetcher callback timed out")
        guard let outcome else { fatalError("Fetcher callback did not execute") }
        rows.append(["id": identifier, "observed": ["accepted": outcome]])
    } else {
        let args = item["args"] as! [String: String]
        let mode: FlagsClient.ExperimentationOptOutMode
        switch args["mode"]! {
        case "disabled": mode = .disabled
        case "immediate": mode = .immediate
        default: mode = .futureExperimentsOnly
        }
        var attributes: [String: AnyValue] = [:]
        if args["attribute"] != "absent" {
            attributes["dd_experimentation_opt_out_at"] = .string(args["attribute"] == "valid" ? "2026-01-01T00:00:00Z" : "invalid")
        }
        let context = FlagsEvaluationContext(targetingKey: "contract-subject", attributes: attributes)
        do {
            let policy = try context.experimentationOptOut(mode: mode)
            let body = FlagAssignmentsRequestBody(
                environment: .init(name: "test", datadogEnvironment: "test"),
                source: .init(sdkName: "dd-sdk-ios", sdkVersion: "probe"),
                subject: .init(targetingKey: context.targetingKey, targetingAttributes: context.attributes),
                experimentationOptOut: policy
            )
            if CommandLine.arguments.contains("--inject-serialization-error") {
                _ = try JSONEncoder().encode(SerializationFailureControl())
            }
            let encoded = try JSONEncoder().encode(body)
            let root = try JSONSerialization.jsonObject(with: encoded) as! [String: Any]
            let data = root["data"] as! [String: Any]
            let wireAttributes = data["attributes"] as! [String: Any]
            rows.append(["id": identifier, "observed": ["send": true, "options": wireAttributes["evaluation_options"] != nil, "error": "NONE"]])
        } catch FlagsError.invalidContext {
            rows.append(["id": identifier, "observed": ["send": false, "options": false, "error": "INVALID_CONTEXT"]])
        } catch {
            rows.append(["id": identifier, "observed": ["send": false, "options": false, "error": "UNCLASSIFIED_ERROR"]])
        }
    }
}
print(String(data: try JSONSerialization.data(withJSONObject: rows, options: [.prettyPrinted, .sortedKeys]), encoding: .utf8)!)
