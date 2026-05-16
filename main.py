import sys
import os
import threading

# 🔥 FIX PYINSTALLER PATH
if getattr(sys, 'frozen', False):
    # If the app is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS.
    base_path = sys._MEIPASS
    sys.path.append(base_path)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(base_path)

def main():
    try:
        from flux.ui import start_app
        from flux.remote_server import start_server
    except ImportError as e:
        print(f"Critical Error: Missing module: {e}")
        # In a GUI app, we might not have a console, but we try to print at least.
        sys.exit(1)

    try:
        # Start the remote control server in a background thread
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
    except Exception as e:
        print(f"Warning: Could not start remote server: {e}")

    try:
        # Start the main PyQt6 application
        start_app()
    except Exception as e:
        print(f"Critical Error: App crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
