import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# API Keys - NEVER hardcode these. Set as environment variables.
# To set: export OPENAI_API_KEY=sk-...  or  export ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY    = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GITHUB_TOKEN      = os.environ.get("GITHUB_TOKEN", "")

# Paths
THREADS_DB     = BASE_DIR / "threads" / "threads.db"
LOGS_DIR       = BASE_DIR / "logs"
HEARTBEAT_FILE = BASE_DIR / "heartbeat" / "heartbeat.json"
VECTOR_DB_DIR  = BASE_DIR / "memory" / "vectordb"

# Token budgets
MAX_TOKENS_CONTEXT    = 6000
MAX_TOKENS_PER_THREAD = 4000
MAX_TOKENS_SUMMARY    = 800

# Security
MAX_INPUT_LENGTH = 8000
RATE_LIMIT_PER_MIN = 30

# Models (change these to switch providers)
DEFAULT_MODEL    = "gpt-4o-mini"
EMBEDDING_MODEL  = "text-embedding-3-small"
SUMMARY_MODEL    = "gpt-4o-mini"

# Heartbeat
HEARTBEAT_INTERVAL = 30
HEARTBEAT_STALE_AFTER = 120