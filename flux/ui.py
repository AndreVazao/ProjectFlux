import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QInputDialog
)

from flux.github_manager import GitHubManager
from flux.git_manager import GitManager
from flux.config import REPOS_DIR

class FluxUI(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProjectFlux")
        self.setGeometry(200, 200, 400, 400)

        self.github = GitHubManager()

        layout = QVBoxLayout()

        btn_create_repo = QPushButton("Create Repo")
        btn_create_repo.clicked.connect(self.create_repo)

        btn_clone = QPushButton("Clone Repo")
        btn_clone.clicked.connect(self.clone_repo)

        btn_branch = QPushButton("Create Branch")
        btn_branch.clicked.connect(self.create_branch)

        btn_commit = QPushButton("Commit & Push")
        btn_commit.clicked.connect(self.commit_push)

        btn_pr = QPushButton("Create PR")
        btn_pr.clicked.connect(self.create_pr)

        btn_status = QPushButton("Check Build Status")
        btn_status.clicked.connect(self.check_status)
        
        btn_merge = QPushButton("Safe Merge PR")
        btn_merge.clicked.connect(self.safe_merge)
        
        layout.addWidget(btn_status)
        layout.addWidget(btn_merge)
        layout.addWidget(btn_create_repo)
        layout.addWidget(btn_clone)
        layout.addWidget(btn_branch)
        layout.addWidget(btn_commit)
        layout.addWidget(btn_pr)

        self.setLayout(layout)

    def create_repo(self):
        name, ok = QInputDialog.getText(self, "Repo Name", "Enter repo name:")
        if ok:
            self.github.create_repo(name)
            QMessageBox.information(self, "Success", f"Repo {name} created")

    def clone_repo(self):
        url, ok = QInputDialog.getText(self, "Clone Repo", "Repo URL:")
        if ok:
            path = REPOS_DIR / url.split("/")[-1].replace(".git", "")
            GitManager.clone_repo(url, str(path))
            QMessageBox.information(self, "Success", "Repo cloned")

    def create_branch(self):
        repo, ok = QInputDialog.getText(self, "Repo Path", "Local repo path:")
        if not ok:
            return

        branch, ok = QInputDialog.getText(self, "Branch Name", "New branch:")
        if ok:
            GitManager.create_branch(repo, branch)
            QMessageBox.information(self, "Success", "Branch created")

    def commit_push(self):
        repo, ok = QInputDialog.getText(self, "Repo Path", "Local repo path:")
        if not ok:
            return

        GitManager.commit_all(repo)
        GitManager.push(repo)
        QMessageBox.information(self, "Success", "Committed & pushed")

    def create_pr(self):
        repo, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok:
            return

        title, ok = QInputDialog.getText(self, "Title", "PR title:")
        if not ok:
            return

        self.github.create_pr(repo, title, "Auto PR", "dev", "main")
        QMessageBox.information(self, "Success", "PR created")


def start_app():
    app = QApplication(sys.argv)
    window = FluxUI()
    window.show()
    sys.exit(app.exec())
