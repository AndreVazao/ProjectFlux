import time
from flux.failover_engine import FailoverEngine


class RedundancyManager:

    def __init__(self):
        # IPs correspond to the user's Tailscale setup
        self.failover = FailoverEngine([
            "http://127.0.0.1:8000",        # Local backend
            "http://100.69.225.48:8000",   # PC principal (Tailscale)
            "http://100.109.173.115:8000"  # fallback (Phone/Second PC Tailscale)
        ])

    def get_active_node(self):
        return self.failover.get_active()

    def ensure_alive(self):
        node = self.get_active_node()

        if not node:
            print("No active nodes. Waiting...")
            node = self.failover.wait_for_node()

        return node
