from flux.agents.dev_agent import DevAgent
from flux.agents.fix_agent import FixAgent
from flux.agents.deploy_agent import DeployAgent
from flux.agents.architect_agent import ArchitectAgent
from flux.repo_registry import RepoRegistry
from flux.memory_engine import MemoryEngine


class SwarmOrchestrator:

    def __init__(self):
        self.registry = RepoRegistry()
        self.memory = MemoryEngine()

        self.dev = DevAgent()
        self.fix = FixAgent()
        self.deploy = DeployAgent()
        self.architect = ArchitectAgent()

    def run(self):
        results = []

        for repo_id, info in self.registry.get_all().items():

            name = info["name"]
            path = info["path"]

            try:
                # 🧠 arquitetura primeiro
                arch = self.architect.analyze(name, path)

                # 🔧 fix se necessário
                fix = self.fix.run(name, path, arch)

                # ⚙️ dev melhorias
                dev = self.dev.run(name, path, arch)

                # 🚀 deploy final
                deploy = self.deploy.run(name, path)

                summary = f"{name} → ARCH:{arch} | FIX:{fix} | DEV:{dev} | DEPLOY:{deploy}"

                self.memory.save_decision(name, summary)

                results.append(summary)

            except Exception as e:
                results.append(f"{name} → ERROR: {str(e)}")

        return "\n".join(results)
