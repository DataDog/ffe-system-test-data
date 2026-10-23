// External SDK boundary shims for the Linux production-source probe. No parser,
// request serializer, response decoder, acknowledgement, or fetcher logic lives here.
import Foundation

struct FlagsClient { enum ExperimentationOptOutMode { case disabled, immediate, futureExperimentsOnly } }
enum DatadogSite { case us1, us3, us5, eu1, ap1, ap2, uk1, us1_fed, us2_fed }
struct RUMCoreContext { var applicationID: String? }
struct DatadogContext {
    var clientToken = "probe"
    var env = "test"
    var sdkVersion = "probe"
    var source = "contract-probe"
    var site = DatadogSite.us1
    func additionalContext<T>(ofType: T.Type) -> T? { nil }
}
struct ProbeTelemetry {
    func error(_ message: String, error: Error) {}
    func debug(_ message: String, attributes: [String: String]) {}
}
protocol FeatureScope {
    var telemetry: ProbeTelemetry { get }
    func context(_ completion: @escaping (DatadogContext) -> Void)
}
final class ProbeFeatureScope: FeatureScope {
    let telemetry = ProbeTelemetry()
    func context(_ completion: @escaping (DatadogContext) -> Void) { completion(DatadogContext()) }
}
struct ProbeLogger {
    func warn(_ message: String, error: Error? = nil) {}
    func error(_ message: String, error: Error) {}
}
enum DD { static let logger = ProbeLogger() }
struct InternalError: Error { let description: String }
struct ProbeEncoderFactory { func `default`() -> JSONEncoder { JSONEncoder() } }
extension JSONEncoder { static var dd: ProbeEncoderFactory { ProbeEncoderFactory() } }

// The pinned acceptance profile contains no obfuscated flags. Fail closed if this
// boundary is reached; the source probe provides no crypto or obfuscation evidence.
struct FlagKeyObfuscation: Equatable, Codable {
    static let capability = "unexercised-obfuscation"
    static func isSupported(source: String) -> Bool {
        precondition(source == "contract-probe")
        return false
    }
    init(from decoder: Decoder) throws {
        throw DecodingError.dataCorrupted(.init(codingPath: decoder.codingPath, debugDescription: "Obfuscation is outside the probe profile"))
    }
    func encode(to encoder: Encoder) throws {
        throw EncodingError.invalidValue(self, .init(codingPath: encoder.codingPath, debugDescription: "Obfuscation is outside the probe profile"))
    }
    func validateKeys(_ keys: Dictionary<String, FlagAssignment>.Keys, codingPath: [CodingKey]) throws {
        throw DecodingError.dataCorrupted(.init(codingPath: codingPath, debugDescription: "Obfuscation is outside the probe profile"))
    }
}
