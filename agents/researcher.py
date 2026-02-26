import sys, re
from pathlib import Path
from typing import Optional, Dict, Any
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.base_agent import BaseAgent
from security.sanitizer import sanitize_input, audit

class ResearcherAgent(BaseAgent):
    def __init__(self, heartbeat=None):
        super().__init__("researcher", heartbeat)

    def run(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            clean_task = sanitize_input(task)
        except ValueError as e:
            return {"status": "rejected", "reason": str(e)}
        audit("RESEARCHER_TASK", clean_task[:100])
        self._record(len(clean_task) // 4)
        urls = re.findall(r'https?://[^\s"<>]+', clean_task)
        safe_urls = [u for u in urls if not any(b in u for b in ["localhost","127.0.0.1","file://"])]
        return {"status": "queued", "agent": "researcher", "task": clean_task, "urls_detected": safe_urls, "note": "Set OPENAI_API_KEY or ANTHROPIC_API_KEY in env to activate."}
