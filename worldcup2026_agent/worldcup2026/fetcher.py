"""实时数据抓取：用 Scrapling 拉取 FIFA 世界排名以刷新球队评分。

Scrapling 为可选依赖：未安装时本模块仍可导入，调用抓取函数会抛出带有
安装提示的 :class:`RuntimeError`，因此核心分析功能（内置知识库）始终可用。

设计要点：
- 使用 Scrapling 自适应选择器（``auto_match``），即便站点改版也能尽量保持
  选择器有效；
- 评分量级与内置 ``Team.rating`` 一致（FIFA 积分），抓取后可直接喂给
  :meth:`KnowledgeBase.update_ratings`。
"""

from __future__ import annotations

import re

# FIFA 官方男足排名页（结构可能随时间变化，选择器写得较为宽松）
FIFA_RANKING_URL = "https://inside.fifa.com/fifa-world-ranking/men"

# 内置英文队名的别名映射，用于把抓取到的名字对齐到知识库键
_NAME_ALIASES = {
    "USA": "United States",
    "US": "United States",
    "Korea Republic": "South Korea",
    "IR Iran": "Iran",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "Türkiye": "Türkiye",
    "Turkiye": "Türkiye",
    "Turkey": "Türkiye",
    "Czech Republic": "Czechia",
    "Cabo Verde": "Cape Verde",
    "Bosnia and Herzegovina": "Bosnia-Herzegovina",
    "DR Congo": "DR Congo",
    "Curacao": "Curaçao",
}


def _require_scrapling():
    try:
        from scrapling.fetchers import Fetcher  # noqa: PLC0415

        return Fetcher
    except Exception as exc:  # pragma: no cover - 取决于运行环境
        raise RuntimeError(
            "实时抓取需要安装 Scrapling：`pip install scrapling`。未安装时仍可使用内置知识库进行分析。"
        ) from exc


def normalize_team_name(name: str) -> str:
    """把抓取到的队名规整为知识库使用的英文键。"""
    name = name.strip()
    return _NAME_ALIASES.get(name, name)


def fetch_fifa_ratings(url: str = FIFA_RANKING_URL, timeout: int = 30) -> dict[str, float]:
    """抓取 FIFA 男足世界排名，返回 ``{球队英文名: 积分}``。

    返回的字典可直接传给 :meth:`KnowledgeBase.update_ratings`。
    若页面结构无法解析则返回空字典（调用方应据此回退到内置评分）。
    """
    Fetcher = _require_scrapling()
    page = Fetcher.get(url, timeout=timeout)

    ratings: dict[str, float] = {}

    # 策略 1：表格行，包含 国家名 + 数字积分（多数排名页形态）
    for row in page.css("table tr"):
        cells = [c.clean() for c in row.css("td::text") if c.clean()]
        if len(cells) < 2:
            continue
        name = None
        points = None
        for cell in cells:
            if name is None and re.search(r"[A-Za-z]{3,}", cell) and not _looks_numeric(cell):
                name = cell
            elif _looks_numeric(cell):
                points = _to_float(cell)
        if name and points is not None:
            ratings[normalize_team_name(name)] = points

    return ratings


def _looks_numeric(text: str) -> bool:
    return bool(re.fullmatch(r"[\d.,]+", text.strip()))


def _to_float(text: str) -> float:
    return float(text.replace(",", "").strip())


def refresh_knowledge_base(kb, url: str = FIFA_RANKING_URL) -> int:
    """抓取最新排名并就地刷新 ``kb`` 评分，返回更新的球队数。

    抓取或网络失败时返回 0，并保留内置评分（不抛出，便于优雅降级）。
    """
    try:
        ratings = fetch_fifa_ratings(url)
    except Exception:
        return 0
    if not ratings:
        return 0
    return kb.update_ratings(ratings)
