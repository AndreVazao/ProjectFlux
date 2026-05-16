import sys
import os
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
        self.setGeometry(200, 200, 420, 500)

        try:
            self.github = GitHubManager()
        except Exception as e:
            QMessageBox.critical(self, "Init Error", f"Failed to initialize GitHub Manager: {e}")
            self.github = None

        layout = QVBoxLayout()

        # 🔥 AUTO MODE
        btn_auto = QPushButton("AUTO MODE (Smart Workflow)")
        btn_auto.clicked.connect(self.safe_call(self.auto_mode))

        # 🔧 AUTO FIX
        btn_fix = QPushButton("AUTO FIX BUILD")
        btn_fix.clicked.connect(self.safe_call(self.auto_fix))

        # 🔍 STATUS
        btn_status = QPushButton("Check Build Status")
        btn_status.clicked.connect(self.safe_call(self.check_status))

        # 🔒 SAFE MERGE
        btn_merge = QPushButton("Safe Merge PR")
        btn_merge.clicked.connect(self.safe_call(self.safe_merge))

        # ⚙️ WORKFLOW MANUAL
        btn_workflow = QPushButton("Generate Workflow (Manual)")
        btn_workflow.clicked.connect(self.safe_call(self.generate_workflow))

        # BASE CONTROLS
        btn_create_repo = QPushButton("Create Repo")
        btn_create_repo.clicked.connect(self.safe_call(self.create_repo))

        btn_clone = QPushButton("Clone Repo")
        btn_clone.clicked.connect(self.safe_call(self.clone_repo))

        btn_branch = QPushButton("Create Branch")
        btn_branch.clicked.connect(self.safe_call(self.create_branch))

        btn_commit = QPushButton("Commit & Push")
        btn_commit.clicked.connect(self.safe_call(self.commit_push))

        btn_pr = QPushButton("Create PR")
        btn_pr.clicked.connect(self.safe_call(self.create_pr))

        # ORDEM
        layout.addWidget(btn_auto)
        layout.addWidget(btn_fix)
        layout.addWidget(btn_status)
        layout.addWidget(btn_merge)
        layout.addWidget(btn_workflow)

        layout.addWidget(btn_create_repo)
        layout.addWidget(btn_clone)
        layout.addWidget(btn_branch)
        layout.addWidget(btn_commit)
        layout.addWidget(btn_pr)

        self.setLayout(layout)

    def safe_call(self, func):
        def wrapper():
            try:
                func()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
        return wrapper

    # -------------------------
    # BASE ACTIONS
    # -------------------------

    def create_repo(self):
        if not self.github:
            raise Exception("GitHub Manager not initialized.")
        name, ok = QInputDialog.getText(self, "Repo Name", "Enter repo name:")
        if ok and name:
            self.github.create_repo(name)
            QMessageBox.information(self, "Success", f"Repo {name} created")

    def clone_repo(self):
        url, ok = QInputDialog.getText(self, "Clone Repo", "Repo URL:")
        if ok and url:
            repo_name = url.split("/")[-1].replace(".git", "")
            path = REPOS_DIR / repo_name
            GitManager.clone_repo(url, str(path))
            QMessageBox.information(self, "Success", f"Repo cloned to {path}")

    def create_branch(self):
        repo, ok = QInputDialog.getText(self, "Repo Path", "Local repo path:")
        if not ok or not repo:
            return

        branch, ok = QInputDialog.getText(self, "Branch Name", "New branch:")
        if ok and branch:
            GitManager.create_branch(repo, branch)
            QMessageBox.information(self, "Success", f"Branch '{branch}' created")

    def commit_push(self):
        repo, ok = QInputDialog.getText(self, "Repo Path", "Local repo path:")
        if not ok or not repo:
            return

        GitManager.commit_all(repo)
        GitManager.push(repo)
        QMessageBox.information(self, "Success", "Committed & pushed")

    def create_pr(self):
        if not self.github:
            raise Exception("GitHub Manager not initialized.")
        repo, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok or not repo:
            return

        title, ok = QInputDialog.getText(self, "Title", "PR title:")
        if not ok or not title:
            return

        self.github.create_pr(repo, title, "Auto PR", "dev", "main")
        QMessageBox.information(self, "Success", "PR created")

    # -------------------------
    # INTELIGÊNCIA
    # -------------------------

    def check_status(self):
        if not self.github:
            raise Exception("GitHub Manager not initialized.")
        repo, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok or not repo:
            return

        status = self.github.get_latest_workflow_status(repo)
        QMessageBox.information(self, "Status", f"Workflow: {status}")

    def safe_merge(self):
        if not self.github:
            raise Exception("GitHub Manager not initialized.")
        repo, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok or not repo:
            return

        pr_number, ok = QInputDialog.getInt(self, "PR Number", "PR number:")
        if not ok:
            return

        result = self.github.safe_merge(repo, pr_number)
        QMessageBox.information(self, "Merge Result", result)

    # -------------------------
    # WORKFLOWS
    # -------------------------

    def generate_workflow(self):
        from flux.workflow_generator import WorkflowGenerator

        repo_path, ok = QInputDialog.getText(self, "Repo Path", "Local repo path:")
        if not ok or not repo_path:
            return

        choice, ok = QInputDialog.getItem(
            self,
            "Workflow Type",
            "Select type:",
            ["Python", "Node", "APK"],
            0,
            False
        )

        if not ok:
            return

        if choice == "Python":
            WorkflowGenerator.generate_python(repo_path)
        elif choice == "Node":
            WorkflowGenerator.generate_node(repo_path)
        elif choice == "APK":
            WorkflowGenerator.generate_apk(repo_path)

        GitManager.commit_all(repo_path, "auto workflow")
        GitManager.push(repo_path)

        QMessageBox.information(self, "OK", "Workflow created & pushed")

    def auto_mode(self):
        from flux.workflow_generator import WorkflowGenerator

        repo_path, ok = QInputDialog.getText(self, "Repo Path", "Local repo path:")
        if not ok or not repo_path:
            return

        WorkflowGenerator.auto(repo_path)

        GitManager.commit_all(repo_path, "auto workflow (AI)")
        GitManager.push(repo_path)

        QMessageBox.information(self, "AUTO", "Workflow auto-detected & deployed")

    # -------------------------
    # AUTO FIX
    # -------------------------

    def auto_fix(self):
        import requests
        from flux.fix_engine import FixEngine

        if not self.github:
            raise Exception("GitHub Manager not initialized.")

        repo_name, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok or not repo_name:
            return

        repo_path, ok = QInputDialog.getText(self, "Repo Path", "Local path:")
        if not ok or not repo_path:
            return

        logs_url = self.github.get_latest_logs(repo_name)

        if not logs_url:
            QMessageBox.warning(self, "Error", "No logs found")
            return

        try:
            logs = requests.get(logs_url, timeout=15).text
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to fetch logs: {e}")
            return

        result = FixEngine.run(repo_path, logs)

        try:
            GitManager.commit_all(repo_path, f"auto fix: {result['issue']}")
            GitManager.push(repo_path)
        except Exception as e:
            QMessageBox.warning(self, "Git Error", str(e))
            return

        QMessageBox.information(
            self,
            "Fix Applied",
            f"Issue: {result['issue']}\nFix: {result['fix']}"
        )


# -------------------------
# APP START
# -------------------------

def start_app():
    app = QApplication(sys.argv)
    window = FluxUI()
    window.show()
    sys.exit(app.exec())
