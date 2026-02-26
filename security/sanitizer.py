import re, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

AUDIT_LOG = Path(__file__).parent.parent / "logs" / "security.log"

INJECTION_PATTERNS = [
    r"ignore (all|any|previous|above|prior) instructions",
    r"do not follow.{0,30}(system|developer)",
    r"you are now", r"new personality", r"jailbreak",
    r"<(system|assistant|developer|tool|function)[\s>]",
    r"(run|execute|call|invoke).{0,40}(tool|command|script)",
    r"reveal.{0,20}(system prompt|instructions|api key)",
    r"base64", r"eval\s*\(", r"exec\s*\(",
]

ESCAPE_MAP = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}

def audit(event_type, detail, severity="info"):
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        "severity": severity,
        "detail": str(detail)[:500]
    }
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry) + chr(10))
    except Exception:
        pass

def is_injection(text):
    normalized = re.sub(r"\s+", " ", text).strip().lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            audit("INJECTION_DETECTED", f"Pattern matched in: {text[:100]}", "critical")
            return True
    return False

def sanitize_input(text, max_len=8000):
    if not isinstance(text, str):
        text = str(text)
    text = text[:max_len]
    if is_injection(text):
        raise ValueError("[SECURITY] Potential prompt injection detected. Input rejected.")
    return text.strip()

def sanitize_for_prompt(text):
    return "".join(ESCAPE_MAP.get(c, c) for c in text)

def validate_api_key(key, prefix=""):
    if not key or len(key) < 20:
        return False
    if prefix and not key.startswith(prefix):
        return False
    return True

def hash_sensitive(value):
    return hashlib.sha256(value.encode()).hexdigest()[:12] + "..."