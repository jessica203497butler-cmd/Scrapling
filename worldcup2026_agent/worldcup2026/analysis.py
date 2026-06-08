"""比赛分析引擎：单场预测、小组蒙特卡洛模拟、夺冠概率。

模型基于 FIFA Elo 期望胜率 + 泊松进球分布：

1. 由两队评分差（含主场优势）经 Elo 公式得到 A 队期望胜率 ``We``。
2. 将 ``We`` 映射为净胜球期望（supremacy），结合总进球期望拆出双方
   进球率 ``lambda``。
3. 用独立泊松分布生成比分网格，聚合出胜/平/负概率与最可能比分。

模型为概率近似，用于分析与娱乐，不构成投注建议。
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .data import KnowledgeBase, Team

# --------------------------------------------------------------------------- #
# 模型常量
# --------------------------------------------------------------------------- #

ELO_DIVISOR = 600.0  # FIFA 排名使用的 Elo 分母
HOME_ADVANTAGE = 60.0  # 主办国在本国比赛的评分加成（约等于 +0.1 期望胜率）
TOTAL_GOALS = 2.65  # 一场比赛双方进球总数期望
SUPREMACY_SCALE = 2.6  # 期望胜率 -> 净胜球期望 的缩放
MAX_GOALS = 8  # 比分网格上限


@dataclass
class MatchPrediction:
    """单场比赛预测结果。"""

    home: str
    away: str
    p_home: float
    p_draw: float
    p_away: float
    xg_home: float
    xg_away: float
    top_scorelines: list[tuple[str, float]]
    home_field: bool

    def summary_zh(self, kb: KnowledgeBase) -> str:
        h, a = kb.team(self.home), kb.team(self.away)
        lines = [
            f"⚽ {h.name_zh} ({h.name}) vs {a.name_zh} ({a.name})",
            f"   评分：{h.rating:.0f} vs {a.rating:.0f}" + ("（含主场优势）" if self.home_field else ""),
            f"   胜平负：{h.name_zh} {self.p_home:.1%} | 平 {self.p_draw:.1%} | {a.name_zh} {self.p_away:.1%}",
            f"   预期进球(xG)：{self.xg_home:.2f} - {self.xg_away:.2f}",
            "   最可能比分：" + "，".join(f"{s} ({p:.1%})" for s, p in self.top_scorelines),
        ]
        return "\n".join(lines)


def _elo_expected(rating_a: float, rating_b: float) -> float:
    """A 队相对 B 队的 Elo 期望胜率（0~1）。"""
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / ELO_DIVISOR))


def _poisson_pmf(k: int, lam: float) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def predict_match(
    kb: KnowledgeBase,
    home: str,
    away: str,
    *,
    neutral: bool | None = None,
) -> MatchPrediction:
    """预测单场比赛。

    ``neutral=None`` 时自动判断：主办国会获得主场优势。显式传入可覆盖。
    """
    h = kb.team(home)
    a = kb.team(away)

    r_h, r_a = h.rating, a.rating
    if neutral is True:
        home_field = False
    elif neutral is False:
        home_field = True  # 显式指定主场
    else:
        home_field = h.name in kb.host_nations  # 自动：主办国享主场优势
    if home_field:
        r_h += HOME_ADVANTAGE

    we = _elo_expected(r_h, r_a)

    # 期望胜率 -> 净胜球期望 -> 双方进球率
    supremacy = (we - 0.5) * 2 * SUPREMACY_SCALE
    lam_h = max(0.15, TOTAL_GOALS / 2 + supremacy / 2)
    lam_a = max(0.15, TOTAL_GOALS / 2 - supremacy / 2)

    # 比分网格
    p_home = p_draw = p_away = 0.0
    scorelines: list[tuple[str, float]] = []
    for gh in range(MAX_GOALS + 1):
        for ga in range(MAX_GOALS + 1):
            p = _poisson_pmf(gh, lam_h) * _poisson_pmf(ga, lam_a)
            scorelines.append((f"{gh}-{ga}", p))
            if gh > ga:
                p_home += p
            elif gh == ga:
                p_draw += p
            else:
                p_away += p

    total = p_home + p_draw + p_away
    p_home, p_draw, p_away = p_home / total, p_draw / total, p_away / total
    scorelines.sort(key=lambda x: x[1], reverse=True)

    return MatchPrediction(
        home=h.name,
        away=a.name,
        p_home=p_home,
        p_draw=p_draw,
        p_away=p_away,
        xg_home=lam_h,
        xg_away=lam_a,
        top_scorelines=scorelines[:3],
        home_field=home_field,
    )


# --------------------------------------------------------------------------- #
# 蒙特卡洛模拟
# --------------------------------------------------------------------------- #


def _simulate_score(kb: KnowledgeBase, home: str, away: str, rng: random.Random) -> tuple[int, int]:
    """按预测的进球率随机生成一场比分。"""
    pred = predict_match(kb, home, away)
    return _poisson_sample(pred.xg_home, rng), _poisson_sample(pred.xg_away, rng)


def _poisson_sample(lam: float, rng: random.Random) -> int:
    """Knuth 算法采样泊松分布。"""
    threshold = math.exp(-lam)
    k, p = 0, 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= threshold:
            return k - 1


@dataclass
class _Standing:
    team: str
    points: int = 0
    gf: int = 0
    ga: int = 0

    @property
    def gd(self) -> int:
        return self.gf - self.ga

    def add(self, scored: int, conceded: int) -> None:
        self.gf += scored
        self.ga += conceded
        if scored > conceded:
            self.points += 3
        elif scored == conceded:
            self.points += 1


def _simulate_group(kb: KnowledgeBase, members: list[str], rng: random.Random) -> list[_Standing]:
    """模拟一个小组的 6 场比赛，返回排好序的积分榜。"""
    table = {m: _Standing(m) for m in members}
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            a, b = members[i], members[j]
            ga, gb = _simulate_score(kb, a, b, rng)
            table[a].add(ga, gb)
            table[b].add(gb, ga)
    standings = list(table.values())
    # 排序键：积分 -> 净胜球 -> 进球数 -> 评分（确定性兜底）
    standings.sort(key=lambda s: (s.points, s.gd, s.gf, kb.team(s.team).rating), reverse=True)
    return standings


@dataclass
class GroupOutcome:
    """单个小组的模拟统计。"""

    group: str
    teams: list[str]
    # 各队完成位次概率 {team: [P(1st), P(2nd), P(3rd), P(4th)]}
    finish: dict[str, list[float]]
    # 各队晋级 32 强概率（前 2 或最佳第三）
    advance: dict[str, float]

    def table_zh(self, kb: KnowledgeBase) -> str:
        rows = sorted(self.teams, key=lambda t: self.advance[t], reverse=True)
        out = [f"小组 {self.group}：", "  球队                 晋级    第1    第2    第3    第4"]
        for t in rows:
            tm = kb.team(t)
            f = self.finish[t]
            out.append(
                f"  {tm.name_zh:<6}{tm.name:<14} {self.advance[t]:5.0%} {f[0]:6.0%} {f[1]:6.0%} {f[2]:6.0%} {f[3]:6.0%}"
            )
        return "\n".join(out)


def simulate_tournament(
    kb: KnowledgeBase,
    iterations: int = 5000,
    seed: int | None = None,
) -> dict[str, GroupOutcome]:
    """对全部 12 个小组做 Monte Carlo 模拟，返回各组晋级概率。

    晋级判定与官方一致：各组前 2 名直接晋级，再加 8 个成绩最好的小组
    第 3 名（按 积分 -> 净胜球 -> 进球数 全局排序）。
    """
    rng = random.Random(seed)
    groups = kb.groups
    finish_counts = {g: {t: [0, 0, 0, 0] for t in members} for g, members in groups.items()}
    advance_counts = {g: {t: 0 for t in members} for g, members in groups.items()}

    for _ in range(iterations):
        thirds: list[tuple[_Standing, str]] = []
        for g, members in groups.items():
            standings = _simulate_group(kb, members, rng)
            for pos, s in enumerate(standings):
                finish_counts[g][s.team][pos] += 1
                if pos < 2:  # 前两名直接晋级
                    advance_counts[g][s.team] += 1
                elif pos == 2:  # 第三名进入全局比较池
                    thirds.append((s, g))
        # 8 个最佳第三名
        thirds.sort(
            key=lambda x: (x[0].points, x[0].gd, x[0].gf, kb.team(x[0].team).rating),
            reverse=True,
        )
        for s, g in thirds[:8]:
            advance_counts[g][s.team] += 1

    results: dict[str, GroupOutcome] = {}
    for g, members in groups.items():
        finish = {t: [c / iterations for c in finish_counts[g][t]] for t in members}
        advance = {t: advance_counts[g][t] / iterations for t in members}
        results[g] = GroupOutcome(g, list(members), finish, advance)
    return results


def championship_odds(
    kb: KnowledgeBase,
    iterations: int = 3000,
    seed: int | None = None,
) -> list[tuple[str, float, float]]:
    """估算各队深度晋级概率。

    返回按夺冠概率降序的 ``(球队, 进入四强概率, 夺冠概率)`` 列表。

    淘汰赛采用「重新播种」近似：每次模拟取出 32 支晋级队，按本次模拟的
    小组表现（积分/净胜球）做蛇形种子分区配对，再逐轮用单场模型决出胜负。
    这是对官方固定对阵表的简化近似，用于给出量级参考。
    """
    rng = random.Random(seed)
    groups = kb.groups
    win_counts: dict[str, int] = {t: 0 for m in groups.values() for t in m}
    sf_counts: dict[str, int] = {t: 0 for m in groups.values() for t in m}

    for _ in range(iterations):
        qualifiers: list[_Standing] = []
        thirds: list[_Standing] = []
        for members in groups.values():
            standings = _simulate_group(kb, members, rng)
            qualifiers.extend(standings[:2])
            thirds.append(standings[2])
        thirds.sort(key=lambda s: (s.points, s.gd, s.gf, kb.team(s.team).rating), reverse=True)
        qualifiers.extend(thirds[:8])  # 共 32 队

        # 以小组表现 + 评分播种，强弱交错配对（近似官方分区思路）
        qualifiers.sort(key=lambda s: (s.points, s.gd, s.gf, kb.team(s.team).rating), reverse=True)
        bracket = [s.team for s in qualifiers]
        # 单淘汰：第 i 名 vs 第 (n-1-i) 名
        while len(bracket) > 1:
            half = len(bracket) // 2
            pairs = [(bracket[i], bracket[len(bracket) - 1 - i]) for i in range(half)]
            bracket = [_knockout_winner(kb, a, b, rng) for a, b in pairs]
            if len(bracket) == 4:  # 进入半决赛
                for t in bracket:
                    sf_counts[t] += 1
        win_counts[bracket[0]] += 1

    odds = [(t, sf_counts[t] / iterations, win_counts[t] / iterations) for t in win_counts]
    odds.sort(key=lambda x: x[2], reverse=True)
    return odds


def _knockout_winner(kb: KnowledgeBase, a: str, b: str, rng: random.Random) -> str:
    """淘汰赛单场决出胜者（平局按胜率掷点模拟点球）。"""
    pred = predict_match(kb, a, b, neutral=True)
    r = rng.random()
    if r < pred.p_home:
        return a
    if r < pred.p_home + pred.p_away:
        return b
    # 平局 -> 点球，按双方相对实力定胜负
    pa = pred.p_home / (pred.p_home + pred.p_away) if (pred.p_home + pred.p_away) else 0.5
    return a if rng.random() < pa else b
