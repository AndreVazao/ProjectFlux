import os
import logging
from flux.config import logger

try:
    from git import Repo
except ImportError:
    Repo = None
    logger.warning("GitPython (git) is not installed. Git operations will fail.")

class GitManager:

    @staticmethod
    def clone_repo(url, path):
        if Repo is None:
            raise ImportError("GitPython (git) is not installed.")
        logger.info(f"Cloning {url} to {path}")
        try:
            return Repo.clone_from(url, path)
        except Exception as e:
            logger.error(f"Error cloning repo {url}: {e}", exc_info=True)
            raise

    @staticmethod
    def init_repo(path):
        if Repo is None:
            raise ImportError("GitPython (git) is not installed.")
        logger.info(f"Initializing git repo at {path}")
        try:
            return Repo.init(path)
        except Exception as e:
            logger.error(f"Error initializing repo at {path}: {e}", exc_info=True)
            raise

    @staticmethod
    def create_branch(repo_path, branch_name):
        if Repo is None:
            raise ImportError("GitPython (git) is not installed.")
        logger.info(f"Creating branch {branch_name} in {repo_path}")
        try:
            repo = Repo(repo_path)
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
        except Exception as e:
            logger.error(f"Error creating branch {branch_name} in {repo_path}: {e}", exc_info=True)
            raise

    @staticmethod
    def commit_all(repo_path, message="auto commit"):
        if Repo is None:
            raise ImportError("GitPython (git) is not installed.")
        logger.info(f"Committing changes in {repo_path} with message: {message}")
        try:
            repo = Repo(repo_path)
            repo.git.add(all=True)
            repo.index.commit(message)
        except Exception as e:
            logger.error(f"Error committing in {repo_path}: {e}", exc_info=True)
            raise

    @staticmethod
    def push(repo_path, branch="main"):
        if Repo is None:
            raise ImportError("GitPython (git) is not installed.")
        logger.info(f"Pushing {branch} from {repo_path}")
        try:
            repo = Repo(repo_path)
            origin = repo.remote(name='origin')
            origin.push(branch)
        except Exception as e:
            logger.error(f"Error pushing in {repo_path}: {e}", exc_info=True)
            raise
