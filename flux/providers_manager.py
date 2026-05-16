import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".projectflux_providers.json"


class ProvidersManager:

    def __init__(self):
        self.data = self.load()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text())
            except:
                return {}
        return {}

    def save(self):
        CONFIG_FILE.write_text(json.dumps(self.data, indent=2))

    def set_key(self, provider, key):
        if provider not in self.data:
            self.data[provider] = {}
        self.data[provider]["api_key"] = key
        self.save()

    def get_key(self, provider):
        return self.data.get(provider, {}).get("api_key")

    def list_providers(self):
        return list(self.data.keys())

    def set_active(self, provider):
        self.data["active"] = provider
        self.save()

    def get_active(self):
        return self.data.get("active")
