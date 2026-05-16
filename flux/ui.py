import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QInputDialog, QScrollArea, QTextEdit, QLineEdit
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
from flux.chat_engine import ChatEngine
from flux.memory_engine import MemoryEngine
from flux.agent_thread import AgentThread
from flux.swarm_thread import SwarmThread


class FluxUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ProjectFlux - Cockpit")
        self.setGeometry(200, 200, 900, 700)

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

        # Engines
        self.memory = MemoryEngine()
        self.chat_engine = ChatEngine(self)

        # Threads
        self.agent_thread = AgentThread()
        self.agent_thread.update_signal.connect(self.agent_update)

        self.swarm_thread = SwarmThread()
        self.swarm_thread.update_signal.connect(self.swarm_update)

        # Timer for background sync
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.background_sync)
        self.sync_timer.start(30000)  # 30s

        # Layouts
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        btn_layout = QVBoxLayout(content_widget)

        # --- LEFT BUTTONS ---

        # 🔥 AUTOPILOT (FULL AUTO)
        btn_autopilot = QPushButton("🤖 AUTOPILOT (FULL AUTO)")
        btn_autopilot.clicked.connect(self.safe_call(self.run_autopilot))
        btn_autopilot.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        btn_layout.addWidget(btn_autopilot)

        # ⚙️ PROVIDERS
        btn_providers = QPushButton("⚙️ Config Providers")
        btn_providers.clicked.connect(self.safe_call(self.configure_providers))
        btn_layout.addWidget(btn_providers)

        btn_openrouter = QPushButton("🔑 Set OpenRouter Key")
        btn_openrouter.clicked.connect(self.safe_call(self.set_openrouter_key))
        btn_layout.addWidget(btn_openrouter)

        # 🧠 MEMORY
        btn_memory = QPushButton("🧠 Sync Memory (Obsidian)")
        btn_memory.clicked.connect(self.safe_call(self.sync_memory))
        btn_layout.addWidget(btn_memory)

        btn_snapshot = QPushButton("📸 Snapshot System")
        btn_snapshot.clicked.connect(self.safe_call(self.snapshot))
        btn_layout.addWidget(btn_snapshot)

        # 🤖 AI LOOP
        btn_start_ai = QPushButton("🧠 START AI (AUTONOMOUS)")
        btn_start_ai.clicked.connect(self.safe_call(self.start_ai))
        btn_layout.addWidget(btn_start_ai)

        btn_stop_ai = QPushButton("🛑 STOP AI")
        btn_stop_ai.clicked.connect(self.safe_call(self.stop_ai))
        btn_layout.addWidget(btn_stop_ai)

        # 🐝 SWARM
        btn_swarm_start = QPushButton("🔥 START SWARM")
        btn_swarm_start.clicked.connect(self.safe_call(self.start_swarm))
        btn_layout.addWidget(btn_swarm_start)

        btn_swarm_stop = QPushButton("🛑 STOP SWARM")
        btn_swarm_stop.clicked.connect(self.safe_call(self.stop_swarm))
        btn_layout.addWidget(btn_swarm_stop)

        # 🚀 DEPLOY
        btn_deploy = QPushButton("🚀 AUTO DEPLOY")
        btn_deploy.clicked.connect(self.safe_call(self.auto_deploy))
        btn_layout.addWidget(btn_deploy)

        # 🔄 SYNC
        btn_sync = QPushButton("🔄 AUTO SYNC")
        btn_sync.clicked.connect(self.safe_call(self.auto_sync))
        btn_layout.addWidget(btn_sync)

        # 🌐 GLOBAL SYNC
        btn_smart_sync = QPushButton("🧠 Smart Sync (All Repos)")
        btn_smart_sync.clicked.connect(self.safe_call(self.smart_sync_all))
        btn_layout.addWidget(btn_smart_sync)

        # 🚀 BOOTSTRAP
        btn_bootstrap = QPushButton("🚀 FIRST RUN (Clone All)")
        btn_bootstrap.clicked.connect(self.safe_call(self.bootstrap_all))
        btn_layout.addWidget(btn_bootstrap)

        # 🧬 EVOLUTION
        btn_evolve = QPushButton("🧬 EVOLVE CODEBASE")
        btn_evolve.clicked.connect(self.safe_call(self.evolve_code))
        btn_layout.addWidget(btn_evolve)

        # 🔗 ORCHESTRATION
        btn_link = QPushButton("🔗 Link Repos")
        btn_link.clicked.connect(self.safe_call(self.link_repos))
        btn_layout.addWidget(btn_link)

        btn_cascade = QPushButton("🧠 Cascade Update")
        btn_cascade.clicked.connect(self.safe_call(self.cascade_update))
        btn_layout.addWidget(btn_cascade)

        # Legacy / Existing Controls
        btn_auto = QPushButton("AUTO MODE (Smart Workflow)")
        btn_auto.clicked.connect(self.safe_call(self.auto_mode))
        btn_layout.addWidget(btn_auto)

        btn_fix = QPushButton("AUTO FIX BUILD")
        btn_fix.clicked.connect(self.safe_call(self.auto_fix))
        btn_layout.addWidget(btn_fix)

        btn_status = QPushButton("Check Build Status")
        btn_status.clicked.connect(self.safe_call(self.check_status))
        btn_layout.addWidget(btn_status)

        btn_merge = QPushButton("Safe Merge PR")
        btn_merge.clicked.connect(self.safe_call(self.safe_merge))
        btn_layout.addWidget(btn_merge)

        btn_workflow = QPushButton("Generate Workflow (Manual)")
        btn_workflow.clicked.connect(self.safe_call(self.generate_workflow))
        btn_layout.addWidget(btn_workflow)

        btn_create_repo = QPushButton("Create New Repo")
        btn_create_repo.clicked.connect(self.safe_call(self.create_repo))
        btn_layout.addWidget(btn_create_repo)

        btn_clone = QPushButton("Clone Repo")
        btn_clone.clicked.connect(self.safe_call(self.clone_repo))
        btn_layout.addWidget(btn_clone)

        btn_branch = QPushButton("Create Branch")
        btn_branch.clicked.connect(self.safe_call(self.create_branch))
        btn_layout.addWidget(btn_branch)

        btn_commit = QPushButton("Commit & Push")
        btn_commit.clicked.connect(self.safe_call(self.commit_push))
        btn_layout.addWidget(btn_commit)

        btn_pr = QPushButton("Create PR")
        btn_pr.clicked.connect(self.safe_call(self.create_pr))
        btn_layout.addWidget(btn_pr)

        scroll.setWidget(content_widget)
        left_layout.addWidget(scroll)

        # --- RIGHT CHAT ---
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas;")

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type command... (ex: autopilot repo ProjectFlux)")
        self.chat_input.returnPressed.connect(self.send_chat)

        right_layout.addWidget(self.chat_display)
        right_layout.addWidget(self.chat_input)

        # Final Assembly
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        self.setLayout(main_layout)

    def safe_call(self, func):
        def wrapper():
            try:
                func()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
        return wrapper

    # -------------------------
    # CHAT LOGIC
    # -------------------------

    def send_chat(self):
        text = self.chat_input.text()
        if not text: return

        self.chat_display.append(f"🧑 <b>User:</b> {text}")

        try:
            result = self.chat_engine.process(text)
        except Exception as e:
            result = f"❌ Error: {str(e)}"

        self.chat_display.append(f"🤖 <b>AI:</b> {result}")
        self.chat_input.clear()

    def get_repo_path(self, repo_name):
        from flux.repo_registry import RepoRegistry
        registry = RepoRegistry()
        for repo_id, info in registry.get_all().items():
            if info["name"] == repo_name:
                return info["path"]
        return None

    # -------------------------
    # NEW ACTIONS
    # -------------------------

    def sync_memory(self):
        result = self.memory.capture_commits()
        QMessageBox.information(self, "Memory", result)

    def snapshot(self):
        result = self.memory.snapshot_all()
        QMessageBox.information(self, "Snapshot", result)

    def start_ai(self):
        self.agent_thread.start()
        QMessageBox.information(self, "AI", "Autonomous mode started")

    def stop_ai(self):
        self.agent_thread.stop()
        QMessageBox.information(self, "AI", "Stopped")

    def agent_update(self, text):
        self.chat_display.append(f"🤖 <b>AI LOOP:</b>\n{text}")

    def start_swarm(self):
        self.swarm_thread.start()
        QMessageBox.information(self, "SWARM", "Swarm started")

    def stop_swarm(self):
        self.swarm_thread.stop()
        QMessageBox.information(self, "SWARM", "Swarm stopped")

    def swarm_update(self, text):
        self.chat_display.append(f"🐝 <b>SWARM:</b>\n{text}")

    def set_openrouter_key(self):
        from flux.providers import ProviderManager
        key, ok = QInputDialog.getText(self, "OpenRouter", "API Key:")
        if ok:
            ProviderManager().set("openrouter", key)
            QMessageBox.information(self, "OK", "Key saved")

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
