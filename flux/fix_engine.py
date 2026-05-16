from flux.ai_engine import AIEngine
from pathlib import Path

class FixEngine:

    @staticmethod
    def run(repo_path, logs):
        issue = AIEngine.analyze_logs(logs)
        command = AIEngine.generate_fix(issue)

        if issue["type"] == "missing_python_module":
            req = Path(repo_path) / "requirements.txt"
            with open(req, "a") as f:
                f.write(f"\n{issue['module']}\n")

        return {
            "issue": issue,
            "fix": command
        }
