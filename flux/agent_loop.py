import time
from flux.ai_engine import AIEngine
from flux.memory_engine import MemoryEngine
from flux.sync_engine import SyncEngine
from flux.evolution_engine import EvolutionEngine
from flux.deploy_manager import DeployManager
from flux.fix_engine import FixEngine
from flux.repo_registry import RepoRegistry
from flux.providers import ProviderManager


class AgentLoop:

    def __init__(self):
        self.ai = AIEngine()
        self.memory = MemoryEngine()
        self.registry = RepoRegistry()
        self.providers = ProviderManager()
        self.deploy = DeployManager(self.providers)
        self.running = False

    def start(self, interval=60):
        self.running = True
        return self._loop(interval)

    def stop(self):
        self.running = False
        return "🛑 Agent stopped"

    def _loop(self, interval):
        results = []

        while self.running:

            for repo_id, info in self.registry.get_all().items():

                repo_name = info["name"]
                repo_path = info["path"]

                try:
                    decision = self.ai.think(repo_name)

                    action = decision.get("action")

                    if action == "fix":
                        result = FixEngine.run(repo_path, "")
                    elif action == "deploy":
                        result = self.deploy.auto_deploy_smart(repo_name, repo_path)
                    elif action == "sync":
                        result = SyncEngine.sync(repo_path)
                    elif action == "evolve":
                        result = EvolutionEngine().evolve(repo_path)
                    else:
                        result = "No action"

                    self.memory.save_decision(
                        repo_name,
                        f"{action} → {decision.get('reason')}"
                    )

                    results.append(f"{repo_name}: {action}")

                except Exception as e:
                    results.append(f"{repo_name}: error {str(e)}")

            time.sleep(interval)

        return "\n".join(results)
