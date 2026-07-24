@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
    echo A criar ambiente virtual...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)
python -m src.webapp
pause
