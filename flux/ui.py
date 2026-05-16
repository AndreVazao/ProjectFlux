import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QInputDialog, QScrollArea
)
from PyQt6.QtCore import QTimer

from flux.github_manager import GitHubManager
from flux.git_manager import GitManager
from flux.config import REPOS_DIR
from flux.providers_manager import ProvidersManager
from flux.deploy_manager import DeployManager
from flux.auto_engine import AutoEngine
from flux.autopilot_engine import AutopilotEngine
from flux.sync_engine import SyncEngine
from flux.orchestrator import Orchestrator
from flux.evolution_engine import EvolutionEngine


class FluxUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ProjectFlux")
        self.setGeometry(200, 200, 420, 700)

        try:
            self.github = GitHubManager()
        except Exception as e:
            QMessageBox.critical(self, "Init Error", f"Failed to initialize GitHub Manager: {e}")
            self.github = None

        self.providers = ProvidersManager()
        self.deploy = DeployManager(self.providers)
        self.autopilot = AutopilotEngine(self.github, self.deploy)
        self.orchestrator = Orchestrator(self.github)
        self.evolution = EvolutionEngine()

        # Timer for background sync
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.background_sync)
        self.sync_timer.start(30000)  # 30s

        main_layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # 🔥 AUTOPILOT (FULL AUTO)
        btn_autopilot = QPushButton("🤖 AUTOPILOT (FULL AUTO)")
        btn_autopilot.clicked.connect(self.safe_call(self.run_autopilot))
        btn_autopilot.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

        # ⚙️ PROVIDERS
        btn_providers = QPushButton("⚙️ Config Providers")
        btn_providers.clicked.connect(self.safe_call(self.configure_providers))

        # 🚀 DEPLOY
        btn_deploy = QPushButton("🚀 AUTO DEPLOY")
        btn_deploy.clicked.connect(self.safe_call(self.auto_deploy))

        # 🔄 SYNC
        btn_sync = QPushButton("🔄 AUTO SYNC")
        btn_sync.clicked.connect(self.safe_call(self.auto_sync))

        # 🌐 GLOBAL SYNC
        btn_smart_sync = QPushButton("🧠 Smart Sync (All Repos)")
        btn_smart_sync.clicked.connect(self.safe_call(self.smart_sync_all))

        # 🚀 BOOTSTRAP
        btn_bootstrap = QPushButton("🚀 FIRST RUN (Clone All)")
        btn_bootstrap.clicked.connect(self.safe_call(self.bootstrap_all))

        # 🧬 EVOLUTION
        btn_evolve = QPushButton("🧬 EVOLVE CODEBASE")
        btn_evolve.clicked.connect(self.safe_call(self.evolve_code))

        # 🔗 ORCHESTRATION
        btn_link = QPushButton("🔗 Link Repos")
        btn_link.clicked.connect(self.safe_call(self.link_repos))

        btn_cascade = QPushButton("🧠 Cascade Update")
        btn_cascade.clicked.connect(self.safe_call(self.cascade_update))

        # Legacy / Existing Controls
        btn_auto = QPushButton("AUTO MODE (Smart Workflow)")
        btn_auto.clicked.connect(self.safe_call(self.auto_mode))

        btn_fix = QPushButton("AUTO FIX BUILD")
        btn_fix.clicked.connect(self.safe_call(self.auto_fix))

        btn_status = QPushButton("Check Build Status")
        btn_status.clicked.connect(self.safe_call(self.check_status))

        btn_merge = QPushButton("Safe Merge PR")
        btn_merge.clicked.connect(self.safe_call(self.safe_merge))

        btn_workflow = QPushButton("Generate Workflow (Manual)")
        btn_workflow.clicked.connect(self.safe_call(self.generate_workflow))

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

        # Add to layout
        layout.addWidget(btn_autopilot)
        layout.addWidget(btn_providers)
        layout.addWidget(btn_deploy)
        layout.addWidget(btn_sync)
        layout.addWidget(btn_smart_sync)
        layout.addWidget(btn_bootstrap)
        layout.addWidget(btn_evolve)
        layout.addWidget(btn_link)
        layout.addWidget(btn_cascade)

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

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def safe_call(self, func):
        def wrapper():
            try:
                func()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
        return wrapper

    # -------------------------
    # NEW ACTIONS
    # -------------------------

    def configure_providers(self):
        providers = ["GitHub", "Vercel", "Render", "Supabase"]
        provider, ok = QInputDialog.getItem(self, "Select Provider", "Provider:", providers, 0, False)
        if not ok: return
        key, ok = QInputDialog.getText(self, f"{provider} API Key", "Enter API Key:")
        if not ok or not key: return
        self.providers.set_key(provider, key)
        use_now, ok = QInputDialog.getItem(self, "Activate Provider", "Use this provider now?", ["Yes", "No"], 0, False)
        if ok and use_now == "Yes":
            self.providers.set_active(provider)
        QMessageBox.information(self, "Saved", f"{provider} configured successfully")

    def auto_deploy(self):
        repo_name, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok: return
        repo_path, ok = QInputDialog.getText(self, "Repo Path", "Local path:")
        if not ok: return

        provider = self.providers.get_active()
        if not provider:
            QMessageBox.warning(self, "Error", "No active provider")
            return

        if provider == "Vercel":
            result = self.deploy.deploy_vercel(repo_name)
        elif provider == "Render":
            service_id, ok = QInputDialog.getText(self, "Render Service ID", "Service ID:")
            if not ok: return
            result = self.deploy.deploy_render(service_id)
        elif provider == "Supabase":
            result = self.deploy.deploy_supabase()
        else:
            result = self.deploy.auto_deploy_smart(repo_name, repo_path)

        QMessageBox.information(self, "Deploy", result)

    def run_autopilot(self):
        repo_name, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok: return
        repo_path, ok = QInputDialog.getText(self, "Repo Path", "Local path:")
        if not ok: return
        result = self.autopilot.run(repo_name, repo_path)
        QMessageBox.information(self, "AUTOPILOT", result)

    def auto_sync(self):
        repo_path, ok = QInputDialog.getText(self, "Repo Path", "Local repo path:")
        if not ok: return
        result = SyncEngine.sync(repo_path)
        QMessageBox.information(self, "SYNC", result)

    def smart_sync_all(self):
        result = self.orchestrator.smart_sync_all()
        QMessageBox.information(self, "Smart Sync", result)

    def bootstrap_all(self):
        result = self.orchestrator.bootstrap(str(REPOS_DIR))
        QMessageBox.information(self, "Bootstrap", result)

    def evolve_code(self):
        result = self.evolution.evolve(str(REPOS_DIR))
        QMessageBox.information(self, "EVOLUTION", result)

    def link_repos(self):
        parent, ok = QInputDialog.getText(self, "Parent Repo", "Parent repo:")
        if not ok: return
        child, ok = QInputDialog.getText(self, "Child Repo", "Child repo:")
        if not ok: return
        self.orchestrator.link(parent, child)
        QMessageBox.information(self, "Linked", f"{parent} → {child}")

    def cascade_update(self):
        repo, ok = QInputDialog.getText(self, "Repo", "Repo name:")
        if not ok: return
        result = self.orchestrator.cascade(repo, str(REPOS_DIR))
        QMessageBox.information(self, "Cascade", result)

    def background_sync(self):
        if os.path.exists(REPOS_DIR):
            for repo in os.listdir(REPOS_DIR):
                repo_path = os.path.join(REPOS_DIR, repo)
                if os.path.isdir(repo_path):
                    SyncEngine.sync(repo_path)

    # -------------------------
    # BASE ACTIONS (Legacy)
    # -------------------------

    def create_repo(self):
        if not self.github: raise Exception("GitHub Manager not initialized.")
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
        if not ok or not repo: return
        branch, ok = QInputDialog.getText(self, "Branch Name", "New branch:")
        if ok and branch:
            GitManager.create_branch(repo, branch)
            QMessageBox.information(self, "Success", f"Branch '{branch}' created")

    def commit_push(self):
        repo, ok = QInputDialog.getText(self, "Repo Path", "Local repo path:")
        if not ok or not repo: return
        GitManager.commit_all(repo)
        GitManager.push(repo)
        QMessageBox.information(self, "Success", "Committed & pushed")

    def create_pr(self):
        if not self.github: raise Exception("GitHub Manager not initialized.")
        repo, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok or not repo: return
        title, ok = QInputDialog.getText(self, "Title", "PR title:")
        if not ok or not title: return
        self.github.create_pr(repo, title, "Auto PR", "dev", "main")
        QMessageBox.information(self, "Success", "PR created")

    def check_status(self):
        if not self.github: raise Exception("GitHub Manager not initialized.")
        repo, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok or not repo: return
        status = self.github.get_latest_workflow_status(repo)
        QMessageBox.information(self, "Status", f"Workflow: {status}")

    def safe_merge(self):
        if not self.github: raise Exception("GitHub Manager not initialized.")
        repo, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok or not repo: return
        pr_number, ok = QInputDialog.getInt(self, "PR Number", "PR number:")
        if not ok: return
        result = self.github.safe_merge(repo, pr_number)
        QMessageBox.information(self, "Merge Result", result)

    def generate_workflow(self):
        from flux.workflow_generator import WorkflowGenerator
        repo_path, ok = QInputDialog.getText(self, "Repo Path", "Local repo path:")
        if not ok or not repo_path: return
        choice, ok = QInputDialog.getItem(self, "Workflow Type", "Select type:", ["Python", "Node", "APK"], 0, False)
        if not ok: return
        if choice == "Python": WorkflowGenerator.generate_python(repo_path)
        elif choice == "Node": WorkflowGenerator.generate_node(repo_path)
        elif choice == "APK": WorkflowGenerator.generate_apk(repo_path)
        GitManager.commit_all(repo_path, "auto workflow")
        GitManager.push(repo_path)
        QMessageBox.information(self, "OK", "Workflow created & pushed")

    def auto_mode(self):
        from flux.workflow_generator import WorkflowGenerator
        repo_path, ok = QInputDialog.getText(self, "Repo Path", "Local repo path:")
        if not ok or not repo_path: return
        WorkflowGenerator.auto(repo_path)
        GitManager.commit_all(repo_path, "auto workflow (AI)")
        GitManager.push(repo_path)
        QMessageBox.information(self, "AUTO", "Workflow auto-detected & deployed")

    def auto_fix(self):
        import requests
        from flux.fix_engine import FixEngine
        if not self.github: raise Exception("GitHub Manager not initialized.")
        repo_name, ok = QInputDialog.getText(self, "Repo Name", "Repo name:")
        if not ok or not repo_name: return
        repo_path, ok = QInputDialog.getText(self, "Repo Path", "Local path:")
        if not ok or not repo_path: return
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
        QMessageBox.information(self, "Fix Applied", f"Issue: {result['issue']}\nFix: {result['fix']}")


def start_app():
    app = QApplication(sys.argv)
    window = FluxUI()
    window.show()
    sys.exit(app.exec())
