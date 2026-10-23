package com.datadog.android.sdk.integration.optout

import androidx.test.platform.app.InstrumentationRegistry
import com.datadog.android.Datadog
import com.datadog.android.core.configuration.BackPressureMitigation
import com.datadog.android.core.configuration.BackPressureStrategy
import com.datadog.android.core.configuration.Configuration
import com.datadog.android.flags.EvaluationContextCallback
import com.datadog.android.flags.ExperimentationOptOutMode
import com.datadog.android.flags.Flags
import com.datadog.android.flags.FlagsClient
import com.datadog.android.flags.FlagsConfiguration
import com.datadog.android.flags.model.EvaluationContext
import com.datadog.android.privacy.TrackingConsent
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.Executors
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

class CallbackRuntimeProbeTest {
    @Test fun callbacksSurviveBackpressureAndReleaseWorkers() {
        val app = InstrumentationRegistry.getInstrumentation().targetContext.applicationContext
        val dropped = CopyOnWriteArrayList<String>()
        val config = Configuration.Builder("test-token", "callback-probe")
            .setBackpressureStrategy(BackPressureStrategy(1, {}, { dropped.add(it.toString()) }, BackPressureMitigation.IGNORE_NEWEST))
            .build()
        val name = "callback-runtime"
        val core = checkNotNull(Datadog.initialize(name, app, config, TrackingConsent.GRANTED))
        val release = CountDownLatch(1)
        val firstEntered = CountDownLatch(1)
        val delivered = CountDownLatch(9)
        val threads = CopyOnWriteArrayList<String>()
        val stopper = Executors.newSingleThreadExecutor()
        try {
            Flags.enable(FlagsConfiguration.Builder().trackEvaluations(false).build(), core)
            val client = FlagsClient.Builder("callbacks", core).experimentationOptOutMode(ExperimentationOptOutMode.IMMEDIATE).build()
            val context = EvaluationContext("callback-subject", mapOf("dd_experimentation_opt_out_at" to "invalid"))
            client.setEvaluationContext(context, object : EvaluationContextCallback {
                override fun onSuccess() = Unit
                override fun onFailure(error: Throwable) {
                    threads.add(Thread.currentThread().name)
                    firstEntered.countDown()
                    release.await(10, TimeUnit.SECONDS)
                    delivered.countDown()
                }
            })
            assertTrue(firstEntered.await(5, TimeUnit.SECONDS))
            repeat(8) {
                client.setEvaluationContext(context, object : EvaluationContextCallback {
                    override fun onSuccess() = Unit
                    override fun onFailure(error: Throwable) {
                        threads.add(Thread.currentThread().name)
                        delivered.countDown()
                    }
                })
            }
            stopper.submit { Datadog.stopInstance(name) }.get(2, TimeUnit.SECONDS)
            release.countDown()
            val allDelivered = delivered.await(3, TimeUnit.SECONDS)
            val workers = Thread.getAllStackTraces().keys.filter { it.name.startsWith("datadog-flags-callbacks-") }
            workers.forEach { it.join(1000) }
            val alive = workers.filter { it.isAlive }.map { it.name }
            File(app.filesDir, "callback-runtime-proof.json").writeText(JSONObject()
                .put("source_sha", "cda7955b6361876526fa2035db23dbf88a9e74e1")
                .put("stop_returned_while_callback_blocked", true)
                .put("submitted", 9).put("delivered", 9 - delivered.count)
                .put("callback_threads", JSONArray(threads)).put("dropped", JSONArray(dropped))
                .put("alive_callback_workers_after_stop", JSONArray(alive)).toString(2))
            assertTrue("all callbacks delivered and callback workers terminated", allDelivered && alive.isEmpty())
        } finally { release.countDown(); stopper.shutdownNow(); Datadog.stopInstance(name) }
    }
}
