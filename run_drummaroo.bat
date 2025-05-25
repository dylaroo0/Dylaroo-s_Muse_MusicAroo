@echo off
REM ─── DrummAroo Quick Launcher ────────────────────────────────────────────────

REM 1) cd into this script’s folder
cd /d "%~dp0"

REM 2) Activate your conda env
call "%USERPROFILE%\miniconda3\Scripts\activate.bat" ai_music_env

REM 3) Check for an argument
if "%~1"=="" (
  echo Usage: run_drummaroo.bat ^<path-to-midi-or-wav^>
  goto :eof
)

REM 4) Full path to the input file
set "INPUT=%~1"
if not exist "%INPUT%" (
  echo ERROR: Input file not found: "%INPUT%"
  goto :eof
)

REM 5) Generate drums
echo.
echo Generating drums for "%INPUT%" …
python src\drummaroo_plugin.py --input "%INPUT%" --out_dir reports
echo.

REM 6) Start the API
echo Launching HTTP API at http://127.0.0.1:8000 …
uvicorn drummaroo_api:app --reload --port 8000

pause
