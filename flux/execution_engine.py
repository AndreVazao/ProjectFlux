from flux.github_manager import GitHubManager
from flux.workflow_generator import WorkflowGenerator
from flux.deploy_manager import DeployManager
from flux.git_manager import GitManager
from flux.providers_manager import ProvidersManager
from pathlib import Path
import os


class ExecutionEngine:

    def __init__(self):
        self.github = GitHubManager()
        self.providers = ProvidersManager()

    def execute(self, idea):

        name = idea["name"]
        repos_dir = Path("repos")
        repos_dir.mkdir(exist_ok=True)
        repo_path = repos_dir / name

        # 1. criar repo
        self.github.create_repo(name)

        # 2. criar estrutura mínima
        repo_path.mkdir(parents=True, exist_ok=True)

        main_file = repo_path / "main.py"
        main_file.write_text("print('ProjectFlux autonomous project')")

        # 3. workflow automático
        # WorkflowGenerator.auto expects a string path
        # It detects type from contents or tries to guess.
        # Here we know the type from idea.
        # But WorkflowGenerator.auto(str(repo_path)) uses ProjectDetector.
        # Let's ensure requirements.txt exists so it detects python.
        req_file = repo_path / "requirements.txt"
        req_file.write_text("requests\n")

        WorkflowGenerator.auto(str(repo_path))

        # 4. git push
        # We need to init git if not already
        os.system(f"git -C {repo_path} init")
        os.system(f"git -C {repo_path} remote add origin https://github.com/{self.github.username}/{name}.git")

        GitManager.commit_all(str(repo_path), "init project")
        GitManager.push(str(repo_path))

        # 5. deploy
        deploy_mgr = DeployManager(self.providers)
        result = deploy_mgr.auto_deploy_smart(name, str(repo_path))

        return f"executed:{name} -> {result}"
