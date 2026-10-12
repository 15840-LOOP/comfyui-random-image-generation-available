@echo off
chcp 65001 >nul
title Anima 随机生图 WebUI
cd /d "%~dp0"

:: 自动探测 Python 路径（按常见整合包命名优先级检查）
set "PY="
for %%D in (python_embeded python python311 py311 python310 py310) do (
    if not defined PY (
        if exist "..\\%%D\python.exe" set "PY=..\\%%D\python.exe"
    )
)

if not defined PY (
    echo [错误] 未在上一层目录找到 Python 环境！
    echo 请确认本项目文件夹是否放在 ComfyUI 便携包根目录下（与 python 或 python_embeded 同级）。
    pause
    exit /b
)

:: 检查并自动安装 aiohttp（使用清华镜像源加速）
"%PY%" -c "import aiohttp" >nul 2>nul
if %errorlevel% neq 0 (
    echo 首次启动，正在安装依赖 aiohttp，请稍候...
    "%PY%" -m pip install aiohttp -i https://pypi.tuna.tsinghua.edu.cn/simple
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查网络连接后重试。
        pause
        exit /b
    )
)

echo 正在启动 WebUI，请确保后台 ComfyUI 已在运行...
echo 启动成功后，请在浏览器访问: http://127.0.0.1:8190
echo.

"%PY%" run.py
pause
