from http.server import BaseHTTPRequestHandler, HTTPServer

class FluxServer(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self.send_html()

        elif self.path == "/status":
            self.send_json('{"status":"running"}')

        elif self.path == "/auto":
            self.send_json('{"action":"auto triggered"}')

        elif self.path == "/fix":
            self.send_json('{"action":"fix triggered"}')

        else:
            self.send_json('{"error":"unknown"}')

    def send_html(self):
        html = """
        <html>
        <head>
            <title>ProjectFlux Cockpit</title>
            <style>
                body { font-family: Arial; text-align:center; background:#111; color:#fff; }
                button {
                    width:80%;
                    padding:20px;
                    margin:15px;
                    font-size:20px;
                    border:none;
                    border-radius:10px;
                    background:#00ff88;
                    color:#000;
                }
            </style>
        </head>
        <body>
            <h1>🚀 ProjectFlux</h1>
            <button onclick="fetch('/auto')">AUTO MODE</button>
            <button onclick="fetch('/fix')">AUTO FIX</button>
            <button onclick="fetch('/status').then(r=>r.text()).then(alert)">STATUS</button>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(data.encode())


def start_server(port=5000):
    server = HTTPServer(("0.0.0.0", port), FluxServer)
    print(f"Server running on port {port}")
    server.serve_forever()
