import re


class ChatEngine:

    def __init__(self, ui):
        self.ui = ui

    # -------------------------
    # MAIN
    # -------------------------

    def process(self, text):
        text = text.lower()

        # SYNC
        if "sync" in text:
            return self.ui.smart_sync_all()

        # AUTOPILOT
        if "autopilot" in text:
            return self._run_autopilot(text)

        # EVOLVE
        if "evolve" in text or "improve" in text:
            return self.ui.evolve_code()

        # DEPLOY
        if "deploy" in text:
            return self._deploy(text)

        # LINK
        if "link" in text:
            return self._link(text)

        # STATUS
        if "status" in text:
            return self._status(text)

        # MEMORY
        if "memory" in text:
            return self.ui.memory.capture_commits()

        # SNAPSHOT
        if "snapshot" in text:
            return self.ui.memory.snapshot_all()

        return "❓ Command not understood"

    # -------------------------
    # COMMANDS
    # -------------------------

    def _run_autopilot(self, text):
        repo = self._extract_repo(text)
        if not repo:
            return "❌ Specify repo name"

        path = self.ui.get_repo_path(repo)

        return self.ui.autopilot.run(repo, path)

    def _deploy(self, text):
        repo = self._extract_repo(text)
        if not repo:
            return "❌ Specify repo"

        path = self.ui.get_repo_path(repo)

        return self.ui.deploy.auto_deploy_smart(repo, path)

    def _link(self, text):
        parts = text.split()

        if len(parts) < 3:
            return "❌ use: link repoA repoB"

        parent = parts[1]
        child = parts[2]

        self.ui.orchestrator.link(parent, child)

        return f"🔗 {parent} → {child}"

    def _status(self, text):
        repo = self._extract_repo(text)
        if not repo:
            return "❌ Specify repo"

        return self.ui.github.get_latest_workflow_status(repo)

    # -------------------------
    # HELPERS
    # -------------------------

    def _extract_repo(self, text):
        match = re.search(r"repo\s+(\w+)", text)
        if match:
            return match.group(1)
        return None
