@echo off
echo Construindo executavel...
pyinstaller --onefile --windowed ^
    --hidden-import pypdf ^
    --hidden-import unicodedata ^
    --hidden-import difflib ^
    --add-data "*.log;." ^
    --name "MescladorPDF" ^
    --icon=icone.ico ^
    mesclador.py
echo Pronto! Executavel esta em dist/MescladorPDF.exe
pause