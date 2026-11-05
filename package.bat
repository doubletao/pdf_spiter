@echo off
setlocal
cd /d "%~dp0"

set APP_NAME=PDF试卷拆分工具

echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python，请先安装并加入 PATH
    pause
    exit /b 1
)

echo [2/4] 安装依赖...
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo 错误：依赖安装失败
    pause
    exit /b 1
)

echo [3/4] 清理旧构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "%APP_NAME%.spec" del /q "%APP_NAME%.spec"

echo [4/4] PyInstaller 打包中（onefile，无控制台窗口）...
python -m PyInstaller --noconfirm --onefile --noconsole --name "%APP_NAME%" --collect-all pymupdf --collect-all PIL main.py
if errorlevel 1 (
    echo 错误：打包失败，请检查上方日志
    pause
    exit /b 1
)

echo.
echo 打包完成：dist\%APP_NAME%.exe
pause