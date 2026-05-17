import subprocess
import time
import os
import sys
from datetime import datetime

LOG_DIR = "logs"
BACKEND_CMD = [sys.executable, "-m", "flux.server"]

os.makedirs(LOG_DIR, exist_ok=True)


def log(msg):
    with open(os.path.join(LOG_DIR, "launcher.log"), "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")


def start_backend():
    log("Starting backend...")
    return subprocess.Popen(
        BACKEND_CMD,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


def monitor():
    while True:
        proc = start_backend()

        while True:
            time.sleep(2)

            if proc.poll() is not None:
                log("Backend crashed. Restarting...")
                break

            # opcional: watchdog simples
            try:
                import requests
                requests.get("http://127.0.0.1:8000/status", timeout=2)
            except:
                log("Healthcheck failed. Restarting backend...")
                proc.kill()
                break


def start_ui():
    from flux.ui import start_app
    start_app()


if __name__ == "__main__":
    import threading

    t = threading.Thread(target=monitor, daemon=True)
    t.start()

    start_ui()
