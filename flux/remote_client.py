import requests


class RemoteClient:

    def __init__(self, base_url):
        self.base_url = base_url

    def start_ai(self):
        return requests.post(f"{self.base_url}/start").json()

    def stop_ai(self):
        return requests.post(f"{self.base_url}/stop").json()

    def status(self):
        return requests.get(f"{self.base_url}/status").json()

    def command(self, action):
        return requests.post(
            f"{self.base_url}/command",
            json={"action": action}
        ).json()
