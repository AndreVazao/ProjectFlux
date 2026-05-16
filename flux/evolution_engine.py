import os
import difflib
from flux.repo_registry import RepoRegistry
from flux.sync_engine import SyncEngine


class EvolutionEngine:

    def __init__(self):
        self.registry = RepoRegistry()

    # -------------------------
    # FIND SIMILAR FILES
    # -------------------------

    def find_similar_files(self, repos_dir):
        files_map = {}

        for repo_id, info in self.registry.get_all().items():
            path = info["path"]

            for root, _, files in os.walk(path):
                for f in files:
                    if f.endswith(".py"):
                        full = os.path.join(root, f)

                        with open(full, "r", errors="ignore") as file:
                            content = file.read()

                        files_map.setdefault(f, []).append((full, content))

        return files_map

    # -------------------------
    # COMPARE & EXTRACT BEST
    # -------------------------

    def compare_versions(self, contents):
        if not contents:
            return ""
        base = contents[0]

        best = base
        best_score = 0

        for content in contents[1:]:
            score = difflib.SequenceMatcher(None, base, content).ratio()

            if score > best_score:
                best_score = score
                best = content

        return best

    # -------------------------
    # APPLY IMPROVEMENTS
    # -------------------------

    def evolve(self, repos_dir):
        files_map = self.find_similar_files(repos_dir)

        results = []

        for filename, versions in files_map.items():

            if len(versions) < 2:
                continue

            best_version = self.compare_versions([c for _, c in versions])

            for path, content in versions:
                if content != best_version:
                    try:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(best_version)

                        repo_path = self.get_repo_path(path)
                        if repo_path:
                            SyncEngine.run_git(["add", "."], repo_path)
                            SyncEngine.run_git(["commit", "-m", f"evolution: improved {filename}"], repo_path)
                            SyncEngine.run_git(["push"], repo_path)

                            results.append(f"✨ Updated {path}")

                    except Exception as e:
                        results.append(f"❌ {path}: {str(e)}")

        return "\n".join(results) if results else "No evolution applied"

    # -------------------------
    # HELPER
    # -------------------------

    def get_repo_path(self, file_path):
        for repo_id, info in self.registry.get_all().items():
            if file_path.startswith(os.path.abspath(info["path"])):
                return info["path"]
        return None
