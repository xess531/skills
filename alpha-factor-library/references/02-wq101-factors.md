# WorldQuant 101 Formulaic Alphas — 完整因子公式

> 来源：Kakushadze Z. (2016). *101 Formulaic Alphas*. Wilmott Magazine.
> 分类标签：[量价] [动量] [反转] [波动率] [形态] [流动性] [复合]

---

## 因子列表

### Alpha#001 — 短期反转 [反转] [波动率]
```
rank(ts_argmax(SignedPower(((returns < 0) ? stddev(returns, 20) : close), 2.), 5)) - 0.5
```
> 下跌日用波动率、上涨日用收盘价，取平方后找5天极值位置。反转+波动率复合信号。

### Alpha#002 — 量价背离 [量价]
```
-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6)
```
> 成交量对数变化 vs 日内涨幅的6日相关性取负。量涨价不涨→做空。

### Alpha#003 — 开盘价量相关 [量价]
```
-1 * correlation(rank(open), rank(volume), 10)
```
> 开盘价与成交量的10日负相关性。

### Alpha#004 — 低价时序排名 [反转]
```
-1 * ts_rank(rank(low), 9)
```
> 低价截面排名的9日时序排名取负。

### Alpha#005 — 开盘价-VWAP偏离 [形态] [流动性]
```
rank((open - (sum(vwap, 10) / 10))) * (-1 * abs(rank((close - vwap))))
```
> 开盘价偏离10日均VWAP × 收盘偏离VWAP的绝对值。

### Alpha#006 — 开盘价量相关（简版）[量价]
```
-1 * correlation(open, volume, 10)
```
> 极简因子：开盘价和成交量的10日相关性取负。

### Alpha#007 — 条件动量 [动量] [流动性]
```
((adv20 < volume) ? ((-1 * ts_rank(abs(delta(close, 7)), 60)) * sign(delta(close, 7))) : (-1 * 1))
```
> 放量时反转，缩量时固定做空。

### Alpha#008 — 动量反转 [反转]
```
-1 * rank(((sum(open, 5) * sum(returns, 5)) - delay((sum(open, 5) * sum(returns, 5)), 10)))
```
> 近5日开盘价×收益率的乘积变化。

### Alpha#009 — 价格趋势延续/反转 [动量] [反转]
```
((0 < ts_min(delta(close, 1), 5)) ? delta(close, 1) : ((ts_max(delta(close, 1), 5) < 0) ? delta(close, 1) : (-1 * delta(close, 1))))
```
> 5天全涨/全跌→顺势，否则反转。

### Alpha#010 — 价格趋势排名版 [动量] [反转]
```
rank(((0 < ts_min(delta(close, 1), 4)) ? delta(close, 1) : ((ts_max(delta(close, 1), 4) < 0) ? delta(close, 1) : (-1 * delta(close, 1)))))
```
> Alpha#009的4日窗口+截面排名版本。

### Alpha#011 — VWAP偏离+量变 [量价] [形态]
```
((rank(ts_max((vwap - close), 3)) + rank(ts_min((vwap - close), 3))) * rank(delta(volume, 3)))
```
> VWAP与收盘价偏离的极值 × 成交量3日变化。

### Alpha#012 — 量价背离反转 [量价] [反转]
```
sign(delta(volume, 1)) * (-1 * delta(close, 1))
```
> 放量上涨→做空，放量下跌→做多。典型量价背离。

### Alpha#013 — 量价协方差 [量价]
```
-1 * rank(covariance(rank(close), rank(volume), 5))
```
> 收盘价排名与成交量排名的5日协方差取负。

### Alpha#014 — 动量+量价 [动量] [量价]
```
((-1 * rank(delta(returns, 3))) * correlation(open, volume, 10))
```
> 收益率加速度 × 开盘价量相关性。

### Alpha#015 — 高价量排名相关 [量价]
```
-1 * sum(rank(correlation(rank(high), rank(volume), 3)), 3)
```
> 最高价排名与成交量排名的短期相关性累积。

### Alpha#016 — 高价量协方差 [量价]
```
-1 * rank(covariance(rank(high), rank(volume), 5))
```
> 最高价排名与成交量排名的5日协方差。

### Alpha#017 — 复合动量 [动量] [流动性]
```
((-1 * rank(ts_rank(close, 10))) * rank(delta(delta(close, 1), 1))) * rank(ts_rank((volume / adv20), 5))
```
> 价格水平排名 × 价格加速度 × 成交量活跃度。

### Alpha#018 — 波动率+日内形态 [波动率] [形态]
```
-1 * rank(((stddev(abs((close - open)), 5) + (close - open)) + correlation(close, open, 10)))
```
> 日内波动幅度 + 收盘偏离开盘 + 收开相关性。

### Alpha#019 — 长期动量反转 [反转]
```
((-1 * sign(((close - delay(close, 7)) + delta(close, 7)))) * (1 + rank((1 + sum(returns, 250)))))
```
> 7日价格变化方向取反 × 250日累积收益排名。

### Alpha#020 — 跳空模式 [形态]
```
(((-1 * rank((open - delay(high, 1)))) * rank((open - delay(close, 1)))) * rank((open - delay(low, 1))))
```
> 开盘价相对昨日高/收/低价的偏离三维组合。

### Alpha#021 — 条件量价 [量价] [复合]
```
((((sum(close, 8) / 8) + stddev(close, 8)) < (sum(close, 2) / 2)) ? (-1 * 1) : (((sum(close, 2) / 2) < ((sum(close, 8) / 8) - stddev(close, 8))) ? 1 : (((1 < (volume / adv20)) or ((volume / adv20) == 1)) ? 1 : (-1 * 1))))
```
> 多层条件判断：价格位置 + 波动率 + 成交量活跃度。

### Alpha#022 — 高价量相关变化 [量价] [波动率]
```
-1 * (delta(correlation(high, volume, 5), 5) * rank(stddev(close, 20)))
```
> 高价-量相关性的变化 × 波动率。

### Alpha#023 — 高位反转 [反转] [形态]
```
(((sum(high, 20) / 20) < high) ? (-1 * delta(high, 2)) : 0)
```
> 今日最高价 > 20日均最高价时触发做空。

### Alpha#024 — 条件均线反转 [反转]
```
((((delta((sum(close, 100) / 100), 100) / delay(close, 100)) < 0.05) or ((delta((sum(close, 100) / 100), 100) / delay(close, 100)) == 0.05)) ? (-1 * (close - ts_min(close, 100))) : (-1 * delta(close, 3)))
```
> 100日均线变化 < 5%时，做空（close - 100日最低），否则做空3日动量。

### Alpha#025 — 复合量价 [量价] [动量]
```
rank(((((-1 * returns) * adv20) * vwap) * (high - close)))
```
> 收益率反转 × 成交额 × VWAP × 上影线。

### Alpha#026 — 量价排名相关 [量价]
```
-1 * ts_max(correlation(ts_rank(volume, 5), ts_rank(high, 5), 5), 3)
```
> 成交量排名与最高价排名的5日相关性的3日最大值取负。

### Alpha#027 — 条件量价 [量价]
```
((0.5 < rank((sum(correlation(rank(volume), rank(vwap), 6), 2) / 2.0))) ? (-1 * 1) : 1)
```
> 量-VWAP相关性高时做空，低时做多。

### Alpha#028 — 流动性 [流动性]
```
scale(((correlation(adv20, low, 5) + ((high + low) / 2)) - close))
```
> 平均成交额与低价的相关性 + 中间价 - 收盘价。

### Alpha#029 — 复合嵌套 [复合]
```
min(product(rank(rank(scale(log(sum(ts_min(rank(rank((-1 * rank(delta((close - 1), 5))))), 2), 1))))), 1), 5) + ts_rank(delay((-1 * returns), 6), 5)
```
> 多层嵌套排名+标准化的复合因子 + 延迟反转。

### Alpha#030 — 连续涨跌+成交量 [动量] [流动性]
```
(((1.0 - rank(((sign((close - delay(close, 1))) + sign((delay(close, 1) - delay(close, 2)))) + sign((delay(close, 2) - delay(close, 3)))))) * sum(volume, 5)) / sum(volume, 20))
```
> 3天连续涨跌方向信号 × 短期/长期成交量比。

### Alpha#031 — 衰减+反转+相关 [反转] [流动性]
```
((rank(rank(rank(decay_linear((-1 * rank(rank(delta(close, 10)))), 10)))) + rank((-1 * delta(close, 3)))) + sign(scale(correlation(adv20, low, 12))))
```
> 10日动量线性衰减 + 3日反转 + 成交额与低价相关性。

### Alpha#032 — 均值回归+VWAP [反转]
```
(scale(((sum(close, 7) / 7) - close)) + (20 * scale(correlation(vwap, delay(close, 5), 230))))
```
> 7日均线偏离 + 长期VWAP-滞后收盘价相关性。

### Alpha#033 — 日内方向 [形态]
```
rank((-1 * ((1 - (open / close))^1)))
```
> 开盘到收盘的涨跌幅排名取负。

### Alpha#034 — 波动率变化+反转 [波动率] [反转]
```
rank(((1 - rank((stddev(returns, 2) / stddev(returns, 5)))) + (1 - rank(delta(close, 1)))))
```
> 短/长波动率比 + 1日反转。

### Alpha#035 — 量×形态×反转 [量价] [反转]
```
((ts_rank(volume, 32) * (1 - ts_rank(((close + high) - low), 16))) * (1 - ts_rank(returns, 32)))
```
> 成交量时序排名 × 价格形态反向 × 收益率反向。

### Alpha#036 — 多因子复合 [复合]
```
(((((2.21 * rank(correlation((close - open), delay(volume, 1), 15))) + (0.7 * rank((open - close)))) + (0.73 * rank(ts_rank(delay((-1 * returns), 6), 5)))) + rank(abs(correlation(vwap, adv20, 6)))) + (0.6 * rank((((sum(close, 200) / 200) - open) * (close - open)))))
```
> 加权组合：日内形态+量价+延迟反转+流动性+均线偏离。

### Alpha#037 — 滞后形态+相关 [形态]
```
(rank(correlation(delay((open - close), 1), close, 200)) + rank((open - close)))
```
> 昨日日内形态与收盘价的长期相关性 + 今日日内形态。

### Alpha#038 — 水平反转 [反转]
```
((-1 * rank(ts_rank(close, 10))) * rank((close / open)))
```
> 价格水平时序排名 × 日内涨幅排名，取负。

### Alpha#039 — 衰减动量 [动量] [流动性]
```
((-1 * rank((delta(close, 7) * (1 - rank(decay_linear((volume / adv20), 9)))))) * (1 + rank(sum(returns, 250))))
```
> 7日动量 × 成交量衰减活跃度 × 长期累积收益。

### Alpha#040 — 波动率×高价量相关 [波动率] [量价]
```
((-1 * rank(stddev(high, 10))) * correlation(high, volume, 10))
```
> 高价波动率排名 × 高价-量相关性。

### Alpha#041 — 几何均值偏离 [形态]
```
(((high * low)^0.5) - vwap)
```
> 最高价×最低价的几何均值 - VWAP。

### Alpha#042 — VWAP方向 [形态]
```
(rank((vwap - close)) / rank((vwap + close)))
```
> VWAP偏离方向的排名比。

### Alpha#043 — 量变×动量 [量价] [动量]
```
(ts_rank((volume / adv20), 20) * ts_rank((-1 * delta(close, 7)), 8))
```
> 成交量活跃度时序排名 × 7日反转时序排名。

### Alpha#044 — 高价量相关 [量价]
```
(-1 * correlation(high, rank(volume), 5))
```
> 最高价与成交量排名的5日负相关。

### Alpha#045 — 均线×量价×相关 [复合]
```
(-1 * ((rank((sum(delay(close, 5), 20) / 20)) * correlation(close, volume, 2)) * rank(correlation(sum(close, 5), sum(close, 20), 2))))
```
> 滞后均线排名 × 短期量价相关 × 短长期价格相关。

### Alpha#046 — 加速度条件 [动量]
```
((0.25 < (((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10))) ? (-1 * 1) : (((((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10)) < 0) ? 1 : ((-1 * 1) * (close - delay(close, 1)))))
```
> 价格加速度判断：减速→做空，加速→做多，否则反转。

### Alpha#047 — 流动性形态 [流动性] [形态]
```
((((rank((1 / close)) * volume) / adv20) * ((high * rank((high - close))) / (sum(high, 5) / 5))) - rank((vwap - delay(vwap, 5))))
```
> 价格倒数×量比 × 上影线×高价偏离 - VWAP动量。

### Alpha#048 ⚠️ 需行业中性化 [量价]
```
(indneutralize(((correlation(delta(close, 1), delta(delay(close, 1), 1), 250) * delta(close, 1)) / close), IndClass.subindustry) / sum(((delta(close, 1) / delay(close, 1))^2), 250))
```

### Alpha#049 — 加速度阈值 [动量]
```
(((((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10)) < (-1 * 0.1)) ? 1 : ((-1 * 1) * (close - delay(close, 1))))
```
> 加速度 < -0.1 时做多，否则反转。

### Alpha#050 — 量-VWAP相关 [量价]
```
(-1 * ts_max(rank(correlation(rank(volume), rank(vwap), 5)), 5))
```
> 成交量排名与VWAP排名的相关性的时序最大值取负。

### Alpha#051 — 加速度阈值（宽松版）[动量]
```
(((((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10)) < (-1 * 0.05)) ? 1 : ((-1 * 1) * (close - delay(close, 1))))
```
> Alpha#049的宽松阈值版（-0.05 vs -0.1）。

### Alpha#052 — 低价反转+长期动量 [反转] [动量]
```
((((-1 * ts_min(low, 5)) + delay(ts_min(low, 5), 5)) * rank(((sum(returns, 240) - sum(returns, 20)) / 220))) * ts_rank(volume, 5))
```
> 低价5日变化 × 长期vs短期收益 × 量排名。

### Alpha#053 — CLV变化 [形态]
```
(-1 * delta((((close - low) - (high - close)) / (close - low)), 9))
```
> Close Location Value 的9日变化取负。

### Alpha#054 — 日内形态 [形态]
```
((-1 * ((low - close) * (open^5))) / ((low - high) * (close^5)))
```
> 复杂的OHLC价格关系表达。

### Alpha#055 — 价格位置×量 [量价] [形态]
```
(-1 * correlation(rank(((close - ts_min(low, 12)) / (ts_max(high, 12) - ts_min(low, 12)))), rank(volume), 6))
```
> 12日价格位置（类Williams%R） vs 成交量的相关性取负。

### Alpha#056 — 累积收益+市值 [动量]
```
(0 - (1 * (rank((sum(returns, 10) / sum(sum(returns, 2), 3))) * rank((returns * cap)))))
```
> 收益率动量 × 收益率×市值。

### Alpha#057 — 收盘偏离VWAP [形态]
```
(0 - (1 * ((close - vwap) / decay_linear(rank(ts_argmax(close, 30)), 2))))
```
> 收盘偏离VWAP / 30日最高价位置的衰减。

### Alpha#058 ⚠️ 需行业中性化 [量价]
```
(-1 * Ts_Rank(decay_linear(correlation(IndNeutralize(vwap, IndClass.sector), volume, 3.92795), 7.89291), 5.50322))
```

### Alpha#059 ⚠️ 需行业中性化 [量价]
```
(-1 * Ts_Rank(decay_linear(correlation(IndNeutralize(((vwap * 0.728317) + (vwap * (1 - 0.728317))), IndClass.industry), volume, 4.25197), 16.2289), 8.19648))
```

### Alpha#060 — CLV×量标准化 [量价] [形态]
```
(0 - (1 * ((2 * scale(rank(((((close - low) - (high - close)) / (high - low)) * volume)))) - scale(rank(ts_argmax(close, 10))))))
```
> CLV×量的标准化 - 10日最高价位置标准化。

### Alpha#061 — VWAP位置 vs 量价相关 [量价]
```
(rank((vwap - ts_min(vwap, 16.1219))) < rank(correlation(vwap, adv180, 17.9282)))
```

### Alpha#062 — 量-价格相关 [量价]
```
((rank(correlation(vwap, sum(adv20, 22.4101), 9.91009)) < rank(((rank(open) + rank(open)) < (rank(((high + low) / 2)) + rank(high))))) * -1)
```

### Alpha#063 ⚠️ 需行业中性化 [动量]
```
((rank(decay_linear(delta(IndNeutralize(close, IndClass.industry), 2.25164), 8.22237)) - rank(decay_linear(correlation(((vwap * 0.318108) + (open * (1 - 0.318108))), sum(adv180, 37.2467), 13.557), 12.2883))) * -1)
```

### Alpha#064 — 加权价格-量相关 [量价]
```
((rank(correlation(sum(((open * 0.178404) + (low * (1 - 0.178404))), 12.7054), sum(adv120, 12.7054), 16.6208)) < rank(delta(((((high + low) / 2) * 0.178404) + (vwap * (1 - 0.178404))), 3.69741))) * -1)
```

### Alpha#065 — 加权价格-量相关2 [量价]
```
((rank(correlation(((open * 0.00817205) + (vwap * (1 - 0.00817205))), sum(adv60, 8.6911), 6.40374)) < rank((open - ts_min(open, 13.635)))) * -1)
```

### Alpha#066 — VWAP变化+形态 [形态]
```
((rank(decay_linear(delta(vwap, 3.51013), 7.23052)) + Ts_Rank(decay_linear(((((low * 0.96633) + (low * (1 - 0.96633))) - vwap) / (open - ((high + low) / 2))), 11.4157), 6.72611)) * -1)
```

### Alpha#067 ⚠️ 需行业中性化 [形态]
```
((rank((high - ts_min(high, 2.14593)))^rank(correlation(IndNeutralize(vwap, IndClass.sector), IndNeutralize(adv20, IndClass.subindustry), 6.02936))) * -1)
```

### Alpha#068 — 量-价格条件 [量价]
```
((Ts_Rank(correlation(rank(high), rank(adv15), 8.91644), 13.9333) < rank(delta(((close * 0.518371) + (low * (1 - 0.518371))), 1.06157))) * -1)
```

### Alpha#069 ⚠️ 需行业中性化 [动量]
```
((rank(ts_max(delta(IndNeutralize(vwap, IndClass.industry), 2.72412), 4.79344))^Ts_Rank(correlation(((close * 0.490655) + (vwap * (1 - 0.490655))), adv20, 4.92416), 9.0615)) * -1)
```

### Alpha#070 ⚠️ 需行业中性化 [动量]
```
((rank(delta(vwap, 1.29456))^Ts_Rank(correlation(IndNeutralize(close, IndClass.industry), adv50, 17.8256), 17.9171)) * -1)
```

### Alpha#071 — max(衰减相关, 衰减形态) [复合]
```
max(Ts_Rank(decay_linear(correlation(Ts_Rank(close, 3.43976), Ts_Rank(adv180, 12.0647), 18.0175), 4.20501), 15.6948), Ts_Rank(decay_linear((rank(((low + open) - (vwap + vwap)))^2), 16.4662), 4.4388))
```

### Alpha#072 — 量价衰减相关比 [量价]
```
(rank(decay_linear(correlation(((high + low) / 2), adv40, 8.93345), 10.1519)) / rank(decay_linear(correlation(Ts_Rank(vwap, 3.72469), Ts_Rank(volume, 18.5188), 6.86671), 2.95011)))
```

### Alpha#073 — VWAP变化+加权低价变化 [形态]
```
(max(rank(decay_linear(delta(vwap, 4.72775), 2.91864)), Ts_Rank(decay_linear(((delta(((open * 0.147155) + (low * (1 - 0.147155))), 2.03608) / ((open * 0.147155) + (low * (1 - 0.147155)))) * -1), 3.33829), 16.7411)) * -1)
```

### Alpha#074 — 量-价相关 [量价]
```
((rank(correlation(close, sum(adv30, 37.4843), 15.1365)) < rank(correlation(rank(((high * 0.0261661) + (vwap * (1 - 0.0261661)))), rank(volume), 11.4791))) * -1)
```

### Alpha#075 — VWAP-量相关 vs 低价-量相关 [量价]
```
(rank(correlation(vwap, volume, 4.24304)) < rank(correlation(rank(low), rank(adv50), 12.4413)))
```

### Alpha#076 ⚠️ 需行业中性化 [动量]
```
(max(rank(decay_linear(delta(vwap, 1.24383), 11.8259)), Ts_Rank(decay_linear(Ts_Rank(correlation(IndNeutralize(low, IndClass.sector), adv81, 8.14941), 19.569), 17.1543), 19.383)) * -1)
```

### Alpha#077 — 价格形态+量 [形态] [量价]
```
min(rank(decay_linear(((((high + low) / 2) + high) - (vwap + high)), 20.0451)), rank(decay_linear(correlation(((high + low) / 2), adv40, 3.1614), 5.64125)))
```

### Alpha#078 — 加权价格-量幂相关 [量价]
```
(rank(correlation(sum(((low * 0.352233) + (vwap * (1 - 0.352233))), 19.7428), sum(adv40, 19.7428), 6.83313))^rank(correlation(rank(vwap), rank(volume), 5.77492)))
```

### Alpha#079 ⚠️ 需行业中性化 [动量]
```
(rank(delta(IndNeutralize(((close * 0.60733) + (open * (1 - 0.60733))), IndClass.sector), 1.23438)) < rank(correlation(Ts_Rank(vwap, 3.60973), Ts_Rank(adv150, 9.18637), 14.6644)))
```

### Alpha#080 ⚠️ 需行业中性化 [动量]
```
((rank(Sign(delta(IndNeutralize(((open * 0.868128) + (high * (1 - 0.868128))), IndClass.industry), 4.04545)))^Ts_Rank(correlation(high, adv10, 5.11456), 5.53756)) * -1)
```

### Alpha#081 ⚠️ 需行业中性化 [量价]
```
((rank(Log(product(rank((rank(correlation(vwap, sum(adv10, 49.6054), 8.47743))^4)), 14.9655))) < rank(correlation(rank(vwap), rank(volume), 5.07914))) * -1)
```

### Alpha#082 ⚠️ 需行业中性化 [动量]
```
(min(rank(decay_linear(delta(open, 1.46063), 14.8717)), Ts_Rank(decay_linear(correlation(IndNeutralize(volume, IndClass.sector), ((open * 0.634196) + (open * (1 - 0.634196))), 17.4842), 6.92131), 13.4283)) * -1)
```

### Alpha#083 — 延迟形态×量 [形态] [量价]
```
((rank(delay(((high - low) / (sum(close, 5) / 5)), 2)) * rank(rank(volume))) / (((high - low) / (sum(close, 5) / 5)) / (vwap - close)))
```

### Alpha#084 — VWAP位置幂 [形态]
```
SignedPower(Ts_Rank((vwap - ts_max(vwap, 15.3217)), 20.7127), delta(close, 4.96796))
```

### Alpha#085 — 加权高价-量幂 [量价]
```
(rank(correlation(((high * 0.876703) + (close * (1 - 0.876703))), adv30, 9.61331))^rank(correlation(Ts_Rank(((high + low) / 2), 3.70596), Ts_Rank(volume, 10.1595), 7.11408)))
```

### Alpha#086 — 量-价条件 [量价]
```
((Ts_Rank(correlation(close, sum(adv20, 14.7444), 6.00049), 20.4195) < rank(((open + close) - (vwap + open)))) * -1)
```

### Alpha#087 ⚠️ 需行业中性化 [动量]
```
(max(rank(decay_linear(delta(((close * 0.369701) + (vwap * (1 - 0.369701))), 1.91233), 2.65461)), Ts_Rank(decay_linear(abs(correlation(IndNeutralize(adv81, IndClass.industry), close, 13.4132)), 4.89768), 14.4535)) * -1)
```

### Alpha#088 — 衰减相关组合 [复合]
```
min(rank(decay_linear(((rank(open) + rank(low)) - (rank(high) + rank(close))), 8.06882)), Ts_Rank(decay_linear(correlation(Ts_Rank(close, 8.44728), Ts_Rank(adv60, 20.6966), 8.01266), 6.65053), 2.61957))
```

### Alpha#089 ⚠️ 需行业中性化 [量价]
```
(Ts_Rank(decay_linear(correlation(((low * 0.967285) + (low * (1 - 0.967285))), adv10, 6.94279), 5.51607), 3.79744) - Ts_Rank(decay_linear(delta(IndNeutralize(vwap, IndClass.industry), 3.48158), 10.1466), 15.3012))
```

### Alpha#090 ⚠️ 需行业中性化 [反转]
```
((rank((close - ts_max(close, 4.66719)))^Ts_Rank(correlation(IndNeutralize(adv40, IndClass.subindustry), low, 5.38375), 3.21856)) * -1)
```

### Alpha#091 ⚠️ 需行业中性化 [量价]
```
((Ts_Rank(decay_linear(decay_linear(correlation(IndNeutralize(close, IndClass.industry), volume, 9.74928), 16.398), 3.83219), 4.8667) - rank(decay_linear(correlation(vwap, adv30, 4.01303), 2.6809))) * -1)
```

### Alpha#092 — min(衰减条件, 衰减相关) [复合]
```
min(Ts_Rank(decay_linear(((((high + low) / 2) + close) < (low + open)), 14.7221), 18.8683), Ts_Rank(decay_linear(correlation(rank(low), rank(adv30), 7.58555), 6.94024), 6.80584))
```

### Alpha#093 ⚠️ 需行业中性化 [量价]
```
(Ts_Rank(decay_linear(correlation(IndNeutralize(vwap, IndClass.industry), adv81, 17.4193), 19.848), 7.54455) / rank(decay_linear(delta(((close * 0.524434) + (vwap * (1 - 0.524434))), 2.77377), 16.2664)))
```

### Alpha#094 — VWAP位置幂相关 [量价]
```
((rank((vwap - ts_min(vwap, 11.5783)))^Ts_Rank(correlation(Ts_Rank(vwap, 19.6462), Ts_Rank(adv60, 4.02992), 18.0926), 2.70756)) * -1)
```

### Alpha#095 — 开盘位置 vs 量价相关 [量价]
```
(rank((open - ts_min(open, 12.4105))) < Ts_Rank((rank(correlation(sum(((high + low) / 2), 19.1351), sum(adv40, 19.1351), 12.8742))^5), 11.7584))
```

### Alpha#096 — max(量-VWAP相关, 时序极值相关) [量价] [复合]
```
(max(Ts_Rank(decay_linear(correlation(rank(vwap), rank(volume), 3.83878), 4.16783), 8.38151), Ts_Rank(decay_linear(Ts_ArgMax(correlation(Ts_Rank(close, 7.45404), Ts_Rank(adv60, 4.13242), 3.65459), 12.6556), 14.0365), 13.4143)) * -1)
```

### Alpha#097 ⚠️ 需行业中性化 [量价]
```
((rank(decay_linear(delta(IndNeutralize(((low * 0.721001) + (vwap * (1 - 0.721001))), IndClass.industry), 3.3705), 20.4523)) - Ts_Rank(decay_linear(Ts_Rank(correlation(Ts_Rank(low, 7.87871), Ts_Rank(adv60, 17.255), 4.97547), 18.5925), 15.7152), 6.71659)) * -1)
```

### Alpha#098 — 衰减量-价相关 [量价]
```
(rank(decay_linear(correlation(vwap, sum(adv5, 26.4719), 4.58418), 7.18088)) - rank(decay_linear(Ts_Rank(Ts_ArgMin(correlation(rank(open), rank(adv15), 20.8187), 8.62571), 6.95668), 8.07206)))
```

### Alpha#099 — 中间价-量相关 [量价]
```
((rank(correlation(sum(((high + low) / 2), 19.8975), sum(adv60, 19.8975), 8.8136)) < rank(correlation(low, volume, 6.28259))) * -1)
```

### Alpha#100 ⚠️ 需行业中性化 [量价]
```
(0 - (1 * (((1.5 * scale(indneutralize(indneutralize(rank(((((close - low) - (high - close)) / (high - low)) * volume)), IndClass.subindustry), IndClass.subindustry))) - scale(indneutralize((correlation(close, rank(adv20), 5) - rank(ts_argmin(close, 30))), IndClass.subindustry))) * (volume / adv20))))
```

### Alpha#101 — 日内方向强度 [形态]
```
((close - open) / ((high - low) + .001))
```
> 日内涨跌幅 / 日内振幅。度量收盘方向强度，类似上影线/下影线的量化表达。

---

## 统计摘要

| 分类 | 数量 |
|------|------|
| 可直接实现 | **80 个** |
| 需行业中性化（IndNeutralize） | **21 个**（#048, #058, #059, #063, #067, #069, #070, #076, #079, #080, #081, #082, #087, #089, #090, #091, #093, #097, #100）|
| 量价关系类 | ~30 个 |
| 动量/反转类 | ~25 个 |
| 波动率类 | ~10 个 |
| 价格形态类 | ~20 个 |
| 复合因子 | ~16 个 |
