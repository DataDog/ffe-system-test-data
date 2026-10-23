package com.datadog.android.sdk.integration.optout

import android.os.Build
import android.os.Looper
import androidx.test.platform.app.InstrumentationRegistry
import com.datadog.android.Datadog
import com.datadog.android._InternalProxy
import com.datadog.android.api.feature.Feature
import com.datadog.android.api.feature.FeatureSdkCore
import com.datadog.android.core.InternalSdkCore
import com.datadog.android.core.configuration.Configuration
import com.datadog.android.flags.EvaluationContextCallback
import com.datadog.android.flags.ExperimentationOptOutMode
import com.datadog.android.flags.Flags
import com.datadog.android.flags.FlagsClient
import com.datadog.android.flags.FlagsConfiguration
import com.datadog.android.flags._FlagsInternalProxy
import com.datadog.android.flags.model.EvaluationContext
import com.datadog.android.privacy.TrackingConsent
import okhttp3.mockwebserver.Dispatcher
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import okhttp3.mockwebserver.RecordedRequest
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.ByteArrayInputStream
import java.io.File
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference
import java.util.zip.GZIPInputStream

class OptOutRuntimeProbeTest {
    @Test
    fun bothModesPreserveValuesAndIndependentIntake() {
        val app = InstrumentationRegistry.getInstrumentation().targetContext.applicationContext
        val results = JSONArray()
        for (mode in listOf(ExperimentationOptOutMode.IMMEDIATE, ExperimentationOptOutMode.FUTURE_EXPERIMENTS_ONLY)) {
            val requests = CopyOnWriteArrayList<JSONObject>()
            val exposures = CopyOnWriteArrayList<JSONObject>()
            val evaluations = CopyOnWriteArrayList<JSONObject>()
            val server = MockWebServer()
            server.dispatcher = object : Dispatcher() {
                override fun dispatch(request: RecordedRequest): MockResponse {
                    val bytes = request.body.clone().readByteArray()
                    val body = if (request.getHeader("Content-Encoding") == "gzip") {
                        GZIPInputStream(ByteArrayInputStream(bytes)).bufferedReader().use { it.readText() }
                    } else bytes.toString(Charsets.UTF_8)
                    return when (request.path) {
                        "/assignments" -> {
                            requests.add(JSONObject(body))
                            MockResponse().setResponseCode(200).setBody(assignments(mode).toString())
                        }
                        "/exposures" -> {
                            body.lineSequence().filter { it.isNotBlank() }.forEach { exposures.add(JSONObject(it)) }
                            MockResponse().setResponseCode(202).setBody("{}")
                        }
                        "/evaluations" -> {
                            body.lineSequence().filter { it.isNotBlank() }.forEach { evaluations.add(JSONObject(it)) }
                            MockResponse().setResponseCode(202).setBody("{}")
                        }
                        else -> MockResponse().setResponseCode(404)
                    }
                }
            }
            server.start()
            val name = "optout-runtime-${mode.name}"
            val core = checkNotNull(Datadog.initialize(name, app, _InternalProxy.allowClearTextHttp(Configuration.Builder("test-token", "optout-probe")).build(), TrackingConsent.GRANTED))
            try {
                Flags.enable(FlagsConfiguration.Builder()
                    .useCustomFlagEndpoint(server.url("/assignments").toString())
                    .useCustomExposureEndpoint(server.url("/exposures").toString())
                    .useCustomEvaluationEndpoint(server.url("/evaluations").toString())
                    .evaluationFlushInterval(1000)
                    .build(), core)
                val client = FlagsClient.Builder("probe", core)
                    .experimentationOptOutMode(mode)
                    .enableEvaluationTelemetryOptOutParameter(true)
                    .build()
                val proxy = _FlagsInternalProxy(client)
                val callbackThreads = JSONArray()
                for (optedOut in listOf(false, true)) {
                    val subject = "${mode.name}-telemetry-${if (optedOut) "off" else "on"}"
                    val done = CountDownLatch(1)
                    val failure = AtomicReference<Throwable>()
                    proxy.setEvaluationContext(EvaluationContext(subject, mapOf("dd_experimentation_opt_out_at" to CUTOFF)), object : EvaluationContextCallback {
                        override fun onSuccess() {
                            callbackThreads.put(Thread.currentThread().name)
                            if (Looper.myLooper() == Looper.getMainLooper()) failure.set(AssertionError("callback on main thread"))
                            done.countDown()
                        }
                        override fun onFailure(error: Throwable) { failure.set(error); done.countDown() }
                    }, optedOut)
                    assertTrue("context callback timed out", done.await(15, TimeUnit.SECONDS))
                    failure.get()?.let { throw AssertionError("context failed", it) }
                    assertTrue(client.resolve("ordinary", false).value)
                    assertTrue(client.resolve("selected", false).value)
                    val snapshot = proxy.getFlagAssignmentsSnapshot()
                    assertEquals("ordinary-fallback", snapshot["ordinary"]?.allocationKey)
                    assertEquals(if (mode == ExperimentationOptOutMode.IMMEDIATE) "ordinary-fallback" else "retained-before-cutoff", snapshot["selected"]?.allocationKey)
                }
                // Drain the production aggregator, disk writer, and HTTP uploader deterministically.
                (core as FeatureSdkCore).getFeature(Feature.FLAGS_EVALUATIONS_FEATURE_NAME)?.unwrap<Feature>()?.onStop()
                (core as InternalSdkCore).flushContextThread()
                core.flushStoredData()
                assertEquals(2, requests.size)
                for ((index, request) in requests.withIndex()) {
                    val attributes = request.getJSONObject("data").getJSONObject("attributes")
                    assertEquals("${mode.name}-telemetry-${if (index == 0) "on" else "off"}", attributes.getJSONObject("subject").getString("targeting_key"))
                    assertEquals(if (mode == ExperimentationOptOutMode.IMMEDIATE) "immediate" else "future_experiments_only", attributes.getJSONObject("evaluation_options").getString("experimentation_opt_out_mode"))
                }
                assertEquals(2, evaluations.size)
                evaluations.forEach {
                    assertEquals("${mode.name}-telemetry-on", it.getString("targeting_key"))
                    assertFalse(it.getBoolean("runtime_default_used"))
                    assertEquals(1, it.getInt("evaluation_count"))
                }
                val expectedExposureCount = if (mode == ExperimentationOptOutMode.IMMEDIATE) 0 else 2
                assertEquals(expectedExposureCount, exposures.size)
                if (expectedExposureCount != 0) {
                    assertEquals(setOf("${mode.name}-telemetry-on", "${mode.name}-telemetry-off"), exposures.map { it.getJSONObject("subject").getString("id") }.toSet())
                    exposures.forEach { assertEquals("retained-before-cutoff", it.getJSONObject("allocation").getString("key")) }
                }
                results.put(JSONObject().put("mode", mode.name).put("requests", JSONArray(requests))
                    .put("evaluations", JSONArray(evaluations)).put("exposures", JSONArray(exposures))
                    .put("callback_threads", callbackThreads).put("evaluations_returning_true", 4))
            } finally {
                Datadog.stopInstance(name)
                server.shutdown()
            }
        }
        File(app.filesDir, "optout-runtime-proof.json").writeText(JSONObject()
            .put("source_sha", "9c18edeca8d99f07ef7e21664d01d7d2d069db0b")
            .put("api_level", Build.VERSION.SDK_INT).put("abis", JSONArray(Build.SUPPORTED_ABIS.toList()))
            .put("boundary", "Real Android core, storage and HTTP over emulator loopback; supplied assignments and forced lifecycle/storage flush; typed telemetry control through SDK bridge proxy")
            .put("results", results).toString(2))
    }

    private fun assignments(mode: ExperimentationOptOutMode): JSONObject {
        fun flag(allocation: String, log: Boolean) = JSONObject().put("variationType", "boolean").put("variationValue", true)
            .put("doLog", log).put("allocationKey", allocation).put("variationKey", "enabled")
            .put("extraLogging", JSONObject()).put("reason", "TARGETING_MATCH").put("serialId", 1)
        val future = mode == ExperimentationOptOutMode.FUTURE_EXPERIMENTS_ONLY
        val options = JSONObject().put("experimentation_opt_out", true)
            .put("experimentation_opt_out_mode", if (future) "future_experiments_only" else "immediate")
            .put("dd_experimentation_opt_out_at", CUTOFF)
        val flags = JSONObject().put("ordinary", flag("ordinary-fallback", false))
            .put("selected", flag(if (future) "retained-before-cutoff" else "ordinary-fallback", future))
        return JSONObject().put("data", JSONObject().put("attributes", JSONObject().put("flags", flags).put("evaluation_options", options)))
    }

    private companion object { const val CUTOFF = "2026-10-01T00:00:00.123456789Z" }
}
