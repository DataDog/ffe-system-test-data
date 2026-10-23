package com.datadog.android.flags.internal.evaluation

import com.datadog.android.api.InternalLogger
import com.datadog.android.api.context.DatadogContext
import com.datadog.android.flags.ExperimentationOptOutMode
import com.datadog.android.flags.internal.net.PrecomputedAssignmentsRequestFactory
import com.datadog.android.flags.internal.repository.net.PrecomputeMapper
import com.datadog.android.flags.model.EvaluationContext
import okio.Buffer
import org.json.JSONObject
import org.junit.jupiter.api.Test
import org.mockito.kotlin.mock
import org.mockito.kotlin.doReturn
import java.io.File

class MobileProfileProbeTest {
    @Test
    fun verifyProfile() {
        val outputs = mutableListOf<String>()
        File("/Users/leo.romanovsky/go/src/github.com/DataDog/.worktrees/opt-out-finish-20261022/evidence/android-audit/profile-cases.jsonl").readLines().forEach { line ->
            val row = JSONObject(line)
            val result = when (row.getString("kind")) {
                "timestamp" -> timestamp(row)
                "request" -> request(row)
                "ack" -> acknowledgement(row)
                else -> error("Unsupported row kind; applicability must be selected by the pinned profile")
            }
            val output = JSONObject().put("id", row.getString("id"))
            if (result.has("wire")) output.put("wire", result.remove("wire"))
            outputs.add(output.put("observed", result).toString())
        }
        File("/Users/leo.romanovsky/go/src/github.com/DataDog/.worktrees/opt-out-finish-20261022/evidence/android-audit/profile-observations.jsonl").writeText(outputs.joinToString("\n", postfix = "\n"))
    }

    private fun acknowledgement(row: JSONObject): JSONObject {
        val args = row.getJSONObject("args")
        val cutoff = "2026-10-01T00:00:00.123456789Z"
        val options = JSONObject()
        when (args.getString("acknowledged")) {
            "missing" -> Unit
            "true" -> options.put("experimentation_opt_out", true)
            "false" -> options.put("experimentation_opt_out", false)
            else -> error("Unknown acknowledgement boolean")
        }
        when (args.getString("mode")) {
            "missing" -> Unit
            "immediate" -> options.put("experimentation_opt_out_mode", "immediate")
            "future" -> options.put("experimentation_opt_out_mode", "future_experiments_only")
            else -> error("Unknown acknowledgement mode")
        }
        val responseCutoff = when (args.getString("cutoff")) {
            "missing" -> null
            "equal" -> cutoff
            "equivalent" -> "2026-10-01T01:00:00.123456789999+01:00"
            "different" -> "2026-10-01T00:00:00.123456788Z"
            "invalid" -> "not-a-timestamp"
            else -> error("Unknown acknowledgement cutoff")
        }
        if (responseCutoff != null) options.put(ExperimentationOptOut.ATTRIBUTE, responseCutoff)
        val flag = JSONObject().put("variationType", "boolean").put("variationValue", true)
            .put("doLog", false).put("allocationKey", "ordinary").put("variationKey", "on")
            .put("extraLogging", JSONObject()).put("reason", "TARGETING_MATCH").put("serialId", 7)
        val attributes = JSONObject().put("evaluation_options", options).put("flags", JSONObject().put("flag", flag))
        val payload = JSONObject().put("data", JSONObject().put("attributes", attributes)).toString()
        val policy = args.getString("policy")
        val modes = when (policy) {
            // Exercise all real caller routes to no effective policy: disabled with a supplied
            // timestamp, or either enabled mode with an absent attribute.
            "none" -> ExperimentationOptOutMode.values().toList()
            "immediate" -> listOf(ExperimentationOptOutMode.IMMEDIATE)
            "future" -> listOf(ExperimentationOptOutMode.FUTURE_EXPERIMENTS_ONLY)
            else -> error("Unknown effective policy")
        }
        val observations = modes.map { mode ->
            val supplied = policy != "none" || mode == ExperimentationOptOutMode.DISABLED
            val context = EvaluationContext("subject", if (supplied) mapOf(ExperimentationOptOut.ATTRIBUTE to cutoff) else emptyMap())
            val prepared = ExperimentationOptOut(mode).prepare(context)
            check(!prepared.invalid)
            // The production caller passes this effective-policy request; lifecycle tests cover dispatch separately.
            val result = PrecomputeMapper(mock<InternalLogger>()).map(payload, prepared.takeIf { it.optedOut })
            if (result != null) {
                check(result.flags["flag"]?.variationValue == "true")
                check(result.flags["flag"]?.allocationKey == "ordinary")
                check(result.flags["flag"]?.serialId == 7L)
            }
            result != null
        }
        check(observations.distinct().size == 1) { "Effective-policy paths disagree: $observations" }
        return JSONObject().put("accepted", observations.singleOrNull() ?: observations.first())
    }

    private fun timestamp(row: JSONObject): JSONObject {
        val value = row.opt("input") as? String
        // Reflection reads the real private result; the adapter implements no parser.
        val parser = ExperimentationOptOut.Companion.javaClass.getDeclaredMethod("parseTimestamp", String::class.java)
        parser.isAccessible = true
        val parsed = parser.invoke(ExperimentationOptOut.Companion, value)
        val result = JSONObject().put("accepted", parsed != null)
        if (parsed != null) {
            val millis = parsed.javaClass.getDeclaredField("wholeSecondMillis").apply { isAccessible = true }.getLong(parsed)
            val fraction = parsed.javaClass.getDeclaredField("fraction").apply { isAccessible = true }.get(parsed) as String
            result.put("seconds", millis / 1000).put("nanos", fraction.padEnd(9, '0').toInt())
        }
        return result
    }

    private fun request(row: JSONObject): JSONObject {
        val args = row.getJSONObject("args")
        val mode = when (args.getString("mode")) {
            "disabled" -> ExperimentationOptOutMode.DISABLED
            "immediate" -> ExperimentationOptOutMode.IMMEDIATE
            "future_experiments_only" -> ExperimentationOptOutMode.FUTURE_EXPERIMENTS_ONLY
            else -> error("Unknown mode")
        }
        val attributes = when (args.getString("attribute")) {
            "absent" -> emptyMap()
            "valid" -> mapOf(ExperimentationOptOut.ATTRIBUTE to "2026-10-01T00:00:00.123456789Z")
            "invalid" -> mapOf(ExperimentationOptOut.ATTRIBUTE to "not-a-timestamp")
            else -> error("Unknown attribute state")
        }
        val context = EvaluationContext("subject", attributes)
        val policy = ExperimentationOptOut(mode)
        val prepared = policy.prepare(context)
        // Same boundary order as EvaluationsManager: prepare/invalid gate, then request factory.
        // This is source-linked composition, not execution of the entire asynchronous client.
        if (prepared.invalid) {
            val error = checkNotNull(policy.resolutionError(null))
            return JSONObject().put("send", false).put("options", false).put("error", error.name)
        }
        val factory = PrecomputedAssignmentsRequestFactory(mock<InternalLogger>(), "https://example.test/assignments", mode)
        val request = checkNotNull(factory.create(context, mock<DatadogContext> {
            on { clientToken } doReturn "test-token"
            on { env } doReturn "test"
            on { sdkVersion } doReturn "test-version"
            on { source } doReturn "android"
            on { featuresContext } doReturn emptyMap()
        }))
        val buffer = Buffer()
        checkNotNull(request.body).writeTo(buffer)
        val body = JSONObject(buffer.readUtf8()).getJSONObject("data").getJSONObject("attributes")
        return JSONObject().put("send", true).put("options", body.has("evaluation_options")).put("error", "NONE")
            .put("wire", body)
    }
}
