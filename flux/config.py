import os
from pathlib import Path

BASE_DIR = Path.home() / "ProjectFlux"
BASE_DIR.mkdir(exist_ok=True)

REPOS_DIR = BASE_DIR / "repos"
REPOS_DIR.mkdir(exist_ok=True)

CONFIG_FILE = BASE_DIR / "config.json"

def get_github_token():
    return os.getenv("GITHUB_TOKEN")
