import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".projectflux_providers.json"


class ProviderManager:

    def __init__(self):
        self.providers = self.load()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text())
            except:
                return {}
        return {}

    def save(self):
        CONFIG_FILE.write_text(json.dumps(self.providers, indent=2))

    def get(self, name):
        return self.providers.get(name)

    def set(self, name, key):
        self.providers[name] = key
        self.save()
