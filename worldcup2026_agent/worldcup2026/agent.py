"""智能体编排层：把知识库、分析引擎与抓取器封装为统一接口。

``WorldCupAgent`` 既可直接在 Python 中调用，也可作为大模型的「工具后端」
（其方法签名与 prompts.SYSTEM_PROMPT_ZH 中描述的工具一致）。
"""

from __future__ import annotations

from .analysis import (
    GroupOutcome,
    MatchPrediction,
    championship_odds,
    predict_match,
    simulate_tournament,
)
from .data import KnowledgeBase
from .prompts import SYSTEM_PROMPT_ZH


class WorldCupAgent:
    """2026 美加墨世界杯比赛分析智能体。"""

    def __init__(self, knowledge_base: KnowledgeBase | None = None):
        self.kb = knowledge_base or KnowledgeBase()

    # --- 信息查询 ----------------------------------------------------------- #

    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT_ZH

    def info(self) -> dict:
        """返回赛事元信息。"""
        return self.kb.tournament

    def list_teams(self) -> list[dict]:
        """返回全部 48 队，按评分降序。"""
        teams = sorted(self.kb.teams.values(), key=lambda t: t.rating, reverse=True)
        return [
            {
                "name": t.name,
                "name_zh": t.name_zh,
                "confederation": t.confederation,
                "rating": t.rating,
                "fifa_rank": t.fifa_rank,
                "group": self.kb.group_of(t.name),
            }
            for t in teams
        ]

    def group(self, letter: str) -> dict:
        """返回某小组成员及其评分。"""
        letter = letter.upper()
        if letter not in self.kb.groups:
            raise KeyError(f"小组不存在：{letter}（A-L）")
        return {
            "group": letter,
            "teams": [
                {
                    "name": self.kb.team(t).name,
                    "name_zh": self.kb.team(t).name_zh,
                    "rating": self.kb.team(t).rating,
                }
                for t in self.kb.groups[letter]
            ],
        }

    # --- 分析工具 ----------------------------------------------------------- #

    def predict_match(self, home: str, away: str, *, neutral: bool | None = None) -> MatchPrediction:
        """预测单场比赛。"""
        return predict_match(self.kb, home, away, neutral=neutral)

    def simulate_tournament(self, iterations: int = 5000, seed: int | None = None) -> dict[str, GroupOutcome]:
        """蒙特卡洛模拟全部小组，返回出线概率。"""
        return simulate_tournament(self.kb, iterations=iterations, seed=seed)

    def championship_odds(self, iterations: int = 3000, seed: int | None = None) -> list[tuple[str, float, float]]:
        """估算各队四强 / 夺冠概率。"""
        return championship_odds(self.kb, iterations=iterations, seed=seed)

    # --- 实时数据 ----------------------------------------------------------- #

    def refresh_ratings(self) -> int:
        """用 Scrapling 抓取最新 FIFA 排名刷新评分，返回更新的球队数。

        网络/依赖不可用时返回 0 并保留内置评分（优雅降级）。
        """
        from .fetcher import refresh_knowledge_base  # 延迟导入，避免硬依赖

        return refresh_knowledge_base(self.kb)
