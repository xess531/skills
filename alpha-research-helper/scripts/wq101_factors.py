"""
WorldQuant 101 Formulaic Alphas — Python 实现
==============================================
全部 101 个因子的 pandas 向量化实现。

数据格式约定:
- 输入: 包含以下 key 的 dict 或命名空间:
    open, high, low, close, volume, vwap, returns
    (可选) cap (市值), industry (行业分类)
- 每个 key 对应一个 DataFrame: index=date, columns=stock_code
- 输出: 与输入同形状的 DataFrame (因子值)

参考: Kakushadze Z. (2016). "101 Formulaic Alphas". Wilmott Magazine.
开源复用: github.com/popbo/alphas (MIT-like), 经过校对和补全。

依赖: numpy, pandas, scipy, operators.py (同目录)
"""

import numpy as np
import pandas as pd
from numpy import abs as np_abs, log, sign
from scipy.stats import rankdata

# 导入同目录算子 (skill 加载时需确保 path 正确)
try:
    from .operators import (
        delay, delta, ts_sum, ts_mean, ts_std, ts_min, ts_max,
        ts_argmin, ts_argmax, ts_rank, ts_product, ts_corr, ts_cov,
        decay_linear, cs_rank, scale, signed_power, ind_neutralize, winsorize
    )
except ImportError:
    from operators import (
        delay, delta, ts_sum, ts_mean, ts_std, ts_min, ts_max,
        ts_argmin, ts_argmax, ts_rank, ts_product, ts_corr, ts_cov,
        decay_linear, cs_rank, scale, signed_power, ind_neutralize, winsorize
    )


# ============================================================
#  辅助别名 (对齐论文命名)
# ============================================================

rank = cs_rank
correlation = ts_corr
covariance = ts_cov
stddev = ts_std
product = ts_product


def _safe_corr(x, y, d):
    """相关系数: 处理 inf/nan"""
    r = correlation(x, y, d)
    return r.replace([np.inf, -np.inf], 0).fillna(0)


def _adv(volume, d):
    """Average Daily Volume"""
    return ts_mean(volume, d)


def _safe_div(a, b, fill=0.0001):
    """安全除法: 避免除零"""
    b_safe = b.replace(0, fill)
    return a / b_safe


# ============================================================
#  WQ101 因子类
# ============================================================

class WQ101Factors:
    """
    WorldQuant 101 Formulaic Alphas

    用法:
        factors = WQ101Factors(open=df_open, high=df_high, low=df_low,
                               close=df_close, volume=df_volume,
                               vwap=df_vwap, returns=df_returns)
        alpha1 = factors.alpha001()
        all_factors = factors.compute_all()  # 返回 dict
    """

    def __init__(self, open, high, low, close, volume, vwap, returns,
                 cap=None, industry=None):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.vwap = vwap
        self.returns = returns
        self.cap = cap          # 市值 (部分因子需要)
        self.industry = industry  # 行业分类 (IndNeutralize 需要)

    # ----------------------------------------------------------
    # Alpha#001 [反转][波动率]
    # rank(ts_argmax(SignedPower(((returns < 0) ? stddev(returns,20) : close), 2.), 5)) - 0.5
    # ----------------------------------------------------------
    def alpha001(self):
        inner = self.close.copy()
        inner[self.returns < 0] = stddev(self.returns, 20)
        return rank(ts_argmax(inner ** 2, 5)) - 0.5

    # ----------------------------------------------------------
    # Alpha#002 [量价]
    # -1 * correlation(rank(delta(log(volume),2)), rank(((close-open)/open)), 6)
    # ----------------------------------------------------------
    def alpha002(self):
        return -1 * _safe_corr(rank(delta(log(self.volume), 2)),
                               rank((self.close - self.open) / self.open), 6)

    # ----------------------------------------------------------
    # Alpha#003 [量价]
    # -1 * correlation(rank(open), rank(volume), 10)
    # ----------------------------------------------------------
    def alpha003(self):
        return -1 * _safe_corr(rank(self.open), rank(self.volume), 10)

    # ----------------------------------------------------------
    # Alpha#004 [反转]
    # -1 * ts_rank(rank(low), 9)
    # ----------------------------------------------------------
    def alpha004(self):
        return -1 * ts_rank(rank(self.low), 9)

    # ----------------------------------------------------------
    # Alpha#005 [形态][流动性]
    # rank((open - (sum(vwap,10)/10))) * (-1 * abs(rank((close - vwap))))
    # ----------------------------------------------------------
    def alpha005(self):
        return rank(self.open - ts_mean(self.vwap, 10)) * (-1 * np.abs(rank(self.close - self.vwap)))

    # ----------------------------------------------------------
    # Alpha#006 [量价]
    # -1 * correlation(open, volume, 10)
    # ----------------------------------------------------------
    def alpha006(self):
        return -1 * _safe_corr(self.open, self.volume, 10)

    # ----------------------------------------------------------
    # Alpha#007 [动量][流动性]
    # (adv20 < volume) ? ((-1*ts_rank(abs(delta(close,7)),60))*sign(delta(close,7))) : -1
    # ----------------------------------------------------------
    def alpha007(self):
        adv20 = _adv(self.volume, 20)
        alpha = -1 * ts_rank(np.abs(delta(self.close, 7)), 60) * sign(delta(self.close, 7))
        alpha[adv20 >= self.volume] = -1
        return alpha

    # ----------------------------------------------------------
    # Alpha#008 [反转]
    # -1 * rank(((sum(open,5)*sum(returns,5)) - delay((sum(open,5)*sum(returns,5)),10)))
    # ----------------------------------------------------------
    def alpha008(self):
        return -1 * rank(ts_sum(self.open, 5) * ts_sum(self.returns, 5) -
                         delay(ts_sum(self.open, 5) * ts_sum(self.returns, 5), 10))

    # ----------------------------------------------------------
    # Alpha#009 [动量][反转]
    # (0<ts_min(delta(close,1),5)) ? delta(close,1) :
    #   ((ts_max(delta(close,1),5)<0) ? delta(close,1) : -1*delta(close,1))
    # ----------------------------------------------------------
    def alpha009(self):
        d = delta(self.close, 1)
        cond1 = ts_min(d, 5) > 0
        cond2 = ts_max(d, 5) < 0
        alpha = -1 * d
        alpha[cond1 | cond2] = d
        return alpha

    # ----------------------------------------------------------
    # Alpha#010 [动量][反转]
    # rank版的 alpha009 (4天窗口)
    # ----------------------------------------------------------
    def alpha010(self):
        d = delta(self.close, 1)
        cond1 = ts_min(d, 4) > 0
        cond2 = ts_max(d, 4) < 0
        alpha = -1 * d
        alpha[cond1 | cond2] = d
        return rank(alpha)

    # ----------------------------------------------------------
    # Alpha#011 [量价][形态]
    # (rank(ts_max((vwap-close),3)) + rank(ts_min((vwap-close),3))) * rank(delta(volume,3))
    # ----------------------------------------------------------
    def alpha011(self):
        return (rank(ts_max(self.vwap - self.close, 3)) +
                rank(ts_min(self.vwap - self.close, 3))) * rank(delta(self.volume, 3))

    # ----------------------------------------------------------
    # Alpha#012 [量价][反转]
    # sign(delta(volume,1)) * (-1 * delta(close,1))
    # ----------------------------------------------------------
    def alpha012(self):
        return sign(delta(self.volume, 1)) * (-1 * delta(self.close, 1))

    # ----------------------------------------------------------
    # Alpha#013 [量价]
    # -1 * rank(covariance(rank(close), rank(volume), 5))
    # ----------------------------------------------------------
    def alpha013(self):
        return -1 * rank(covariance(rank(self.close), rank(self.volume), 5))

    # ----------------------------------------------------------
    # Alpha#014 [动量][量价]
    # (-1 * rank(delta(returns,3))) * correlation(open, volume, 10)
    # ----------------------------------------------------------
    def alpha014(self):
        return -1 * rank(delta(self.returns, 3)) * _safe_corr(self.open, self.volume, 10)

    # ----------------------------------------------------------
    # Alpha#015 [量价]
    # -1 * sum(rank(correlation(rank(high), rank(volume), 3)), 3)
    # ----------------------------------------------------------
    def alpha015(self):
        return -1 * ts_sum(rank(_safe_corr(rank(self.high), rank(self.volume), 3)), 3)

    # ----------------------------------------------------------
    # Alpha#016 [量价]
    # -1 * rank(covariance(rank(high), rank(volume), 5))
    # ----------------------------------------------------------
    def alpha016(self):
        return -1 * rank(covariance(rank(self.high), rank(self.volume), 5))

    # ----------------------------------------------------------
    # Alpha#017 [动量][流动性]
    # (-1*rank(ts_rank(close,10))) * rank(delta(delta(close,1),1)) * rank(ts_rank(volume/adv20,5))
    # ----------------------------------------------------------
    def alpha017(self):
        adv20 = _adv(self.volume, 20)
        return (-1 * rank(ts_rank(self.close, 10)) *
                rank(delta(delta(self.close, 1), 1)) *
                rank(ts_rank(self.volume / adv20, 5)))

    # ----------------------------------------------------------
    # Alpha#018 [波动率]
    # -1 * rank(((stddev(abs(close-open),5) + (close-open)) + correlation(close,open,10)))
    # ----------------------------------------------------------
    def alpha018(self):
        return -1 * rank(stddev(np.abs(self.close - self.open), 5) +
                         (self.close - self.open) +
                         _safe_corr(self.close, self.open, 10))

    # ----------------------------------------------------------
    # Alpha#019 [动量]
    # (-1*sign(close-delay(close,7)+delta(close,7))) * (1+rank(1+sum(returns,250)))
    # ----------------------------------------------------------
    def alpha019(self):
        return (-1 * sign((self.close - delay(self.close, 7)) + delta(self.close, 7)) *
                (1 + rank(1 + ts_sum(self.returns, 250))))

    # ----------------------------------------------------------
    # Alpha#020 [形态]
    # (-1*rank(open-delay(high,1))) * rank(open-delay(close,1)) * rank(open-delay(low,1))
    # ----------------------------------------------------------
    def alpha020(self):
        return (-1 * rank(self.open - delay(self.high, 1)) *
                rank(self.open - delay(self.close, 1)) *
                rank(self.open - delay(self.low, 1)))

    # ----------------------------------------------------------
    # Alpha#021 [量价][复合]
    # 条件: sma(close,8)±stddev vs sma(close,2), volume/adv20
    # ----------------------------------------------------------
    def alpha021(self):
        cond1 = ts_mean(self.close, 8) + stddev(self.close, 8) < ts_mean(self.close, 2)
        cond2 = ts_mean(self.close, 2) < ts_mean(self.close, 8) - stddev(self.close, 8)
        cond3 = ts_mean(self.volume, 20) / self.volume < 1
        return (cond1 | ((~cond1) & (~cond2) & (~cond3))).astype(float) * (-2) + 1

    # ----------------------------------------------------------
    # Alpha#022 [量价][波动率]
    # -1 * delta(correlation(high,volume,5),5) * rank(stddev(close,20))
    # ----------------------------------------------------------
    def alpha022(self):
        return -1 * delta(_safe_corr(self.high, self.volume, 5), 5) * rank(stddev(self.close, 20))

    # ----------------------------------------------------------
    # Alpha#023 [动量]
    # (sma(high,20) < high) ? -1*delta(high,2) : 0
    # ----------------------------------------------------------
    def alpha023(self):
        cond = ts_mean(self.high, 20) < self.high
        alpha = pd.DataFrame(0.0, index=self.close.index, columns=self.close.columns)
        alpha[cond] = -1 * delta(self.high, 2)
        return alpha.fillna(0)

    # ----------------------------------------------------------
    # Alpha#024 [动量]
    # 条件: delta(sma(close,100),100)/delay(close,100) <= 0.05
    # ----------------------------------------------------------
    def alpha024(self):
        cond = delta(ts_mean(self.close, 100), 100) / delay(self.close, 100) <= 0.05
        alpha = -1 * delta(self.close, 3)
        alpha[cond] = -1 * (self.close - ts_min(self.close, 100))
        return alpha

    # ----------------------------------------------------------
    # Alpha#025 [动量][流动性]
    # rank((-1*returns) * adv20 * vwap * (high-close))
    # ----------------------------------------------------------
    def alpha025(self):
        adv20 = _adv(self.volume, 20)
        return rank(-1 * self.returns * adv20 * self.vwap * (self.high - self.close))

    # ----------------------------------------------------------
    # Alpha#026 [量价]
    # -1 * ts_max(correlation(ts_rank(volume,5), ts_rank(high,5), 5), 3)
    # ----------------------------------------------------------
    def alpha026(self):
        return -1 * ts_max(_safe_corr(ts_rank(self.volume, 5), ts_rank(self.high, 5), 5), 3)

    # ----------------------------------------------------------
    # Alpha#027 [量价]
    # (0.5 < rank(sma(correlation(rank(volume),rank(vwap),6),2)/2)) ? -1 : 1
    # ----------------------------------------------------------
    def alpha027(self):
        alpha = rank(ts_mean(_safe_corr(rank(self.volume), rank(self.vwap), 6), 2) / 2.0)
        return sign((alpha - 0.5) * (-2))

    # ----------------------------------------------------------
    # Alpha#028 [流动性]
    # scale(correlation(adv20,low,5) + (high+low)/2 - close)
    # ----------------------------------------------------------
    def alpha028(self):
        adv20 = _adv(self.volume, 20)
        return scale(_safe_corr(adv20, self.low, 5) + (self.high + self.low) / 2 - self.close)

    # ----------------------------------------------------------
    # Alpha#029 [动量][流动性]
    # ----------------------------------------------------------
    def alpha029(self):
        return (ts_min(rank(rank(scale(log(ts_sum(rank(rank(-1 * rank(delta(self.close - 1, 5)))), 2))))), 5) +
                ts_rank(delay(-1 * self.returns, 6), 5))

    # ----------------------------------------------------------
    # Alpha#030 [动量]
    # ----------------------------------------------------------
    def alpha030(self):
        d = delta(self.close, 1)
        inner = sign(d) + sign(delay(d, 1)) + sign(delay(d, 2))
        return (1.0 - rank(inner)) * ts_sum(self.volume, 5) / ts_sum(self.volume, 20)

    # ----------------------------------------------------------
    # Alpha#031 [复合]
    # ----------------------------------------------------------
    def alpha031(self):
        adv20 = _adv(self.volume, 20)
        p1 = rank(rank(rank(decay_linear(-1 * rank(rank(delta(self.close, 10))), 10))))
        p2 = rank(-1 * delta(self.close, 3))
        p3 = sign(scale(_safe_corr(adv20, self.low, 12)))
        return p1 + p2 + p3

    # ----------------------------------------------------------
    # Alpha#032 [量价]
    # scale(sma(close,7) - close) + 20*scale(correlation(vwap, delay(close,5), 230))
    # ----------------------------------------------------------
    def alpha032(self):
        return (scale(ts_mean(self.close, 7) - self.close) +
                20 * scale(_safe_corr(self.vwap, delay(self.close, 5), 230)))

    # ----------------------------------------------------------
    # Alpha#033 [形态]
    # rank(-1 + open/close)
    # ----------------------------------------------------------
    def alpha033(self):
        return rank(-1 + self.open / self.close)

    # ----------------------------------------------------------
    # Alpha#034 [波动率][反转]
    # ----------------------------------------------------------
    def alpha034(self):
        inner = _safe_div(stddev(self.returns, 2), stddev(self.returns, 5))
        inner = inner.replace([np.inf, -np.inf], 1).fillna(1)
        return rank(2 - rank(inner) - rank(delta(self.close, 1)))

    # ----------------------------------------------------------
    # Alpha#035 [动量][量价]
    # ts_rank(volume,32) * (1-ts_rank(close+high-low,16)) * (1-ts_rank(returns,32))
    # ----------------------------------------------------------
    def alpha035(self):
        return (ts_rank(self.volume, 32) *
                (1 - ts_rank(self.close + self.high - self.low, 16)) *
                (1 - ts_rank(self.returns, 32)))

    # ----------------------------------------------------------
    # Alpha#036 [复合]
    # ----------------------------------------------------------
    def alpha036(self):
        adv20 = _adv(self.volume, 20)
        return (2.21 * rank(_safe_corr(self.close - self.open, delay(self.volume, 1), 15)) +
                0.7 * rank(self.open - self.close) +
                0.73 * rank(ts_rank(delay(-1 * self.returns, 6), 5)) +
                rank(np.abs(_safe_corr(self.vwap, adv20, 6))) +
                0.6 * rank((ts_mean(self.close, 200) - self.open) * (self.close - self.open)))

    # ----------------------------------------------------------
    # Alpha#037 [动量]
    # ----------------------------------------------------------
    def alpha037(self):
        return (rank(_safe_corr(delay(self.open - self.close, 1), self.close, 200)) +
                rank(self.open - self.close))

    # ----------------------------------------------------------
    # Alpha#038 [动量][形态]
    # -1 * rank(ts_rank(close,10)) * rank(close/open)
    # ----------------------------------------------------------
    def alpha038(self):
        inner = (self.close / self.open).replace([np.inf, -np.inf], 1).fillna(1)
        return -1 * rank(ts_rank(self.open, 10)) * rank(inner)

    # ----------------------------------------------------------
    # Alpha#039 [动量][流动性]
    # ----------------------------------------------------------
    def alpha039(self):
        adv20 = _adv(self.volume, 20)
        return (-1 * rank(delta(self.close, 7) * (1 - rank(decay_linear(self.volume / adv20, 9)))) *
                (1 + rank(ts_mean(self.returns, 250))))

    # ----------------------------------------------------------
    # Alpha#040 [波动率][量价]
    # -1 * rank(stddev(high,10)) * correlation(high, volume, 10)
    # ----------------------------------------------------------
    def alpha040(self):
        return -1 * rank(stddev(self.high, 10)) * _safe_corr(self.high, self.volume, 10)

    # ----------------------------------------------------------
    # Alpha#041 [形态]
    # (high*low)^0.5 - vwap
    # ----------------------------------------------------------
    def alpha041(self):
        return (self.high * self.low) ** 0.5 - self.vwap

    # ----------------------------------------------------------
    # Alpha#042 [量价]
    # rank(vwap-close) / rank(vwap+close)
    # ----------------------------------------------------------
    def alpha042(self):
        return rank(self.vwap - self.close) / rank(self.vwap + self.close)

    # ----------------------------------------------------------
    # Alpha#043 [动量][流动性]
    # ts_rank(volume/adv20, 20) * ts_rank(-1*delta(close,7), 8)
    # ----------------------------------------------------------
    def alpha043(self):
        adv20 = _adv(self.volume, 20)
        return ts_rank(self.volume / adv20, 20) * ts_rank(-1 * delta(self.close, 7), 8)

    # ----------------------------------------------------------
    # Alpha#044 [量价]
    # -1 * correlation(high, rank(volume), 5)
    # ----------------------------------------------------------
    def alpha044(self):
        return -1 * _safe_corr(self.high, rank(self.volume), 5)

    # ----------------------------------------------------------
    # Alpha#045 [量价]
    # -1 * (rank(sma(delay(close,5),20)) * corr(close,volume,2) * rank(corr(sum(close,5),sum(close,20),2)))
    # ----------------------------------------------------------
    def alpha045(self):
        return (-1 * rank(ts_mean(delay(self.close, 5), 20)) *
                _safe_corr(self.close, self.volume, 2) *
                rank(_safe_corr(ts_sum(self.close, 5), ts_sum(self.close, 20), 2)))

    # ----------------------------------------------------------
    # Alpha#046 [动量]
    # 价格加速度条件判断
    # ----------------------------------------------------------
    def alpha046(self):
        inner = ((delay(self.close, 20) - delay(self.close, 10)) / 10 -
                 (delay(self.close, 10) - self.close) / 10)
        alpha = -1 * delta(self.close, 1)
        alpha[inner < 0] = 1
        alpha[inner > 0.25] = -1
        return alpha

    # ----------------------------------------------------------
    # Alpha#047 [量价][流动性]
    # ----------------------------------------------------------
    def alpha047(self):
        adv20 = _adv(self.volume, 20)
        return ((rank(1 / self.close) * self.volume / adv20 *
                 self.high * rank(self.high - self.close) / (ts_mean(self.high, 5))) -
                rank(self.vwap - delay(self.vwap, 5)))

    # ----------------------------------------------------------
    # Alpha#048 [IndNeutralize]
    # IndNeutralize(((correlation(delta(close,1), delta(delay(close,1),1), 250) *
    #   delta(close,1)) / close), SubIndustryGroups) * ...
    # ----------------------------------------------------------
    def alpha048(self):
        inner = (_safe_corr(delta(self.close, 1), delta(delay(self.close, 1), 1), 250) *
                 delta(self.close, 1) / self.close)
        if self.industry is not None:
            inner = ind_neutralize(inner, self.industry)
        return inner / _safe_div(ts_sum(((delta(self.close, 1) / delay(self.close, 1)) ** 2), 250),
                                 pd.DataFrame(250.0, index=self.close.index, columns=self.close.columns))

    # ----------------------------------------------------------
    # Alpha#049 [动量]
    # 价格加速度 < -0.1 条件
    # ----------------------------------------------------------
    def alpha049(self):
        inner = ((delay(self.close, 20) - delay(self.close, 10)) / 10 -
                 (delay(self.close, 10) - self.close) / 10)
        alpha = -1 * delta(self.close, 1)
        alpha[inner < -0.1] = 1
        return alpha

    # ----------------------------------------------------------
    # Alpha#050 [量价]
    # -1 * ts_max(rank(correlation(rank(volume), rank(vwap), 5)), 5)
    # ----------------------------------------------------------
    def alpha050(self):
        return -1 * ts_max(rank(_safe_corr(rank(self.volume), rank(self.vwap), 5)), 5)

    # ----------------------------------------------------------
    # Alpha#051 [动量]
    # 价格加速度 < -0.05 条件
    # ----------------------------------------------------------
    def alpha051(self):
        inner = ((delay(self.close, 20) - delay(self.close, 10)) / 10 -
                 (delay(self.close, 10) - self.close) / 10)
        alpha = -1 * delta(self.close, 1)
        alpha[inner < -0.05] = 1
        return alpha

    # ----------------------------------------------------------
    # Alpha#052 [动量][流动性]
    # ----------------------------------------------------------
    def alpha052(self):
        return ((-1 * delta(ts_min(self.low, 5), 5)) *
                rank((ts_sum(self.returns, 240) - ts_sum(self.returns, 20)) / 220) *
                ts_rank(self.volume, 5))

    # ----------------------------------------------------------
    # Alpha#053 [形态]
    # -1 * delta(((close-low)-(high-close))/(close-low), 9)
    # ----------------------------------------------------------
    def alpha053(self):
        inner = _safe_div(self.close - self.low, self.close - self.low)  # (close-low)
        clv = _safe_div((self.close - self.low) - (self.high - self.close),
                        self.close - self.low)
        return -1 * delta(clv, 9)

    # ----------------------------------------------------------
    # Alpha#054 [形态]
    # ((-1*(low-close))*(open^5)) / ((low-high)*(close^5))
    # ----------------------------------------------------------
    def alpha054(self):
        denom = _safe_div(self.low - self.high, pd.DataFrame(1.0, index=self.close.index, columns=self.close.columns))
        return -1 * (self.low - self.close) * (self.open ** 5) / (denom * (self.close ** 5))

    # ----------------------------------------------------------
    # Alpha#055 [量价]
    # -1 * correlation(rank((close-ts_min(low,12))/(ts_max(high,12)-ts_min(low,12))), rank(volume), 6)
    # ----------------------------------------------------------
    def alpha055(self):
        divisor = _safe_div(ts_max(self.high, 12) - ts_min(self.low, 12),
                            pd.DataFrame(1.0, index=self.close.index, columns=self.close.columns))
        inner = (self.close - ts_min(self.low, 12)) / divisor
        return -1 * _safe_corr(rank(inner), rank(self.volume), 6)

    # ----------------------------------------------------------
    # Alpha#056 (需 cap 市值)
    # -1 * (sum(returns,10)/sum(sum(returns,2),3)) * rank(volume*vwap/(sum(vwap,10)/10))
    # ----------------------------------------------------------
    def alpha056(self):
        # 简化版: 不依赖 cap
        return (-1 * rank(ts_sum(self.returns, 10) /
                          ts_sum(ts_sum(self.returns, 2), 3)) *
                rank(self.volume * self.vwap / ts_mean(self.vwap, 10)))

    # ----------------------------------------------------------
    # Alpha#057 [反转]
    # -(close-vwap) / decay_linear(rank(ts_argmax(close,30)), 2)
    # ----------------------------------------------------------
    def alpha057(self):
        return -(self.close - self.vwap) / decay_linear(rank(ts_argmax(self.close, 30)), 2)

    # ----------------------------------------------------------
    # Alpha#058 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha058(self):
        inner = -1 * ts_rank(decay_linear(
            _safe_corr(
                ind_neutralize(self.vwap, self.industry) if self.industry is not None else self.vwap,
                self.volume, 4), 8), 6)
        return inner

    # ----------------------------------------------------------
    # Alpha#059 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha059(self):
        inner = -1 * ts_rank(decay_linear(
            _safe_corr(
                ind_neutralize(self.vwap, self.industry) if self.industry is not None else self.vwap,
                self.volume, 3), 7), 4)
        return inner

    # ----------------------------------------------------------
    # Alpha#060 [量价]
    # -(2*scale(rank(CLV*volume)) - scale(rank(ts_argmax(close,10))))
    # ----------------------------------------------------------
    def alpha060(self):
        divisor = _safe_div(self.high - self.low,
                            pd.DataFrame(1.0, index=self.close.index, columns=self.close.columns))
        inner = ((self.close - self.low) - (self.high - self.close)) * self.volume / divisor
        return -(2 * scale(rank(inner)) - scale(rank(ts_argmax(self.close, 10))))

    # ----------------------------------------------------------
    # Alpha#061 [量价]
    # rank(vwap - ts_min(vwap,16)) < rank(correlation(vwap, adv180, 18))
    # ----------------------------------------------------------
    def alpha061(self):
        adv180 = _adv(self.volume, 180)
        return (rank(self.vwap - ts_min(self.vwap, 16)) <
                rank(_safe_corr(self.vwap, adv180, 18))).astype(float)

    # ----------------------------------------------------------
    # Alpha#062 [量价]
    # ----------------------------------------------------------
    def alpha062(self):
        adv20 = _adv(self.volume, 20)
        return ((rank(_safe_corr(self.vwap, ts_mean(adv20, 22), 10)) <
                 rank(2 * rank(self.open) < rank((self.high + self.low) / 2) + rank(self.high))) * -1).astype(float)

    # ----------------------------------------------------------
    # Alpha#063 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha063(self):
        adv20 = _adv(self.volume, 20)
        inn_vwap = ind_neutralize(self.vwap, self.industry) if self.industry is not None else self.vwap
        p1 = rank(decay_linear(delta(inn_vwap, 2), 3))
        p2 = ts_rank(decay_linear(
            _safe_corr(self.close * 0.318108 + self.low * (1 - 0.318108), adv20, 13) * (-1), 7), 4)
        return -(p1 + p2)

    # ----------------------------------------------------------
    # Alpha#064 [量价]
    # ----------------------------------------------------------
    def alpha064(self):
        adv120 = _adv(self.volume, 120)
        return ((rank(_safe_corr(ts_mean(self.open * 0.178404 + self.low * 0.821596, 13),
                                 ts_mean(adv120, 13), 17)) <
                 rank(delta((self.high + self.low) / 2 * 0.178404 + self.vwap * 0.821596, 4))) * -1).astype(float)

    # ----------------------------------------------------------
    # Alpha#065 [量价]
    # ----------------------------------------------------------
    def alpha065(self):
        adv60 = _adv(self.volume, 60)
        return ((rank(_safe_corr(self.open * 0.00817205 + self.vwap * (1 - 0.00817205),
                                 ts_mean(adv60, 9), 6)) <
                 rank(self.open - ts_min(self.open, 14))) * -1).astype(float)

    # ----------------------------------------------------------
    # Alpha#066 [动量]
    # ----------------------------------------------------------
    def alpha066(self):
        return ((rank(decay_linear(delta(self.vwap, 4), 7)) +
                 ts_rank(decay_linear(
                     _safe_div(self.low - self.vwap,
                               self.open - (self.high + self.low) / 2), 11), 7)) * -1)

    # ----------------------------------------------------------
    # Alpha#067 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha067(self):
        adv20 = _adv(self.volume, 20)
        inn_vwap = ind_neutralize(self.vwap, self.industry) if self.industry is not None else self.vwap
        p1 = rank(ts_max(rank(inn_vwap - ts_min(inn_vwap, 16)), 2))
        p2 = rank(delta(_safe_corr(self.close, adv20, 8), 2))
        return -(p1 ** p2)

    # ----------------------------------------------------------
    # Alpha#068 [量价]
    # ----------------------------------------------------------
    def alpha068(self):
        adv15 = _adv(self.volume, 15)
        return ((ts_rank(_safe_corr(rank(self.high), rank(adv15), 9), 14) <
                 rank(delta(self.close * 0.518371 + self.low * (1 - 0.518371), 2))) * -1).astype(float)

    # ----------------------------------------------------------
    # Alpha#069 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha069(self):
        adv20 = _adv(self.volume, 20)
        inn_vwap = ind_neutralize(self.vwap, self.industry) if self.industry is not None else self.vwap
        p1 = rank(ts_max(delta(inn_vwap, 3), 5))
        p2 = ts_rank(delta(self.open * 0.490655 + self.vwap * (1 - 0.490655), 1) * (-1), 12)
        return -(p1 ** p2)

    # ----------------------------------------------------------
    # Alpha#070 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha070(self):
        adv50 = _adv(self.volume, 50)
        inn_close = ind_neutralize(self.close, self.industry) if self.industry is not None else self.close
        p1 = rank(delta(inn_close, 1))
        p2 = ts_rank(decay_linear(
            _safe_corr(self.close, adv50, 18) * (-1), 4), 16)
        return -(p1 ** p2)

    # ----------------------------------------------------------
    # Alpha#071 [量价]
    # ----------------------------------------------------------
    def alpha071(self):
        adv180 = _adv(self.volume, 180)
        p1 = ts_rank(decay_linear(
            _safe_corr(ts_rank(self.close, 3), ts_rank(adv180, 12), 18), 4), 16)
        p2 = ts_rank(decay_linear(
            rank((self.low + self.open - 2 * self.vwap) ** 2), 16), 4)
        return np.maximum(p1, p2)

    # ----------------------------------------------------------
    # Alpha#072 [量价]
    # ----------------------------------------------------------
    def alpha072(self):
        adv40 = _adv(self.volume, 40)
        return (rank(decay_linear(_safe_corr((self.high + self.low) / 2, adv40, 9), 10)) /
                rank(decay_linear(_safe_corr(ts_rank(self.vwap, 4), ts_rank(self.volume, 19), 7), 3)))

    # ----------------------------------------------------------
    # Alpha#073 [动量]
    # ----------------------------------------------------------
    def alpha073(self):
        p1 = rank(decay_linear(delta(self.vwap, 5), 3))
        p2 = ts_rank(decay_linear(
            _safe_div(delta(self.open * 0.147155 + self.low * (1 - 0.147155), 2),
                      self.open * 0.147155 + self.low * (1 - 0.147155)) * (-1), 3), 17)
        return -1 * np.maximum(p1, p2)

    # ----------------------------------------------------------
    # Alpha#074 [量价]
    # ----------------------------------------------------------
    def alpha074(self):
        adv30 = _adv(self.volume, 30)
        return ((rank(_safe_corr(self.close, ts_mean(adv30, 37), 15)) <
                 rank(_safe_corr(rank(self.high * 0.0261661 + self.vwap * (1 - 0.0261661)),
                                 rank(self.volume), 11))) * -1).astype(float)

    # ----------------------------------------------------------
    # Alpha#075 [流动性]
    # rank(corr(vwap, volume, 4)) < rank(corr(rank(low), rank(adv50), 12))
    # ----------------------------------------------------------
    def alpha075(self):
        adv50 = _adv(self.volume, 50)
        return (rank(_safe_corr(self.vwap, self.volume, 4)) <
                rank(_safe_corr(rank(self.low), rank(adv50), 12))).astype(float)

    # ----------------------------------------------------------
    # Alpha#076 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha076(self):
        adv81 = _adv(self.volume, 81)
        inn_low = ind_neutralize(self.low, self.industry) if self.industry is not None else self.low
        p1 = rank(decay_linear(delta(self.vwap, 1), 12))
        p2 = ts_rank(decay_linear(
            ts_rank(_safe_corr(inn_low, adv81, 8), 20), 6), 3)
        return -1 * np.maximum(p1, p2)

    # ----------------------------------------------------------
    # Alpha#077 [量价]
    # ----------------------------------------------------------
    def alpha077(self):
        adv40 = _adv(self.volume, 40)
        p1 = rank(decay_linear((self.high + self.low) / 2 + self.high - self.vwap - self.high, 20))
        p2 = rank(decay_linear(_safe_corr((self.high + self.low) / 2, adv40, 3), 6))
        return np.minimum(p1, p2)

    # ----------------------------------------------------------
    # Alpha#078 [量价]
    # ----------------------------------------------------------
    def alpha078(self):
        adv40 = _adv(self.volume, 40)
        return (rank(_safe_corr(
            ts_sum(self.low * 0.352233 + self.vwap * (1 - 0.352233), 20),
            ts_sum(adv40, 20), 7)) **
                rank(_safe_corr(rank(self.vwap), rank(self.volume), 6)))

    # ----------------------------------------------------------
    # Alpha#079 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha079(self):
        adv10 = _adv(self.volume, 10)
        inn_close = ind_neutralize(self.close, self.industry) if self.industry is not None else self.close
        p1 = rank(delta(inn_close, 1))
        p2 = rank(decay_linear(
            _safe_corr(self.vwap, adv10, 4) * (-1), 7))
        return np.maximum(p1, p2)

    # ----------------------------------------------------------
    # Alpha#080 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha080(self):
        adv60 = _adv(self.volume, 60)
        inn_open = ind_neutralize(self.open, self.industry) if self.industry is not None else self.open
        p1 = rank(np.sign(delta(inn_open, 1)) * (-1))
        p2 = rank(-1 * ts_rank(
            _safe_corr(self.close, adv60, 4), 17))
        return -(p1 ** p2)

    # ----------------------------------------------------------
    # Alpha#081 [量价]
    # ----------------------------------------------------------
    def alpha081(self):
        adv10 = _adv(self.volume, 10)
        return ((rank(log(product(rank(rank(
            _safe_corr(self.vwap, ts_sum(adv10, 50), 8) ** 4)), 15))) <
                 rank(_safe_corr(rank(self.vwap), rank(self.volume), 5))) * -1).astype(float)

    # ----------------------------------------------------------
    # Alpha#082 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha082(self):
        adv20 = _adv(self.volume, 20)
        inn_open = ind_neutralize(self.open, self.industry) if self.industry is not None else self.open
        p1 = rank(decay_linear(delta(inn_open, 1), 15))
        p2 = rank(decay_linear(_safe_corr(
            self.volume * 0.634196 + self.open * (1 - 0.634196),
            ts_sum(adv20, 22), 17) * (-1), 7))
        return -1 * np.minimum(p1, p2)

    # ----------------------------------------------------------
    # Alpha#083 [形态][量价]
    # ----------------------------------------------------------
    def alpha083(self):
        return (rank(delay((self.high - self.low) / (ts_mean(self.close, 5)), 2)) *
                rank(rank(self.volume)) /
                _safe_div((self.high - self.low) / (ts_mean(self.close, 5)),
                          self.vwap - self.close))

    # ----------------------------------------------------------
    # Alpha#084 [动量]
    # ----------------------------------------------------------
    def alpha084(self):
        return ts_rank(self.vwap - ts_max(self.vwap, 15), 21) ** delta(self.close, 5)

    # ----------------------------------------------------------
    # Alpha#085 [量价]
    # ----------------------------------------------------------
    def alpha085(self):
        adv30 = _adv(self.volume, 30)
        return (rank(_safe_corr(self.high * 0.876703 + self.close * (1 - 0.876703), adv30, 10)) **
                rank(_safe_corr(ts_rank((self.high + self.low) / 2, 4), ts_rank(self.volume, 10), 7)))

    # ----------------------------------------------------------
    # Alpha#086 [量价]
    # ----------------------------------------------------------
    def alpha086(self):
        adv20 = _adv(self.volume, 20)
        return ((ts_rank(_safe_corr(self.close, ts_mean(adv20, 15), 6), 20) <
                 rank(self.open + self.close - self.vwap - self.open)) * -1).astype(float)

    # ----------------------------------------------------------
    # Alpha#087 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha087(self):
        adv81 = _adv(self.volume, 81)
        inn_close = ind_neutralize(self.close, self.industry) if self.industry is not None else self.close
        p1 = rank(decay_linear(delta(inn_close, 4), 5))
        p2 = ts_rank(decay_linear(
            _safe_corr(self.vwap, ts_mean(adv81, 10), 6) * (-1), 10), 16)
        return -1 * np.maximum(p1, p2)

    # ----------------------------------------------------------
    # Alpha#088 [量价]
    # ----------------------------------------------------------
    def alpha088(self):
        adv60 = _adv(self.volume, 60)
        p1 = rank(decay_linear(
            rank(self.open) + rank(self.low) - rank(self.high) - rank(self.close), 8))
        p2 = ts_rank(decay_linear(
            _safe_corr(ts_rank(self.close, 8), ts_rank(adv60, 21), 8), 7), 3)
        return np.minimum(p1, p2)

    # ----------------------------------------------------------
    # Alpha#089 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha089(self):
        adv10 = _adv(self.volume, 10)
        inn_low = ind_neutralize(self.low, self.industry) if self.industry is not None else self.low
        p1 = ts_rank(decay_linear(
            _safe_corr(self.close * 0.967285 + self.low * (1 - 0.967285), adv10, 7), 6), 4)
        p2 = ts_rank(decay_linear(delta(inn_low, 3), 10), 15)
        return -(p1 + p2)

    # ----------------------------------------------------------
    # Alpha#090 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha090(self):
        adv40 = _adv(self.volume, 40)
        inn_close = ind_neutralize(self.close, self.industry) if self.industry is not None else self.close
        p1 = rank(inn_close - ts_max(inn_close, 5))
        p2 = ts_rank(_safe_corr(adv40, self.low, 5), 3)
        return -(p1 ** p2)

    # ----------------------------------------------------------
    # Alpha#091 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha091(self):
        adv30 = _adv(self.volume, 30)
        inn_close = ind_neutralize(self.close, self.industry) if self.industry is not None else self.close
        p1 = rank(self.close - ts_max(self.close, 5))
        p2 = ts_rank(decay_linear(
            _safe_corr(inn_close, adv30, 10) * (-1), 8), 17)
        return -(p1 * p2)

    # ----------------------------------------------------------
    # Alpha#092 [量价]
    # ----------------------------------------------------------
    def alpha092(self):
        adv30 = _adv(self.volume, 30)
        p1 = ts_rank(decay_linear(
            ((self.high + self.low) / 2 + self.close < self.low + self.open).astype(float), 15), 19)
        p2 = ts_rank(decay_linear(
            _safe_corr(rank(self.low), rank(adv30), 8), 7), 7)
        return np.minimum(p1, p2)

    # ----------------------------------------------------------
    # Alpha#093 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha093(self):
        adv81 = _adv(self.volume, 81)
        inn_vwap = ind_neutralize(self.vwap, self.industry) if self.industry is not None else self.vwap
        p1 = ts_rank(decay_linear(
            _safe_corr(inn_vwap, adv81, 17), 20), 8)
        p2 = rank(delta(
            (self.close * 0.524434 + self.vwap * (1 - 0.524434)), 3))
        return -(p1 / p2)

    # ----------------------------------------------------------
    # Alpha#094 [量价]
    # ----------------------------------------------------------
    def alpha094(self):
        adv60 = _adv(self.volume, 60)
        return (-(rank(self.vwap - ts_min(self.vwap, 12)) **
                  ts_rank(_safe_corr(ts_rank(self.vwap, 20), ts_rank(adv60, 4), 18), 3)))

    # ----------------------------------------------------------
    # Alpha#095 [量价]
    # ----------------------------------------------------------
    def alpha095(self):
        adv40 = _adv(self.volume, 40)
        return (rank(self.open - ts_min(self.open, 12)) <
                ts_rank(rank(_safe_corr(
                    ts_mean((self.high + self.low) / 2, 19),
                    ts_mean(adv40, 19), 13) ** 5), 12)).astype(float)

    # ----------------------------------------------------------
    # Alpha#096 [量价]
    # ----------------------------------------------------------
    def alpha096(self):
        adv60 = _adv(self.volume, 60)
        p1 = ts_rank(decay_linear(
            _safe_corr(rank(self.vwap), rank(self.volume), 4), 4), 8)
        p2 = ts_rank(decay_linear(
            ts_argmax(_safe_corr(ts_rank(self.close, 7), ts_rank(adv60, 4), 4), 13), 14), 13)
        return -1 * np.maximum(p1, p2)

    # ----------------------------------------------------------
    # Alpha#097 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha097(self):
        adv60 = _adv(self.volume, 60)
        inn_low = ind_neutralize(self.low, self.industry) if self.industry is not None else self.low
        p1 = rank(decay_linear(delta(inn_low, 2), 6))
        p2 = ts_rank(decay_linear(
            ts_rank(_safe_corr(self.vwap, adv60, 4), 17), 7), 18)
        return -1 * np.maximum(p1, p2)

    # ----------------------------------------------------------
    # Alpha#098 [量价]
    # ----------------------------------------------------------
    def alpha098(self):
        adv5 = _adv(self.volume, 5)
        adv15 = _adv(self.volume, 15)
        return (rank(decay_linear(_safe_corr(self.vwap, ts_mean(adv5, 26), 5), 7)) -
                rank(decay_linear(
                    ts_rank(ts_argmin(
                        _safe_corr(rank(self.open), rank(adv15), 21), 9), 7), 8)))

    # ----------------------------------------------------------
    # Alpha#099 [量价]
    # ----------------------------------------------------------
    def alpha099(self):
        adv60 = _adv(self.volume, 60)
        return ((rank(_safe_corr(
            ts_sum((self.high + self.low) / 2, 20), ts_sum(adv60, 20), 9)) <
                 rank(_safe_corr(self.low, self.volume, 6))) * -1).astype(float)

    # ----------------------------------------------------------
    # Alpha#100 [IndNeutralize]
    # ----------------------------------------------------------
    def alpha100(self):
        adv20 = _adv(self.volume, 20)
        inn_close = ind_neutralize(self.close, self.industry) if self.industry is not None else self.close
        p1 = rank(
            stddev(inn_close, 20) * scale(
                _safe_corr(inn_close, adv20, 6)) * (-1))
        return -1 * p1

    # ----------------------------------------------------------
    # Alpha#101 [形态]
    # (close - open) / ((high - low) + 0.001)
    # ----------------------------------------------------------
    def alpha101(self):
        return (self.close - self.open) / ((self.high - self.low) + 0.001)

    # ============================================================
    # 批量计算
    # ============================================================

    def compute_all(self):
        """
        计算全部 101 个因子，返回 dict: {name: DataFrame}
        跳过计算报错的因子 (打印警告)。
        """
        results = {}
        for i in range(1, 102):
            name = f"alpha{i:03d}"
            method = getattr(self, name, None)
            if method is None:
                continue
            try:
                results[name] = method()
            except Exception as e:
                print(f"[WQ101] {name} 计算失败: {e}")
        return results

    def compute_list(self, alpha_ids):
        """
        计算指定因子列表。

        Parameters
        ----------
        alpha_ids : list of int
            例如 [1, 2, 12, 26, 42]

        Returns
        -------
        dict: {name: DataFrame}
        """
        results = {}
        for i in alpha_ids:
            name = f"alpha{i:03d}"
            method = getattr(self, name, None)
            if method is None:
                print(f"[WQ101] {name} 未实现")
                continue
            try:
                results[name] = method()
            except Exception as e:
                print(f"[WQ101] {name} 计算失败: {e}")
        return results
