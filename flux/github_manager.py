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
        r = requests.get("https://api.github.com/user", headers=self.headers)
        if r.status_code == 200:
            return r.json()["login"]
        return None

    # -------------------------
    # REPO
    # -------------------------

    def create_repo(self, name):
        url = "https://api.github.com/user/repos"
        data = {"name": name, "private": True}
        requests.post(url, headers=self.headers, json=data)

    def rename_repo(self, repo, new_name):
        url = f"https://api.github.com/repos/{self.username}/{repo}"
        requests.patch(url, headers=self.headers, json={"name": new_name})

    # -------------------------
    # PR
    # -------------------------

    def create_pr(self, repo, title, body, head, base):
        url = f"https://api.github.com/repos/{self.username}/{repo}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        requests.post(url, headers=self.headers, json=data)

    def safe_merge(self, repo, pr_number):
        status = self.get_latest_workflow_status(repo)

        if status != "success":
            return "❌ Build not passing"

        url = f"https://api.github.com/repos/{self.username}/{repo}/pulls/{pr_number}/merge"
        r = requests.put(url, headers=self.headers)

        if r.status_code == 200:
            return "✅ Merge done"
        return f"❌ Merge failed: {r.text}"

    # -------------------------
    # WORKFLOWS
    # -------------------------

    def get_latest_workflow_status(self, repo):
        url = f"https://api.github.com/repos/{self.username}/{repo}/actions/runs"
        r = requests.get(url, headers=self.headers)

        if r.status_code != 200:
            return "error"

        runs = r.json().get("workflow_runs", [])
        if not runs:
            return "no runs"

        return runs[0]["conclusion"]

    def get_latest_logs(self, repo):
        url = f"https://api.github.com/repos/{self.username}/{repo}/actions/runs"
        r = requests.get(url, headers=self.headers)

        if r.status_code != 200:
            return None

        runs = r.json().get("workflow_runs", [])
        if not runs:
            return None

        return runs[0]["logs_url"]
