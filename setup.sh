#!/bin/bash
# ============================================================
# R2HC AI System — One-Command Setup Script
# Run this on ANY machine (Linux/Mac) to get started
# ============================================================

echo "================================================"
echo "  R2HC AI System — Setup"
echo "================================================"

# 1. Check Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python3 not found. Installing..."
    sudo apt-get update && sudo apt-get install -y python3 python3-pip
else
    echo "✅ Python3 found: $(python3 --version)"
fi

# 2. Install dependencies
echo ""
echo "📦 Installing Python packages..."
pip3 install --quiet \
    openai \
    anthropic \
    chromadb \
    tiktoken \
    requests \
    python-dotenv \
    schedule \
    flask \
    rich

echo "✅ Packages installed"

# 3. Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "🔐 Creating .env file for your API keys..."
    cat > .env << 'ENVEOF'
# R2HC AI System — Environment Variables
# Fill in your keys below — NEVER commit this file to GitHub

OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GITHUB_TOKEN=your-github-token-here

# System settings
MAX_TOKENS=6000
HEARTBEAT_INTERVAL=30
LOG_LEVEL=INFO
ENVEOF
    echo "✅ .env file created — open it and add your API keys"
else
    echo "✅ .env file already exists"
fi

# 4. Create required directories
mkdir -p logs threads memory/vectordb heartbeat
echo "✅ Directories ready"

# 5. Run a quick health check
echo ""
echo "🔍 Running system health check..."
python3 -c "
import sys
modules = ['sqlite3', 'hashlib', 'json', 'threading', 'datetime']
for m in modules:
    try:
        __import__(m)
        print(f'  ✅ {m}')
    except:
        print(f'  ❌ {m} MISSING')
print('Health check complete.')
"

echo ""
echo "================================================"
echo "  ✅ Setup Complete!"
echo ""
echo "  Next steps:"
echo "  1. Edit .env and add your OpenAI API key"
echo "  2. Run: python3 main.py"
echo "  3. Watch the heartbeat: cat heartbeat/heartbeat.json"
echo "================================================"
