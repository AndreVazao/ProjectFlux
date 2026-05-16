from flux.ui import start_app
from flux.remote_server import start_server
import threading


if __name__ == "__main__":
    # 🚀 Arranca servidor remoto (cockpit)
    threading.Thread(target=start_server, daemon=True).start()

    # 🖥️ Arranca UI normal
    start_app()
