import sys
import os
from pathlib import Path
from git import Repo
from github import Github
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QInputDialog

# CONFIG
BASE_DIR = Path.home() / "ProjectFlux"
REPOS_DIR = BASE_DIR / "repos"
REPOS_DIR.mkdir(parents=True, exist_ok=True)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise Exception("Define GITHUB_TOKEN")

gh = Github(GITHUB_TOKEN)
user = gh.get_user()


class FluxUI(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProjectFlux")
        self.setGeometry(200, 200, 400, 400)

        layout = QVBoxLayout()

        buttons = [
            ("Create Repo", self.create_repo),
            ("Clone Repo", self.clone_repo),
            ("Create Branch", self.create_branch),
            ("Commit & Push", self.commit_push),
            ("Create PR", self.create_pr),
        ]

        for text, func in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            layout.addWidget(btn)

        self.setLayout(layout)

    def create_repo(self):
        name, ok = QInputDialog.getText(self, "Repo Name", "Enter repo name:")
        if ok:
            user.create_repo(name)
            QMessageBox.information(self, "OK", f"{name} created")

    def clone_repo(self):
        url, ok = QInputDialog.getText(self, "Clone Repo", "Repo URL:")
        if ok:
            name = url.split("/")[-1].replace(".git", "")
            path = REPOS_DIR / name
            Repo.clone_from(url, str(path))
            QMessageBox.information(self, "OK", "Cloned")

    def create_branch(self):
        path, ok = QInputDialog.getText(self, "Repo Path", "Local path:")
        if not ok:
            return

        branch, ok = QInputDialog.getText(self, "Branch", "Branch name:")
        if ok:
            repo = Repo(path)
            new_branch = repo.create_head(branch)
            new_branch.checkout()
            QMessageBox.information(self, "OK", "Branch created")

    def commit_push(self):
        path, ok = QInputDialog.getText(self, "Repo Path", "Local path:")
        if not ok:
            return

        repo = Repo(path)
        repo.git.add(all=True)
        repo.index.commit("auto commit")
        repo.remote(name='origin').push()
        QMessageBox.information(self, "OK", "Pushed")

    def create_pr(self):
        repo_name, ok = QInputDialog.getText(self, "Repo", "Repo name:")
        if not ok:
            return

        title, ok = QInputDialog.getText(self, "Title", "PR title:")
        if not ok:
            return

        repo = user.get_repo(repo_name)
        repo.create_pull(title=title, body="auto PR", head="dev", base="main")
        QMessageBox.information(self, "OK", "PR created")


def start():
    app = QApplication(sys.argv)
    win = FluxUI()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start()
