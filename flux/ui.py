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
        self.setGeometry(200, 200, 420, 500)

        self.github = GitHubManager()

        layout = QVBoxLayout()

        # 🔥 AUTO MODE (zero cliques inteligente)
        btn_auto = QPushButton("AUTO MODE (Smart Workflow)")
        btn_auto.clicked.connect(self.auto_mode)

        # 🔧 AUTO FIX
        btn_fix = QPushButton("AUTO FIX BUILD")
        btn_fix.clicked.connect(self.auto_fix)

        # 🔍 STATUS
        btn_status = QPushButton("Check Build Status")
        btn_status.clicked.connect(self.check_status)

        # 🔒 SAFE MERGE
        btn_merge = QPushButton("Safe Merge PR")
        btn_merge.clicked.connect(self.safe_merge)

        # ⚙️ WORKFLOW MANUAL
        btn_workflow = QPushButton("Generate Workflow (Manual)")
        btn_workflow.clicked.connect(self.generate_workflow)

        # BASE CONTROLS
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

        # ORDEM (topo = inteligência)
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

    # -------------------------
    # BASE ACTIONS
    # -------------------------

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

    # -------------------------
    # INTELIGÊNCIA
    # -------------------------

    def check_status(self):
        repo, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok:
            return

        status = self.github.get_latest_workflow_status(repo)
        QMessageBox.information(self, "Status", f"Workflow: {status}")

    def safe_merge(self):
        repo, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok:
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
        if not ok:
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
        if not ok:
            return

        WorkflowGenerator.auto(repo_path)

        GitManager.commit_all(repo_path, "auto workflow (AI)")
        GitManager.push(repo_path)

        QMessageBox.information(self, "AUTO", "Workflow auto-detected & deployed")

    # -------------------------
    # AUTO FIX
    # -------------------------

    def auto_fix(self):
        from flux.fix_engine import FixEngine
        import requests

        repo_name, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok:
            return

        repo_path, ok = QInputDialog.getText(self, "Repo Path", "Local path:")
        if not ok:
            return

        logs_url = self.github.get_latest_logs(repo_name)

        if not logs_url:
            QMessageBox.warning(self, "Error", "No logs found")
            return

        logs = requests.get(logs_url).text

        issue = FixEngine.analyze(logs)
        FixEngine.fix(repo_path, issue)

        GitManager.commit_all(repo_path, f"auto fix: {issue}")
        GitManager.push(repo_path)

        QMessageBox.information(self, "Fix", f"Issue detected: {issue}")


def start_app():
    app = QApplication(sys.argv)
    window = FluxUI()
    window.show()
    sys.exit(app.exec())
