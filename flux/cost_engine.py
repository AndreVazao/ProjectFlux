import psutil

class CostEngine:
    def estimate(self):
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent

            # Simple cost model based on resource usage
            cost = cpu * 0.01 + mem * 0.005

            return {
                "cpu": cpu,
                "mem": mem,
                "cost": round(cost, 3)
            }
        except Exception:
            return {"cpu": 0, "mem": 0, "cost": 0}
