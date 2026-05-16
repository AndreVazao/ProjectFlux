import json
from pathlib import Path


class MetricsEngine:

    def __init__(self):
        self.file = Path("flux_metrics.json")
        self.data = self._load()

    def _load(self):
        if self.file.exists():
            try:
                return json.loads(self.file.read_text())
            except:
                return {}
        return {}

    def save(self):
        self.file.write_text(json.dumps(self.data, indent=2))

    def record(self, project, result):

        if project not in self.data:
            self.data[project] = []

        self.data[project].append(result)

        self.save()

    def summary(self):
        return self.data
