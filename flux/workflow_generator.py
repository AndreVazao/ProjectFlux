from pathlib import Path
from flux.project_detector import ProjectDetector

class WorkflowGenerator:

    @staticmethod
    def auto(repo_path):
        project_type = ProjectDetector.detect(repo_path)

        if project_type == "python":
            WorkflowGenerator.generate_python(repo_path)

        elif project_type == "node":
            WorkflowGenerator.generate_node(repo_path)

        elif project_type == "apk":
            WorkflowGenerator.generate_apk(repo_path)

        else:
            raise Exception("Unknown project type")

class WorkflowGenerator:

    @staticmethod
    def generate_python(repo_path):
        content = f"""
name: Python CI

on:
  push:
    branches: [ "main", "dev", "feature/**" ]

jobs:
  build:
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v4

    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install deps
      run: pip install -r requirements.txt

    - name: Build EXE
      run: |
        pip install pyinstaller
        pyinstaller --onefile --windowed main.py
"""

        WorkflowGenerator._write(repo_path, content)

    @staticmethod
    def generate_node(repo_path):
        content = f"""
name: Node CI

on:
  push:
    branches: [ "main", "dev", "feature/**" ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - uses: actions/setup-node@v4
      with:
        node-version: 18

    - run: npm install
    - run: npm run build
"""

        WorkflowGenerator._write(repo_path, content)

    @staticmethod
    def generate_apk(repo_path):
        content = f"""
name: Android Build

on:
  push:
    branches: [ "main", "dev" ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Setup Java
      uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
        java-version: '17'

    - name: Build APK
      run: ./gradlew assembleDebug
"""

        WorkflowGenerator._write(repo_path, content)

    @staticmethod
    def _write(repo_path, content):
        path = Path(repo_path) / ".github" / "workflows"
        path.mkdir(parents=True, exist_ok=True)

        file = path / "auto.yml"
        file.write_text(content)
