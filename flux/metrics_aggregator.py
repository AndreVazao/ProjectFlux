import time
import requests

class MetricsAggregator:
    def __init__(self, nodes):
        self.nodes = nodes

    def collect(self):
        data = []

        for node in self.nodes:
            try:
                r = requests.get(f"{node}/status", timeout=2)
                data.append({
                    "node": node,
                    "status": r.json()
                })
            except:
                data.append({
                    "node": node,
                    "status": "down"
                })

        return {
            "timestamp": time.time(),
            "nodes": data
        }
