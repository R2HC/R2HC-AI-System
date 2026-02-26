# R2HC AI System — Ant Farm Architecture

**Security | Persistent Memory | Token Efficiency | Multi-Agent**

## Architecture Overview

```
                    USER INPUT
                        |
                   [SANITIZER] <-- blocks injections, enforces limits
                        |
              [ORCHESTRATOR / QUEEN]
              /     |       |      \
        [RESEARCHER] [CODER] [MEMORY] [SECURITY]
              \     |       |      /
                [THREAD STORE / DB]
                        |
                 [HEARTBEAT FILE]
```

## Core Modules

| Module | File | Purpose |
|--------|------|---------|
| Orchestrator (Queen) | `core/orchestrator.py` | Routes tasks to agents |
| Context Manager | `core/context_manager.py` | Token budgeting, context trimming |
| Config | `core/config.py` | All settings, env vars, paths |
| Heartbeat | `heartbeat/monitor.py` | Live status JSON, uptime, alerts |
| Thread Store | `memory/thread_store.py` | SQLite: all conversations persist |
| Memory Agent | `agents/memory_agent.py` | Recall facts, browse thread history |
| Researcher | `agents/researcher.py` | Web search, URL reading |
| Coder | `agents/coder.py` | Code generation, review, debugging |
| Security Agent | `agents/security_agent.py` | Rate limiting, audit logs, threat scan |
| Sanitizer | `security/sanitizer.py` | Injection detection, input cleaning |
| Base Agent | `agents/base_agent.py` | Abstract base all agents extend |

## Security Features
- Prompt injection detection (regex patterns)
- Input length limits (8000 chars max)
- Rate limiting (30 req/min per user)
- Full audit log at `logs/security.log`
- API keys via environment variables ONLY — never hardcoded
- Heartbeat checksum to detect file tampering

## Memory & Token Efficiency
- All conversations stored in SQLite (`threads/threads.db`)
- Threads auto-summarized when token count exceeds 4000
- Context window budget: 6000 tokens total (not 128k!)
- Smart trim: keeps most recent messages, uses summaries for older
- Nothing is lost — full history always retrievable from DB

## Heartbeat File
Located at `heartbeat/heartbeat.json` — updated every 30 seconds:
- System status (healthy/degraded/critical)
- Active agents list
- Token usage today
- Alerts queue
- SHA256 checksum for integrity

## Quick Start
```bash
# 1. Set your API key (optional — system runs without it in queued mode)
export OPENAI_API_KEY=sk-...

# 2. Run
python3 main.py

# 3. Check heartbeat anytime
cat heartbeat/heartbeat.json
```

## File Structure
```
R2HC_AI_System/
├── main.py                    # Entry point
├── README.md
├── core/
│   ├── orchestrator.py        # Queen agent — routes all tasks
│   ├── context_manager.py     # Token budgeting
│   └── config.py              # Settings & env vars
├── agents/
│   ├── base_agent.py          # Abstract base class
│   ├── researcher.py          # Web research agent
│   ├── coder.py               # Code generation agent
│   ├── memory_agent.py        # Memory recall agent
│   └── security_agent.py     # Security & audit agent
├── heartbeat/
│   ├── monitor.py             # HeartbeatMonitor class
│   └── heartbeat.json         # Live status file (auto-generated)
├── memory/
│   ├── thread_store.py        # SQLite thread management
│   └── facts.json             # Key-value long-term memory
├── security/
│   └── sanitizer.py           # Injection detection & audit
├── threads/
│   └── threads.db             # SQLite database (auto-created)
└── logs/
    └── security.log           # Audit trail (auto-created)
```

## Roadmap
- [ ] Connect OpenAI/Anthropic API for live responses
- [ ] Vector DB (ChromaDB) for semantic memory search
- [ ] Web UI dashboard for heartbeat monitoring
- [ ] Telegram/Discord channel integration via OpenClaw fork
- [ ] Agent-to-agent communication protocol
