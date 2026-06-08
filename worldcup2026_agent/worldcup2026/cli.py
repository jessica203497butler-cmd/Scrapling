"""命令行界面：``python -m worldcup2026 <command>``。

子命令：
    info                赛事信息总览
    teams               按评分列出全部 48 队
    group <A-L>         查看某小组并模拟出线概率
    match <主队> <客队>   单场比赛预测
    simulate            模拟全部小组的出线概率
    odds                各队四强 / 夺冠概率
"""

from __future__ import annotations

import argparse
import sys

from .agent import WorldCupAgent


def _cmd_info(agent: WorldCupAgent, args) -> None:
    t = agent.info()
    print(f"🏆 {t['name_zh']}")
    print(f"   {t['name']}")
    print(f"   主办：{'、'.join(t['hosts_zh'].values())}")
    print(f"   赛期：{t['dates']}  |  {t['teams']} 队 / {t['groups']} 组 / {t['matches']} 场")
    print(f"   赛制：{t['format']}")
    print(f"   揭幕战：{t['opening_match']}")
    print(f"   决赛：{t['final']}")
    print(f"   抽签：{t['draw']}")
    print(f"\n   主办球场（{len(agent.kb.venues)} 座）：")
    for v in agent.kb.venues:
        print(f"     - {v['city_zh']}（{v['city']}）：{v['stadium']}")


def _cmd_teams(agent: WorldCupAgent, args) -> None:
    print(f"{'排名':>4} {'评分':>6}  {'组':<3}{'球队'}")
    for i, t in enumerate(agent.list_teams(), 1):
        print(f"{i:>4} {t['rating']:>6.0f}  {t['group'] or '-':<3}{t['name_zh']}（{t['name']}）")


def _cmd_group(agent: WorldCupAgent, args) -> None:
    g = args.letter.upper()
    info = agent.group(g)
    print(f"小组 {g}：")
    for tm in info["teams"]:
        print(f"  {tm['name_zh']}（{tm['name']}）  评分 {tm['rating']:.0f}")
    print(f"\n模拟出线概率（{args.iterations} 次）：")
    outcomes = agent.simulate_tournament(iterations=args.iterations, seed=args.seed)
    print(outcomes[g].table_zh(agent.kb))


def _cmd_match(agent: WorldCupAgent, args) -> None:
    neutral = None
    if args.neutral:
        neutral = True
    pred = agent.predict_match(args.home, args.away, neutral=neutral)
    print(pred.summary_zh(agent.kb))


def _cmd_simulate(agent: WorldCupAgent, args) -> None:
    print(f"全小组蒙特卡洛模拟（{args.iterations} 次）……\n")
    outcomes = agent.simulate_tournament(iterations=args.iterations, seed=args.seed)
    for g in sorted(outcomes):
        print(outcomes[g].table_zh(agent.kb))
        print()


def _cmd_odds(agent: WorldCupAgent, args) -> None:
    print(f"夺冠 / 四强概率（{args.iterations} 次模拟）……\n")
    odds = agent.championship_odds(iterations=args.iterations, seed=args.seed)
    print(f"{'排名':>4}  {'球队':<22}{'进四强':>8}{'夺冠':>8}")
    for i, (team, sf, win) in enumerate(odds[: args.top], 1):
        tm = agent.kb.team(team)
        label = f"{tm.name_zh}（{tm.name}）"
        print(f"{i:>4}  {label:<22}{sf:>8.1%}{win:>8.1%}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="worldcup2026",
        description="2026 美加墨世界杯比赛分析工具智能体",
    )
    p.add_argument("--refresh", action="store_true", help="先用 Scrapling 抓取最新 FIFA 排名")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("info", help="赛事信息总览").set_defaults(func=_cmd_info)
    sub.add_parser("teams", help="按评分列出全部球队").set_defaults(func=_cmd_teams)

    g = sub.add_parser("group", help="查看小组并模拟出线概率")
    g.add_argument("letter", help="小组字母 A-L")
    g.add_argument("--iterations", type=int, default=5000)
    g.add_argument("--seed", type=int, default=None)
    g.set_defaults(func=_cmd_group)

    m = sub.add_parser("match", help="单场比赛预测")
    m.add_argument("home", help="主队（英文或中文名）")
    m.add_argument("away", help="客队（英文或中文名）")
    m.add_argument("--neutral", action="store_true", help="按中立场地预测（默认主办国享主场）")
    m.set_defaults(func=_cmd_match)

    s = sub.add_parser("simulate", help="模拟全部小组出线概率")
    s.add_argument("--iterations", type=int, default=5000)
    s.add_argument("--seed", type=int, default=None)
    s.set_defaults(func=_cmd_simulate)

    o = sub.add_parser("odds", help="各队四强 / 夺冠概率")
    o.add_argument("--iterations", type=int, default=3000)
    o.add_argument("--top", type=int, default=16, help="显示前 N 名")
    o.add_argument("--seed", type=int, default=None)
    o.set_defaults(func=_cmd_odds)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    agent = WorldCupAgent()
    if getattr(args, "refresh", False):
        n = agent.refresh_ratings()
        print(f"🔄 已用 Scrapling 刷新 {n} 支球队评分。\n" if n else "🔄 未能抓取实时排名，使用内置评分。\n")
    args.func(agent, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
