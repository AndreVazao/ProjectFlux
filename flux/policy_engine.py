class PolicyEngine:

    def evaluate(self, metrics, cost):
        decisions = []

        # Rule 1: High cost threshold
        if cost.get("cost", 0) > 1.5:
            decisions.append("reduce_load")

        # Rule 2: Node status monitoring
        for n in metrics.get("nodes", []):
            if n.get("status") == "down":
                decisions.append(("restart_node", n.get("node")))

        # Rule 3: Latency monitoring
        for n in metrics.get("nodes", []):
            status = n.get("status")
            if isinstance(status, dict):
                if status.get("latency", 0) > 2000:
                    decisions.append(("move_workload", n.get("node")))

        return decisions
