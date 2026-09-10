@echo off
cd /d E:\workspace\password_generator
python -m PyInstaller --noconfirm --onefile --windowed --name PasswordGenerator --icon app.ico --add-data "app.ico;." password_generator.py
echo BUILD_EXIT=%ERRORLEVEL%
