import os
from pathlib import Path


class ContextEngine:

    def __init__(self, vault_path):
        self.vault = Path(vault_path)

    # -------------------------
    # LOAD CONTEXT
    # -------------------------

    def load_repo_context(self, repo_name):
        file = self.vault / f"ProjectFlux/Repos/{repo_name}.md"

        if not file.exists():
            return ""

        try:
            content = file.read_text(encoding="utf-8")
            return content[-5000:]  # últimos eventos (mais relevantes)
        except:
            return ""

    # -------------------------
    # GLOBAL CONTEXT
    # -------------------------

    def load_global_context(self):
        logs = self.vault / "ProjectFlux/Logs"

        context = ""

        if logs.exists():
            for f in logs.glob("*.md"):
                try:
                    context += f.read_text(encoding="utf-8")[-2000:]
                except:
                    pass

        return context

    # -------------------------
    # BUILD PROMPT CONTEXT
    # -------------------------

    def build_context(self, repo):
        repo_ctx = self.load_repo_context(repo)
        global_ctx = self.load_global_context()

        return f"""
### REPO CONTEXT
{repo_ctx}

### GLOBAL CONTEXT
{global_ctx}
"""
