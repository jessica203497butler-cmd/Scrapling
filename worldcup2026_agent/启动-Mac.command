#!/bin/bash
# Mac 用户：在「访达」里双击本文件即可打开。
# 若提示"无法打开因为来自身份不明的开发者"，请右键点本文件 → 打开 → 再点打开。
cd "$(dirname "$0")" || exit 1

if command -v python3 >/dev/null 2>&1; then
  python3 菜单.py
elif command -v python >/dev/null 2>&1; then
  python 菜单.py
else
  echo "没有检测到 Python，请先安装：在终端运行  brew install python  或到 https://www.python.org 下载。"
  read -r -p "按回车键关闭……" _
fi
