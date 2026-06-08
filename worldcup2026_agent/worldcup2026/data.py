"""美加墨世界杯（2026 FIFA World Cup）内置知识库。

数据来源：FIFA 官方公告、2025-12-05 华盛顿特区抽签结果，以及公开的
FIFA/Coca-Cola 男足世界排名（2026-04 更新）。评分（``rating``）以 FIFA
排名积分量级为种子值，可通过 :mod:`worldcup2026.fetcher` 抓取实时数据后覆盖。

所有数据均为「分析种子」，并非官方实时数据；如需最新结果请调用 fetcher。
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --------------------------------------------------------------------------- #
# 赛事元信息
# --------------------------------------------------------------------------- #

TOURNAMENT = {
    "name": "2026 FIFA World Cup",
    "name_zh": "2026年国际足联世界杯（美加墨世界杯）",
    "hosts": ["United States", "Canada", "Mexico"],
    "hosts_zh": {"United States": "美国", "Canada": "加拿大", "Mexico": "墨西哥"},
    "dates": "2026-06-11 ~ 2026-07-19",
    "teams": 48,
    "groups": 12,
    "matches": 104,
    "format": "12 组，每组 4 队；各组前 2 名 + 8 个成绩最好的小组第 3 名晋级 32 强淘汰赛",
    "opening_match": "墨西哥 vs 南非 @ 墨西哥城阿兹特克体育场（2026-06-11）",
    "final": "MetLife 体育场（新泽西，纽约都会区），2026-07-19",
    "draw": "2026 抽签于 2025-12-05 在华盛顿特区肯尼迪表演艺术中心举行",
}

# 16 座主办城市与球场（11 美国 / 3 墨西哥 / 2 加拿大）
VENUES = [
    {"city": "Mexico City", "city_zh": "墨西哥城", "country": "Mexico", "stadium": "Estadio Azteca"},
    {"city": "Guadalajara", "city_zh": "瓜达拉哈拉", "country": "Mexico", "stadium": "Estadio Akron"},
    {"city": "Monterrey", "city_zh": "蒙特雷", "country": "Mexico", "stadium": "Estadio BBVA"},
    {"city": "Toronto", "city_zh": "多伦多", "country": "Canada", "stadium": "BMO Field"},
    {"city": "Vancouver", "city_zh": "温哥华", "country": "Canada", "stadium": "BC Place"},
    {"city": "Los Angeles", "city_zh": "洛杉矶", "country": "United States", "stadium": "SoFi Stadium"},
    {
        "city": "San Francisco Bay Area",
        "city_zh": "旧金山湾区",
        "country": "United States",
        "stadium": "Levi's Stadium",
    },
    {"city": "Seattle", "city_zh": "西雅图", "country": "United States", "stadium": "Lumen Field"},
    {"city": "Kansas City", "city_zh": "堪萨斯城", "country": "United States", "stadium": "Arrowhead Stadium"},
    {"city": "Dallas", "city_zh": "达拉斯", "country": "United States", "stadium": "AT&T Stadium"},
    {"city": "Houston", "city_zh": "休斯顿", "country": "United States", "stadium": "NRG Stadium"},
    {"city": "Atlanta", "city_zh": "亚特兰大", "country": "United States", "stadium": "Mercedes-Benz Stadium"},
    {"city": "Miami", "city_zh": "迈阿密", "country": "United States", "stadium": "Hard Rock Stadium"},
    {"city": "Boston", "city_zh": "波士顿", "country": "United States", "stadium": "Gillette Stadium"},
    {"city": "Philadelphia", "city_zh": "费城", "country": "United States", "stadium": "Lincoln Financial Field"},
    {"city": "New York/New Jersey", "city_zh": "纽约/新泽西", "country": "United States", "stadium": "MetLife Stadium"},
]


# --------------------------------------------------------------------------- #
# 球队
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Team:
    """一支参赛球队。

    ``rating`` 量级对齐 FIFA 排名积分（约 1350-1880）；数值越高越强。
    """

    name: str
    name_zh: str
    confederation: str
    rating: float
    fifa_rank: int | None = None


# 48 支球队的评分种子（依据 2026-04 FIFA 排名相对顺序构造，可被实时数据覆盖）。
TEAMS: dict[str, Team] = {
    t.name: t
    for t in [
        Team("France", "法国", "UEFA", 1875, 1),
        Team("Spain", "西班牙", "UEFA", 1868, 2),
        Team("Argentina", "阿根廷", "CONMEBOL", 1861, 3),
        Team("England", "英格兰", "UEFA", 1820, 4),
        Team("Portugal", "葡萄牙", "UEFA", 1778, 5),
        Team("Brazil", "巴西", "CONMEBOL", 1760, 6),
        Team("Netherlands", "荷兰", "UEFA", 1752, 7),
        Team("Belgium", "比利时", "UEFA", 1740, 8),
        Team("Germany", "德国", "UEFA", 1724, 9),
        Team("Croatia", "克罗地亚", "UEFA", 1712, 10),
        Team("Morocco", "摩洛哥", "CAF", 1706, 11),
        Team("Colombia", "哥伦比亚", "CONMEBOL", 1690, 12),
        Team("Uruguay", "乌拉圭", "CONMEBOL", 1679, 13),
        Team("Switzerland", "瑞士", "UEFA", 1655, 14),
        Team("Mexico", "墨西哥", "CONCACAF", 1653, 15),
        Team("United States", "美国", "CONCACAF", 1650, 16),
        Team("Japan", "日本", "AFC", 1648, 17),
        Team("Senegal", "塞内加尔", "CAF", 1645, 18),
        Team("Iran", "伊朗", "AFC", 1620, 19),
        Team("Ecuador", "厄瓜多尔", "CONMEBOL", 1610, 20),
        Team("Austria", "奥地利", "UEFA", 1600, 21),
        Team("Australia", "澳大利亚", "AFC", 1595, 22),
        Team("South Korea", "韩国", "AFC", 1590, 23),
        Team("Egypt", "埃及", "CAF", 1585, 24),
        Team("Türkiye", "土耳其", "UEFA", 1580, 25),
        Team("Norway", "挪威", "UEFA", 1575, 26),
        Team("Ivory Coast", "科特迪瓦", "CAF", 1570, 27),
        Team("Sweden", "瑞典", "UEFA", 1565, 28),
        Team("Algeria", "阿尔及利亚", "CAF", 1560, 29),
        Team("Canada", "加拿大", "CONCACAF", 1555, 30),
        Team("Panama", "巴拿马", "CONCACAF", 1520, 31),
        Team("Paraguay", "巴拉圭", "CONMEBOL", 1518, 32),
        Team("Tunisia", "突尼斯", "CAF", 1515, 33),
        Team("Scotland", "苏格兰", "UEFA", 1510, 34),
        Team("Qatar", "卡塔尔", "AFC", 1505, 35),
        Team("Bosnia-Herzegovina", "波黑", "UEFA", 1500, 36),
        Team("Saudi Arabia", "沙特阿拉伯", "AFC", 1498, 37),
        Team("Ghana", "加纳", "CAF", 1496, 38),
        Team("DR Congo", "刚果（金）", "CAF", 1494, 39),
        Team("Czechia", "捷克", "UEFA", 1492, 40),
        Team("Uzbekistan", "乌兹别克斯坦", "AFC", 1488, 41),
        Team("Iraq", "伊拉克", "AFC", 1480, 42),
        Team("New Zealand", "新西兰", "OFC", 1465, 43),
        Team("Jordan", "约旦", "AFC", 1455, 44),
        Team("South Africa", "南非", "CAF", 1445, 45),
        Team("Cape Verde", "佛得角", "CAF", 1430, 46),
        Team("Curaçao", "库拉索", "CONCACAF", 1390, 47),
        Team("Haiti", "海地", "CONCACAF", 1365, 48),
    ]
}


# --------------------------------------------------------------------------- #
# 小组抽签结果（2025-12-05）
# --------------------------------------------------------------------------- #

GROUPS: dict[str, list[str]] = {
    "A": ["Mexico", "South Africa", "South Korea", "Czechia"],
    "B": ["Canada", "Bosnia-Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Türkiye"],
    "E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# 主办国——在本国比赛享有主场优势加成（详见 analysis.HOME_ADVANTAGE）
HOST_NATIONS = {"United States", "Canada", "Mexico"}


@dataclass
class KnowledgeBase:
    """聚合所有内置数据，便于注入/覆盖（如抓取实时数据后）。"""

    tournament: dict = field(default_factory=lambda: dict(TOURNAMENT))
    venues: list = field(default_factory=lambda: list(VENUES))
    teams: dict = field(default_factory=lambda: dict(TEAMS))
    groups: dict = field(default_factory=lambda: {k: list(v) for k, v in GROUPS.items()})
    host_nations: set = field(default_factory=lambda: set(HOST_NATIONS))

    def team(self, name: str) -> Team:
        """按英文或中文名查找球队（大小写不敏感）。"""
        if name in self.teams:
            return self.teams[name]
        low = name.strip().lower()
        for t in self.teams.values():
            if t.name.lower() == low or t.name_zh == name.strip():
                return t
        raise KeyError(f"未找到球队：{name!r}（请使用 list_teams() 查看全部名称）")

    def group_of(self, name: str) -> str | None:
        """返回球队所在小组字母，找不到返回 None。"""
        team = self.team(name)
        for g, members in self.groups.items():
            if team.name in members:
                return g
        return None

    def update_ratings(self, ratings: dict[str, float]) -> int:
        """用 ``{球队名: 评分}`` 覆盖评分，返回成功更新的数量。"""
        n = 0
        for name, value in ratings.items():
            try:
                t = self.team(name)
            except KeyError:
                continue
            self.teams[t.name] = Team(t.name, t.name_zh, t.confederation, float(value), t.fifa_rank)
            n += 1
        return n
