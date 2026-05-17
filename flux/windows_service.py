import win32serviceutil
import win32service
import win32event
import servicemanager
import subprocess
import time
import os
import sys

LOG_DIR = "C:\\ProjectFlux\\logs"
BACKEND_CMD = [sys.executable, "-m", "flux.server"]

os.makedirs(LOG_DIR, exist_ok=True)


def log(msg):
    with open(os.path.join(LOG_DIR, "service.log"), "a", encoding="utf-8") as f:
        f.write(msg + "\n")


class ProjectFluxService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ProjectFluxService"
    _svc_display_name_ = "ProjectFlux Backend Service"
    _svc_description_ = "Autonomous DevOps AI Backend"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.process = None
        self.running = True

    def SvcStop(self):
        self.running = False
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        if self.process:
            self.process.terminate()

        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("ProjectFlux Service Started")

        while self.running:
            try:
                log("Starting backend...")
                self.process = subprocess.Popen(
                    BACKEND_CMD,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                while self.running:
                    time.sleep(3)

                    if self.process.poll() is not None:
                        log("Backend crashed. Restarting...")
                        break

            except Exception as e:
                log(f"Service error: {str(e)}")
                time.sleep(5)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(ProjectFluxService)
