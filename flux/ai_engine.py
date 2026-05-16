import re

class AIEngine:

    @staticmethod
    def analyze_logs(logs: str):
        logs = logs.lower()

        if "no module named" in logs:
            module = re.findall(r"no module named '(.+?)'", logs)
            return {
                "type": "missing_python_module",
                "module": module[0] if module else "unknown"
            }

        if "cannot find module" in logs:
            return {"type": "node_missing_module"}

        if "gradle" in logs and "failed" in logs:
            return {"type": "apk_build_error"}

        return {"type": "unknown"}

    @staticmethod
    def generate_fix(issue):
        if issue["type"] == "missing_python_module":
            module = issue["module"]
            return f"pip install {module}"

        if issue["type"] == "node_missing_module":
            return "npm install"

        if issue["type"] == "apk_build_error":
            return "./gradlew clean build"

        return "no_fix"
