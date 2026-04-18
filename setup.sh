#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# ResolvaBot LLM — Setup Script (Linux / macOS)
# Usage:  bash setup.sh
# ─────────────────────────────────────────────────────────────────────────────
set -e

echo "========================================"
echo "  ResolvaBot LLM — Setup"
echo "========================================"

# 1. Check Python version
PYTHON=$(python3 --version 2>&1)
echo "Found: $PYTHON"
PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$PY_MINOR" -lt 10 ]; then
    echo "❌ Python 3.10+ is required. Please upgrade."
    exit 1
fi

# 2. Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Virtual environment activated."

# 3. Upgrade pip
pip install --upgrade pip --quiet

# 4. Install dependencies
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt

# 5. Download NLTK data
python3 -c "
import nltk
for pkg in ['punkt', 'punkt_tab', 'wordnet', 'omw-1.4']:
    nltk.download(pkg, quiet=True)
print('NLTK data downloaded.')
"

# 6. Set up .env file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  .env file created from .env.example"
    echo "   → Open .env and add your OpenAI API key before running the app."
else
    echo ".env file already exists."
fi

echo ""
echo "========================================"
echo "  ✅ Setup complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add: OPENAI_API_KEY=sk-..."
echo "  2. Run the app:  source venv/bin/activate && streamlit run app.py"
echo ""
