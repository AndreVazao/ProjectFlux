import sys
import os
import threading
import uvicorn

# 🔥 FIX PYINSTALLER PATH
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    sys.path.append(base_path)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(base_path)

def start_fastapi():
    try:
        uvicorn.run("flux.server:app", host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"FastAPI Server Error: {e}")

def main():
    try:
        from flux.ui import start_app
    except ImportError as e:
        print(f"Critical Error: Missing module: {e}")
        sys.exit(1)

    # Start the remote control server in a background thread
    server_thread = threading.Thread(target=start_fastapi, daemon=True)
    server_thread.start()

    try:
        # Start the main PyQt6 application
        start_app()
    except Exception as e:
        print(f"Critical Error: App crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
