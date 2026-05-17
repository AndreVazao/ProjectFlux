import sys
import os
import threading
import uvicorn
import logging
import time
from flux.watchdog import Watchdog
from flux.consciousness import Consciousness

# 🔥 FIX PYINSTALLER PATH & IMPORTS
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

if base_path not in sys.path:
    sys.path.insert(0, base_path)

from flux.config import logger

def start_fastapi():
    logger.info("Starting FastAPI Server...")
    try:
        # We use the string import format so uvicorn can handle reloads/threading better
        # In frozen mode, we point directly to the app object to avoid module resolution issues
        if getattr(sys, 'frozen', False):
            from flux.server import app
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        else:
            uvicorn.run("flux.server:app", host="0.0.0.0", port=8000, log_level="info", reload=False)
    except Exception as e:
        logger.error(f"FastAPI Server Crash: {e}", exc_info=True)

def start_watchdog():
    logger.info("Starting Global Watchdog...")
    Watchdog("http://127.0.0.1:8000").run()

def consciousness_loop():
    logger.info("Starting Operational Consciousness...")
    c = Consciousness()
    while True:
        try:
            result = c.run_cycle()
            logger.debug(f"CONSCIOUSNESS CYCLE: {result}")
        except Exception as e:
            logger.error(f"Consciousness Cycle Error: {e}")
        time.sleep(10)

def main():
    logger.info("ProjectFlux Starting...")

    try:
        from flux.ui import start_app
    except ImportError as e:
        logger.critical(f"Critical Error: Missing module: {e}")
        print(f"Critical Error: Missing module: {e}")
        sys.exit(1)

    # Start the remote control server in a background thread
    server_thread = threading.Thread(target=start_fastapi, daemon=True, name="FastAPI-Thread")
    server_thread.start()

    # Give the server a second to initialize
    time.sleep(1)
    if not server_thread.is_alive():
        logger.error("FastAPI Server thread died immediately after start.")

    # Start Watchdog and Consciousness
    threading.Thread(target=start_watchdog, daemon=True, name="Watchdog-Thread").start()
    threading.Thread(target=consciousness_loop, daemon=True, name="Consciousness-Thread").start()

    try:
        # Start the main PyQt6 application
        logger.info("Launching UI...")
        start_app()
    except Exception as e:
        logger.critical(f"Critical Error: App crashed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("ProjectFlux Exiting.")

if __name__ == "__main__":
    main()
