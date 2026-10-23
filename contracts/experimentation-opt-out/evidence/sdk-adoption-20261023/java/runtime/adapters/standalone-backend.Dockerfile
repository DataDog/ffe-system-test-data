FROM ffe-java-optout-test-agent:a4d3dfb-v2
COPY optout_backend.py /optout_backend.py
COPY server-cert.pem /server-cert.pem
COPY server-key.pem /server-key.pem
