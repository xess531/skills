# 模块一：因子基础知识

> Alpha 因子核心概念、评估指标体系、中性化方法、数据预处理与标签设计。

---

## 1. Alpha 因子核心概念

**Alpha（超额收益）**：资产收益中超出市场风险解释水平的部分，源于 CAPM 模型。在量化投资中，Alpha 通过"因子"来寻找——即系统性解释资产收益差异的变量。

**因子分类总览**（详细构造见 `02-factor-taxonomy.md`）：

| 大类 | 子类 | 典型因子 | 经济逻辑 |
|------|------|----------|----------|
| **价值** | 低估值 | PE、PB、EV/EBITDA | 低估值→均值回归 |
| **动量/反转** | 趋势/反转 | 12 月动量、1 月反转 | A 股短期反转 > 中期动量 |
| **质量** | 盈利质量 | ROE、ROA、Accruals、F-Score | 高质量公司长期跑赢 |
| **波动率** | 风险异象 | RV、IVOL、特质波动率 | 低波异象（彩票偏好/杠杆约束） |
| **流动性** | 流动性溢价 | 换手率、Amihud ILLIQ | 低流动性→溢价补偿 |
| **成长** | 盈利增长 | 营收增长率、利润增长率 | 高增长→市场低估 |
| **情绪** | 行为偏差 | 散户关注度、分析师一致预期变化 | 行为金融学偏差 |
| **量价** | 微观结构 | 量价背离、VWAP偏离、波动率偏度 | 知情交易信号 |
| **高频** | 日内数据 | OFI、大单占比、日内动量 | 知情交易者行为 |
| **AI 端到端** | 模型输出 | AlphaNet因子、CNN-Transformer因子 | 非线性特征提取 |

---

## 2. 因子评估指标体系

### 2.1 关键术语速查

| 术语 | 定义 | 用途 |
|------|------|------|
| **IC (Information Coefficient)** | 因子值与未来收益的截面 Pearson 相关系数 | 衡量因子预测能力 |
| **RankIC** | 因子排名与收益排名的 Spearman 秩相关 | 更关注排序能力，对异常值不敏感 |
| **IR (Information Ratio)** | IC_mean / IC_std | 衡量因子稳定性 |
| **IC 胜率** | IC > 0 的天数占比 | 正确预测的交易日比例 |
| **分层收益** | 按因子值分组后各组平均收益 | 检验因子单调性（区分度） |
| **多空组合** | 做多高分组 + 做空低分组 | 对冲 beta，获取纯因子收益 |
| **因子换手率** | 相邻期因子排名变化程度 | 换手太高→交易成本吞噬收益 |
| **因子衰减** | IC 随持有期增长而下降的速度 | 判断最佳使用频率 |
| **因子拥挤度** | 同一因子被多少策略使用 | 拥挤因子容易反转 |
| **因子暴露 (Factor Exposure / Loading)** | 资产对因子的敏感度，即截面回归中的系数 | 度量组合在某因子方向上的"下注"大小 |

### 2.2 一级指标（必看）

| 指标 | 计算 | 好因子标准 | 解释 |
|------|------|------------|------|
| RankIC 均值 | 每日 Spearman(factor_rank, return_rank) 的均值 | > 0.03 | 绝对值越大预测力越强 |
| IR | IC_mean / IC_std | > 0.5 | 越大越稳定 |
| IC 胜率 | count(IC > 0) / total_days | > 55% | 正确预测的交易日占比 |
| 分层收益单调性 | 5/10/20 组年化收益是否递增/递减 | 单调或近似单调 | 组间收益差越大区分度越高 |
| 多空年化收益 | Top 组 - Bottom 组的年化超额 | > 10% | 纯因子的经济价值 |
| 多空 Sharpe | 多空收益 / 多空波动率 | > 1.0 | 风险调整后的因子收益 |
| 多空最大回撤 | 多空组合的历史最大回撤 | < 20% | 因子的尾部风险 |

### 2.3 二级指标（进阶）

| 指标 | 用途 |
|------|------|
| IC 时序稳定性 | 滚动窗口 IC 标准差，检查结构性变化 |
| 子样本检验 | 分牛/熊/震荡市分别看 IC |
| 行业内 IC | 行业中性化后的 IC |
| 规模分层 IC | 大/中/小盘股分别看 IC |
| 因子自相关性 | 相邻期因子值自相关系数 |
| 因子半衰期 | IC 衰减到一半的持有天数 |
| **因子暴露分析** | 对 Barra 10 风格因子做回归，检查新因子是否只是已知 beta 暴露 |

### 2.4 IC vs RankIC 的选择

```python
# IC: Pearson 相关
IC_t = corr(factor_t, return_{t+H})

# RankIC: Spearman 秩相关
RankIC_t = spearman_corr(rank(factor_t), rank(return_{t+H}))
```

**RankIC 通常优于 IC 的原因**：
- 对异常值不敏感（只看排名）
- 不假设线性关系（只要单调即可）
- 选股本质上是排序问题，RankIC 直接衡量排序质量
- 行业惯例：多数券商研报以 RankIC 为主

**IC 的解读标准**：
| 范围 | 判断 |
|------|------|
| IC > 0.05 | 强因子（A 股日频很少见） |
| IC > 0.03 | 有效因子 |
| IC > 0.02 | 弱有效因子 |
| IC < 0.02 | 基本无效 |

### 2.5 分层回测

**方法**：
1. 每个调仓日，按因子值对全部股票排序
2. 等分为 N 组（常用 5/10/20 组）
3. 每组内等权持有到下一调仓日
4. 计算各组的年化收益、Sharpe、最大回撤

**关键观察维度**：
- **单调性**：第 1 组到第 N 组收益递增/递减
- **多空价差**：Top 组 - Bottom 组的年化超额
- **Top 组绝对收益**：实际选股标的的表现
- **各组 Sharpe**：风险调整后的收益
- **换手率**：调仓时组内股票变化程度

### 2.6 多空组合回测

```python
long_portfolio = top_quantile_return
short_portfolio = bottom_quantile_return
long_short_return = long_portfolio - short_portfolio
```

**评估指标**：年化收益（>10%）、Sharpe（>1.0）、最大回撤（<20%）、Calmar

**A 股注意**：做空受限（融券成本高、券源少），多空组合更多用于评估；实盘更关注**多头端超额**（Top 组 vs 基准）。

### 2.7 Qlib 标准评估框架

| 类别 | 指标 | 说明 |
|------|------|------|
| 信号质量 | IC, ICIR, RankIC, RankICIR | 因子预测质量 |
| 组合表现 | Annualized Return, Excess Return, IR | 策略收益 |
| 风险 | Max Drawdown, Annualized Volatility | 尾部风险 |
| 交易 | Turnover | 换手率 |

```python
from qlib.contrib.evaluate import backtest, risk_analysis
from qlib.contrib.report import analysis_model

pred = model.predict(dataset)
analysis_model.model_performance_graph(pred_label)  # IC 时序图
portfolio = backtest(pred, topk=50, n_drop=5)
report = risk_analysis(portfolio)
```

---

## 3. 因子中性化

### 3.1 为什么要中性化

消除特定维度（行业、市值、beta）对因子的污染，让因子收益更纯粹。本质是对 Barra 风格因子做正交化。

### 3.2 方法一：分组标准化法（行业中性化常用）

```python
# 每个日期、每个行业组内做 Z-score
factor_neutral = df.groupby(['date', 'industry'])['factor'] \
    .transform(lambda x: (x - x.mean()) / x.std())
```

适用：行业、板块等离散分类变量。假设组内方差差别不大。

### 3.3 方法二：回归残差法（市值中性化常用）

```python
import statsmodels.api as sm

def neutralize(group):
    X = group[['log_mcap']]  # 可同时放多个风险因子
    X = sm.add_constant(X)
    model = sm.OLS(group['factor'], X).fit()
    return model.resid

factor_neutral = df.groupby('date').apply(neutralize)
```

适用：市值、beta 等连续风险因子。可同时对多个因子做中性化。

### 3.4 行业+市值联合中性化

```python
def joint_neutralize(group):
    # 行业哑变量 + log 市值
    industry_dummies = pd.get_dummies(group['industry'], drop_first=True)
    X = pd.concat([industry_dummies, group[['log_mcap']]], axis=1)
    X = sm.add_constant(X)
    model = sm.OLS(group['factor'], X).fit()
    return model.resid

factor_neutral = df.groupby('date').apply(joint_neutralize)
```

### 3.5 何时不应中性化

- 因子本身在挖掘**行业轮动**信号时（行业中性化会消灭信号）
- 因子的 alpha 明确来自**市值暴露**且你愿意承担该风险时
- **端到端深度学习**模型内部已隐式做了中性化（如使用行业超额收益标签）

### 3.6 中性化与标签设计的关系

- 使用**行业超额收益标签**（r_stock − r_industry）≈ 标签端行业中性化
- 用行业超额标签后，因子端通常不再需要额外行业中性化
- 但市值中性化仍可能需要，视策略而定

### 3.7 因子暴露（Factor Exposure）实操指南

**定义**：资产 i 对因子 j 的暴露度 X_ij，即截面标准化后的因子值。

**检查新因子独立性的标准流程**：

```python
import numpy as np
from sklearn.linear_model import LinearRegression

def check_barra_exposure(new_factor, barra_factors, dates):
    """
    检查新因子在 Barra 风格因子上的暴露度。
    如果 R² > 0.3，说明新因子大部分是已知 beta 暴露而非独立 alpha。
    """
    results = []
    for date in dates:
        X = barra_factors.loc[date].values  # [N_stocks, 10] Barra 因子
        y = new_factor.loc[date].values      # [N_stocks] 新因子
        reg = LinearRegression().fit(X, y)
        results.append({
            'date': date,
            'R2': reg.score(X, y),
            'exposures': dict(zip(barra_names, reg.coef_))
        })
    return pd.DataFrame(results)
```

**判断标准**：
- R² < 0.1 → 新因子基本独立于 Barra → 有独立 alpha 价值
- R² 0.1-0.3 → 部分暴露 → 需中性化后再评估
- R² > 0.3 → 大部分是已知 beta → alpha 价值存疑

---

## 4. 数据与预处理

### 4.1 股票池筛选（A 股标准）

```
有效样本 = 正常交易状态 (status == 1)
         & 属于指数成分股或满足流动性要求
         & 价格/换手率完整 (无 NaN)
         & 上市天数 ≥ 120 (剔除次新股 IPO 效应)
         & 非 ST/PT 股票
         & 非涨跌停（涨跌停日因子值失真）
```

### 4.2 预处理流水线

```
原始数据
  → ① 去极值 (Winsorize: 1%/99% 分位截断)
    → ② 标准化 (截面 Z-score 或面板级相对化)
      → ③ 缺失值处理 (前向填充 / 行业均值 / 删除)
        → ④ 行业分类对齐 (申万一级 / 中信一级)
          → ⑤ 标签构造
            → ⑥ 标签截断 (1%/99.5% 分位)
```

### 4.3 面板级相对化 vs 截面标准化

| 方法 | 公式 | 优点 | 缺点 |
|------|------|------|------|
| **面板级相对化** | price_t / close_{t-N} | 保留 OHLCV 相对大小关系 | 前 N 天 NaN |
| **截面 Z-score** | (x - mean_cross) / std_cross | 消除截面差异 | 破坏特征间相对关系 |
| **Channel-wise Z-score** | (x - μ_train) / σ_train | 防止泄露 | 测试集分布可能偏移 |

**推荐**：数据准备用面板级相对化（保留特征间关系），模型入口再做 channel-wise Z-score（基于训练集统计量）。

### 4.4 标签设计

| 标签类型 | 公式 | 适用场景 |
|----------|------|----------|
| **原始收益** | r = close_{t+H} / close_t - 1 | 绝对收益预测 |
| **行业超额收益** | r_excess = r_stock − mean(r_industry) | 个股 alpha 提取（**推荐**） |
| **市场超额收益** | r_excess = r_stock − r_market | 简单但含行业 beta |
| **排名标签** | rank(r) / N | 直接优化排序 |

**推荐**：行业超额收益标签 + 标签截断（1%/99.5%）。原因：
- 剥离行业 beta，模型只学个股 alpha
- 降低标签方差，提高信噪比
- 行业轮动由宏观驱动，个股模型难捕捉

### 4.5 行业分类对齐

| 分类体系 | 级别 | 行业数 | 常用场景 |
|----------|------|--------|----------|
| **申万一级** | 一级 | 31 | 最通用，绝大多数研报使用 |
| **中信一级** | 一级 | 30 | 中金/中信系研报 |
| **GICS** | 四级 | 158 | 国际对比、MSCI 指数 |
| **证监会** | 二级 | 90+ | 监管口径 |

**注意**：行业分类会变化（如申万 2021 版新增 7 个行业），需用新分类进行历史回溯。
