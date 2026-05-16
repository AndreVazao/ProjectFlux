import sys
import os

# 🔥 FIX PYINSTALLER PATH
if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(__file__))

from flux.ui import start_app
from flux.remote_server import start_server
import threading

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    start_app()
