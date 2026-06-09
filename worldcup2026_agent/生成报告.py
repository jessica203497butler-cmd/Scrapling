# -*- coding: utf-8 -*-
"""生成 2026 世界杯完整预测报告（Markdown）。"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from worldcup2026 import WorldCupAgent

agent = WorldCupAgent()
kb = agent.kb
SEED = 2026

def zh(name): return kb.team(name).name_zh

def order_match(a, b):
    """主办国放主场（享主场优势）；否则按评分高者在前。"""
    a_host = a in kb.host_nations
    b_host = b in kb.host_nations
    if a_host and not b_host: return a, b
    if b_host and not a_host: return b, a
    # 都不是或都是主办国：评分高者在前，按中立处理
    return (a, b) if kb.team(a).rating >= kb.team(b).rating else (b, a)

lines = []
def w(s=""): lines.append(s)

w("# ⚽ 2026 美加墨世界杯 · 全量预测报告")
w()
w("> 模型：FIFA Elo 期望胜率 + 泊松进球分布。主办国（美/加/墨）在本国比赛享主场优势。")
w("> 所有比分/概率均为模型近似，仅供分析娱乐，**不构成投注建议**。")
w()

# ---------- 一、各组逐场比分预测 ----------
w("## 一、小组赛逐场比分预测（全 72 场）")
w()
for g in sorted(kb.groups):
    members = kb.groups[g]
    w(f"### 🅰️ 小组 {g}　" + " / ".join(zh(m) for m in members))
    w()
    w("| 对阵 | 预测比分 | 胜 / 平 / 负 | 预期进球(xG) |")
    w("|---|---|---|---|")
    for a, b in itertools.combinations(members, 2):
        h, aw = order_match(a, b)
        p = agent.predict_match(h, aw)
        score = p.top_scorelines[0][0]
        host_tag = "（主）" if p.home_field else ""
        w(f"| {zh(h)}{host_tag} vs {zh(aw)} | **{score}** | "
          f"{p.p_home:.0%} / {p.p_draw:.0%} / {p.p_away:.0%} | {p.xg_home:.2f}–{p.xg_away:.2f} |")
    w()

# ---------- 二、各组出线概率 ----------
w("## 二、各组出线概率（蒙特卡洛模拟 8000 次）")
w()
outcomes = agent.simulate_tournament(iterations=8000, seed=SEED)
for g in sorted(outcomes):
    o = outcomes[g]
    rows = sorted(o.teams, key=lambda t: o.advance[t], reverse=True)
    w(f"**小组 {g}**")
    w()
    w("| 球队 | 晋级32强 | 头名 | 第2 | 第3 | 第4 |")
    w("|---|---|---|---|---|---|")
    for t in rows:
        f = o.finish[t]
        w(f"| {zh(t)} | {o.advance[t]:.0%} | {f[0]:.0%} | {f[1]:.0%} | {f[2]:.0%} | {f[3]:.0%} |")
    w()

# ---------- 三、夺冠概率 ----------
w("## 三、夺冠 / 四强概率排行（模拟 8000 次）")
w()
odds = agent.championship_odds(iterations=8000, seed=SEED)
w("| 排名 | 球队 | 进四强 | 夺冠 |")
w("|---|---|---|---|")
for i,(t,sf,win) in enumerate(odds[:20],1):
    w(f"| {i} | {zh(t)} | {sf:.1%} | {win:.1%} |")
w()

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "预测报告.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("OK 已生成 预测报告.md，共", len(lines), "行")
print("\n".join(lines[:0]))  # 占位
