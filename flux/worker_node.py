from fastapi import FastAPI
from pydantic import BaseModel

from flux.sync_engine import SyncEngine
from flux.evolution_engine import EvolutionEngine
from flux.deploy_manager import DeployManager
from flux.fix_engine import FixEngine
from flux.providers_manager import ProvidersManager

app = FastAPI()


class Task(BaseModel):
    action: str
    repo: str
    path: str


@app.post("/execute")
def execute(task: Task):

    try:
        if task.action == "sync":
            result = SyncEngine.sync(task.path)

        elif task.action == "fix":
            result = FixEngine.run(task.path, "")

        elif task.action == "evolve":
            # EvolutionEngine().evolve normally takes a directory of repos
            # but here we pass the path from the task.
            result = EvolutionEngine().evolve(task.path)

        elif task.action == "deploy":
            providers = ProvidersManager()
            result = DeployManager(providers).auto_deploy_smart(task.repo, task.path)

        else:
            result = "unknown action"

        return {"status": "ok", "result": result}

    except Exception as e:
        return {"status": "error", "error": str(e)}
