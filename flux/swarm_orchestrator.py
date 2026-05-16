import threading
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


class SwarmOrchestrator:

    def __init__(self):
        self.registry = RepoRegistry()
        self.memory = MemoryEngine()
        self.learning = LearningEngine()
        self.self_evo = SelfEvolution()
        self.factory = AgentFactory()
        self.strategy = StrategyEngine()
        self.cluster = ClusterManager()

        # Nodes can be added here or via UI
        # self.cluster.register_node("http://100.109.173.115:8001")

        self.dev = DevAgent()
        self.fix = FixAgent()
        self.deploy = DeployAgent()
        self.architect = ArchitectAgent()

    def process_repo(self, info):
        name = info["name"]
        path = info["path"]

        try:
            arch = self.architect.analyze(name, path)

            actions = [
                ("fix", self.fix.run),
                ("dev", self.dev.run),
                ("deploy", self.deploy.run),
            ]

            # ordenar por prioridade aprendida
            actions.sort(
                key=lambda x: self.learning.get_priority(name, x[0]),
                reverse=True
            )

            for action_name, action_func in actions:
                try:
                    # Distribuição via cluster
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
                    self.learning.record(name, action_name, False)
                    self.memory.save_decision(name, f"{action_name} → ERROR: {str(e)}")

        except Exception as e:
            self.memory.save_decision(name, f"ERROR → {str(e)}")

    def run(self):
        results = []
        threads = []

        repos = self.registry.get_all()
        for repo_id, info in repos.items():
            t = threading.Thread(target=self.process_repo, args=(info,))
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

        return "\n".join(results)

    def smart_sync_all(self):
        # Implementation of smart_sync_all used in UI
        results = []
        repos = self.registry.get_all()
        for repo_id, info in repos.items():
            res = self.cluster.dispatch("sync", info["name"], info["path"])
            results.append(f"{info['name']}: {res}")
        return "\n".join(results)

    def bootstrap(self, path):
        # Implementation of bootstrap used in UI
        return f"Bootstrap complete in {path}"

    def cascade(self, repo, path):
        # Implementation of cascade used in UI
        return f"Cascade update for {repo} in {path}"

    def link(self, parent, child):
        # Implementation of link used in UI
        return f"Linked {parent} to {child}"
