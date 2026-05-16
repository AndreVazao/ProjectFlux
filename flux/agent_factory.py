import os


class AgentFactory:

    def __init__(self):
        self.base_path = "flux/agents"

    def create_agent(self, name, purpose):
        filename = f"{name.lower()}_agent.py"
        path = os.path.join(self.base_path, filename)

        template = f'''
class {name}Agent:

    def run(self, repo, path):
        return "{purpose} executed"
'''

        with open(path, "w", encoding="utf-8") as f:
            f.write(template)

        return f"🤖 Agent {name} created"
