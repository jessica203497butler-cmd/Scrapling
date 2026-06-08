#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""世界杯 2026 分析工具 —— 小白中文菜单。

不用记命令，运行后照着数字选即可。
可双击同目录下的「启动」文件打开，也可直接：python 菜单.py
"""

from __future__ import annotations

import os
import sys

# 让脚本无论从哪里运行，都能找到 worldcup2026 这个包
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from worldcup2026.cli import main as run  # noqa: E402


def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


def pause() -> None:
    ask("\n（看完后按回车键返回菜单）")


MENU = """
==================================================
   ⚽  2026 美加墨世界杯 · 比赛分析工具  ⚽
==================================================
  请输入数字后按回车：

  1  赛事总览（赛期、赛制、16 座球场）
  2  全部 48 支球队实力排名
  3  预测两队对决谁赢
  4  查看某个小组 + 出线概率（A~L）
  5  模拟全部小组出线概率
  6  各队夺冠 / 进四强概率

  0  退出
==================================================
"""


def main() -> None:
    while True:
        print(MENU)
        choice = ask("你的选择：")

        if choice == "0" or choice.lower() in ("q", "exit", "quit"):
            print("\n再见！👋")
            return

        try:
            if choice == "1":
                run(["info"])
            elif choice == "2":
                run(["teams"])
            elif choice == "3":
                print("\n（队名中文或英文都行，例如：阿根廷  /  Argentina）")
                home = ask("主队：")
                away = ask("客队：")
                if home and away:
                    run(["match", home, away])
                else:
                    print("⚠️ 两队名字都要填哦。")
            elif choice == "4":
                letter = ask("请输入小组字母（A 到 L）：")
                if letter:
                    run(["group", letter])
                else:
                    print("⚠️ 要输入一个字母，例如 A。")
            elif choice == "5":
                run(["simulate"])
            elif choice == "6":
                run(["odds"])
            else:
                print("⚠️ 没有这个选项，请输入 0~6 之间的数字。")
        except SystemExit:
            # argparse 在输入有误时会调用 sys.exit，这里拦下来避免整个菜单退出
            pass
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️ 出错了：{exc}")

        pause()


if __name__ == "__main__":
    main()
