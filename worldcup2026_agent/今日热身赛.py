# -*- coding: utf-8 -*-
"""临时分析今日国际热身赛（友谊赛）。
注意：秘鲁/中国/泰国/匈牙利/哈萨克斯坦/冰岛不在世界杯48队名单中，
这里按其 FIFA 排名量级补一个近似评分，套用同一 Elo+泊松模型预测，仅供参考。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from worldcup2026 import WorldCupAgent
from worldcup2026.data import Team

agent = WorldCupAgent()
kb = agent.kb

# 按 FIFA 排名量级补充的近似评分（越高越强；西/阿用工具内置值）
extra = {
    "Peru":       Team("Peru", "秘鲁", "CONMEBOL", 1500, None),
    "China":      Team("China", "中国", "AFC", 1300, None),
    "Thailand":   Team("Thailand", "泰国", "AFC", 1230, None),
    "Hungary":    Team("Hungary", "匈牙利", "UEFA", 1500, None),
    "Kazakhstan": Team("Kazakhstan", "哈萨克斯坦", "UEFA", 1255, None),
    "Iceland":    Team("Iceland", "冰岛", "UEFA", 1378, None),
}
kb.teams.update(extra)

# (主队, 客队, 主队是否有主场优势, 备注)
fixtures = [
    ("Spain", "Peru", False, "中立(友谊赛)"),      # 秘鲁 vs 西班牙，按中立
    ("China", "Thailand", True, "中国主场"),         # 中国 vs 泰国
    ("Hungary", "Kazakhstan", True, "匈牙利主场"),   # 匈牙利 vs 哈萨克
    ("Argentina", "Iceland", False, "中立(友谊赛)"), # 阿根廷 vs 冰岛
]

for home, away, hf, note in fixtures:
    p = agent.predict_match(home, away, neutral=(not hf))
    h, a = kb.team(home), kb.team(away)
    print(f"【{a.name_zh} 客  vs  {h.name_zh} 主】 ({note})  评分 {h.name_zh}{h.rating:.0f} - {a.name_zh}{a.rating:.0f}")
    print(f"   预测比分: {p.top_scorelines[0][0]}（最可能）；其他可能: " +
          "，".join(f"{s}({pr:.0%})" for s, pr in p.top_scorelines))
    print(f"   胜平负: {h.name_zh}赢 {p.p_home:.0%} | 平 {p.p_draw:.0%} | {a.name_zh}赢 {p.p_away:.0%}")
    print(f"   预期进球(xG): {h.name_zh} {p.xg_home:.2f} - {a.name_zh} {p.xg_away:.2f}")
    print()
