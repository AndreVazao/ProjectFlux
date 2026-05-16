import os

try:
    from git import Repo
except ImportError:
    Repo = None

class GitManager:

    @staticmethod
    def clone_repo(url, path):
        if Repo is None:
            raise ImportError("GitPython (git) is not installed.")
        try:
            return Repo.clone_from(url, path)
        except Exception as e:
            print(f"Error cloning repo: {e}")
            raise

    @staticmethod
    def init_repo(path):
        if Repo is None:
            raise ImportError("GitPython (git) is not installed.")
        try:
            return Repo.init(path)
        except Exception as e:
            print(f"Error initializing repo: {e}")
            raise

    @staticmethod
    def create_branch(repo_path, branch_name):
        if Repo is None:
            raise ImportError("GitPython (git) is not installed.")
        try:
            repo = Repo(repo_path)
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
        except Exception as e:
            print(f"Error creating branch: {e}")
            raise

    @staticmethod
    def commit_all(repo_path, message="auto commit"):
        if Repo is None:
            raise ImportError("GitPython (git) is not installed.")
        try:
            repo = Repo(repo_path)
            repo.git.add(all=True)
            repo.index.commit(message)
        except Exception as e:
            print(f"Error committing all: {e}")
            raise

    @staticmethod
    def push(repo_path, branch="main"):
        if Repo is None:
            raise ImportError("GitPython (git) is not installed.")
        try:
            repo = Repo(repo_path)
            origin = repo.remote(name='origin')
            origin.push(branch)
        except Exception as e:
            print(f"Error pushing: {e}")
            raise
