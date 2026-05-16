import requests
import json
from flux.memory_engine import MemoryEngine
from flux.context_engine import ContextEngine


class AIEngine:

    def __init__(self):
        self.api_key = self._load_key()
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "mistralai/mistral-7b-instruct"  # free tier

        self.memory = MemoryEngine()
        self.context_engine = ContextEngine(str(self.memory.vault_path))

    # -------------------------
    # LOAD KEY
    # -------------------------

    def _load_key(self):
        try:
            from flux.providers import ProviderManager
            return ProviderManager().get("openrouter")
        except:
            return None

    # -------------------------
    # THINK
    # -------------------------

    def think(self, repo, user_input="", logs=""):
        context = self.context_engine.build_context(repo)

        prompt = f"""
You are an autonomous DevOps AI.

Your job:
- Analyze context
- Decide action

Available actions:
- fix
- deploy
- sync
- evolve
- nothing

Reply ONLY in JSON:

{{
  "action": "...",
  "reason": "...",
  "steps": ["..."]
}}

CONTEXT:
{context}

LOGS:
{logs}

USER:
{user_input}
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:
            res = requests.post(self.base_url, headers=headers, json=data)
            result = res.json()

            content = result["choices"][0]["message"]["content"]

            return json.loads(content)

        except Exception as e:
            return {
                "action": "nothing",
                "reason": f"AI error: {str(e)}",
                "steps": []
            }
