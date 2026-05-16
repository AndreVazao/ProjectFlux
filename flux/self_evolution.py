import os
from flux.ai_engine import AIEngine
from flux.memory_engine import MemoryEngine


class SelfEvolution:

    def __init__(self):
        self.ai = AIEngine()
        self.memory = MemoryEngine()

    def evolve_system(self):
        target_files = [
            "flux/swarm_orchestrator.py",
            "flux/agents/dev_agent.py",
            "flux/agents/fix_agent.py",
        ]

        results = []

        for file in target_files:
            if not os.path.exists(file):
                continue

            try:
                with open(file, "r", encoding="utf-8") as f:
                    code = f.read()

                decision = self.ai.think(
                    repo="ProjectFlux",
                    user_input=f"Improve this code:\n{code}"
                )

                if "steps" in decision and decision["steps"]:
                    improved = "\n".join(decision["steps"])

                    with open(file, "w", encoding="utf-8") as f:
                        f.write(improved)

                    results.append(f"✨ Improved {file}")

            except Exception as e:
                results.append(f"❌ {file}: {str(e)}")

        return "\n".join(results)
