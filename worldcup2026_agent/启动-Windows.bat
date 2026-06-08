@echo off
chcp 65001 >nul
title 2026 世界杯比赛分析工具
cd /d "%~dp0"

REM 优先用 py 启动器（只有真正装了 Python 才有），再退回 python / python3。
set "PYEXE="
where py        >nul 2>nul && set "PYEXE=py"
if not defined PYEXE  where python  >nul 2>nul && set "PYEXE=python"
if not defined PYEXE  where python3 >nul 2>nul && set "PYEXE=python3"

if not defined PYEXE (
  echo.
  echo ============================================================
  echo  没有检测到 Python，无法运行。
  echo  请到 https://www.python.org/downloads/ 下载安装，
  echo  安装第一屏底部务必勾选 "Add python.exe to PATH"，
  echo  装好后重新双击本文件即可。
  echo ============================================================
  echo.
  pause
  exit /b
)

echo 正在用 %PYEXE% 启动……
echo.
"%PYEXE%" "%~dp0菜单.py"

REM 无论成功或出错，都停在这里，方便看到信息（不会再一闪而过）。
echo.
echo ============================================================
echo  程序已结束。如上方有红色错误，请截图发给我。
echo ============================================================
pause
