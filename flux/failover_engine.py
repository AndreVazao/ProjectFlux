import requests
import time


class FailoverEngine:

    def __init__(self, nodes):
        self.nodes = nodes
        self.current = nodes[0]

    def check(self, node):
        try:
            r = requests.get(f"{node}/status", timeout=2)
            return r.status_code == 200
        except:
            return False

    def get_active(self):
        for node in self.nodes:
            if self.check(node):
                self.current = node
                return node

        return None

    def wait_for_node(self):
        while True:
            active = self.get_active()
            if active:
                return active
            time.sleep(3)
