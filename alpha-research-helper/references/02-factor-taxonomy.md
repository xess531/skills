# 模块二：因子分类学 (Factor Taxonomy)

> 完整的因子分类体系。每个因子类别包含：定义与经济逻辑 → 构造公式 → A 股实证 → 已知陷阱。

---

## 1. 价值因子 (Value Factors)

### 1.1 定义与经济逻辑

低估值股票长期跑赢高估值股票。源自 Fama-French HML 因子。经济解释：
- **风险补偿**：低估值公司可能面临更高的财务困境风险
- **行为偏差**：投资者过度外推成长性，低估价值股

### 1.2 核心因子构造

| 因子 | 公式 | 说明 |
|------|------|------|
| **EP (Earnings-to-Price)** | 净利润_TTM / 总市值 | 传统价值因子，注意 TTM 处理 |
| **BP (Book-to-Price)** | 净资产 / 总市值 | Fama-French HML 的基础 |
| **SP (Sales-to-Price)** | 营业收入_TTM / 总市值 | 适合亏损公司 |
| **CFOP (Cashflow/Price)** | 经营现金流_TTM / 总市值 | 比 EP 更难操纵 |
| **EV/EBITDA** | 企业价值 / EBITDA | 考虑了资本结构差异 |
| **DP (Dividend Yield)** | 每股股利 / 股价 | 红利因子变体 |

```python
# EP 因子构造（TTM 口径）
ep = df['net_profit_ttm'] / df['total_market_cap']
# 处理异常值：排除 EP < 0 或极端值
ep = ep.clip(lower=ep.quantile(0.01), upper=ep.quantile(0.99))
```

### 1.3 A 股实证

- **有效但弱于美股**：A 股定价效率低，价值回归速度慢
- **牛市失效**：2014-2015、2019-2020 年牛市中，成长股大幅跑赢
- **EP > BP**：EP 因子在 A 股通常优于 BP（盈利信息含量更高）
- **与市值的交互**：小盘价值股效果最好，大盘价值股效果一般
- **行业差异大**：周期行业中 EP 失效（盈利波动大），消费行业中有效

### 1.4 已知陷阱

- **价值陷阱 (Value Trap)**：低 PE 可能是因为盈利即将恶化
- **财报时滞**：中国财报发布有延迟（一季报最迟 4/30，年报最迟 4/30），必须用 point-in-time 数据
- **亏损公司**：EP/BP 对亏损公司无意义，需特殊处理

---

## 2. 动量与反转因子 (Momentum & Reversal)

### 2.1 定义与经济逻辑

- **动量 (Momentum)**：过去涨的继续涨（趋势延续）
- **反转 (Reversal)**：过去涨的反而跌（均值回归）

经济解释：
- 动量：反应不足（投资者对新信息消化缓慢）
- 反转：过度反应（投资者对短期事件过度解读）

### 2.2 核心因子构造

| 因子 | 公式 | 说明 |
|------|------|------|
| **12-1 动量** | ret_{t-252:t-21} | 过去 12 月收益（跳过最近 1 月） |
| **1 月反转** | -ret_{t-21:t} | 过去 1 月收益取反 |
| **5 日反转** | -ret_{t-5:t} | 短期反转（A 股最强信号之一） |
| **行业调整动量** | ret_stock - ret_industry | 剥离行业共同运动 |
| **特质动量** | FF3 回归残差的累积收益 | 剥离市场/规模/价值 |

```python
# 5 日反转因子
reversal_5d = -df.groupby('stock_code')['close'].pct_change(5)

# 12-1 动量因子（跳过最近 21 天）
mom_12_1 = df.groupby('stock_code')['close'].apply(
    lambda x: x.shift(21) / x.shift(252) - 1
)
```

### 2.3 A 股实证（与美股的关键差异）

| 特征 | A 股 | 美股 |
|------|------|------|
| **短期反转 (1-5 日)** | ✅ 极强（RankIC ~5-8%） | 较弱 |
| **中期动量 (3-12 月)** | ❌ 弱或不显著 | ✅ 强（Jegadeesh-Titman） |
| **长期反转 (1-3 年)** | ✅ 存在 | ✅ 存在 |

**A 股短期反转特别强的原因**：
1. **散户占比高**（>60%交易量）→ 追涨杀跌 → 价格过度反应 → 反转
2. **T+1 制度**：日内无法止损 → 次日集中卖出 → 反转
3. **涨跌停板**：限制了单日价格发现效率 → 信息在次日继续释放

### 2.4 已知陷阱

- **中期动量在 A 股不work**：不能照搬美股 12-1 动量策略
- **反转与换手率交互**：高换手率+高收益 → 反转最强（过度投机）
- **停牌后复牌**：补涨/补跌会严重污染动量/反转信号

---

## 3. 质量因子 (Quality Factors) 🆕

### 3.1 定义与经济逻辑

高质量公司（盈利能力强、盈利稳定、财务健康）长期跑赢低质量公司。

经济解释：
- **盈利持续性**：高 ROE 公司有竞争护城河
- **错误定价**：市场低估盈利质量的持续性
- **应计异象 (Accrual Anomaly)**：高应计利润→盈利质量差→未来收益低

### 3.2 核心因子构造

#### 3.2.1 盈利能力因子

| 因子 | 公式 | 说明 |
|------|------|------|
| **ROE** | 净利润_TTM / 平均净资产 | 最核心的质量指标 |
| **ROA** | 净利润_TTM / 平均总资产 | 不受杠杆影响 |
| **Gross Margin** | (营收 - 营业成本) / 营收 | Novy-Marx (2013) 推荐 |
| **ROIC** | NOPAT / 投入资本 | 最严格的盈利质量指标 |
| **ROE 稳定性** | 1 / std(ROE_quarterly, 8Q) | 盈利波动越小质量越高 |

```python
# ROE 因子（TTM 口径）
roe = df['net_profit_ttm'] / ((df['equity'] + df['equity_prev']) / 2)

# ROE 稳定性（过去 8 个季度 ROE 标准差的倒数）
roe_stability = 1 / df.groupby('stock_code')['roe_quarterly'].rolling(8).std()
```

#### 3.2.2 应计利润因子 (Accruals Factor)

**核心原理**：净利润 = 经营现金流 + 应计利润。应计利润高→盈利中"水分"多→未来盈利质量差。

```python
# 资产负债表法（Sloan, 1996）
accruals_bs = (ΔCA - ΔCash - ΔCL + ΔSTD + ΔTP - DA) / avg_total_assets
# 其中：
# ΔCA = 流动资产变化
# ΔCash = 现金变化
# ΔCL = 流动负债变化
# ΔSTD = 短期借款变化
# ΔTP = 应付税款变化
# DA = 折旧摊销

# 现金流量表法（更简洁，推荐）
accruals_cf = (net_profit - operating_cashflow) / avg_total_assets
```

**A 股实证**：
- 应计因子 RankIC 约 2-4%，稳定有效
- **A 股特殊**：非经常性损益（政府补贴、资产处置收益）对应计因子的干扰比美股大
- **处理建议**：使用扣除非经常性损益后的净利润

#### 3.2.3 Piotroski F-Score

**定义**：9 个二元信号的加总分（0-9），分数越高财务质量越好。

| 维度 | 信号 | 条件（得 1 分） |
|------|------|-----------------|
| **盈利** | ROA | ROA > 0 |
| | ΔROA | ROA 同比上升 |
| | CFO | 经营现金流 > 0 |
| | Accrual | CFO > ROA（现金流质量好） |
| **杠杆/流动性** | ΔLeverage | 长期负债率下降 |
| | ΔLiquidity | 流动比率上升 |
| | Equity | 未增发新股 |
| **运营效率** | ΔMargin | 毛利率上升 |
| | ΔTurnover | 资产周转率上升 |

```python
def piotroski_fscore(row):
    score = 0
    score += (row['roa'] > 0)
    score += (row['roa_change'] > 0)
    score += (row['cfo'] > 0)
    score += (row['cfo'] > row['roa'] * row['total_assets'])
    score += (row['leverage_change'] < 0)
    score += (row['current_ratio_change'] > 0)
    score += (row['equity_issuance'] == 0)
    score += (row['gross_margin_change'] > 0)
    score += (row['asset_turnover_change'] > 0)
    return score
```

**A 股实证**：
- F-Score ≥ 7 的组合长期显著跑赢 F-Score ≤ 3 的组合
- 在小盘股中效果更显著（分析师覆盖少→信息不对称大）
- **组合用法**：F-Score 常与价值因子配合使用（选低估值+高质量）

### 3.3 A 股质量因子特殊考量

| 问题 | A 股特有 | 处理建议 |
|------|----------|----------|
| **财务造假风险** | A 股更突出 | 用现金流为主的指标（CFO/营收>ROE） |
| **非经常性损益** | 政府补贴频繁 | 用扣非净利润计算 ROE/ROA |
| **IPO 后业绩变脸** | 次新股盈利美化 | 上市<2年的公司单独处理 |
| **商誉减值** | 并购后遗症 | 关注商誉/净资产比率 |
| **季报频率** | 一季报/半年报/三季报/年报 | TTM 口径优于单季度 |

---

## 4. 波动率因子与特质波动率 (Volatility & IVOL) 🆕

### 4.1 波动率因子体系

| 因子 | 公式 | 说明 |
|------|------|------|
| **历史波动率** | std(daily_return, 20d) | 最简单的波动率度量 |
| **已实现波动率 (RV)** | √Σ(r_intraday²) | 日内高频数据计算 |
| **Parkinson 波动率** | 基于日内最高/最低价 | 比收盘价波动率更准确 |
| **IVOL (特质波动率)** | FF3 回归残差的标准差 | **低波异象核心因子** |
| **下行波动率** | std(min(r, 0)) | 只关注下跌风险 |

### 4.2 特质波动率 (IVOL) — A 股最重要的风险异象之一

#### 定义与构造

**IVOL (Idiosyncratic Volatility)**：个股收益中不能被市场系统因子解释的波动。

```python
import statsmodels.api as sm

def compute_ivol(stock_returns, market_factors, window=20):
    """
    Fama-French 三因子回归残差的标准差
    
    stock_returns: 个股日收益率序列
    market_factors: [MKT, SMB, HML] 日收益率
    window: 回看窗口（通常 20 天）
    """
    X = sm.add_constant(market_factors[-window:])
    y = stock_returns[-window:]
    model = sm.OLS(y, X).fit()
    ivol = model.resid.std() * np.sqrt(252)  # 年化
    return ivol
```

**简化版（实务中更常用）**：

```python
# CAPM 残差标准差（省去 SMB/HML，效果差异不大）
def compute_ivol_simple(stock_ret, market_ret, window=20):
    beta = np.cov(stock_ret[-window:], market_ret[-window:])[0, 1] / \
           np.var(market_ret[-window:])
    resid = stock_ret[-window:] - beta * market_ret[-window:]
    return resid.std() * np.sqrt(252)
```

#### 低 IVOL 异象（Low Volatility Anomaly）

**核心发现**：低特质波动率的股票未来收益**更高**。这与 CAPM 预测相反（高风险应高收益）。

**三大成因解释**：

| 理论 | 解释 | 核心论文 |
|------|------|----------|
| **彩票偏好 (Lottery Preference)** | 散户偏好高波动"彩票股"→推高定价→未来收益低 | Bali, Cakici, Whitelaw (2011) |
| **杠杆约束 (Leverage Constraint)** | 投资者不能充分加杠杆→通过买高beta股替代→高beta被高估 | Frazzini & Pedersen (2014) |
| **套利限制 (Limits to Arbitrage)** | 高IVOL = 高特质风险 = 套利成本高 → 错误定价难以纠正 | Stambaugh, Yu, Yuan (2015) |

#### A 股 IVOL 实证

| 特征 | A 股表现 |
|------|----------|
| **低 IVOL 效应** | ✅ 显著存在，低 IVOL 组 vs 高 IVOL 组年化价差 8-15% |
| **散户放大效应** | A 股散户占比高 → 彩票偏好更强 → IVOL 效应比美股更显著 |
| **与换手率的关系** | 高 IVOL ≈ 高换手率，两者有 0.5-0.7 的正相关 |
| **行业分布** | 高 IVOL 集中在题材股/概念股/次新股 |
| **牛市中减弱** | 2014-2015、2020 年牛市中低波效应显著减弱 |
| **做空限制影响** | A 股融券困难 → 高 IVOL 股票被高估难以纠正 → 效应持续 |

#### 构造建议

1. 回看窗口：20 日（短）或 60 日（稳），建议同时计算对比
2. 基准模型：CAPM 残差 vs FF3 残差差异不大，实务用 CAPM 即可
3. **必须行业中性化**：IVOL 有明显行业偏好（科技/医药偏高）
4. **必须市值中性化**：小盘股 IVOL 天然偏高
5. 与换手率因子有较高相关性，合成时需正交化

### 4.3 已实现波动率分解

```python
# 连续波动率（双幂变差）
BV_t = (π/2) * Σ |r_i| * |r_{i-1}|

# 跳跃波动率
JV_t = max(RV_t - BV_t, 0)
```

**因子含义**：跳跃波动率高→信息驱动的价格变动→选股信号。

---

## 5. 流动性因子与换手率因子 (Liquidity & Turnover) 🆕

### 5.1 流动性因子体系

| 因子 | 公式 | 经济含义 |
|------|------|----------|
| **换手率 (Turnover)** | 成交量 / 流通股本 | 最直观的流动性度量 |
| **Amihud ILLIQ** | \|r_t\| / volume_t | 单位成交额引起的价格变动，越大越不流动 |
| **SemiILLIQ** | 分开计算上涨日/下跌日的 ILLIQ | 区分买方/卖方冲击 |
| **Kyle's Lambda** | 回归系数 Δp = λ × OFI | 每单位订单流的价格影响 |
| **Roll Spread** | 2√(-Cov(Δp_t, Δp_{t-1})) | 隐含买卖价差 |
| **Bid-Ask Spread** | (ask - bid) / mid | 直接的流动性成本 |
| **Zero Return Days** | 零收益天数 / 总天数 | 无交易活跃度度量 |

### 5.2 换手率因子详细构造

#### 四种变体

```python
# 变体 1：日均换手率（最基础）
turnover_20d = df.groupby('stock_code')['turnover_rate'].rolling(20).mean()

# 变体 2：对数换手率（处理右偏分布）
log_turnover_20d = np.log(turnover_20d + 1e-8)

# 变体 3：异常换手率（相对自身历史）
abnormal_turnover = turnover_20d / turnover_60d - 1
# 短期换手率相对长期的偏离 → 捕捉突然放量/缩量

# 变体 4：标准化换手率（行业中性化后）
std_turnover = df.groupby(['date', 'industry'])['log_turnover_20d'] \
    .transform(lambda x: (x - x.mean()) / x.std())
```

#### Amihud ILLIQ 非流动性指标

```python
# 标准 Amihud ILLIQ
illiq_t = abs(return_t) / dollar_volume_t  # 单日
ILLIQ_20d = mean(illiq_t, 20d) * 1e6       # 20 日均值（乘以 10^6 便于阅读）

# SemiILLIQ（区分方向）
ILLIQ_up = mean(abs(r_t) / vol_t, for r_t > 0)   # 上涨日的 ILLIQ → 买方冲击
ILLIQ_down = mean(abs(r_t) / vol_t, for r_t < 0)  # 下跌日的 ILLIQ → 卖方冲击
# ILLIQ_down > ILLIQ_up → 卖压大于买压
```

### 5.3 低换手率效应：A 股最强单因子之一

**核心发现**：低换手率股票长期显著跑赢高换手率股票。

**效应强度**：
- 20 日换手率分 10 组，低换手率组 vs 高换手率组年化价差 **15-25%**
- RankIC 约 **5-8%**（远超多数传统因子）
- 在 A 股中，换手率因子的有效性**长期稳定**，是少数"不太衰减"的因子之一

**三重经济机理**：

| 机理 | 解释 | 学术来源 |
|------|------|----------|
| **流动性溢价** | 低流动性资产要求更高收益补偿 → 低换手率→流动性差→溢价 | Amihud (2002) |
| **投资者关注度** | 低换手率≈低关注度→被忽略→定价偏低 | Barber & Odean (2008) |
| **散户过度交易** | 高换手率多为散户驱动→非理性交易→长期亏损 | A 股特有现象 |

**A 股特殊增强因素**：
1. **散户交易量占比 >60%**：散户偏好高换手率（频繁交易）→ 高换手率股票被系统性高估
2. **融券限制**：高换手率+高估的股票无法被做空纠正
3. **题材炒作文化**：炒作期换手率飙升 → 炒作结束后下跌 → 高换手率→低未来收益

### 5.4 换手率因子使用要点

| 要点 | 说明 |
|------|------|
| **必须市值中性化** | 小盘股天然换手率高，不中性化会变成伪市值因子 |
| **行业中性化** | 不同行业换手率中枢不同（科技>银行） |
| **与 IVOL 正交化** | 换手率与 IVOL 相关 ~0.5-0.7，合成时需正交化 |
| **对数变换** | 换手率右偏严重，建议用 log(turnover) |
| **短期异常换手更有效** | abnormal_turnover（短/长比）比绝对换手率更有增量 |
| **与动量/反转交互** | 高换手率+高收益→反转概率极大（过度投机信号） |

---

## 6. 成长因子 (Growth Factors)

### 6.1 核心因子

| 因子 | 公式 | 说明 |
|------|------|------|
| **营收增长率** | (revenue_TTM / revenue_TTM_prev) - 1 | 最稳定的成长指标 |
| **利润增长率** | (net_profit_TTM / net_profit_TTM_prev) - 1 | 波动大，需去极值 |
| **ROE 变化** | ROE_Q - ROE_Q_prev | 盈利趋势 |
| **SUE (标准化预期外盈利)** | (EPS_actual - EPS_expected) / std(EPS) | 盈利惊喜因子 |

### 6.2 A 股实证

- 成长因子在 A 股**周期性有效**：成长股行情中有效，价值股行情中失效
- **高增长陷阱**：超高增长率（>100%）往往不可持续，需非线性处理
- 建议：用 ROE 变化（趋势）替代绝对增长率（水平）

---

## 7. 情绪因子 (Sentiment Factors)

### 7.1 核心因子

| 因子 | 数据来源 | 说明 |
|------|----------|------|
| **分析师一致预期变化** | Wind/iFinD | 预期上调→利好信号 |
| **分析师覆盖度** | 研报数量 | 低覆盖→信息不对称→alpha 机会 |
| **融资融券余额变化** | 交易所 | 融资买入→看多信号 |
| **北向资金** | 沪深港通 | 外资流入→利好 |
| **舆情/新闻情绪** | NLP处理新闻/社交 | 情绪极端→反转信号 |

### 7.2 A 股实证

- 分析师一致预期调整是 A 股**较强的中频信号**
- 北向资金因子短期有效，但近年来有所衰减
- 散户情绪指标（如搜索热度、论坛活跃度）做**反向指标**更有效

---

## 8. 高频因子 (High-Frequency Factors)

### 8.1 八大类高频因子

| 类别 | 典型因子 | 经济逻辑 | 数据频率 |
|------|----------|----------|----------|
| **日内动量** | 开盘收益率、尾盘收益率、第一小时收益率 | 知情交易者在特定时段交易 | 分钟 |
| **日内波动率** | RV、已实现偏度 (RS)、已实现峰度 (RK) | 波动率非对称性反映信息流 | 分钟 |
| **量价关系** | VWAP 偏离度、成交额加权收益率 | 量价背离信号 | 分钟 |
| **订单流 (OFI)** | 订单流不平衡度、净买入强度 | 买卖压力→价格变动 | Tick |
| **大单因子** | 大单净流入、大单占比 | 知情交易者以大单进场 | 分钟 |
| **波动率分解** | 连续波动率 vs 跳跃波动率 | 跳跃因子捕捉突发信息 | 分钟 |
| **价格影响** | Amihud ILLIQ、Kyle Lambda | 每单位成交量的价格影响 | 日/分钟 |
| **微观结构** | 买卖价差、报价深度、订单簿不平衡 | 微观结构信息 | Tick |

### 8.2 OFI 订单流不平衡

```python
OFI_t = Σ (buy_volume_i - sell_volume_i)  # 日内汇总

# 变体
weighted_OFI = Σ (buy_vol_i - sell_vol_i) * abs(price_change_i)  # 价格加权
decay_OFI = Σ (buy_vol_i - sell_vol_i) * exp(-λ(T-i))           # 指数衰减
std_OFI = OFI / total_volume                                      # 标准化
```

### 8.3 大单因子

```python
# 大单：单笔成交额 > 阈值（如 50 万元）
big_order_net = big_buy_amount - big_sell_amount
big_order_ratio = big_order_amount / total_amount
```

### 8.4 日内动量因子

```python
first_hour_return = price_10_30 / price_09_30 - 1
last_30min_return = close / price_14_30 - 1
overnight_return = open / prev_close - 1
```

**A 股已知规律**：
- 隔夜收益率与次日收益负相关（短期反转）
- 尾盘大幅拉升→次日易回调
- 第一小时收益率信息量最大（信息不对称最强时段）

### 8.5 高频因子研究注意事项

- **数据量巨大**：Parquet/Arrow 格式 + 增量计算
- **过拟合风险极高**：分钟级数据自由度多
- **换手率高→交易成本是核心约束**
- **A 股 T+1 制度**：日内信号必须考虑隔夜风险
- **信号衰减快**：需频繁调仓（日频或 T+1）
