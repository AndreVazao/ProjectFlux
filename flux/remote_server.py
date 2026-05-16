from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
import threading
import os

from flux.workflow_generator import WorkflowGenerator
from flux.git_manager import GitManager
from flux.fix_engine import FixEngine
from flux.github_manager import GitHubManager

# ⚠️ define aqui o caminho da repo local no PC
REPO_PATH = os.path.join("C:\\", "ProgramasGodMode", "ProjectFlux")


class FluxServer(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path == "/":
                self.send_html()

            elif self.path == "/status":
                self.send_json({"status": "running"})

            elif self.path == "/auto":
                threading.Thread(target=self.auto_mode, daemon=True).start()
                self.send_json({"result": "AUTO MODE started"})

            elif self.path == "/fix":
                threading.Thread(target=self.auto_fix, daemon=True).start()
                self.send_json({"result": "AUTO FIX started"})

            else:
                self.send_json({"error": "unknown route"})
        except Exception as e:
            print(f"Server error: {e}")
            try:
                self.send_json({"error": str(e)})
            except:
                pass

    # -------------------------
    # REAL ACTIONS
    # -------------------------

    def auto_mode(self):
        try:
            WorkflowGenerator.auto(REPO_PATH)
            GitManager.commit_all(REPO_PATH, "auto workflow (remote)")
            GitManager.push(REPO_PATH)
            print("AUTO MODE DONE")
        except Exception as e:
            print("AUTO ERROR:", e)

    def auto_fix(self):
        try:
            github = GitHubManager()
            logs_url = github.get_latest_logs("ProjectFlux")
            if not logs_url:
                print("No logs found for ProjectFlux")
                return

            import requests
            logs = requests.get(logs_url, timeout=15).text

            result = FixEngine.run(REPO_PATH, logs)

            GitManager.commit_all(REPO_PATH, f"auto fix: {result['issue']}")
            GitManager.push(REPO_PATH)

            print("AUTO FIX DONE")
        except Exception as e:
            print("FIX ERROR:", e)

    # -------------------------
    # UI
    # -------------------------

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
        self.wfile.write(json.dumps(data).encode())


def start_server(port=5000):
    try:
        server = HTTPServer(("0.0.0.0", port), FluxServer)
        print(f"Server running on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Failed to start server: {e}")
