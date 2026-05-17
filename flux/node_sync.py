import subprocess


class NodeSync:

    def sync_repo(self, path):
        try:
            # Sync local changes before pulling
            subprocess.run(["git", "-C", path, "add", "."], check=False)
            subprocess.run(["git", "-C", path, "commit", "-m", "Auto-sync before pull"], check=False)

            subprocess.run(["git", "-C", path, "pull"], check=True)
            subprocess.run(["git", "-C", path, "push"], check=True)
            return "synced"
        except Exception as e:
            return str(e)
