import os
import logging
from pathlib import Path

# --- DIRECTORIES ---
BASE_DIR = Path.home() / "ProjectFlux"
BASE_DIR.mkdir(exist_ok=True)

REPOS_DIR = BASE_DIR / "repos"
REPOS_DIR.mkdir(exist_ok=True)

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

CONFIG_FILE = BASE_DIR / "config.json"

# --- LOGGING ---
def setup_logging():
    log_file = LOGS_DIR / "runtime.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("ProjectFlux")

logger = setup_logging()

def get_github_token():
    return os.getenv("GITHUB_TOKEN")
