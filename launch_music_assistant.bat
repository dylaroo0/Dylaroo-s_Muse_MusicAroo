@echo off
:: ========================
:: AI Music Assistant Launcher
:: ========================

:: 1. Activate the right Conda environment
CALL conda activate ai_music_env
IF ERRORLEVEL 1 (
    echo [ERROR] Failed to activate Conda environment 'ai_music_env'. Please check your Anaconda installation.
    pause
    exit /b
)

:: 2. Confirm you are at the correct project folder
cd /d C:\Users\12502\Documents\AI_music_assistant
IF NOT EXIST src\main.py (
    echo [ERROR] main.py not found. Please check you are in the right folder.
    pause
    exit /b
)

:: 3. Check if torch and torchaudio are installed
python -c "import torch, torchaudio" 2>NUL
IF ERRORLEVEL 1 (
    echo [INFO] Missing torch or torchaudio. Attempting to install now...
    pip install --extra-index-url https://download.pytorch.org/whl/cu121 torch==2.1.0+cu121 torchaudio==2.1.0+cu121
)

:: 4. Confirm input/output directories
set /p AUDIO_DIR=Enter AUDIO folder (default: input_files\audio): 
if "%AUDIO_DIR%"=="" set AUDIO_DIR=input_files\audio

set /p MIDI_DIR=Enter MIDI folder (default: input_files\midi): 
if "%MIDI_DIR%"=="" set MIDI_DIR=input_files\midi

set /p MUSICXML_DIR=Enter MusicXML folder (default: input_files\musicxml): 
if "%MUSICXML_DIR%"=="" set MUSICXML_DIR=input_files\musicxml

set /p OUT_DIR=Enter OUTPUT folder (default: reports): 
if "%OUT_DIR%"=="" set OUT_DIR=reports

:: 5. Validate folders
IF NOT EXIST "%AUDIO_DIR%" (
    echo [ERROR] Audio folder "%AUDIO_DIR%" not found.
    pause
    exit /b
)
IF NOT EXIST "%MIDI_DIR%" (
    echo [ERROR] MIDI folder "%MIDI_DIR%" not found.
    pause
    exit /b
)
IF NOT EXIST "%MUSICXML_DIR%" (
    echo [ERROR] MusicXML folder "%MUSICXML_DIR%" not found.
    pause
    exit /b
)

:: 6. Launch the main pipeline
echo Running AI Music Assistant...
python src\main.py --audio_dir "%AUDIO_DIR%" --midi_dir "%MIDI_DIR%" --musicxml_dir "%MUSICXML_DIR%" --out_dir "%OUT_DIR%"

:: 7. Done
echo.
echo [SUCCESS] Pipeline complete. Master report should be in %OUT_DIR%.
pause
exit /b
