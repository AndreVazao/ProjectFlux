import json
from pathlib import Path


class LearningEngine:

    def __init__(self):
        self.file = Path("flux_learning.json")
        self.state_file = Path("flux_state.json")
        self.data = self._load(self.file)
        self.state = self._load(self.state_file)

    def _load(self, file_path):
        if file_path.exists():
            try:
                return json.loads(file_path.read_text())
            except:
                return {}
        return {}

    def _save(self, data, file_path):
        file_path.write_text(json.dumps(data, indent=2))

    # -------------------------
    # REGISTAR RESULTADO (Swarm)
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

        self._save(self.data, self.file)

    # -------------------------
    # PRIORIDADE DINÂMICA (Swarm)
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

    # -------------------------
    # CONSCIÊNCIA OPERACIONAL
    # -------------------------

    def update(self, metrics, decisions):
        self.state["last_metrics"] = metrics
        self.state["last_decisions"] = decisions
        self._save(self.state, self.state_file)
