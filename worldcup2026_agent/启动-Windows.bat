@echo off
chcp 65001 >nul
title 2026 世界杯比赛分析工具
cd /d "%~dp0"

REM 依次尝试 python / py / python3 三种常见命令
python "%~dp0菜单.py" 2>nul
if %errorlevel%==0 goto end
py "%~dp0菜单.py" 2>nul
if %errorlevel%==0 goto end
python3 "%~dp0菜单.py" 2>nul
if %errorlevel%==0 goto end

echo.
echo 没有检测到 Python，请先到 https://www.python.org 下载安装，
echo 安装时记得勾选 "Add Python to PATH"，装好后再双击本文件。
pause

:end
