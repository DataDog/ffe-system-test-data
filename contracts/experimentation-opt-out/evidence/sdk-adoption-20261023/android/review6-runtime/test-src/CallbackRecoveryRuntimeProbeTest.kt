package com.datadog.android.sdk.integration.optout

import android.os.Looper
import androidx.test.platform.app.InstrumentationRegistry
import com.datadog.android.Datadog
import com.datadog.android.api.feature.FeatureSdkCore
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
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.CountDownLatch
import java.util.concurrent.ExecutorService
import java.util.concurrent.RejectedExecutionException
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger

class CallbackRecoveryRuntimeProbeTest {
    @Test fun soleCallbackRecoversAfterStartupFailureAndSdkStop() {
        val app = InstrumentationRegistry.getInstrumentation().targetContext.applicationContext
        val observations = JSONArray()
        for (failure in listOf("creation-security", "submission-security", "submission-rejection")) {
            val name = "callback-recovery-$failure"
            val actualCore = checkNotNull(Datadog.initialize(name, app,
                Configuration.Builder("test-token", "callback-recovery").build(), TrackingConsent.GRANTED)) as FeatureSdkCore
            val attempts = AtomicInteger()
            val attemptThreads = CopyOnWriteArrayList<Boolean>()
            val workers = CopyOnWriteArrayList<ExecutorService>()
            val core = object : FeatureSdkCore by actualCore {
                override fun createSingleThreadExecutorService(executorContext: String): ExecutorService {
                    if (executorContext != "flags-callbacks") return actualCore.createSingleThreadExecutorService(executorContext)
                    val attempt = attempts.incrementAndGet()
                    attemptThreads.add(Looper.myLooper() == Looper.getMainLooper())
                    if (attempt == 1 && failure == "creation-security") throw SecurityException("Injected initial creation denial")
                    val worker = actualCore.createSingleThreadExecutorService(executorContext)
                    workers.add(worker)
                    return object : ExecutorService by worker {
                        override fun execute(command: Runnable) {
                            if (attempt == 1) {
                                if (failure == "submission-security") throw SecurityException("Injected initial submission denial")
                                throw RejectedExecutionException("Injected initial submission rejection")
                            }
                            worker.execute(command)
                        }
                    }
                }
            }
            val delivered = CountDownLatch(1)
            val stopped = CountDownLatch(1)
            val callbackThreads = CopyOnWriteArrayList<String>()
            val afterStop = CopyOnWriteArrayList<Boolean>()
            val errors = CopyOnWriteArrayList<String>()
            val deliveredCount = AtomicInteger()
            try {
                Flags.enable(FlagsConfiguration.Builder().trackEvaluations(false).build(), core)
                val client = FlagsClient.Builder("recovery", core)
                    .experimentationOptOutMode(ExperimentationOptOutMode.IMMEDIATE).build()
                client.setEvaluationContext(EvaluationContext("recovery-subject", mapOf("dd_experimentation_opt_out_at" to "invalid")),
                    object : EvaluationContextCallback {
                        override fun onSuccess() = Unit
                        override fun onFailure(error: Throwable) {
                            callbackThreads.add(Thread.currentThread().name)
                            afterStop.add(stopped.count == 0L)
                            errors.add(error.javaClass.simpleName)
                            deliveredCount.incrementAndGet()
                            delivered.countDown()
                        }
                    })
                Datadog.stopInstance(name)
                stopped.countDown()
                val completed = delivered.await(5, TimeUnit.SECONDS)
                val allTerminated = workers.all { it.awaitTermination(2, TimeUnit.SECONDS) }
                val row = JSONObject().put("failure", failure).put("submitted_callbacks", 1)
                    .put("delivered_callbacks", deliveredCount.get()).put("worker_start_attempts", attempts.get())
                    .put("attempts_on_main_looper", JSONArray(attemptThreads)).put("callback_threads", JSONArray(callbackThreads))
                    .put("delivered_after_sdk_stop", JSONArray(afterStop)).put("callback_errors", JSONArray(errors))
                    .put("all_created_workers_shutdown", workers.all { it.isShutdown }).put("all_created_workers_terminated", allTerminated)
                observations.put(row)
                File(app.filesDir, "callback-recovery-runtime-proof.json").writeText(JSONObject()
                    .put("source_sha", "6e5fe6cf6266a5d965a44a7f1958f1bfe1fcf735").put("cases", observations).toString(2))
                assertTrue("Sole accepted callback recovers without another execute", completed)
                assertEquals(1, deliveredCount.get())
                assertEquals(2, attempts.get())
                assertEquals(listOf(false, true), attemptThreads.toList())
                assertEquals(listOf(true), afterStop.toList())
                assertEquals(listOf("FlagsInvalidContextException"), errors.toList())
                assertTrue(callbackThreads.all { it.startsWith("datadog-flags-callbacks-") })
                assertTrue(workers.all { it.isShutdown } && allTerminated)
            } finally { Datadog.stopInstance(name); workers.forEach { it.shutdownNow() } }
        }
    }
}
