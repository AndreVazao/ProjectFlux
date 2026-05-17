import logging
import threading
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# Using absolute imports to ensure consistency
from flux.config import logger
from flux.swarm_orchestrator import SwarmOrchestrator
from flux.memory_engine import MemoryEngine

app = FastAPI(title="ProjectFlux Remote API")

# Global instances with lazy-ish initialization or error protection
try:
    swarm = SwarmOrchestrator()
except Exception as e:
    logger.error(f"Failed to initialize SwarmOrchestrator: {e}", exc_info=True)
    swarm = None

try:
    memory = MemoryEngine()
except Exception as e:
    logger.error(f"Failed to initialize MemoryEngine: {e}", exc_info=True)
    memory = None

running = False

class Command(BaseModel):
    action: str
    repo: Optional[str] = None

# -------------------------
# START SWARM
# -------------------------

@app.post("/start")
def start():
    global running

    if running:
        return {"status": "already running"}

    if swarm is None:
        return {"status": "error", "message": "SwarmOrchestrator not initialized"}

    running = True

    def run_loop():
        global running
        logger.info("Swarm loop started via API")
        try:
            while running:
                swarm.run()
        except Exception as e:
            logger.error(f"Swarm loop crashed: {e}", exc_info=True)
            running = False

    threading.Thread(target=run_loop, daemon=True, name="API-Swarm-Thread").start()

    return {"status": "started"}

# -------------------------
# STOP
# -------------------------

@app.post("/stop")
def stop():
    global running
    running = False
    logger.info("Swarm loop stopped via API")
    return {"status": "stopped"}

# -------------------------
# STATUS
# -------------------------

@app.get("/status")
def status():
    repos = {}
    if memory and memory.registry:
        repos = memory.registry.get_all()

    return {
        "running": running,
        "repos": list(repos.values()) if repos else []
    }

# -------------------------
# COMMAND EXECUTION
# -------------------------

@app.post("/command")
def command(cmd: Command):
    logger.info(f"API Command received: {cmd.action}")

    if swarm is None or memory is None:
        return {"error": "Internal components not initialized"}

    try:
        if cmd.action == "sync":
            return {"result": swarm.run()}

        if cmd.action == "memory":
            return {"result": memory.capture_commits()}

        if cmd.action == "snapshot":
            return {"result": memory.snapshot_all()}

        return {"error": "unknown command"}
    except Exception as e:
        logger.error(f"Error executing command {cmd.action}: {e}", exc_info=True)
        return {"error": str(e)}

@app.get("/")
def health():
    return {"status": "ok", "service": "ProjectFlux Backend"}
