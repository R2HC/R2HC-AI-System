import abc, time, json
from datetime import datetime, timezone
from typing import Optional, Dict, Any

class BaseAgent(abc.ABC):
    def __init__(self, agent_id: str, heartbeat=None):
        self.agent_id = agent_id
        self.heartbeat = heartbeat
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.call_count = 0
        self.token_total = 0
        if heartbeat:
            heartbeat.register_agent(agent_id)
        print(f"[{agent_id}] Agent initialized")

    @abc.abstractmethod
    def run(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        pass

    def _record(self, tokens_used: int):
        self.call_count += 1
        self.token_total += tokens_used
        if self.heartbeat:
            self.heartbeat.add_tokens(tokens_used)
            self.heartbeat.update_activity()

    def shutdown(self):
        if self.heartbeat:
            self.heartbeat.deregister_agent(self.agent_id)
        print(f"[{self.agent_id}] Shut down. Calls: {self.call_count}, Tokens used: {self.token_total}")

    def status(self):
        return {
            "agent_id": self.agent_id,
            "created_at": self.created_at,
            "call_count": self.call_count,
            "token_total": self.token_total
        }