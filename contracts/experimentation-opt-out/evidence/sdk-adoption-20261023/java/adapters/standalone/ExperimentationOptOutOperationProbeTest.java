package com.datadog.openfeature.internal.evaluation;

import static java.nio.charset.StandardCharsets.UTF_8;
import static net.bytebuddy.matcher.ElementMatchers.named;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.datadog.openfeature.ExperimentationOptOutMode;
import com.datadog.openfeature.internal.JsonReading;
import com.datadog.openfeature.internal.ufc.Allocation;
import com.datadog.openfeature.internal.ufc.Flag;
import com.datadog.openfeature.internal.ufc.ServerConfiguration;
import com.datadog.openfeature.internal.ufc.ValueType;
import dev.openfeature.sdk.MutableContext;
import dev.openfeature.sdk.ProviderEvaluation;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.stream.Stream;
import net.bytebuddy.ByteBuddy;
import net.bytebuddy.agent.ByteBuddyAgent;
import net.bytebuddy.asm.Advice;
import net.bytebuddy.dynamic.loading.ClassReloadingStrategy;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

public class ExperimentationOptOutOperationProbeTest {
  private static ClassReloadingStrategy strategy;
  public static class Trace {
    public static final List<Boolean> calls = new ArrayList<>();
    public static final List<String> retained = new ArrayList<>();
    @Advice.OnMethodExit
    public static void exit(@Advice.Return final boolean excluded) { calls.add(excluded); }
  }
  public static class ActiveTrace {
    @Advice.OnMethodEnter
    public static void enter(@Advice.Argument(0) final Allocation allocation) { Trace.retained.add(allocation.key); }
  }
  @BeforeAll
  static void instrumentNativeBoundary() {
    strategy = ClassReloadingStrategy.of(ByteBuddyAgent.install());
    new ByteBuddy().redefine(ExperimentationOptOut.class)
        .visit(Advice.to(Trace.class).on(named("excludes")))
        .make().load(ExperimentationOptOut.class.getClassLoader(), strategy);
    new ByteBuddy().redefine(FlagEvaluator.class)
        .visit(Advice.to(ActiveTrace.class).on(named("isAllocationActive")))
        .make().load(FlagEvaluator.class.getClassLoader(), strategy);
  }
  @AfterAll
  static void restoreNativeBoundary() throws Exception { strategy.reset(ExperimentationOptOut.class, FlagEvaluator.class); }
  @SuppressWarnings("unchecked")
  static Stream<Arguments> operations() throws Exception {
    final List<String> lines = Files.readAllLines(Paths.get(System.getProperty("optout.operations")), UTF_8);
    assertEquals(36, lines.size());
    final List<Arguments> cases = new ArrayList<>();
    for (final String line : lines) {
      final Map<String,Object> testCase = (Map<String,Object>) JsonReading.read(line);
      cases.add(Arguments.of(testCase.get("id"),testCase));
    }
    return cases.stream();
  }
  @ParameterizedTest(name="{0}")
  @MethodSource("operations")
  @SuppressWarnings("unchecked")
  void recordsRealExclusionCalls(final String id, final Map<String,Object> testCase) {
    final Map<String,Object> args=(Map<String,Object>)testCase.get("args");
    final Map<String,Object> expected=(Map<String,Object>)testCase.get("expected");
    final ExperimentationOptOutMode mode=ExperimentationOptOutMode.valueOf(((String)args.get("mode")).toUpperCase(Locale.ROOT));
    final List<Allocation> allocations=new ArrayList<>();
    for (final boolean excluded : (List<Boolean>)args.get("checkResults")) {
      allocations.add(new Allocation("allocation-" + allocations.size(),null,null,null,Collections.emptyList(),excluded));
    }
    final Flag flag=new Flag("target",true,ValueType.STRING,Collections.emptyMap(),allocations);
    final ServerConfiguration config=new ServerConfiguration("","",false,null,Collections.singletonMap("target",flag));
    final MutableContext context=new MutableContext("subject");
    final String attribute=(String)args.get("attribute");
    if (!"absent".equals(attribute)) {
      context.add("dd_experimentation_opt_out_at", "valid".equals(attribute)?"2026-10-19T12:00:00Z":"bad");
    }
    final FlagEvaluator evaluator=new FlagEvaluator(false,(a,b,c,d,f)->false,mode);
    Trace.calls.clear();
    Trace.retained.clear();
    final ProviderEvaluation<String> result=evaluator.evaluate(config,String.class,"target","default",context);
    final List<Boolean> excludedAllocations = new ArrayList<>();
    if (result.getErrorCode() == null) {
      for (final Allocation allocation : allocations) {
        excludedAllocations.add(!Trace.retained.contains(allocation.key));
      }
    }
    System.out.println("OPTOUT_OBSERVATION {\"id\":\"" + id + "\",\"exclusionChecks\":"
        + Trace.calls.size() + ",\"excluded\":" + excludedAllocations + ",\"helperResults\":" + Trace.calls
        + ",\"error\":\"" + (result.getErrorCode() == null ? "NONE" : result.getErrorCode().name()) + "\"}");
    assertEquals(expected.get("excluded"),excludedAllocations,id);
    assertEquals(((Number)expected.get("exclusionChecks")).intValue(),Trace.calls.size(),id);
    assertEquals(expected.get("error"),result.getErrorCode()==null?"NONE":result.getErrorCode().name(),id);
    assertEquals("default",result.getValue(),id);
    if (!Trace.calls.isEmpty()) { assertEquals(expected.get("excluded"),Trace.calls,id); }
  }
}
