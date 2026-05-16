import os


class AutoEngine:

    @staticmethod
    def detect_project_type(repo_path):
        files = os.listdir(repo_path)

        if "package.json" in files:
            return "node"

        if "requirements.txt" in files or any(f.endswith(".py") for f in files):
            return "python"

        if "android" in files or "build.gradle" in files:
            return "apk"

        return "unknown"

    @staticmethod
    def choose_provider(project_type):
        if project_type == "node":
            return "Vercel"

        if project_type == "python":
            return "Render"

        if project_type == "apk":
            return "GitHub"

        return None
