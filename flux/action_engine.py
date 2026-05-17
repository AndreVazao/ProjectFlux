import requests
from flux.config import logger

class ActionEngine:

    def run(self, actions):
        results = []

        for action_tuple in actions:
            if isinstance(action_tuple, str):
                action = action_tuple
                node = None
            else:
                action, node = action_tuple

            try:
                if action == "restart" and node:
                    logger.info(f"ActionEngine: Restarting node {node}")
                    requests.post(f"{node}/restart", timeout=3)

                elif action == "failover" and node:
                    logger.info(f"ActionEngine: Failing over workload from {node}")
                    requests.post(f"{node}/drain", timeout=3)

                elif action == "scale_down":
                    logger.info("ActionEngine: Scaling down workload")
                    # Integration with swarm could go here
                    pass

                results.append(f"{action}:{node}")

            except Exception as e:
                logger.error(f"ActionEngine Error for {action} on {node}: {e}")
                results.append(str(e))

        return results
