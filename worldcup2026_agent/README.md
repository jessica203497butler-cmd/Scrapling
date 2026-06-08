# ⚽ worldcup2026 — 美加墨世界杯比赛分析工具智能体

一个基于 **网络搜集信息 + 内置知识库** 构建的 2026 国际足联世界杯（美国 /
加拿大 / 墨西哥联合主办，48 队 12 组）比赛分析智能体。它把「确认的赛事事实」
与「概率分析模型」结合起来，既可作为命令行工具直接使用，也可作为大模型
（如 Claude）的工具后端。

> 本工具是 [Scrapling](../README.md) 仓库中的一个独立示例项目：分析所需的实时
> FIFA 排名通过 Scrapling 的自适应抓取能力获取，离线时则回退到内置评分。

## ✨ 功能

| 能力 | 说明 |
| --- | --- |
| 📅 赛事信息 | 赛期、赛制、16 座主办球场、揭幕战 / 决赛、抽签结果（已确认事实）|
| 🧩 分组数据 | 2025-12-05 抽签产生的 12 个小组（A–L）完整名单 |
| ⚽ 单场预测 | 基于 FIFA Elo + 泊松进球模型的胜/平/负概率、xG、最可能比分 |
| 🎲 小组模拟 | 蒙特卡洛模拟各组出线（晋级 32 强）概率，含「8 个最佳第三名」规则 |
| 🏆 夺冠概率 | 全赛事蒙特卡洛，给出各队进四强 / 夺冠概率 |
| 🔄 实时刷新 | 用 Scrapling 抓取最新 FIFA 排名以覆盖内置评分（可选）|
| 🤖 智能体 | 内置中文 system prompt，可挂接到大模型作为「世界杯分析师」|

## 🚀 快速开始

```bash
cd worldcup2026_agent

# 赛事总览
python -m worldcup2026 info

# 按评分列出全部 48 队
python -m worldcup2026 teams

# 单场预测（支持中英文队名）
python -m worldcup2026 match Argentina Brazil
python -m worldcup2026 match 墨西哥 韩国          # 主办国自动享主场优势
python -m worldcup2026 match 西班牙 乌拉圭 --neutral

# 查看某小组并模拟出线概率
python -m worldcup2026 group A --iterations 5000 --seed 1

# 模拟全部小组 / 夺冠概率
python -m worldcup2026 simulate --iterations 5000
python -m worldcup2026 odds --top 16

# 先抓取最新 FIFA 排名再分析（需安装 scrapling）
python -m worldcup2026 --refresh odds
```

### Python API

```python
from worldcup2026 import WorldCupAgent

agent = WorldCupAgent()

pred = agent.predict_match("Argentina", "Brazil")
print(pred.summary_zh(agent.kb))

outcomes = agent.simulate_tournament(iterations=5000, seed=1)
print(outcomes["L"].table_zh(agent.kb))     # 英格兰 / 克罗地亚 / 加纳 / 巴拿马

for team, sf, win in agent.championship_odds(iterations=3000)[:5]:
    print(team, f"四强 {sf:.1%}", f"夺冠 {win:.1%}")
```

### 作为大模型工具后端

```python
import anthropic
from worldcup2026 import WorldCupAgent

agent = WorldCupAgent()
client = anthropic.Anthropic()

msg = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    system=agent.system_prompt,          # 中文「世界杯分析师」人设
    messages=[{"role": "user", "content": "帮我分析阿根廷小组出线形势"}],
)
# 在你的工具循环里把 agent.predict_match / simulate_tournament 暴露为工具
```

## 🧮 模型说明

1. **Elo 期望胜率**：`We = 1 / (1 + 10^((R_b - R_a)/600))`，与 FIFA 排名一致的
   分母 600；主办国（美 / 加 / 墨）在本国比赛获得约 +60 分的主场加成。
2. **泊松进球分布**：由期望胜率推出净胜球期望（supremacy）与双方进球率
   `λ`，再用独立泊松分布生成比分网格，聚合出胜/平/负概率与最可能比分。
3. **小组模拟**：对每组 6 场比赛做蒙特卡洛抽样，按 积分 → 净胜球 → 进球数
   排序；第三名进入全局比较池，取 8 个成绩最好者晋级（与官方规则一致）。
4. **淘汰赛**：采用「按表现重新播种」的强弱交错配对作为官方固定对阵表的
   **简化近似**，用于给出夺冠 / 四强概率的量级参考。

> ⚠️ 评分为依据 FIFA 排名（2026-04）相对顺序构造的**种子值**，所有概率均为
> 模型近似，仅供分析与娱乐，**不构成任何投注建议**。运行 `--refresh` 可用
> Scrapling 抓取最新排名覆盖种子值。

## 📁 结构

```
worldcup2026_agent/
├── worldcup2026/
│   ├── data.py        # 内置知识库：球队、分组、球场、赛事元信息
│   ├── analysis.py    # 分析引擎：单场预测 + 蒙特卡洛模拟
│   ├── fetcher.py     # Scrapling 实时抓取（可选，优雅降级）
│   ├── prompts.py     # 中文智能体 system prompt
│   ├── agent.py       # 编排层：WorldCupAgent 统一接口
│   └── cli.py         # 命令行界面
├── tests/test_agent.py
└── README.md
```

## 🧪 测试

```bash
cd worldcup2026_agent
pip install pytest
python -m pytest tests/ -q
```

## 📚 数据来源

- 2026 FIFA World Cup（赛制、主办城市、赛程）— FIFA 官方 / Wikipedia
- 2025-12-05 华盛顿特区抽签结果（12 个小组）— FIFA 官方公告
- FIFA/Coca-Cola 男足世界排名（2026-04 更新）— 用于评分种子的相对顺序

数据为构建时（2026-06）快照；如需最新结果请使用 `--refresh` 抓取实时排名。
