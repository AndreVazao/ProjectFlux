import time
import requests

from flux.workflow_generator import WorkflowGenerator
from flux.git_manager import GitManager
from flux.fix_engine import FixEngine
from flux.auto_engine import AutoEngine
from flux.ai_engine import AIEngine
from flux.memory_engine import MemoryEngine
from flux.evolution_engine import EvolutionEngine


class AutopilotEngine:

    def __init__(self, github, deploy):
        self.github = github
        self.deploy = deploy
        self.ai = AIEngine()
        self.memory = MemoryEngine()

    # -------------------------
    # MAIN LOOP
    # -------------------------

    def run(self, repo_name, repo_path):
        try:
            # AI THINK
            decision = self.ai.think(repo_name)
            action = decision.get("action")

            if action == "fix":
                result = FixEngine.run(repo_path, "")
            elif action == "deploy":
                result = self.deploy.auto_deploy_smart(repo_name, repo_path)
            elif action == "sync":
                from flux.sync_engine import SyncEngine
                result = SyncEngine.sync(repo_path)
            elif action == "evolve":
                result = EvolutionEngine().evolve(repo_path)
            else:
                # FALLBACK TO LEGACY RUN IF AI SAYS NOTHING OR FOR INITIAL SETUP
                return self.run_legacy(repo_name, repo_path)

            self.memory.save_decision(repo_name, f"{action} → {decision.get('reason')}")
            return f"{action.upper()} → {result}"

        except Exception as e:
            return f"❌ Autopilot error: {str(e)}"

    def run_legacy(self, repo_name, repo_path):
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
            return f"❌ Legacy Autopilot error: {str(e)}"

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
