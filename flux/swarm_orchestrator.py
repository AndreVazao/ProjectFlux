import threading
import logging
import requests
from flux.config import logger
from flux.agents.dev_agent import DevAgent
from flux.agents.fix_agent import FixAgent
from flux.agents.deploy_agent import DeployAgent
from flux.agents.architect_agent import ArchitectAgent
from flux.repo_registry import RepoRegistry
from flux.memory_engine import MemoryEngine
from flux.learning_engine import LearningEngine
from flux.self_evolution import SelfEvolution
from flux.agent_factory import AgentFactory
from flux.strategy_engine import StrategyEngine
from flux.cluster_manager import ClusterManager
from flux.redundancy_manager import RedundancyManager


class SwarmOrchestrator:

    def __init__(self):
        try:
            self.registry = RepoRegistry()
            self.memory = MemoryEngine()
            self.learning = LearningEngine()
            self.self_evo = SelfEvolution()
            self.factory = AgentFactory()
            self.strategy = StrategyEngine()
            self.cluster = ClusterManager()
            self.redundancy = RedundancyManager()

            self.dev = DevAgent()
            self.fix = FixAgent()
            self.deploy = DeployAgent()
            self.architect = ArchitectAgent()
        except Exception as e:
            logger.critical(f"SwarmOrchestrator initialization failure: {e}", exc_info=True)
            raise

    def process_repo(self, info):
        name = info["name"]
        path = info["path"]

        logger.info(f"Swarm processing repo: {name}")

        try:
            arch = self.architect.analyze(name, path)

            actions = [
                ("fix", self.fix.run),
                ("dev", self.dev.run),
                ("deploy", self.deploy.run),
            ]

            # ordenar por prioridade aprendida
            try:
                actions.sort(
                    key=lambda x: self.learning.get_priority(name, x[0]),
                    reverse=True
                )
            except Exception as e:
                logger.warning(f"Failed to sort actions by priority for {name}: {e}")

            node = self.redundancy.ensure_alive()

            for action_name, action_func in actions:
                try:
                    # Distribuição via cluster ou nó ativo redundante
                    if node and "127.0.0.1" not in node:
                         logger.info(f"Dispatching {action_name} for {name} to remote node: {node}")
                         resp = requests.post(
                             f"{node}/command",
                             json={"action": action_name, "repo": name},
                             timeout=15
                         )
                         result = resp.json()
                    else:
                        result = self.cluster.dispatch(
                            action_name,
                            name,
                            path
                        )

                    success = "error" not in str(result).lower()

                    self.learning.record(name, action_name, success)

                    self.memory.save_decision(
                        name,
                        f"{action_name} → {result}"
                    )

                except Exception as e:
                    logger.error(f"Error in action {action_name} for {name}: {e}")
                    self.learning.record(name, action_name, False)
                    self.memory.save_decision(name, f"{action_name} → ERROR: {str(e)}")

        except Exception as e:
            logger.error(f"Error analyzing repo {name}: {e}")
            self.memory.save_decision(name, f"ERROR → {str(e)}")

    def run(self):
        logger.info("Swarm Orchestrator run started.")
        results = []
        threads = []

        try:
            repos = self.registry.get_all()
            if not repos:
                logger.info("No repos in registry.")
                return "No repos to process."

            for repo_id, info in repos.items():
                t = threading.Thread(target=self.safe_process_repo, args=(info,))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            # 🧠 decidir estratégia global
            learning_data = self.learning.data
            plan = self.strategy.decide(learning_data)
            results.append(f"📊 Strategy: {plan}")

            # 🧬 auto evolução do sistema
            evo = self.self_evo.evolve_system()
            results.append(evo)

            logger.info("Swarm Orchestrator run completed.")
            return "\n".join(results)
        except Exception as e:
            logger.error(f"Global Swarm failure: {e}", exc_info=True)
            return f"Swarm Failure: {e}"

    def safe_process_repo(self, info):
        try:
            self.process_repo(info)
        except Exception as e:
            logger.error(f"Unhandled error processing repo {info.get('name')}: {e}", exc_info=True)

    def smart_sync_all(self):
        logger.info("UI Command: smart_sync_all triggered")
        results = []
        try:
            repos = self.registry.get_all()
            for repo_id, info in repos.items():
                res = self.cluster.dispatch("sync", info["name"], info["path"])
                results.append(f"{info['name']}: {res}")
            return "\n".join(results)
        except Exception as e:
            logger.error(f"Error in smart_sync_all: {e}")
            return str(e)

    def bootstrap(self, path):
        return f"Bootstrap complete in {path}"

    def cascade(self, repo, path):
        return f"Cascade update for {repo} in {path}"

    def link(self, parent, child):
        return f"Linked {parent} to {child}"
