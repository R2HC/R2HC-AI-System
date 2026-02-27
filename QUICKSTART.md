# 🚀 R2HC AI System — Quick Start Guide

## How to run this on YOUR computer (Windows, Mac, or Linux)

---

## Step 1 — Install Python
- Go to **python.org/downloads**
- Download Python 3.11 or newer
- Install it (check "Add to PATH" on Windows)

---

## Step 2 — Download the code from GitHub
Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:

```bash
git clone https://github.com/R2HC/R2HC-AI-System.git
cd R2HC-AI-System
```

---

## Step 3 — Run the setup script

**On Mac/Linux:**
```bash
bash setup.sh
```

**On Windows:**
```bash
pip install -r requirements.txt
```

---

## Step 4 — Add your API key
Open the `.env` file in any text editor and replace:
```
OPENAI_API_KEY=your-openai-key-here
```
with your actual OpenAI key from **platform.openai.com/api-keys**

---

## Step 5 — Start the system
```bash
python3 main.py
```

That's it! The system will:
- ✅ Start the heartbeat monitor
- ✅ Initialize the memory database
- ✅ Load all agents
- ✅ Wait for your commands

---

## 💡 What each part does

| Component | What It Does |
|-----------|-------------|
| **Heartbeat** | Checks system health every 30 seconds, writes status to `heartbeat/heartbeat.json` |
| **Memory** | Saves every conversation to a local database — nothing is ever lost |
| **Context Manager** | Keeps token usage under 6,000 — saves you money |
| **Security Agent** | Blocks suspicious inputs, rate limits, audit logs |
| **Orchestrator** | Receives your task, picks the right agent, returns result |
| **Researcher Agent** | Searches and summarizes information |
| **Coder Agent** | Writes and reviews code |
| **Memory Agent** | Recalls past conversations and facts |

---

## 🔐 Security Notes
- Your `.env` file is **never uploaded to GitHub**
- Never share your API keys with anyone
- The security agent scans all inputs for injection attacks

---

## ❓ Need Help?
Open an issue at: `github.com/R2HC/R2HC-AI-System/issues`
