@echo off
rem PyInstaller 单文件打包脚本（在脚本所在目录执行，无需修改路径）
setlocal
cd /d "%~dp0"
python -m PyInstaller --noconfirm --onefile --windowed --name PasswordGenerator --icon app.ico --add-data "app.ico;." password_generator.py
echo BUILD_EXIT=%ERRORLEVEL%
endlocal
