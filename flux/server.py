from fastapi import FastAPI
from pydantic import BaseModel
import threading

from flux.swarm_orchestrator import SwarmOrchestrator
from flux.memory_engine import MemoryEngine

app = FastAPI()

swarm = SwarmOrchestrator()
memory = MemoryEngine()

running = False


class Command(BaseModel):
    action: str
    repo: str | None = None


# -------------------------
# START SWARM
# -------------------------

@app.post("/start")
def start():
    global running

    if running:
        return {"status": "already running"}

    running = True

    def run():
        while running:
            swarm.run()

    threading.Thread(target=run).start()

    return {"status": "started"}


# -------------------------
# STOP
# -------------------------

@app.post("/stop")
def stop():
    global running
    running = False
    return {"status": "stopped"}


# -------------------------
# STATUS
# -------------------------

@app.get("/status")
def status():
    return {
        "running": running,
        "repos": list(memory.registry.get_all().values())
    }


# -------------------------
# COMMAND EXECUTION
# -------------------------

@app.post("/command")
def command(cmd: Command):

    if cmd.action == "sync":
        return {"result": swarm.run()}

    if cmd.action == "memory":
        return {"result": memory.capture_commits()}

    if cmd.action == "snapshot":
        return {"result": memory.snapshot_all()}

    return {"error": "unknown command"}
