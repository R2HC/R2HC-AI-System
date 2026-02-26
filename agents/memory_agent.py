import sys, json, time
from pathlib import Path
from typing import Optional, Dict, Any, List
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.base_agent import BaseAgent
from security.sanitizer import sanitize_input, audit
from memory.thread_store import list_threads, get_thread_messages, get_thread_summary

class MemoryAgent(BaseAgent):
    def __init__(self, heartbeat=None):
        super().__init__("memory", heartbeat)
        self._facts_file = Path(__file__).parent.parent / "memory" / "facts.json"
        self._load_facts()

    def _load_facts(self):
        try:
            self._facts = json.loads(self._facts_file.read_text()) if self._facts_file.exists() else {}
        except Exception:
            self._facts = {}

    def _save_facts(self):
        self._facts_file.parent.mkdir(parents=True, exist_ok=True)
        self._facts_file.write_text(json.dumps(self._facts, indent=2))

    def store_fact(self, key: str, value: str):
        try:
            key = sanitize_input(key, max_len=200)
            value = sanitize_input(value, max_len=2000)
        except ValueError as e:
            return {"status": "rejected", "reason": str(e)}
        self._facts[key] = {"value": value, "stored_at": time.time()}
        self._save_facts()
        audit("MEMORY_STORE", "key=" + key[:50])
        if self.heartbeat:
            self.heartbeat.memory_entries = len(self._facts)
        return {"status": "stored", "key": key}

    def recall(self, query: str) -> List[Dict]:
        q = query.lower()
        results = []
        for k, v in self._facts.items():
            if q in k.lower() or q in v["value"].lower():
                results.append({"key": k, "value": v["value"]})
        return results[:10]

    def run(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            clean_task = sanitize_input(task)
        except ValueError as e:
            return {"status": "rejected", "reason": str(e)}
        audit("MEMORY_QUERY", clean_task[:100])
        self._record(len(clean_task) // 4)
        t = clean_task.lower()
        if any(w in t for w in ["list","threads","history","conversations"]):
            return {"status": "ok", "threads": list_threads(20)}
        if any(w in t for w in ["recall","remember","find","search"]):
            return {"status": "ok", "results": self.recall(clean_task)}
        return {"status": "ok", "facts_count": len(self._facts), "threads": list_threads(5)}
