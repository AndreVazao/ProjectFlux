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
