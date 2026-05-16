import json
from pathlib import Path


class LearningEngine:

    def __init__(self):
        self.file = Path("flux_learning.json")
        self.data = self._load()

    def _load(self):
        if self.file.exists():
            try:
                return json.loads(self.file.read_text())
            except:
                return {}
        return {}

    def _save(self):
        self.file.write_text(json.dumps(self.data, indent=2))

    # -------------------------
    # REGISTAR RESULTADO
    # -------------------------

    def record(self, repo, action, success):
        if repo not in self.data:
            self.data[repo] = {}

        if action not in self.data[repo]:
            self.data[repo][action] = {"success": 0, "fail": 0}

        if success:
            self.data[repo][action]["success"] += 1
        else:
            self.data[repo][action]["fail"] += 1

        self._save()

    # -------------------------
    # PRIORIDADE DINÂMICA
    # -------------------------

    def get_priority(self, repo, action):
        stats = self.data.get(repo, {}).get(action, None)

        if not stats:
            return 1  # default

        success = stats["success"]
        fail = stats["fail"]

        total = success + fail
        if total == 0:
            return 1

        score = success / total

        return score  # quanto maior, mais prioridade
