import os
from datetime import datetime
from pathlib import Path
from flux.repo_registry import RepoRegistry
from flux.sync_engine import SyncEngine


class MemoryEngine:

    def __init__(self):
        self.registry = RepoRegistry()
        self.vault_path = Path.home() / "ObsidianVault"  # 🔥 ajusta se necessário

    # -------------------------
    # INIT
    # -------------------------

    def ensure_structure(self):
        (self.vault_path / "ProjectFlux").mkdir(parents=True, exist_ok=True)
        (self.vault_path / "ProjectFlux/Repos").mkdir(parents=True, exist_ok=True)
        (self.vault_path / "ProjectFlux/Logs").mkdir(parents=True, exist_ok=True)

    # -------------------------
    # SAVE MEMORY
    # -------------------------

    def save_event(self, repo, title, content):
        self.ensure_structure()

        file = self.vault_path / f"ProjectFlux/Repos/{repo}.md"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        entry = f"""
## {timestamp} - {title}

{content}

---
"""

        with open(file, "a", encoding="utf-8") as f:
            f.write(entry)

    # -------------------------
    # AUTO CAPTURE COMMITS
    # -------------------------

    def capture_commits(self):
        results = []

        for repo_id, info in self.registry.get_all().items():
            path = info["path"]
            name = info["name"]

            if not os.path.exists(path):
                continue

            log = SyncEngine.run_git(
                ["log", "-1", "--pretty=format:%h - %s"],
                path
            )

            if log:
                self.save_event(
                    name,
                    "Commit Update",
                    log
                )
                results.append(f"🧠 {name} memory updated")

        return "\n".join(results) if results else "No updates"

    # -------------------------
    # SAVE AI DECISIONS
    # -------------------------

    def save_decision(self, repo, decision):
        self.save_event(repo, "AI Decision", decision)

    # -------------------------
    # GLOBAL SNAPSHOT
    # -------------------------

    def snapshot_all(self):
        self.ensure_structure()

        file = self.vault_path / "ProjectFlux/Logs/system_snapshot.md"

        content = "# System Snapshot\n\n"

        for repo_id, info in self.registry.get_all().items():
            content += f"- {info['name']} → {info['path']}\n"

        with open(file, "w", encoding="utf-8") as f:
            f.write(content)

        return "📸 Snapshot saved"
