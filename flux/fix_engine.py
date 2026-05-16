class FixEngine:

    @staticmethod
    def analyze(logs):
        logs = logs.lower()

        if "no module named" in logs:
            return "missing_python_dependency"

        if "npm ERR!" in logs:
            return "node_dependency_issue"

        if "gradle" in logs:
            return "apk_build_issue"

        return "unknown"

    @staticmethod
    def fix(repo_path, issue_type):
        from pathlib import Path

        if issue_type == "missing_python_dependency":
            req = Path(repo_path) / "requirements.txt"
            with open(req, "a") as f:
                f.write("\nrequests\n")

        elif issue_type == "node_dependency_issue":
            # placeholder realista (podes expandir depois)
            pass

        elif issue_type == "apk_build_issue":
            pass
