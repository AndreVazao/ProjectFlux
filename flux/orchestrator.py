import os
import json
from pathlib import Path

from flux.sync_engine import SyncEngine
from flux.auto_engine import AutoEngine
from flux.repo_registry import RepoRegistry
from flux.git_manager import GitManager


MAP_FILE = Path.home() / ".projectflux_map.json"


class Orchestrator:

    def __init__(self, github=None):
        self.github = github
        self.registry = RepoRegistry()
        self.map = self.load_map()

    # -------------------------
    # MAP
    # -------------------------

    def load_map(self):
        if MAP_FILE.exists():
            try:
                return json.loads(MAP_FILE.read_text())
            except:
                return {}
        return {}

    def save_map(self):
        MAP_FILE.write_text(json.dumps(self.map, indent=2))

    def link(self, parent, child):
        if parent not in self.map:
            self.map[parent] = []

        if child not in self.map[parent]:
            self.map[parent].append(child)

        self.save_map()

    def get_children(self, repo):
        return self.map.get(repo, [])

    # -------------------------
    # FIRST RUN (CLONE ALL)
    # -------------------------

    def bootstrap(self, repos_dir):
        if not self.github:
            return "❌ GitHub Manager not initialized"

        repos = self.github.list_repos()

        results = []

        for repo in repos:
            repo_name = repo["name"]
            repo_id = str(repo["id"])
            clone_url = repo["clone_url"]

            local_path = os.path.join(repos_dir, repo_name)

            # já existe → skip
            if self.registry.exists(repo_id):
                results.append(f"✔ {repo_name} already linked")
                continue

            # clone
            try:
                GitManager.clone_repo(clone_url, local_path)

                # guardar identidade
                self.registry.register(repo_name, repo_id, local_path)

                # puxar TODAS as branches
                self.fetch_all_branches(local_path)

                results.append(f"⬇️ Cloned {repo_name}")

            except Exception as e:
                results.append(f"❌ {repo_name}: {str(e)}")

        return "\n".join(results)

    # -------------------------
    # FETCH ALL BRANCHES
    # -------------------------

    def fetch_all_branches(self, repo_path):
        SyncEngine.run_git(["fetch", "--all"], repo_path)

        branches = SyncEngine.run_git(
            ["branch", "-r"],
            repo_path
        ).splitlines()

        for branch in branches:
            branch = branch.strip().replace("origin/", "")

            if branch and branch != "HEAD":
                SyncEngine.run_git(["checkout", "-B", branch, f"origin/{branch}"], repo_path)

    # -------------------------
    # SMART SYNC (IDENTITY SAFE)
    # -------------------------

    def smart_sync_all(self):
        results = []

        for repo_id, info in self.registry.get_all().items():
            path = info["path"]

            if os.path.exists(path):
                result = SyncEngine.sync(path)
                results.append(f"{info['name']}: {result}")

        return "\n".join(results)

    # -------------------------
    # SMART SYNC CASCADE (Legacy-ish)
    # -------------------------

    def sync_all(self, repos_dir):
        results = []

        for repo in os.listdir(repos_dir):
            repo_path = os.path.join(repos_dir, repo)

            if os.path.isdir(repo_path):
                result = SyncEngine.sync(repo_path)
                results.append(f"{repo}: {result}")

        return "\n".join(results)

    # -------------------------
    # CASCADE UPDATE
    # -------------------------

    def cascade(self, repo, repos_dir):
        results = []

        children = self.get_children(repo)

        for child in children:
            path = os.path.join(repos_dir, child)

            if os.path.exists(path):
                result = SyncEngine.sync(path)
                results.append(f"{child}: {result}")

        return "\n".join(results) if results else "No linked repos"

    # -------------------------
    # SMART ANALYSIS
    # -------------------------

    def analyze(self, repo_path):
        project_type = AutoEngine.detect_project_type(repo_path)

        if project_type == "node":
            return "Frontend / Web App"

        if project_type == "python":
            return "Backend / Script"

        if project_type == "apk":
            return "Mobile App"

        return "Unknown"
