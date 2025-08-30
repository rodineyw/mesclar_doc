import ttkbootstrap
import os
# Isso vai imprimir o caminho que precisamos
print(os.path.dirname(ttkbootstrap.__file__))

pyinstaller --onefile --noconsole --hidden-import=pypdf --name "Mesclador de PDFs por Similaridade" app.py