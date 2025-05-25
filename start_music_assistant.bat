@echo off
echo Launching AI Music Assistant Environment...

REM Activate Conda environment
call C:\Users\12502\miniconda3\Scripts\activate.bat ai_music_env

REM Change directory to project folder
cd /d C:\Users\12502\Documents\AI_music_assistant

REM Start Python
python

exit
