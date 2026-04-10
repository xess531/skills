# 算子体系 — Operators

> WQ101 + GTJA191 共用算子定义 + 191 新增算子

---

## 一、输入变量

### 1.1 通用变量

| 变量 | WQ101 写法 | GTJA191 写法 | 含义 | 备注 |
|------|-----------|-------------|------|------|
| 开盘价 | `open` | `OPEN` | 日开盘价 | 需前复权 |
| 最高价 | `high` | `HIGH` | 日最高价 | 需前复权 |
| 最低价 | `low` | `LOW` | 日最低价 | 需前复权 |
| 收盘价 | `close` | `CLOSE` | 日收盘价 | 需前复权 |
| 成交量 | `volume` | `VOLUME` / `VOL` | 日成交量（手） | |
| VWAP | `vwap` | `VWAP` | 成交量加权平均价 | = AMOUNT / VOLUME |
| 日收益率 | `returns` | `RET` | close-to-close | = CLOSE/DELAY(CLOSE,1) - 1 |

### 1.2 WQ101 特有变量

| 变量 | 含义 | 备注 |
|------|------|------|
| `cap` | 市值 | market_cap |
| `adv{d}` | d 日平均成交额 | 如 adv5, adv10, adv20, adv60, adv120, adv180 |
| `IndClass` | 行业分类 | sector / industry / subindustry |

### 1.3 GTJA191 特有变量

| 变量 | 含义 | 备注 |
|------|------|------|
| `AMOUNT` | 成交额（元） | WQ101 没有，A 股特色 |
| `BANCHMARKINDEXCLOSE` | 基准指数收盘价 | 通常用中证 500 |
| `BANCHMARKINDEXOPEN` | 基准指数开盘价 | 通常用中证 500 |

### 1.4 GTJA191 衍生中间变量

| 变量 | 定义 | 使用因子 |
|------|------|----------|
| `DTM` | `(OPEN<=DELAY(OPEN,1)) ? 0 : MAX(HIGH-OPEN, OPEN-DELAY(OPEN,1))` | Alpha#49~#51 |
| `DBM` | `(OPEN>=DELAY(OPEN,1)) ? 0 : MAX(OPEN-LOW, OPEN-DELAY(OPEN,1))` | Alpha#49~#51 |
| `TR` | `MAX(MAX(HIGH-LOW, ABS(HIGH-DELAY(CLOSE,1))), ABS(LOW-DELAY(CLOSE,1)))` | Alpha#172, #186 |
| `HD` | `HIGH - DELAY(HIGH, 1)` | Alpha#172, #186 |
| `LD` | `DELAY(LOW, 1) - LOW` | Alpha#172, #186 |
| `MKT/SMB/HML` | Fama-French 三因子 | Alpha#30 |

---

## 二、共用算子（101 + 191 均使用）

### 2.1 时序算子

| 算子 | WQ101 写法 | GTJA191 写法 | 定义 | 典型参数 |
|------|-----------|-------------|------|----------|
| 延迟 | `delay(x, d)` | `DELAY(X, d)` | x 在 d 天前的值 | d=1,5,10 |
| 差分 | `delta(x, d)` | `DELTA(X, d)` | x(today) - x(d days ago) | d=1,5 |
| 时序最小 | `ts_min(x, d)` | `TSMIN(X, d)` | 过去 d 天 x 的最小值 | d=5,10,20 |
| 时序最大 | `ts_max(x, d)` | `TSMAX(X, d)` | 过去 d 天 x 的最大值 | d=5,10,20 |
| 时序排名 | `ts_rank(x, d)` | `TSRANK(X, d)` | 过去 d 天 x 的时序排名（百分位） | d=5,10 |
| 求和 | `sum(x, d)` | `SUM(X, d)` | 过去 d 天累计求和 | d=5,10,20 |
| 均值 | — | `MEAN(X, d)` | 过去 d 天均值 = SUM/d | d=5,10,20 |
| 标准差 | `stddev(x, d)` | `STD(X, d)` | 过去 d 天标准差 | d=5,10,20 |
| 相关系数 | `correlation(x, y, d)` | `CORR(X, Y, d)` | 过去 d 天 Pearson 相关系数 | d=5,6,10 |
| 协方差 | `covariance(x, y, d)` | `COVIANCE(X, Y, d)` | 过去 d 天协方差 | d=5,10 |
| 连乘 | `product(x, d)` | `PROD(X, d)` | 过去 d 天累乘 | d=5,10 |
| 线性衰减 | `decay_linear(x, d)` | `DECAYLINEAR(X, d)` | 线性加权移动平均（近期权重大） | d=5,10 |

### 2.2 截面算子

| 算子 | WQ101 写法 | GTJA191 写法 | 定义 |
|------|-----------|-------------|------|
| 截面排名 | `rank(x)` | `RANK(X)` | 当日所有股票 x 值的截面百分位排名 ∈ (0, 1] |
| 截面标准化 | `scale(x, a=1)` | — | a × x / Σ\|x\| |
| 符号幂 | `SignedPower(x, a)` | — | sign(x) × \|x\|^a |

### 2.3 基础运算

| 算子 | 定义 |
|------|------|
| `abs(x)` / `ABS(X)` | 绝对值 |
| `log(x)` / `LOG(X)` | 自然对数 |
| `sign(x)` / `SIGN(X)` | 符号函数 (+1, -1, 0) |
| `min(x, y)` / `MIN(X, Y)` | 逐元素取较小值 |
| `max(x, y)` / `MAX(X, Y)` | 逐元素取较大值 |
| `x ? y : z` | 三元条件运算 |

---

## 三、191 新增算子

### 3.1 SMA — 中国式指数加权移动平均

```
SMA(X, N, M)
Y(t) = (X(t) * M + Y(t-1) * (N - M)) / N
```

- α = M/N
- **与 pandas ewm 不同**，需要手动递推
- 大量 GTJA191 因子使用此算子（如 RSI/KDJ 类）
- 典型参数：`SMA(X, 20, 1)`, `SMA(X, 13, 2)`, `SMA(X, 27, 2)`

### 3.2 WMA — 加权移动平均

```
WMA(X, N)
权重 = [1, 2, 3, ..., N] / sum(1..N)
```

### 3.3 REGBETA — 回归斜率

```
REGBETA(Y, X, N)
过去 N 天 Y 对 X 的线性回归斜率
```

- 当 X = SEQUENCE(N) 时，等价于价格趋势强度
- 使用因子：GTJA Alpha#21, #30, #116, #147, #149

### 3.4 REGRESI — 多元回归残差

```
REGRESI(Y, X1, X2, ..., N)
过去 N 天 Y 对 (X1, X2, ...) 的多元回归残差
```

- 使用因子：GTJA Alpha#30（Fama-French 三因子残差）

### 3.5 COUNT — 条件计数

```
COUNT(COND, N)
过去 N 天满足条件 COND 的天数
```

- 使用因子：GTJA Alpha#53, #58, #75, #182

### 3.6 SUMIF — 条件求和

```
SUMIF(X, N, COND)
过去 N 天中满足条件 COND 时 X 值的累计求和
```

- 使用因子：GTJA Alpha#144, #190

### 3.7 FILTER — 条件过滤

```
FILTER(X, COND)
仅保留满足 COND 的 X 值
```

- 使用因子：GTJA Alpha#149

### 3.8 HIGHDAY / LOWDAY — 极值距今天数

```
HIGHDAY(X, N): 过去 N 天内 X 最高值距今天数
LOWDAY(X, N): 过去 N 天内 X 最低值距今天数
```

- 使用因子：GTJA Alpha#103, #133, #177

### 3.9 SUMAC — 累积求和

```
SUMAC(X, N)
= X(t) + X(t-1) + ... + X(t-N+1)  的递归版本
```

### 3.10 SEQUENCE — 序列生成

```
SEQUENCE(N)
生成 [1, 2, 3, ..., N] 序列，通常用于 REGBETA 的 X 变量
```

### 3.11 IndNeutralize — 行业中性化（WQ101 特有）

```
indneutralize(x, IndClass.{level})
对 x 在行业内去均值，level = sector / industry / subindustry
```

- WQ101 中 21 个因子使用此算子（Alpha#048, #058, #059, #063, #067, #069, #070, #076, #079, #080, #081, #082, #087, #089, #090, #091, #093, #097, #100）
- 这些因子通常标记为"未实现"，因为需要行业分类数据

---

## 四、算子等价对照表

| 功能 | WQ101 | GTJA191 | 是否等价 |
|------|-------|---------|---------|
| 截面排名 | `rank(x)` | `RANK(X)` | ✅ 等价 |
| 延迟 | `delay(x,d)` | `DELAY(X,d)` | ✅ 等价 |
| 差分 | `delta(x,d)` | `DELTA(X,d)` | ✅ 等价 |
| 时序排名 | `ts_rank(x,d)` | `TSRANK(X,d)` | ✅ 等价 |
| 时序最大/小 | `ts_max/ts_min` | `TSMAX/TSMIN` | ✅ 等价 |
| 时序最大位置 | `ts_argmax(x,d)` | `HIGHDAY(X,d)` | ⚠️ 方向相反：argmax 返回位置，HIGHDAY 返回距今天数 |
| 时序最小位置 | `ts_argmin(x,d)` | `LOWDAY(X,d)` | ⚠️ 同上 |
| 滚动求和 | `sum(x,d)` | `SUM(X,d)` | ✅ 等价 |
| 均值 | `sum(x,d)/d` | `MEAN(X,d)` | ✅ 等价 |
| 标准差 | `stddev(x,d)` | `STD(X,d)` | ✅ 等价 |
| 相关系数 | `correlation(x,y,d)` | `CORR(X,Y,d)` | ✅ 等价 |
| 线性衰减 | `decay_linear(x,d)` | `DECAYLINEAR(X,d)` | ✅ 等价 |
| 指数加权 | — | `SMA(X,N,M)` | 191 独有 |
| 回归斜率 | — | `REGBETA(Y,X,N)` | 191 独有 |
| 条件计数 | — | `COUNT(COND,N)` | 191 独有 |
| 条件求和 | — | `SUMIF(X,N,COND)` | 191 独有 |
| 行业中性化 | `indneutralize` | — | 101 独有 |
