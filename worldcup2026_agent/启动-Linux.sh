#!/bin/bash
# Linux 用户：双击运行（文件管理器里可能需选"运行"），或在终端执行  ./启动-Linux.sh
cd "$(dirname "$0")" || exit 1

if command -v python3 >/dev/null 2>&1; then
  python3 菜单.py
elif command -v python >/dev/null 2>&1; then
  python 菜单.py
else
  echo "没有检测到 Python，请先安装：sudo apt install python3 （或对应发行版命令）。"
  read -r -p "按回车键关闭……" _
fi
