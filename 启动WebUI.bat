@echo off
chcp 65001 >nul
title Anima 随机生图 WebUI
cd /d "%~dp0"

set "PY=..\python_embeded\python.exe"

:: 检查是否已安装 aiohttp，未安装则自动执行 pip 安装
"%PY%" -c "import aiohttp" >nul 2>nul
if %errorlevel% neq 0 (
    echo 首次启动，正在安装依赖 aiohttp，请稍候...
    "%PY%" -m pip install aiohttp
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查网络后重试。
        pause
        exit /b
    )
)

echo 正在启动 WebUI，请确保后台 ComfyUI 已在运行...
echo 启动成功后，请在浏览器访问: http://127.0.0.1:8190
echo.

"%PY%" run.py
pause