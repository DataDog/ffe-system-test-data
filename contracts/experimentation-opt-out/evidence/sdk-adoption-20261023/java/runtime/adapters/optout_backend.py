"""Test-only HTTP configuration and HTTPS intake. Uses no production credentials."""
import json
import ssl
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

state = {"configuration": None, "events": []}
lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        with lock:
            if self.path == "/configuration":
                self.respond(200 if state["configuration"] is not None else 503, state["configuration"])
            elif self.path == "/events":
                self.respond(200, state["events"])
            else:
                self.respond(404, {})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        with lock:
            if self.path == "/configuration" and self.server.server_port == 4330:
                state["configuration"] = body
            elif self.path in ("/api/v2/exposures", "/api/v2/flagevaluation") and self.server.server_port == 443:
                assert self.headers["dd-api-key"] == "java-optout-local-test-key"
                state["events"].append({"path": self.path, "body": body})
            else:
                self.respond(404, {})
                return
            self.respond(200, {})


plain = ThreadingHTTPServer(("0.0.0.0", 4330), Handler)
tls = ThreadingHTTPServer(("0.0.0.0", 443), Handler)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("/server-cert.pem", "/server-key.pem")
tls.socket = context.wrap_socket(tls.socket, server_side=True)
threading.Thread(target=plain.serve_forever, daemon=True).start()
tls.serve_forever()
