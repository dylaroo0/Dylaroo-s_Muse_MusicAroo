@echo off
rem === make_clean_archive.bat =========================================
rem Creates a lightweight 7-Zip archive that keeps code/docs,
rem skips big binaries (audio, video, models, pictures, etc.)

rem --- CONFIG ---
set "ZIP=C:\Program Files\7-Zip\7z.exe"   rem adjust if 7-Zip lives elsewhere
set "SRC=AI_music_assistant"              rem root folder to archive
set "OUT=AI_music_assistant_clean.7z"     rem output file name
set "FLAGS=-t7z -mx9 -r"                  rem 7-Zip: format 7z, max compression, recurse

rem --- RUN ---
echo.
echo =============================================================
echo  Creating %OUT%  ... please wait
echo =============================================================
echo.

"%ZIP%" a %FLAGS% "%OUT%" ^
 -i!%SRC%\*.py   -i!%SRC%\*.txt  -i!%SRC%\*.md   -i!%SRC%\*.json ^
 -i!%SRC%\*.csv  -i!%SRC%\*.xml -i!%SRC%\*.yml  -i!%SRC%\*.yaml ^
 -i!%SRC%\*.cfg  -i!%SRC%\*.ini -i!%SRC%\*.ipynb

if errorlevel 1 (
    echo.
    echo *** 7-Zip reported an error. Check the path to 7z.exe or file names.
    pause
    goto :eof
)

echo.
echo =============================================================
echo  DONE.  Archive size:
for %%A in ("%OUT%") do echo   %%~nA%%~xA  —  %%~zA bytes
echo  Archive saved in: %~dp0
echo =============================================================
echo.
pause
