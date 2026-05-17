from flux.metrics_aggregator import MetricsAggregator
from flux.cost_engine import CostEngine
from flux.policy_engine import PolicyEngine
from flux.decision_engine import DecisionEngine
from flux.action_engine import ActionEngine
from flux.learning_engine import LearningEngine


class Consciousness:

    def __init__(self):
        # Localhost and Tailscale IPs
        self.nodes = [
            "http://127.0.0.1:8000",
            "http://100.69.225.48:8000",
            "http://100.109.173.115:8000"
        ]

        self.metrics = MetricsAggregator(self.nodes)
        self.cost = CostEngine()
        self.policy = PolicyEngine()
        self.decision = DecisionEngine()
        self.action = ActionEngine()
        self.learning = LearningEngine()

    def run_cycle(self):

        m = self.metrics.collect()
        c = self.cost.estimate()

        p = self.policy.evaluate(m, c)
        d = self.decision.decide(p)

        r = self.action.run(d)

        self.learning.update(m, d)

        return {
            "metrics": m,
            "cost": c,
            "decisions": d,
            "results": r
        }
