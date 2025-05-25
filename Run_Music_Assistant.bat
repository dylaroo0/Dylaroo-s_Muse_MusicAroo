@echo off
echo Running AI Music Assistant full pipeline...

REM Activate Conda environment
call C:\Users\12502\miniconda3\Scripts\activate.bat ai_music_env

REM Change to project folder
cd /d C:\Users\12502\Documents\AI_music_assistant

REM Run main.py with your input/output folders
python src\main.py --audio_dir input_files\audio --midi_dir input_files\midi --musicxml_dir input_files\musicxml --out_dir reports

pause
exit
