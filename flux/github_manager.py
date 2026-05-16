import os
import requests


class GitHubManager:

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN") or ""
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json"
        }
        self.username = self.get_user()

    # -------------------------
    # USER
    # -------------------------

    def get_user(self):
        if not self.token:
            return None
        try:
            r = requests.get("https://api.github.com/user", headers=self.headers, timeout=10)
            if r.status_code == 200:
                return r.json()["login"]
        except Exception as e:
            print(f"Error fetching user: {e}")
        return None

    # -------------------------
    # REPO
    # -------------------------

    def create_repo(self, name):
        if not self.username:
            raise Exception("GitHub username not found. Check your GITHUB_TOKEN.")
        url = "https://api.github.com/user/repos"
        data = {"name": name, "private": True}
        try:
            r = requests.post(url, headers=self.headers, json=data, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error creating repo: {e}")
            raise

    def rename_repo(self, repo, new_name):
        if not self.username:
            raise Exception("GitHub username not found. Check your GITHUB_TOKEN.")
        url = f"https://api.github.com/repos/{self.username}/{repo}"
        try:
            r = requests.patch(url, headers=self.headers, json={"name": new_name}, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error renaming repo: {e}")
            raise

    # -------------------------
    # PR
    # -------------------------

    def create_pr(self, repo, title, body, head, base):
        if not self.username:
            raise Exception("GitHub username not found. Check your GITHUB_TOKEN.")
        url = f"https://api.github.com/repos/{self.username}/{repo}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        try:
            r = requests.post(url, headers=self.headers, json=data, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error creating PR: {e}")
            raise

    def safe_merge(self, repo, pr_number):
        try:
            status = self.get_latest_workflow_status(repo)

            if status != "success":
                return f"❌ Build not passing (status: {status})"

            if not self.username:
                return "❌ GitHub username not found. Check your GITHUB_TOKEN."

            url = f"https://api.github.com/repos/{self.username}/{repo}/pulls/{pr_number}/merge"
            r = requests.put(url, headers=self.headers, timeout=10)

            if r.status_code == 200:
                return "✅ Merge done"
            return f"❌ Merge failed: {r.text}"
        except Exception as e:
            return f"❌ Error during merge: {e}"

    # -------------------------
    # WORKFLOWS
    # -------------------------

    def get_latest_workflow_status(self, repo):
        if not self.username:
            return "error: missing username"
        url = f"https://api.github.com/repos/{self.username}/{repo}/actions/runs"
        try:
            r = requests.get(url, headers=self.headers, timeout=10)

            if r.status_code != 200:
                return f"error: {r.status_code}"

            runs = r.json().get("workflow_runs", [])
            if not runs:
                return "no runs"

            return runs[0].get("conclusion") or "running"
        except Exception as e:
            print(f"Error getting workflow status: {e}")
            return "error"

    def get_latest_logs(self, repo):
        if not self.username:
            return None
        url = f"https://api.github.com/repos/{self.username}/{repo}/actions/runs"
        try:
            r = requests.get(url, headers=self.headers, timeout=10)

            if r.status_code != 200:
                return None

            runs = r.json().get("workflow_runs", [])
            if not runs:
                return None

            return runs[0].get("logs_url")
        except Exception as e:
            print(f"Error getting latest logs: {e}")
            return None
