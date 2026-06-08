"""worldcup2026 —— 2026 美加墨世界杯比赛分析工具智能体。

快速上手::

    from worldcup2026 import WorldCupAgent

    agent = WorldCupAgent()
    pred = agent.predict_match("Argentina", "Brazil")
    print(pred.summary_zh(agent.kb))
"""

from .agent import WorldCupAgent
from .analysis import (
    GroupOutcome,
    MatchPrediction,
    championship_odds,
    predict_match,
    simulate_tournament,
)
from .data import GROUPS, TEAMS, TOURNAMENT, VENUES, KnowledgeBase, Team
from .prompts import SYSTEM_PROMPT_ZH

__version__ = "0.1.0"

__all__ = [
    "WorldCupAgent",
    "KnowledgeBase",
    "Team",
    "MatchPrediction",
    "GroupOutcome",
    "predict_match",
    "simulate_tournament",
    "championship_odds",
    "SYSTEM_PROMPT_ZH",
    "TEAMS",
    "GROUPS",
    "VENUES",
    "TOURNAMENT",
]
