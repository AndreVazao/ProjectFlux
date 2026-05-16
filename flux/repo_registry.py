import json
from pathlib import Path

REGISTRY_FILE = Path.home() / ".projectflux_registry.json"


class RepoRegistry:

    def __init__(self):
        self.data = self.load()

    def load(self):
        if REGISTRY_FILE.exists():
            try:
                return json.loads(REGISTRY_FILE.read_text())
            except:
                return {}
        return {}

    def save(self):
        REGISTRY_FILE.write_text(json.dumps(self.data, indent=2))

    # -------------------------
    # REGISTER
    # -------------------------

    def register(self, repo_name, repo_id, local_path):
        self.data[repo_id] = {
            "name": repo_name,
            "path": local_path
        }
        self.save()

    def get_by_id(self, repo_id):
        return self.data.get(repo_id)

    def exists(self, repo_id):
        return repo_id in self.data

    def get_all(self):
        return self.data
