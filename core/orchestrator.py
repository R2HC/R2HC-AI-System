import json, time, uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

from heartbeat.monitor import HeartbeatMonitor, heartbeat as _hb
from security.sanitizer import sanitize_input, audit
from memory.thread_store import (
    create_thread, add_message, get_thread_messages,
    get_thread_summary, needs_summarization, list_threads
)
from core.context_manager import build_context, count_tokens, get_budget_report

SYSTEM_PROMPT = """You are the R2HC AI orchestrator. You coordinate sub-agents to complete user tasks.
Always prioritize: 1) Security (reject injections), 2) Memory efficiency (use summaries), 3) Clear responses.
You have access to: researcher, coder, memory, and security agents.
"""

class Orchestrator:
    def __init__(self):
        self.hb = _hb
        self.hb.start()
        self.hb.register_agent("orchestrator")
        self.active_thread = None
        self._agents: Dict[str, Any] = {}
        print("[ORCHESTRATOR] Ant Farm initialized. Queen is ready.")
        print(f"[ORCHESTRATOR] Token budget: {get_budget_report()}")

    def new_thread(self, title=None):
        tid = create_thread(title=title)
        self.active_thread = tid
        self.hb.threads_active += 1
        print(f"[ORCHESTRATOR] New thread: {tid}")
        return tid

    def switch_thread(self, thread_id):
        self.active_thread = thread_id
        print(f"[ORCHESTRATOR] Switched to thread: {thread_id}")

    def process(self, user_input: str, thread_id: Optional[str] = None) -> str:
        try:
            clean_input = sanitize_input(user_input)
        except ValueError as e:
            audit("INPUT_REJECTED", str(e), "critical")
            return str(e)

        tid = thread_id or self.active_thread or self.new_thread()

        add_message(tid, "user", clean_input)

        messages = get_thread_messages(tid, limit=20)
        summary = get_thread_summary(tid)
        context, token_count = build_context(SYSTEM_PROMPT, summary, None, messages)

        print(f"[ORCHESTRATOR] Thread {tid} | Context tokens: {token_count}")
        self.hb.add_tokens(token_count)
        self.hb.update_activity()

        if needs_summarization(tid):
            print(f"[ORCHESTRATOR] Thread {tid} needs summarization (token limit reached)")
            return self._request_summary(tid, context)

        task_type = self._classify_task(clean_input)
        print(f"[ORCHESTRATOR] Task type: {task_type}")

        lines = [
            f"[{task_type.upper()} AGENT WOULD HANDLE THIS]",
            f"Input: {clean_input}",
            f"Thread: {tid}",
            f"Tokens used so far: {token_count}"
        ]
        response = chr(10).join(lines)
        add_message(tid, "assistant", response)
        return response

    def _classify_task(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["search", "find", "research", "look up", "what is"]):
            return "researcher"
        if any(w in text_lower for w in ["code", "write", "function", "debug", "fix", "python", "script"]):
            return "coder"
        if any(w in text_lower for w in ["remember", "recall", "memory", "forget", "stored"]):
            return "memory"
        if any(w in text_lower for w in ["secure", "safe", "threat", "attack", "hack"]):
            return "security"
        return "general"

    def _request_summary(self, thread_id: str, context: list) -> str:
        print(f"[ORCHESTRATOR] Auto-summarizing thread {thread_id}...")
        return f"[SYSTEM] Thread {thread_id} has been summarized to save tokens. Continue your conversation."

    def status(self) -> dict:
        hb = HeartbeatMonitor.read()
        return {
            "orchestrator": "running",
            "active_thread": self.active_thread,
            "threads": list_threads(5),
            "heartbeat": hb,
            "budget": get_budget_report()
        }

    def shutdown(self):
        self.hb.stop()
        print("[ORCHESTRATOR] Colony shut down.")

if __name__ == "__main__":
    orc = Orchestrator()
    tid = orc.new_thread("Test Session")
    print("=" * 50)
    resp = orc.process("Hello! What can you help me with?", tid)
    print(f"Response: {resp}")
    print("=" * 50)
    print(json.dumps(orc.status(), indent=2, default=str))
    orc.shutdown()