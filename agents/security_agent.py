import sys, json, time
from pathlib import Path
from typing import Optional, Dict, Any, List
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.base_agent import BaseAgent
from security.sanitizer import sanitize_input, audit, is_injection, AUDIT_LOG

class SecurityAgent(BaseAgent):
    def __init__(self, heartbeat=None):
        super().__init__("security", heartbeat)
        self._rate_buckets: Dict[str, List[float]] = defaultdict(list)
        self.RATE_LIMIT = 30

    def check_rate_limit(self, user_id: str = "default") -> bool:
        now = time.time()
        self._rate_buckets[user_id] = [t for t in self._rate_buckets[user_id] if now - t < 60.0]
        if len(self._rate_buckets[user_id]) >= self.RATE_LIMIT:
            audit("RATE_LIMIT_EXCEEDED", "user=" + user_id, "warning")
            if self.heartbeat:
                self.heartbeat.add_alert("Rate limit hit: " + user_id, "warning")
            return False
        self._rate_buckets[user_id].append(now)
        return True

    def scan_input(self, text: str) -> Dict:
        try:
            sanitize_input(text)
            return {"safe": True, "threats": []}
        except ValueError as e:
            return {"safe": False, "threats": [str(e)]}

    def read_audit_log(self, last_n=20) -> List[Dict]:
        try:
            lines = AUDIT_LOG.read_text().strip().splitlines()[-last_n:]
            return [json.loads(l) for l in lines if l.strip()]
        except FileNotFoundError:
            return []
        except Exception as e:
            return [{"error": str(e)}]

    def threat_summary(self) -> Dict:
        logs = self.read_audit_log(100)
        critical = [l for l in logs if l.get("severity") == "critical"]
        warnings  = [l for l in logs if l.get("severity") == "warning"]
        return {"total_events": len(logs), "critical": len(critical), "warnings": len(warnings), "recent_critical": critical[-3:]}

    def run(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            clean_task = sanitize_input(task)
        except ValueError as e:
            return {"status": "rejected", "reason": str(e)}
        audit("SECURITY_QUERY", clean_task[:100])
        self._record(len(clean_task) // 4)
        t = clean_task.lower()
        if any(w in t for w in ["audit","log","events"]):
            return {"status": "ok", "audit_log": self.read_audit_log(20)}
        if any(w in t for w in ["threat","summary","report","status"]):
            return {"status": "ok", "summary": self.threat_summary()}
        return {"status": "ok", "summary": self.threat_summary()}
