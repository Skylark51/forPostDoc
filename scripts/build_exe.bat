@echo off
setlocal
python -m pip install -e .[google]
python -m PyInstaller --noconfirm --clean --windowed --name CCRA --paths src src\ccra\main.py
echo Built: dist\CCRA\CCRA.exe
