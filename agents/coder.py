import sys
from pathlib import Path
from typing import Optional, Dict, Any
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.base_agent import BaseAgent
from security.sanitizer import sanitize_input, audit

LANGUAGES = ["python", "javascript", "typescript", "bash", "sql", "rust", "go"]

class CoderAgent(BaseAgent):
    def __init__(self, heartbeat=None):
        super().__init__("coder", heartbeat)

    def run(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            clean_task = sanitize_input(task)
        except ValueError as e:
            return {"status": "rejected", "reason": str(e)}
        audit("CODER_TASK", clean_task[:100])
        self._record(len(clean_task) // 4)
        lang = next((l for l in LANGUAGES if l in clean_task.lower()), "unknown")
        t = clean_task.lower()
        if any(w in t for w in ["debug","fix","bug","error"]): action = "debug"
        elif any(w in t for w in ["review","check","analyze"]): action = "review"
        elif any(w in t for w in ["refactor","clean","improve"]): action = "refactor"
        elif any(w in t for w in ["write","create","generate","build"]): action = "generate"
        else: action = "general"
        return {"status": "queued", "agent": "coder", "task": clean_task, "language": lang, "action": action, "note": "Set OPENAI_API_KEY or ANTHROPIC_API_KEY in env to activate."}
