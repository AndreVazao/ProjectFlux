import json
import logging
from pathlib import Path

CONFIG_FILE = Path.home() / ".projectflux_providers.json"
logger = logging.getLogger("ProjectFlux.Providers")

class ProviderManager:
    def __init__(self):
        self.data = self.load()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text())
            except Exception as e:
                if logger.handlers:
                    logger.error(f"Failed to load providers config: {e}")
                return {}
        return {}

    def save(self):
        try:
            CONFIG_FILE.write_text(json.dumps(self.data, indent=2))
        except Exception as e:
            if logger.handlers:
                logger.error(f"Failed to save providers config: {e}")

    def get(self, name):
        val = self.data.get(name)
        if isinstance(val, dict):
            return val.get("api_key")
        return val

    def set(self, name, key):
        self.data[name] = key
        self.save()

    def set_key(self, provider, key):
        if provider not in self.data or not isinstance(self.data[provider], dict):
            self.data[provider] = {}
        self.data[provider]["api_key"] = key
        self.save()

    def get_key(self, provider):
        return self.get(provider)

    def list_providers(self):
        return [k for k in self.data.keys() if k != "active"]

    def set_active(self, provider):
        self.data["active"] = provider
        self.save()

    def get_active(self):
        return self.data.get("active")
