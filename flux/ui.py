import sys
import os
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QInputDialog, QScrollArea, QTextEdit, QLineEdit, QLabel
)
from PyQt6.QtCore import QTimer, Qt

# Absolute imports
from flux.config import REPOS_DIR, logger
from flux.github_manager import GitHubManager
from flux.git_manager import GitManager
from flux.providers import ProviderManager
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
        logger.info("Initializing UI...")
        self.setWindowTitle("ProjectFlux - Cockpit")
        self.setGeometry(200, 200, 1000, 800)

        # Initialize Managers with Error Handling
        try:
            self.github = GitHubManager()
        except Exception as e:
            logger.error(f"GitHub Manager Init Fail: {e}")
            self.github = None

        self.providers = ProviderManager()
        self.deploy = DeployManager(self.providers)
        self.autopilot = AutopilotEngine(self.github, self.deploy)
        self.orchestrator = Orchestrator(self.github)
        self.evolution = EvolutionEngine()
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

        self.init_ui()
        logger.info("UI Initialized successfully.")

    def init_ui(self):
        # Layouts
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # --- LEFT PANEL (Controls) ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        btn_layout = QVBoxLayout(content_widget)

        # Labels
        btn_layout.addWidget(QLabel("<b>🚀 CORE OPERATIONS</b>"))

        # AUTOPILOT
        btn_autopilot = QPushButton("🤖 AUTOPILOT (FULL AUTO)")
        btn_autopilot.clicked.connect(self.safe_call(self.run_autopilot))
        btn_autopilot.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        btn_layout.addWidget(btn_autopilot)

        btn_layout.addWidget(QLabel("<b>⚙️ CONFIGURATION</b>"))

        btn_providers = QPushButton("⚙️ Config Providers")
        btn_providers.clicked.connect(self.safe_call(self.configure_providers))
        btn_layout.addWidget(btn_providers)

        btn_openrouter = QPushButton("🔑 Set OpenRouter Key")
        btn_openrouter.clicked.connect(self.safe_call(self.set_openrouter_key))
        btn_layout.addWidget(btn_openrouter)

        btn_layout.addWidget(QLabel("<b>🧠 INTELLIGENCE</b>"))

        btn_start_ai = QPushButton("🧠 START AI LOOP")
        btn_start_ai.clicked.connect(self.safe_call(self.start_ai))
        btn_layout.addWidget(btn_start_ai)

        btn_stop_ai = QPushButton("🛑 STOP AI LOOP")
        btn_stop_ai.clicked.connect(self.safe_call(self.stop_ai))
        btn_layout.addWidget(btn_stop_ai)

        btn_start_swarm = QPushButton("🐝 START SWARM")
        btn_start_swarm.clicked.connect(self.safe_call(self.start_swarm))
        btn_layout.addWidget(btn_start_swarm)

        btn_stop_swarm = QPushButton("🛑 STOP SWARM")
        btn_stop_swarm.clicked.connect(self.safe_call(self.stop_swarm))
        btn_layout.addWidget(btn_stop_swarm)

        btn_layout.addWidget(QLabel("<b>📂 REPO MANAGEMENT</b>"))

        btn_sync_all = QPushButton("🔄 Smart Sync All")
        btn_sync_all.clicked.connect(self.safe_call(self.smart_sync_all))
        btn_layout.addWidget(btn_sync_all)

        btn_bootstrap = QPushButton("🏗️ Bootstrap Repos")
        btn_bootstrap.clicked.connect(self.safe_call(self.bootstrap_all))
        btn_layout.addWidget(btn_bootstrap)

        btn_layout.addStretch()
        scroll.setWidget(content_widget)
        left_layout.addWidget(scroll)

        # --- RIGHT PANEL (Terminal / Chat) ---
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; font-family: Consolas, monospace;")
        right_layout.addWidget(QLabel("<b>🖥️ COCKPIT LOGS / CHAT</b>"))
        right_layout.addWidget(self.chat_display)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type command (e.g. sync, deploy repo X)...")
        self.chat_input.returnPressed.connect(self.send_chat)
        right_layout.addWidget(self.chat_input)

        # Assemble
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        self.setLayout(main_layout)

    # -------------------------
    # WRAPPERS
    # -------------------------

    def safe_call(self, func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"UI Action Error in {func.__name__}: {e}", exc_info=True)
                QMessageBox.warning(self, "Error", f"Action failed: {e}")
        return wrapper

    # -------------------------
    # ACTIONS
    # -------------------------

    def send_chat(self):
        text = self.chat_input.text()
        if not text: return
        self.chat_display.append(f"<b>USER:</b> {text}")
        self.chat_input.clear()

        try:
            response = self.chat_engine.process(text)
            self.chat_display.append(f"<b>FLUX:</b> {response}")
        except Exception as e:
            self.chat_display.append(f"<b>ERROR:</b> {e}")

    def start_ai(self):
        if not self.agent_thread.isRunning():
            self.agent_thread.start()
            self.chat_display.append("🤖 AI Loop Started")

    def stop_ai(self):
        self.agent_thread.stop()
        self.chat_display.append("🤖 AI Loop Stopped")

    def start_swarm(self):
        if not self.swarm_thread.isRunning():
            self.swarm_thread.start()
            self.chat_display.append("🐝 Swarm Started")

    def stop_swarm(self):
        self.swarm_thread.stop()
        self.chat_display.append("🐝 Swarm Stopped")

    def agent_update(self, text):
        self.chat_display.append(f"🤖 <b>AI:</b> {text}")

    def swarm_update(self, text):
        self.chat_display.append(f"🐝 <b>SWARM:</b> {text}")

    def configure_providers(self):
        providers = ["GitHub", "Vercel", "Render", "Supabase"]
        provider, ok = QInputDialog.getItem(self, "Select Provider", "Provider:", providers, 0, False)
        if not ok: return
        key, ok = QInputDialog.getText(self, f"{provider} API Key", f"Enter {provider} API Key:", QLineEdit.EchoMode.Password)
        if not ok or not key: return
        self.providers.set_key(provider, key)
        QMessageBox.information(self, "Saved", f"{provider} configured.")

    def set_openrouter_key(self):
        key, ok = QInputDialog.getText(self, "OpenRouter", "API Key:", QLineEdit.EchoMode.Password)
        if ok and key:
            self.providers.set("openrouter", key)
            QMessageBox.information(self, "OK", "OpenRouter key saved")

    def run_autopilot(self):
        repo_name, ok = QInputDialog.getText(self, "Autopilot", "Enter Repo Name:")
        if not ok or not repo_name: return
        repo_path = REPOS_DIR / repo_name
        result = self.autopilot.run(repo_name, str(repo_path))
        QMessageBox.information(self, "Autopilot", result)

    def smart_sync_all(self):
        result = self.orchestrator.smart_sync_all()
        self.chat_display.append(f"🔄 Sync Results:\n{result}")

    def bootstrap_all(self):
        result = self.orchestrator.bootstrap(str(REPOS_DIR))
        QMessageBox.information(self, "Bootstrap", result)

    def evolve_code(self):
        result = self.evolution.evolve(str(REPOS_DIR))
        self.chat_display.append(f"🧬 Evolution: {result}")

    def background_sync(self):
        if REPOS_DIR.exists():
            for repo_dir in REPOS_DIR.iterdir():
                if repo_dir.is_dir():
                    try:
                        SyncEngine.sync(str(repo_dir))
                    except:
                        pass

    def get_repo_path(self, repo_name):
        return str(REPOS_DIR / repo_name)

    # -------------------------
    # LIFECYCLE
    # -------------------------

    def closeEvent(self, event):
        logger.info("Closing UI and stopping threads...")
        self.agent_thread.stop()
        self.swarm_thread.stop()

        if self.agent_thread.isRunning():
            self.agent_thread.wait(2000)
        if self.swarm_thread.isRunning():
            self.swarm_thread.wait(2000)

        logger.info("UI Exit.")
        event.accept()

def start_app():
    app = QApplication(sys.argv)
    # Set dark theme or similar if needed
    window = FluxUI()
    window.show()
    sys.exit(app.exec())
