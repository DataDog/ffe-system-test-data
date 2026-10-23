FROM ghcr.io/datadog/dd-apm-test-agent/ddapm-test-agent:v1.67.0
COPY add_test_agent_capture.py /tmp/add_test_agent_capture.py
RUN python /tmp/add_test_agent_capture.py
