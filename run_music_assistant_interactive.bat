@echo off
echo Welcome to the AI Music Assistant Interactive Runner!

REM Activate Conda environment
call C:\Users\12502\miniconda3\Scripts\activate.bat ai_music_env

REM Change to project folder
cd /d C:\Users\12502\Documents\AI_music_assistant

REM Ask for input directories
set /p AUDIO_DIR=Enter path to audio folder (default: input_files\audio): 
if "%AUDIO_DIR%"=="" set AUDIO_DIR=input_files\audio

set /p MIDI_DIR=Enter path to MIDI folder (default: input_files\midi): 
if "%MIDI_DIR%"=="" set MIDI_DIR=input_files\midi

set /p MUSICXML_DIR=Enter path to MusicXML folder (default: input_files\musicxml): 
if "%MUSICXML_DIR%"=="" set MUSICXML_DIR=input_files\musicxml

set /p OUT_DIR=Enter path to output reports folder (default: reports): 
if "%OUT_DIR%"=="" set OUT_DIR=reports

REM Run main.py with dynamic inputs
python src\main.py --audio_dir %AUDIO_DIR% --midi_dir %MIDI_DIR% --musicxml_dir %MUSICXML_DIR% --out_dir %OUT_DIR%

pause
exit
