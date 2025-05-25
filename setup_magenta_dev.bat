@echo off
echo [1/4] Activating virtual environment...
call venv\Scripts\activate

echo [2/4] Installing compatible dependencies...
pip install numpy==1.23.5
pip install setuptools==65.5.0

echo [3/4] Installing Magenta in editable mode...
pip install -e ./magenta

echo [4/4] Done! Magenta is now linked and editable.
pause
