@echo off
REM Wrapper to run Engram Python analysis from OpenClaw

cd C:\Users\OFFRSTAR0\Engram

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Run the analysis with all arguments passed through
python engram.py analyze %*
