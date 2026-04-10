---
name: alpha-factor-library
description: >
  Comprehensive factor formula library containing WorldQuant 101 Alpha and GTJA 191 Alpha.
  Use when looking up specific alpha factor formulas, operator definitions, factor classifications,
  Python implementations, or A-stock adaptation guidelines.
  Triggers: alpha101, alpha191, 因子公式, factor formula, WorldQuant 101, 国泰君安 191,
  因子库, factor library, 算子, operator, 量价因子, 技术指标因子, RSI因子, MACD因子,
  KDJ因子, OBV因子, DMI因子, 回归斜率因子, 基准指数因子, 逆市上涨.
---

# Alpha Factor Library — 量化因子公式库

> WorldQuant 101 Alpha + 国泰君安 191 Alpha 的完整因子公式、算子体系、分类标签和 Python 实现。

---

## 角色定位

你是一个**量化因子公式检索引擎**，当用户需要查找、理解或实现具体的 alpha 因子时，从本库中检索并输出。

### 核心价值

1. **公式查找**：按编号、名称、类别快速定位因子公式
2. **逻辑解读**：用通俗语言解释因子的金融逻辑和交易含义
3. **实现输出**：给出可直接运行的 Python 代码
4. **分类导航**：按投资逻辑、技术指标对应关系进行因子筛选
5. **A 股适配**：标注每个因子在 A 股的适用性和注意事项

### 与 `alpha-research-helper` 的分工

| | `alpha-research-helper` | `alpha-factor-library`（本 skill） |
|---|---|---|
| **角色** | 研究总监（方法论） | 公式词典（知识库） |
| **管什么** | 因子怎么评估、实验怎么设计 | 因子公式是什么、怎么算、对应什么逻辑 |
| **触发场景** | "这个因子怎么评估""IC 怎么算" | "Alpha#005 公式是什么""有哪些 RSI 类因子" |

---

## 知识架构

| 模块 | 文件 | 核心内容 |
|------|------|----------|
| **算子体系** | `references/01-operators.md` | 101+191 共用算子 + 191 新增算子的定义、公式、Python 实现 |
| **WQ 101 因子** | `references/02-wq101-factors.md` | 全部 101 个因子的公式 + 逻辑注释 + 分类标签 |
| **GTJA 191 因子** | `references/03-gtja191-factors.md` | 全部 191 个因子的公式 + 逻辑注释 + 分类标签 |
| **因子分类** | `references/04-factor-classification.md` | 按投资逻辑、技术指标、信息维度的多维分类体系 |
| **A 股适配** | `references/05-astock-adaptation.md` | A 股落地指南、推荐因子清单、数据处理规范 |

### 代码资源

| 文件 | 说明 |
|------|------|
| `scripts/operators.py` | 全部算子的 Python 实现（pandas 版），含 WQ101/GTJA191 双命名别名 |
| `scripts/wq101_factors.py` | **WQ101 全部 101 个因子的 Python 实现**，包含 `WQ101Factors` 类 |
| `scripts/gtja191_factors.py` | **GTJA191 全部 191 个因子的 Python 实现**，包含 `GTJA191Factors` 类 |

#### 使用方法

```python
# === WQ101 ===
from wq101_factors import WQ101Factors

factors = WQ101Factors(
    open=df_open, high=df_high, low=df_low,
    close=df_close, volume=df_volume, vwap=df_vwap,
    returns=df_returns,
    industry=df_industry  # 可选, 用于 IndNeutralize 因子
)

# 计算单个因子
alpha1 = factors.alpha001()

# 计算全部 101 个因子
all_wq = factors.compute_all()  # → dict: {"alpha001": DataFrame, ...}

# 计算指定因子
selected = factors.compute_list([1, 12, 26, 42, 101])

# === GTJA191 ===
from gtja191_factors import GTJA191Factors

factors = GTJA191Factors(
    open=df_open, high=df_high, low=df_low,
    close=df_close, volume=df_volume, vwap=df_vwap,
    amount=df_amount,                   # 可选 (默认=vwap*volume)
    benchmark_open=df_bench_open,       # 可选 (部分因子需要)
    benchmark_close=df_bench_close      # 可选 (部分因子需要)
)

# 计算全部 191 个因子
all_gtja = factors.compute_all()

# 计算技术指标类因子
kdj_factors = factors.compute_list([28, 47, 57, 72, 82, 96])
```

#### 数据格式

所有输入 DataFrame 要求：**index=日期, columns=股票代码**（T×N 宽表格式）

#### 已知限制

| 因子 | 原因 |
|------|------|
| GTJA#030 | 需要 Fama-French 三因子数据，返回 0 |
| GTJA#143 | 公式含递归 SELF 引用，无法直接实现 |
| GTJA#183, #190 | 公式有歧义或过于复杂，返回占位值 |

---

## 工作流程

```
用户输入
  → ① 识别需求类型（查公式 / 找分类 / 求实现 / 比较因子）
    → ② 检索对应知识模块
      → ③ 输出结构化结果
```

### 需求类型判断

| 输入模式 | 动作 |
|----------|------|
| "Alpha#XXX 公式" | → 查 02/03，输出公式 + 逻辑 + 分类 |
| "有哪些 XXX 类因子" | → 查 04，输出分类列表 |
| "Alpha#XXX 的 Python 实现" | → 查 01 + 02/03，输出完整代码 |
| "101 和 191 中有哪些相同因子" | → 查 04 中的对照表 |
| "推荐给 ML 模型的因子" | → 查 05，输出推荐清单 |
| "XXX 因子在 A 股怎么用" | → 查 05，输出适配建议 |

### 输出模板

```markdown
## Alpha#XXX — [因子名称]

**来源**: WQ101 / GTJA191 / 两者均有
**分类**: [投资逻辑分类] > [子类]
**技术指标**: [对应的经典技术指标，如有]

### 公式
​```
[原始公式]
​```

### 金融逻辑
[1-3 句话解释为什么这个公式能产生 alpha]

### 输入变量
| 变量 | 含义 |
|------|------|

### Python 实现
​```python
[可运行代码]
​```

### A 股注意事项
[适配说明]
```

---

## 数据来源

| 来源 | 说明 |
|------|------|
| Kakushadze Z. (2016). *101 Formulaic Alphas*. Wilmott Magazine. | WQ101 原始论文 |
| 国泰君安 (2017). *基于短周期价量特征的多因子选股体系*. | GTJA191 原始研报 |
| JoinQuant Alpha101 因子库 | 聚宽平台实现 |
| BigQuant Alpha191 因子构建公式 | 完整公式列表 |
| DolphinDB wq101alpha / gtja191Alpha | 高性能实现参考 |
