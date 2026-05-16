from flux.ideation_engine import IdeationEngine
from flux.scoring_engine import ScoringEngine
from flux.execution_engine import ExecutionEngine
from flux.metrics_engine import MetricsEngine
from flux.ceo_engine import CEOEngine


class CompanyOrchestrator:

    def __init__(self):
        self.ideation = IdeationEngine()
        self.scoring = ScoringEngine()
        self.execution = ExecutionEngine()
        self.metrics = MetricsEngine()
        self.ceo = CEOEngine()

    def run(self):

        ideas = self.ideation.generate()
        ranked = self.scoring.rank(ideas)

        results = []

        # executa só top 2 para controlo
        for idea in ranked[:2]:
            try:
                result = self.execution.execute(idea)
                self.metrics.record(idea["name"], result)
                results.append(result)
            except Exception as e:
                results.append(f"error:{idea['name']} -> {str(e)}")

        decisions = self.ceo.decide(self.metrics.summary())

        return {
            "executed": results,
            "decisions": decisions
        }
