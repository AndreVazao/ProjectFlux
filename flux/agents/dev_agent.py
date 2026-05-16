from flux.evolution_engine import EvolutionEngine


class DevAgent:

    def run(self, repo, path, context):
        try:
            return EvolutionEngine().evolve(path)
        except:
            return "no_changes"
