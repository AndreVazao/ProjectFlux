from PyQt6.QtCore import QThread, pyqtSignal
from flux.agent_loop import AgentLoop


class AgentThread(QThread):

    update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.agent = AgentLoop()

    def run(self):
        result = self.agent.start()
        self.update_signal.emit(result)

    def stop(self):
        self.agent.stop()
        self.quit()
