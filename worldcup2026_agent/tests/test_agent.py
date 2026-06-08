"""worldcup2026 智能体的基础单元测试（无需网络）。"""

import math

import pytest

from worldcup2026 import WorldCupAgent
from worldcup2026.analysis import _elo_expected, _poisson_pmf


@pytest.fixture
def agent():
    return WorldCupAgent()


def test_knowledge_base_complete(agent):
    assert len(agent.kb.teams) == 48
    assert len(agent.kb.groups) == 12
    assert all(len(m) == 4 for m in agent.kb.groups.values())
    assert len(agent.kb.venues) == 16
    # 每队恰好出现在一个小组
    all_in_groups = [t for m in agent.kb.groups.values() for t in m]
    assert len(all_in_groups) == 48
    assert set(all_in_groups) == set(agent.kb.teams)


def test_team_lookup_zh_and_en(agent):
    assert agent.kb.team("Argentina").name_zh == "阿根廷"
    assert agent.kb.team("阿根廷").name == "Argentina"
    assert agent.kb.team("argentina").name == "Argentina"
    with pytest.raises(KeyError):
        agent.kb.team("Atlantis")


def test_group_of(agent):
    assert agent.kb.group_of("Mexico") == "A"
    assert agent.kb.group_of("England") == "L"


def test_elo_symmetry():
    # 同分应为 0.5；强队期望 > 0.5
    assert math.isclose(_elo_expected(1700, 1700), 0.5)
    assert _elo_expected(1800, 1600) > 0.5
    assert _elo_expected(1600, 1800) < 0.5


def test_poisson_pmf_sums_to_one():
    total = sum(_poisson_pmf(k, 1.5) for k in range(40))
    assert math.isclose(total, 1.0, abs_tol=1e-6)


def test_predict_match_probabilities(agent):
    pred = agent.predict_match("Argentina", "Haiti")
    # 概率归一
    assert math.isclose(pred.p_home + pred.p_draw + pred.p_away, 1.0, abs_tol=1e-9)
    # 强队（阿根廷）应明显被看好
    assert pred.p_home > pred.p_away
    assert pred.xg_home > pred.xg_away
    assert len(pred.top_scorelines) == 3


def test_home_advantage_applied(agent):
    # 主办国默认享主场优势
    home = agent.predict_match("Mexico", "South Korea")
    neutral = agent.predict_match("Mexico", "South Korea", neutral=True)
    assert home.home_field is True
    assert neutral.home_field is False
    assert home.p_home > neutral.p_home


def test_simulate_tournament_probabilities_normalized(agent):
    outcomes = agent.simulate_tournament(iterations=300, seed=42)
    assert set(outcomes) == set(agent.kb.groups)
    for g, outcome in outcomes.items():
        for team in outcome.teams:
            # 四个位次概率之和约为 1
            assert math.isclose(sum(outcome.finish[team]), 1.0, abs_tol=1e-9)
            assert 0.0 <= outcome.advance[team] <= 1.0
        # 每组恰好 2 个直接晋级名额 + 部分第三名 -> 晋级概率之和介于 2 与 3
        total_adv = sum(outcome.advance[t] for t in outcome.teams)
        assert 2.0 <= total_adv <= 3.0 + 1e-9


def test_simulate_reproducible(agent):
    a = agent.simulate_tournament(iterations=200, seed=7)
    b = agent.simulate_tournament(iterations=200, seed=7)
    assert a["A"].advance == b["A"].advance


def test_championship_odds(agent):
    odds = agent.championship_odds(iterations=200, seed=1)
    assert len(odds) == 48
    win_total = sum(w for _, _, w in odds)
    assert math.isclose(win_total, 1.0, abs_tol=1e-9)
    # 概率降序
    wins = [w for _, _, w in odds]
    assert wins == sorted(wins, reverse=True)


def test_list_teams_sorted(agent):
    teams = agent.list_teams()
    assert len(teams) == 48
    ratings = [t["rating"] for t in teams]
    assert ratings == sorted(ratings, reverse=True)
    assert teams[0]["name"] == "France"


def test_system_prompt_nonempty(agent):
    assert "世界杯" in agent.system_prompt
    assert len(agent.system_prompt) > 200
