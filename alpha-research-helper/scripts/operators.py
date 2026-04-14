"""
Alpha Factor Library — 算子实现
================================
WQ101 + GTJA191 共用算子和191新增算子的 pandas 实现。

数据格式约定:
- 所有输入均为 pandas DataFrame 或 Series
- DataFrame: index=date, columns=stock_code
- 截面算子沿 axis=1 操作（同一天的所有股票）
- 时序算子沿 axis=0 操作（同一只股票的历史）

依赖: numpy, pandas, scipy
"""

import numpy as np
import pandas as pd
from scipy.stats import rankdata


# ============================================================
#  一、时序算子 (Time-Series Operators)
# ============================================================

def delay(df, d=1):
    """延迟 d 天: x(t-d)"""
    return df.shift(d)


def delta(df, d=1):
    """差分: x(t) - x(t-d)"""
    return df.diff(d)


def ts_sum(df, d=10):
    """过去 d 天求和"""
    return df.rolling(d, min_periods=d).sum()


def ts_mean(df, d=10):
    """过去 d 天均值"""
    return df.rolling(d, min_periods=d).mean()


def ts_std(df, d=10):
    """过去 d 天标准差 (ddof=1)"""
    return df.rolling(d, min_periods=d).std()


def ts_min(df, d=10):
    """过去 d 天最小值"""
    return df.rolling(d, min_periods=d).min()


def ts_max(df, d=10):
    """过去 d 天最大值"""
    return df.rolling(d, min_periods=d).max()


def ts_argmin(df, d=10):
    """过去 d 天最小值出现位置 (1-based, 1=最早)"""
    return df.rolling(d, min_periods=d).apply(
        lambda x: np.argmin(x) + 1, raw=True
    )


def ts_argmax(df, d=10):
    """过去 d 天最大值出现位置 (1-based, 1=最早)"""
    return df.rolling(d, min_periods=d).apply(
        lambda x: np.argmax(x) + 1, raw=True
    )


def ts_rank(df, d=10):
    """过去 d 天时序排名 (百分位)"""
    def _rank_pct(x):
        return rankdata(x)[-1] / len(x)
    return df.rolling(d, min_periods=d).apply(_rank_pct, raw=True)


def ts_product(df, d=10):
    """过去 d 天累乘"""
    return df.rolling(d, min_periods=d).apply(np.prod, raw=True)


def ts_corr(x, y, d=10):
    """过去 d 天滚动 Pearson 相关系数"""
    return x.rolling(d, min_periods=d).corr(y)


def ts_cov(x, y, d=10):
    """过去 d 天滚动协方差"""
    return x.rolling(d, min_periods=d).cov(y)


def decay_linear(df, d=10):
    """线性衰减加权移动平均 (权重: [1, 2, ..., d] / sum)"""
    weights = np.arange(1, d + 1, dtype=float)
    weights /= weights.sum()
    return df.rolling(d, min_periods=d).apply(
        lambda x: np.dot(x, weights), raw=True
    )


# ============================================================
#  二、GTJA191 新增时序算子
# ============================================================

def sma_cn(df, n, m):
    """
    中国式 SMA (指数加权移动平均)
    Y(t) = (X(t) * M + Y(t-1) * (N - M)) / N

    注意: 与 pandas ewm 不同，必须手动递推。

    Parameters
    ----------
    df : DataFrame or Series
    n : int - 周期
    m : int - 权重参数
    """
    alpha = m / n
    result = df.copy().astype(float)

    if isinstance(df, pd.DataFrame):
        for i in range(1, len(result)):
            result.iloc[i] = alpha * df.iloc[i] + (1 - alpha) * result.iloc[i - 1]
    else:
        for i in range(1, len(result)):
            result.iloc[i] = alpha * df.iloc[i] + (1 - alpha) * result.iloc[i - 1]
    return result


def wma(df, n):
    """加权移动平均 (权重: [1, 2, ..., N] / sum)"""
    weights = np.arange(1, n + 1, dtype=float)
    return df.rolling(n, min_periods=n).apply(
        lambda x: np.average(x, weights=weights), raw=True
    )


def regbeta(y, x=None, n=20):
    """
    滚动回归斜率

    Parameters
    ----------
    y : Series or DataFrame - 因变量
    x : Series, DataFrame or None - 自变量 (None 则用 SEQUENCE)
    n : int - 回归窗口

    Returns
    -------
    与 y 同形状的回归斜率
    """
    def _slope(y_arr):
        x_arr = np.arange(1, len(y_arr) + 1, dtype=float)
        try:
            return np.polyfit(x_arr, y_arr, 1)[0]
        except (np.linalg.LinAlgError, ValueError):
            return np.nan

    if x is None:
        # SEQUENCE 模式: y 对 [1,2,...,N] 回归
        return y.rolling(n, min_periods=n).apply(_slope, raw=True)
    else:
        # 双变量模式: y 对 x 回归
        def _slope_xy(args):
            mid = len(args) // 2
            y_arr = args[:mid]
            x_arr = args[mid:]
            try:
                return np.polyfit(x_arr, y_arr, 1)[0]
            except (np.linalg.LinAlgError, ValueError):
                return np.nan

        combined = pd.concat([y, x], axis=1)
        return combined.rolling(n, min_periods=n).apply(
            lambda row: _slope_xy(row.values), raw=True
        )


def count(cond, n):
    """条件计数: 过去 n 天满足条件的天数"""
    return cond.astype(float).rolling(n, min_periods=n).sum()


def sumif(x, n, cond):
    """条件求和: 过去 n 天中满足条件时 x 值的累计"""
    return (x * cond.astype(float)).rolling(n, min_periods=n).sum()


def highday(x, n):
    """过去 n 天内最高值距今天数"""
    return x.rolling(n, min_periods=n).apply(
        lambda arr: n - 1 - np.argmax(arr), raw=True
    )


def lowday(x, n):
    """过去 n 天内最低值距今天数"""
    return x.rolling(n, min_periods=n).apply(
        lambda arr: n - 1 - np.argmin(arr), raw=True
    )


def sequence(n):
    """生成 [1, 2, ..., N] 序列"""
    return np.arange(1, n + 1, dtype=float)


# ============================================================
#  三、截面算子 (Cross-Sectional Operators)
# ============================================================

def cs_rank(df):
    """截面排名, 归一化到 (0, 1]"""
    if isinstance(df, pd.DataFrame):
        return df.rank(axis=1, pct=True)
    else:
        return df.rank(pct=True)


def scale(df, k=1):
    """截面标准化: k * x / sum(|x|)"""
    if isinstance(df, pd.DataFrame):
        return df.mul(k).div(df.abs().sum(axis=1), axis=0)
    else:
        return k * df / df.abs().sum()


def signed_power(df, exp):
    """sign(x) * |x|^exp"""
    return np.sign(df) * np.abs(df) ** exp


# ============================================================
#  四、GTJA191 衍生中间变量
# ============================================================

def calc_dtm(open_price, high):
    """
    DTM = (OPEN<=DELAY(OPEN,1)) ? 0 : MAX(HIGH-OPEN, OPEN-DELAY(OPEN,1))
    """
    prev_open = delay(open_price, 1)
    cond = open_price > prev_open
    val = pd.DataFrame(
        np.maximum(high - open_price, open_price - prev_open),
        index=open_price.index, columns=open_price.columns
    )
    return val.where(cond, 0.0)


def calc_dbm(open_price, low):
    """
    DBM = (OPEN>=DELAY(OPEN,1)) ? 0 : MAX(OPEN-LOW, OPEN-DELAY(OPEN,1))
    """
    prev_open = delay(open_price, 1)
    cond = open_price < prev_open
    val = pd.DataFrame(
        np.maximum(open_price - low, open_price - prev_open),
        index=open_price.index, columns=open_price.columns
    )
    return val.where(cond, 0.0)


def calc_tr(high, low, close):
    """
    TR = MAX(MAX(HIGH-LOW, ABS(HIGH-DELAY(CLOSE,1))), ABS(LOW-DELAY(CLOSE,1)))
    """
    prev_close = delay(close, 1)
    return pd.DataFrame(
        np.maximum(
            np.maximum(high - low, np.abs(high - prev_close)),
            np.abs(low - prev_close)
        ),
        index=high.index, columns=high.columns
    )


def calc_hd(high):
    """HD = HIGH - DELAY(HIGH, 1)"""
    return delta(high, 1)


def calc_ld(low):
    """LD = DELAY(LOW, 1) - LOW"""
    return delay(low, 1) - low


# ============================================================
#  五、辅助函数
# ============================================================

def ind_neutralize(factor, industry):
    """
    行业中性化 (去均值/标准化)

    Parameters
    ----------
    factor : DataFrame (index=date, columns=stock)
    industry : Series or dict (stock -> industry_code)
    """
    if isinstance(industry, pd.Series):
        ind_map = industry
    else:
        ind_map = pd.Series(industry)

    result = factor.copy()
    for date in factor.index:
        row = factor.loc[date]
        for ind in ind_map.unique():
            mask = ind_map == ind
            stocks_in_ind = mask[mask].index.intersection(row.index)
            if len(stocks_in_ind) > 1:
                vals = row[stocks_in_ind]
                mean = vals.mean()
                std = vals.std()
                if std > 1e-8:
                    result.loc[date, stocks_in_ind] = (vals - mean) / std
                else:
                    result.loc[date, stocks_in_ind] = 0.0
    return result


def winsorize(df, lower=0.01, upper=0.99):
    """截面截断 (Q1%-Q99%)"""
    if isinstance(df, pd.DataFrame):
        q_low = df.quantile(lower, axis=1)
        q_high = df.quantile(upper, axis=1)
        return df.clip(q_low, q_high, axis=0)
    else:
        q_low = df.quantile(lower)
        q_high = df.quantile(upper)
        return df.clip(q_low, q_high)


# ============================================================
#  六、别名映射 (兼容两套命名)
# ============================================================

# WQ101 命名 → 函数
correlation = ts_corr
covariance = ts_cov
stddev = ts_std
product = ts_product
rank = cs_rank

# GTJA191 命名 → 函数 (大写别名)
DELAY = delay
DELTA = delta
SUM = ts_sum
MEAN = ts_mean
STD = ts_std
CORR = ts_corr
TSMAX = ts_max
TSMIN = ts_min
TSRANK = ts_rank
RANK = cs_rank
DECAYLINEAR = decay_linear
SMA = sma_cn
WMA = wma
REGBETA = regbeta
COUNT = count
SUMIF = sumif
HIGHDAY = highday
LOWDAY = lowday
