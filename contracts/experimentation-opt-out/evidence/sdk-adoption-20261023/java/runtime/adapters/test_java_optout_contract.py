"""Exact-source Java runtime checks for the pinned experimentation contract."""

import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any

import requests

from utils import features, pytest, scenarios
from utils.docker_fixtures._core import docker_run, get_host_port
from utils.dd_constants import RemoteConfigApplyState
from utils.docker_fixtures import TestAgentAPI
from tests.parametric.conftest import APMLibrary

CASE_PATH = Path(__file__).with_name("java-policy-v1-cases.json")
CASE_BYTES = CASE_PATH.read_bytes()
assert hashlib.sha256(CASE_BYTES).hexdigest() == "289a5d2dca4a7e5dd1e0428b4c56e9c1660668375aab67b71c91b27b9391f4e2"
CASES: list[dict[str, Any]] = json.loads(CASE_BYTES)
assert len(CASES) == 90
CUTOFF = "2026-10-19T12:00:00Z"
ATTRIBUTE = "dd_experimentation_opt_out_at"
BASE_ENV = {
    "DD_FEATURE_FLAGS_ENABLED": "true",
    "DD_FEATURE_FLAGS_CONFIGURATION_SOURCE": "remote_config",
    "DD_REMOTE_CONFIG_POLL_INTERVAL_SECONDS": "0.2",
    "DD_FEATURE_FLAGS_EVALUATION_TELEMETRY_PER_SUBJECT_OPT_OUT_ENABLED": "true",
}
MODES = ["disabled", "immediate", "future_experiments_only"]


@pytest.fixture
def standalone_backend(test_agent: TestAgentAPI, worker_id: str):
    if os.environ["JAVA_OPTOUT_VARIANT"] != "standalone":
        yield None
        return
    name = f"event-platform-intake.java-optout-{worker_id}.test"
    host_port = get_host_port(worker_id, 4600)
    base = f"http://localhost:{host_port}"
    with (
        open(f"{test_agent.log_path}.standalone_backend.log", "w+") as log,
        docker_run(
            image="ffe-java-optout-backend:a4d3dfb",
            name=name,
            env={},
            volumes={},
            network=test_agent.network,
            ports={"4330/tcp": host_port},
            log_file=log,
            command=["python", "/optout_backend.py"],
        ),
    ):
        for attempt in range(100):
            try:
                requests.get(base + "/events", timeout=1).raise_for_status()
                break
            except requests.RequestException:
                if attempt == 99:
                    raise
                time.sleep(0.1)
        yield {"control": base, "cdn": f"http://{name}:4330/configuration", "site": f"java-optout-{worker_id}.test"}


@pytest.fixture
def library_env(request: pytest.FixtureRequest, standalone_backend: dict[str, str] | None):
    env = dict(request.param)
    if standalone_backend is not None:
        env.update(
            {
                "DD_FEATURE_FLAGS_CONFIGURATION_SOURCE": "agentless",
                "DD_FEATURE_FLAGS_CONFIGURATION_SOURCE_AGENTLESS_BASE_URL": standalone_backend["cdn"],
                "DD_FEATURE_FLAGS_CONFIGURATION_SOURCE_AGENTLESS_POLL_INTERVAL_SECONDS": "1",
                "DD_API_KEY": "java-optout-local-test-key",
                "DD_SITE": standalone_backend["site"],
                "DD_INSTRUMENTATION_TELEMETRY_ENABLED": "false",
                "JAVA_TOOL_OPTIONS": "-Djavax.net.ssl.trustStore=/opt/java-optout-trust.p12 -Djavax.net.ssl.trustStorePassword=local-test-password",
            }
        )
    return env


def _allocation(key: str, *, do_log: bool | None, activation: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"key": key, "doLog": do_log, "splits": [{"variationKey": key, "shards": []}]}
    if activation is not None:
        result["randomizationActivatedAt"] = activation
    return result


def _flag(key: str, allocations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "key": key,
        "enabled": True,
        "variationType": "STRING",
        "variations": {name: {"key": name, "value": name} for name in ["experiment", "ordinary"]},
        "allocations": allocations,
    }


def _config(flags: dict[str, Any]) -> dict[str, Any]:
    root: dict[str, Any] = json.loads((Path(__file__).parent / "ffe-system-test-data" / "ufc-config.json").read_text())
    root["flags"] = flags
    root["observeFullEvaluationData"] = True
    return root


def _install(
    test_agent: TestAgentAPI,
    test_library: APMLibrary,
    config: dict[str, Any],
    standalone_backend: dict[str, str] | None,
) -> None:
    if standalone_backend is not None:
        requests.post(
            standalone_backend["control"] + "/configuration",
            json={"data": {"type": "universal-flag-configuration", "attributes": config}},
            timeout=5,
        ).raise_for_status()
        assert test_library.ffe_start()
        return
    config_id = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    test_agent.set_remote_config(path=f"datadog/2/FFE_FLAGS/{config_id}/config", payload=config)
    state = test_agent.wait_for_rc_apply_state(
        "FFE_FLAGS", state=RemoteConfigApplyState.ACKNOWLEDGED, config_id=config_id, wait_loops=500, clear=True
    )
    assert state["apply_state"] == RemoteConfigApplyState.ACKNOWLEDGED.value
    assert test_library.ffe_start()


def _evaluate(test_library: APMLibrary, flag: str, attributes: dict[str, Any]) -> dict[str, Any]:
    for _ in range(100):
        result = test_library.ffe_evaluate(
            flag=flag,
            variation_type="STRING",
            default_value="default",
            targeting_key="optout-runtime-subject",
            attributes=attributes,
        )
        if result.get("errorCode") != "PROVIDER_NOT_READY":
            return result
        time.sleep(0.1)
    return result


def _events(
    test_agent: TestAgentAPI, route: str, field: str, standalone_backend: dict[str, str] | None
) -> list[dict[str, Any]]:
    if standalone_backend is not None:
        response = requests.get(standalone_backend["control"] + "/events", timeout=5)
        response.raise_for_status()
        return [
            event
            for request in response.json()
            if request["path"].endswith("/" + route)
            for event in request["body"][field]
        ]
    events: list[dict[str, Any]] = []
    for request in test_agent.requests():
        if not request["url"].endswith("/" + route):
            continue
        body = base64.b64decode(request["body"])
        if body.startswith(b"\x1f\x8b"):
            body = gzip.decompress(body)
        events.extend(json.loads(body)[field])
    return events


@scenarios.parametric
@features.not_reported
class Test_Java_OptOut_Contract:
    @pytest.mark.parametrize(
        ("library_env", "mode"),
        [({**BASE_ENV, "DD_FEATURE_FLAGS_EXPERIMENTATION_OPT_OUT_MODE": mode}, mode) for mode in MODES],
        indirect=["library_env"],
    )
    def test_policy(
        self, test_agent: TestAgentAPI, test_library: APMLibrary, mode: str, standalone_backend: dict[str, str] | None
    ) -> None:
        cases = [case for case in CASES if case["args"]["mode"] == mode]
        assert len(cases) == 30
        timestamps = {
            "missing": None,
            "invalid": "bad",
            "before": "2026-10-19T11:59:59.999999999Z",
            "equal": CUTOFF,
            "after": "2026-10-19T12:00:00.000000001Z",
        }
        flags = {}
        for index, case in enumerate(cases):
            args = case["args"]
            key = f"policy-{index}"
            flags[key] = _flag(
                key,
                [
                    _allocation("experiment", do_log=args["doLog"], activation=timestamps[args["activation"]]),
                    _allocation("ordinary", do_log=False),
                ],
            )
        flags["unreachable"] = _flag(
            "unreachable",
            [_allocation("ordinary", do_log=False), _allocation("experiment", do_log=True, activation="bad")],
        )
        for name in ["omitted", "null"]:
            allocation = _allocation("experiment", do_log=None)
            if name == "omitted":
                del allocation["doLog"]
            flags[name] = _flag(name, [allocation, _allocation("ordinary", do_log=False)])
        _install(test_agent, test_library, _config(flags), standalone_backend)
        observations = []
        for index, case in enumerate(cases):
            args, expected = case["args"], case["expected"]
            attrs = (
                {} if args["attribute"] == "absent" else {ATTRIBUTE: CUTOFF if args["attribute"] == "valid" else "bad"}
            )
            result = _evaluate(test_library, f"policy-{index}", attrs)
            assert (result.get("errorCode") or "NONE") == expected["error"], (case["id"], result)
            expected_value = (
                "default" if expected["error"] != "NONE" else "ordinary" if expected["exclude"] else "experiment"
            )
            assert result["value"] == expected_value, (case["id"], result)
            observations.append({"id": case["id"], "result": result})
        (Path(os.environ["JAVA_OPTOUT_RECEIPT_DIR"]) / f"policy-{mode}.json").write_text(
            json.dumps(observations, indent=2) + "\n"
        )
        for attrs in [{}, {ATTRIBUTE: CUTOFF}]:
            result = _evaluate(test_library, "unreachable", attrs)
            invalid = mode == "future_experiments_only" and bool(attrs)
            assert result["value"] == ("default" if invalid else "ordinary"), result
            assert result.get("errorCode") == ("PARSE_ERROR" if invalid else None), result
        for name in ["omitted", "null"]:
            result = _evaluate(test_library, name, {ATTRIBUTE: CUTOFF})
            assert result["value"] == "experiment", result
            assert not result.get("errorCode"), result

    @pytest.mark.parametrize(
        "library_env",
        [{**BASE_ENV, "DD_FEATURE_FLAGS_EXPERIMENTATION_OPT_OUT_MODE": "future_experiments_only"}],
        indirect=True,
    )
    @pytest.mark.parametrize("suppressed", [False, True])
    def test_retained_exposure_and_telemetry(
        self,
        test_agent: TestAgentAPI,
        test_library: APMLibrary,
        standalone_backend: dict[str, str] | None,
        *,
        suppressed: bool,
    ) -> None:
        retained = _flag(
            "retained", [_allocation("experiment", do_log=True, activation="2026-10-19T11:59:59.999999999Z")]
        )
        control = _flag("control", [_allocation("ordinary", do_log=False)])
        _install(test_agent, test_library, _config({"retained": retained, "control": control}), standalone_backend)
        for _ in range(3):
            result = _evaluate(
                test_library, "retained", {ATTRIBUTE: CUTOFF, "dd_evaluation_telemetry_opt_out": suppressed}
            )
            assert result["value"] == "experiment", result
            assert not result.get("errorCode"), result
        assert _evaluate(test_library, "control", {})["value"] == "ordinary"
        start = time.monotonic()
        while time.monotonic() - start < 30:
            exposures = [
                event
                for event in _events(test_agent, "exposures", "exposures", standalone_backend)
                if event["flag"]["key"] == "retained"
            ]
            evaluations = _events(test_agent, "flagevaluation", "flagEvaluations", standalone_backend)
            if (
                exposures
                and any(event["flag"]["key"] == "control" for event in evaluations)
                and time.monotonic() - start > 12
            ):
                break
            time.sleep(0.5)
        assert len(exposures) == 1, exposures
        assert exposures[0]["allocation"]["key"] == "experiment", exposures
        assert any(event["flag"]["key"] == "control" for event in evaluations), evaluations
        retained_events = [event for event in evaluations if event["flag"]["key"] == "retained"]
        assert sum(event["evaluation_count"] for event in retained_events) == (0 if suppressed else 3), retained_events

        (Path(os.environ["JAVA_OPTOUT_RECEIPT_DIR"]) / f"intake-{suppressed}.json").write_text(
            json.dumps({"suppressed": suppressed, "exposures": exposures, "evaluations": evaluations}, indent=2) + "\n"
        )
