from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class FluxServer(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/status":
            self._send({"status": "running"})

        elif self.path == "/auto":
            self._send({"action": "auto workflow trigger"})

        elif self.path == "/fix":
            self._send({"action": "auto fix trigger"})

        else:
            self._send({"error": "unknown route"})

    def _send(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def start_server(port=5000):
    server = HTTPServer(("0.0.0.0", port), FluxServer)
    print(f"Server running on port {port}")
    server.serve_forever()
