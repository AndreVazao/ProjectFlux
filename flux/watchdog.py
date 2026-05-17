import time
import requests


class Watchdog:

    def __init__(self, url):
        self.url = url

    def run(self):
        while True:
            try:
                requests.get(f"{self.url}/status", timeout=3)
            except:
                # tenta reiniciar via endpoint remoto
                try:
                    requests.post(f"{self.url}/start", timeout=3)
                except:
                    pass

            time.sleep(5)
