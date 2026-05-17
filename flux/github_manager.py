import os
import requests
import logging
from github import Github
from flux.config import logger

class GitHubManager:

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN") or ""
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json"
        }
        try:
            self.client = Github(self.token) if self.token else None
            self.user = self.client.get_user() if self.client else None
            self.username = self.get_user()
        except Exception as e:
            logger.error(f"GitHub Client initialization failed: {e}")
            self.client = None
            self.user = None
            self.username = None

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
            else:
                logger.warning(f"Failed to fetch GitHub user: {r.status_code} {r.text}")
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
        return None

    # -------------------------
    # REPO
    # -------------------------

    def list_repos(self):
        if not self.user:
            return []
        try:
            repos = self.user.get_repos()
            return [
                {
                    "name": r.name,
                    "id": r.id,
                    "clone_url": r.clone_url
                }
                for r in repos
            ]
        except Exception as e:
            logger.error(f"Error listing repos: {e}")
            return []

    def create_repo(self, name):
        if not self.username:
            raise Exception("GitHub username not found. Check your GITHUB_TOKEN.")
        url = "https://api.github.com/user/repos"
        data = {"name": name, "private": True}
        logger.info(f"Creating repository: {name}")
        try:
            r = requests.post(url, headers=self.headers, json=data, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"Error creating repo {name}: {e}")
            raise

    def rename_repo(self, repo, new_name):
        if not self.username:
            raise Exception("GitHub username not found. Check your GITHUB_TOKEN.")
        url = f"https://api.github.com/repos/{self.username}/{repo}"
        logger.info(f"Renaming repository {repo} to {new_name}")
        try:
            r = requests.patch(url, headers=self.headers, json={"name": new_name}, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"Error renaming repo {repo}: {e}")
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
        logger.info(f"Creating PR for {repo}: {title}")
        try:
            r = requests.post(url, headers=self.headers, json=data, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"Error creating PR in {repo}: {e}")
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
            logger.error(f"Error during merge in {repo} (PR {pr_number}): {e}")
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
            logger.error(f"Error getting workflow status for {repo}: {e}")
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
            logger.error(f"Error getting latest logs for {repo}: {e}")
            return None

    def trigger_workflow(self, repo_name, workflow_file):
        if not self.client:
            return "error: github client not initialized"
        try:
            repo = self.client.get_repo(f"{self.username}/{repo_name}")
            workflows = repo.get_workflows()
            target_wf = None
            for wf in workflows:
                if wf.path.endswith(workflow_file) or wf.name == workflow_file:
                    target_wf = wf
                    break
            if target_wf:
                target_wf.create_dispatch("main")
                return "workflow_triggered"
            else:
                repo.create_repository_dispatch("trigger-workflow", {"ref": "main"})
                return "repository_dispatch_triggered"
        except Exception as e:
            logger.error(f"Error triggering workflow for {repo_name}: {e}")
            return f"error: {str(e)}"
