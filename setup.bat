@echo off
:: ─────────────────────────────────────────────────────────────────────────────
:: ResolvaBot LLM — Setup Script (Windows)
:: Usage: Double-click setup.bat  OR  run in Command Prompt
:: ─────────────────────────────────────────────────────────────────────────────

echo ========================================
echo   ResolvaBot LLM -- Setup (Windows)
echo ========================================

:: 1. Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
echo Virtual environment activated.

:: 2. Upgrade pip
python -m pip install --upgrade pip --quiet

:: 3. Install dependencies
echo Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt

:: 4. Download NLTK data
python -c "import nltk; [nltk.download(p, quiet=True) for p in ['punkt','punkt_tab','wordnet','omw-1.4']]; print('NLTK data ready.')"

:: 5. Create .env if missing
if not exist ".env" (
    copy .env.example .env
    echo.
    echo WARNING: .env created from .env.example
    echo          Open .env and add your OPENAI_API_KEY before running.
) else (
    echo .env already exists.
)

echo.
echo ========================================
echo   Setup complete!
echo ========================================
echo.
echo Next steps:
echo   1. Open .env and set OPENAI_API_KEY=sk-...
echo   2. Run: venv\Scripts\activate.bat ^&^& streamlit run app.py
echo.
pause
