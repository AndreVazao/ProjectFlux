from pathlib import Path

class ProjectDetector:

    @staticmethod
    def detect(repo_path):
        path = Path(repo_path)

        if (path / "requirements.txt").exists():
            return "python"

        if (path / "package.json").exists():
            return "node"

        if (path / "gradlew").exists() or (path / "app").exists():
            return "apk"

        return "unknown"
