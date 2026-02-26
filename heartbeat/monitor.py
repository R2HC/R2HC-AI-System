import json, time, threading, os, hashlib
from datetime import datetime, timezone
from pathlib import Path

HEARTBEAT_FILE = Path(__file__).parent / "heartbeat.json"
HEARTBEAT_INTERVAL = 30

class HeartbeatMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.agents_active = []
        self.memory_entries = 0
        self.threads_active = 0
        self.last_activity = datetime.now(timezone.utc).isoformat()
        self.token_usage_today = 0
        self.alerts = []
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def update_activity(self):
        with self._lock:
            self.last_activity = datetime.now(timezone.utc).isoformat()

    def add_alert(self, message, level="warning"):
        with self._lock:
            self.alerts.append({"ts": datetime.now(timezone.utc).isoformat(), "level": level, "msg": message})
            self.alerts = self.alerts[-10:]

    def register_agent(self, agent_id):
        with self._lock:
            if agent_id not in self.agents_active:
                self.agents_active.append(agent_id)

    def deregister_agent(self, agent_id):
        with self._lock:
            self.agents_active = [a for a in self.agents_active if a != agent_id]

    def add_tokens(self, count):
        with self._lock:
            self.token_usage_today += count

    def _build_status(self):
        uptime = int(time.time() - self.start_time)
        status = "healthy"
        if self.alerts:
            lvl = self.alerts[-1]["level"]
            if lvl == "critical": status = "critical"
            elif lvl == "warning": status = "degraded"
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status, "uptime_seconds": uptime,
            "agents_active": list(self.agents_active),
            "memory_entries": self.memory_entries,
            "threads_active": self.threads_active,
            "last_activity": self.last_activity,
            "token_usage_today": self.token_usage_today,
            "alerts": list(self.alerts),
            "system": "R2HC-AI-v1.0"
        }
        s = json.dumps({k: v for k, v in payload.items() if k != "checksum"}, sort_keys=True)
        payload["checksum"] = hashlib.sha256(s.encode()).hexdigest()[:16]
        return payload

    def write(self):
        with self._lock:
            status = self._build_status()
        try:
            tmp = str(HEARTBEAT_FILE) + ".tmp"
            with open(tmp, "w") as f:
                json.dump(status, f, indent=2)
            os.replace(tmp, HEARTBEAT_FILE)
        except Exception as e:
            print(f"[HEARTBEAT ERROR] {e}")

    def _run_loop(self):
        while self._running:
            self.write()
            time.sleep(HEARTBEAT_INTERVAL)

    def start(self):
        self._running = True
        self.write()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print(f"[HEARTBEAT] Started -> {HEARTBEAT_FILE}")

    def stop(self):
        self._running = False
        self.add_alert("System shutting down", "info")
        self.write()

    @staticmethod
    def read():
        try:
            with open(HEARTBEAT_FILE) as f:
                return json.load(f)
        except FileNotFoundError:
            return {"status": "unknown", "error": "not found"}
        except json.JSONDecodeError:
            return {"status": "error", "error": "corrupted"}

    @staticmethod
    def is_healthy():
        hb = HeartbeatMonitor.read()
        if hb.get("status") not in ("healthy", "degraded"):
            return False
        ts = hb.get("timestamp", "")
        if ts:
            try:
                age = (datetime.now(timezone.utc) - datetime.fromisoformat(ts)).total_seconds()
                if age > 120: return False
            except Exception:
                pass
        return True

heartbeat = HeartbeatMonitor()