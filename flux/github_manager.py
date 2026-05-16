from github import Github
from flux.config import get_github_token

class GitHubManager:

    def __init__(self):
        token = get_github_token()
        if not token:
            raise Exception("GITHUB_TOKEN not set")
        self.gh = Github(token)
        self.user = self.gh.get_user()

    def create_repo(self, name):
        return self.user.create_repo(name)

    def create_branch(self, repo_name, new_branch, base="main"):
        repo = self.user.get_repo(repo_name)
        source = repo.get_branch(base)
        repo.create_git_ref(ref=f"refs/heads/{new_branch}", sha=source.commit.sha)

    def create_pr(self, repo_name, title, body, head, base="main"):
        repo = self.user.get_repo(repo_name)
        return repo.create_pull(title=title, body=body, head=head, base=base)

    def get_latest_workflow_status(self, repo_name):
        repo = self.user.get_repo(repo_name)
        runs = repo.get_workflow_runs()
        if runs.totalCount == 0:
            return "NO_RUNS"

        latest = runs[0]
        return latest.conclusion  # success, failure, null

    def get_latest_logs(self, repo_name):
    repo = self.user.get_repo(repo_name)
    runs = repo.get_workflow_runs()

    if runs.totalCount == 0:
        return None

    latest = runs[0]
    return latest.logs_url
    
    def safe_merge(self, repo_name, pr_number):
        status = self.get_latest_workflow_status(repo_name)

        if status != "success":
            return f"BLOCKED: Workflow status = {status}"

        repo = self.user.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        pr.merge()
        return "MERGED"
