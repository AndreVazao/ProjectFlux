import os
from git import Repo

class GitManager:

    @staticmethod
    def clone_repo(url, path):
        return Repo.clone_from(url, path)

    @staticmethod
    def init_repo(path):
        return Repo.init(path)

    @staticmethod
    def create_branch(repo_path, branch_name):
        repo = Repo(repo_path)
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()

    @staticmethod
    def commit_all(repo_path, message="auto commit"):
        repo = Repo(repo_path)
        repo.git.add(all=True)
        repo.index.commit(message)

    @staticmethod
    def push(repo_path, branch="main"):
        repo = Repo(repo_path)
        origin = repo.remote(name='origin')
        origin.push(branch)
