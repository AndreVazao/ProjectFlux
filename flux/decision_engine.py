import re


class DecisionEngine:

    def analyze(self, context, logs=""):
        text = (context + "\n" + logs).lower()

        # 🔥 DETEÇÃO DE PROBLEMAS
        if "error" in text or "failed" in text:
            return {
                "action": "fix",
                "reason": "Detected failure in logs"
            }

        # 🚀 DEPLOY
        if "build success" in text or "ready" in text:
            return {
                "action": "deploy",
                "reason": "Build is successful"
            }

        # 🔄 SYNC
        if "outdated" in text or "behind" in text:
            return {
                "action": "sync",
                "reason": "Repo outdated"
            }

        return {
            "action": "none",
            "reason": "No action needed"
        }

    def decide(self, policy_output):
        actions = []

        for item in policy_output:
            if item == "reduce_load":
                actions.append(("scale_down", None))

            elif isinstance(item, tuple):
                action, node = item

                if action == "restart_node":
                    actions.append(("restart", node))

                elif action == "failover":
                    actions.append(("failover", node))

        return actions
