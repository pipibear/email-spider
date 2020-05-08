#/bin/bash

#pyinstaller --windowed --onefile --clean --noconfirm main.py
#pyinstaller --clean --noconfirm --windowed --onefile main.spec
pyinstaller -F -w -i logo.icns  main.py
