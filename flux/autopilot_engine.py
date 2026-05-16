import time
import requests

from flux.workflow_generator import WorkflowGenerator
from flux.git_manager import GitManager
from flux.fix_engine import FixEngine
from flux.auto_engine import AutoEngine


class AutopilotEngine:

    def __init__(self, github, deploy):
        self.github = github
        self.deploy = deploy

    # -------------------------
    # MAIN LOOP
    # -------------------------

    def run(self, repo_name, repo_path):
        try:
            # 1. Detect project
            project_type = AutoEngine.detect_project_type(repo_path)

            # 2. Generate workflow automatically
            WorkflowGenerator.auto(repo_path)

            GitManager.commit_all(repo_path, "autopilot: workflow")
            GitManager.push(repo_path)

            # 3. Wait for CI
            status = self.wait_for_ci(repo_name)

            # 4. Fix loop
            attempts = 0
            while status != "success" and attempts < 3:
                logs = self.get_logs(repo_name)

                if not logs:
                    return "❌ No logs available"

                result = FixEngine.run(repo_path, logs)

                GitManager.commit_all(repo_path, f"autofix: {result['issue']}")
                GitManager.push(repo_path)

                status = self.wait_for_ci(repo_name)
                attempts += 1

            if status != "success":
                return "❌ Failed after auto-fix attempts"

            # 5. Deploy
            return self.deploy.auto_deploy_smart(repo_name, repo_path)

        except Exception as e:
            return f"❌ Autopilot error: {str(e)}"

    # -------------------------
    # HELPERS
    # -------------------------

    def wait_for_ci(self, repo_name):
        for _ in range(20):
            status = self.github.get_latest_workflow_status(repo_name)

            if status in ["success", "failure"]:
                return status

            time.sleep(5)

        return "timeout"

    def get_logs(self, repo_name):
        logs_url = self.github.get_latest_logs(repo_name)

        if not logs_url:
            return None

        try:
            return requests.get(logs_url).text
        except:
            return None
