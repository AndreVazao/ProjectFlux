import os
import subprocess
import time


class SyncEngine:

    # -------------------------
    # CORE
    # -------------------------

    @staticmethod
    def run_git(cmd, repo_path):
        try:
            return subprocess.check_output(
                ["git", "-C", repo_path] + cmd,
                stderr=subprocess.STDOUT
            ).decode()
        except subprocess.CalledProcessError as e:
            return e.output.decode()

    # -------------------------
    # TIME CHECK
    # -------------------------

    @staticmethod
    def get_last_local_commit(repo_path):
        result = SyncEngine.run_git(
            ["log", "-1", "--format=%ct"],
            repo_path
        )
        return int(result.strip()) if result.strip().isdigit() else 0

    @staticmethod
    def get_last_remote_commit(repo_path):
        SyncEngine.run_git(["fetch"], repo_path)

        result = SyncEngine.run_git(
            ["log", "origin/main", "-1", "--format=%ct"],
            repo_path
        )
        return int(result.strip()) if result.strip().isdigit() else 0

    # -------------------------
    # CONFLICT DETECTION
    # -------------------------

    @staticmethod
    def has_conflicts(repo_path):
        status = SyncEngine.run_git(["status"], repo_path)
        return "both modified" in status or "CONFLICT" in status

    # -------------------------
    # AUTO RESOLVE (SAFE)
    # -------------------------

    @staticmethod
    def resolve_conflicts(repo_path):
        # estratégia: manter versão local
        SyncEngine.run_git(["merge", "--abort"], repo_path)

        SyncEngine.run_git(["fetch"], repo_path)
        SyncEngine.run_git(["reset", "--hard", "HEAD"], repo_path)

        return "⚠️ Conflict resolved (kept local version)"

    # -------------------------
    # BACKUP
    # -------------------------

    @staticmethod
    def create_backup_branch(repo_path):
        branch_name = f"backup-{int(time.time())}"
        SyncEngine.run_git(["checkout", "-b", branch_name], repo_path)
        SyncEngine.run_git(["push", "-u", "origin", branch_name], repo_path)
        return branch_name

    # -------------------------
    # MAIN SYNC
    # -------------------------

    @staticmethod
    def sync(repo_path):

        local_time = SyncEngine.get_last_local_commit(repo_path)
        remote_time = SyncEngine.get_last_remote_commit(repo_path)

        if local_time == 0 and remote_time == 0:
            return "❌ Repo not initialized"

        # LOCAL → REMOTE
        if local_time > remote_time:
            result = SyncEngine.run_git(["push"], repo_path)

            if "rejected" in result.lower():
                # conflito → backup + pull
                backup = SyncEngine.create_backup_branch(repo_path)
                SyncEngine.run_git(["checkout", "main"], repo_path)

                pull = SyncEngine.run_git(["pull"], repo_path)

                if SyncEngine.has_conflicts(repo_path):
                    SyncEngine.resolve_conflicts(repo_path)

                return f"⚠️ Conflict handled, backup: {backup}"

            return "⬆️ Local → GitHub"

        # REMOTE → LOCAL
        elif remote_time > local_time:
            result = SyncEngine.run_git(["pull"], repo_path)

            if SyncEngine.has_conflicts(repo_path):
                SyncEngine.resolve_conflicts(repo_path)
                return "⚠️ Conflict auto-resolved (local priority)"

            return "⬇️ GitHub → Local"

        return "✅ Synced"
