from PyQt6.QtCore import QThread, pyqtSignal
from flux.swarm_orchestrator import SwarmOrchestrator


class SwarmThread(QThread):

    update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.swarm = SwarmOrchestrator()
        self.running = True

    def run(self):
        while self.running:
            result = self.swarm.run()
            self.update_signal.emit(result)

    def stop(self):
        self.running = False
        self.quit()
