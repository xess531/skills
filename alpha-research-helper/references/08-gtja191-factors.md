# 国泰君安 191 Alpha — 完整因子公式

> 来源：国泰君安 (2017). 《基于短周期价量特征的多因子选股体系》
> 分类标签：[量价] [动量] [反转] [波动率] [形态] [流动性] [技术指标:RSI] [技术指标:KDJ] [技术指标:MACD] [技术指标:OBV] [技术指标:DMI] [技术指标:CCI] [基准相对] [趋势强度]

---

## 因子列表

### Alpha#001 — 量价背离 [量价] ≈WQ101#002
```
(-1 * CORR(RANK(DELTA(LOG(VOLUME), 1)), RANK(((CLOSE - OPEN) / OPEN)), 6))
```
> 成交量对数变化 vs 日内涨幅的6日相关性取负。

### Alpha#002 — CLV变化 [形态]
```
(-1 * DELTA((((CLOSE - LOW) - (HIGH - CLOSE)) / (HIGH - LOW)), 1))
```
> Close Location Value 的1日变化取负。

### Alpha#003 — 条件累积变化 [动量]
```
SUM((CLOSE=DELAY(CLOSE,1)?0:CLOSE-(CLOSE>DELAY(CLOSE,1)?MIN(LOW,DELAY(CLOSE,1)):MAX(HIGH,DELAY(CLOSE,1)))),6)
```
> 6日条件价格变化累积。上涨时取(CLOSE-MIN(LOW,前收))，下跌时取(CLOSE-MAX(HIGH,前收))。

### Alpha#004 — 条件量价 [量价] ≈WQ101#021
```
((((SUM(CLOSE, 8) / 8) + STD(CLOSE, 8)) < (SUM(CLOSE, 2) / 2)) ? (-1 * 1) : (((SUM(CLOSE, 2) / 2) < ((SUM(CLOSE, 8) / 8) - STD(CLOSE, 8))) ? 1 : (((1 < (VOLUME / MEAN(VOLUME,20))) || ((VOLUME / MEAN(VOLUME,20)) == 1)) ? 1 : (-1 * 1))))
```
> 多层条件判断：价格位置 + 波动率 + 成交量活跃度。

### Alpha#005 — 量价排名相关 [量价] =WQ101#026
```
(-1 * TSMAX(CORR(TSRANK(VOLUME, 5), TSRANK(HIGH, 5), 5), 3))
```
> 成交量时序排名与最高价时序排名的相关性极值取负。

### Alpha#006 — 加权价格方向 [形态]
```
(RANK(SIGN(DELTA((((OPEN * 0.85) + (HIGH * 0.15))), 4))) * -1)
```
> 加权(开盘+最高)价格的4日方向取负。

### Alpha#007 — VWAP偏离+量变 [量价] ≈WQ101#011
```
((RANK(MAX((VWAP - CLOSE), 3)) + RANK(MIN((VWAP - CLOSE), 3))) * RANK(DELTA(VOLUME, 3)))
```

### Alpha#008 — 加权价格动量 [动量]
```
RANK(DELTA(((((HIGH + LOW) / 2) * 0.2) + (VWAP * 0.8)), 4) * -1)
```
> 加权(中间价+VWAP)的4日反转。

### Alpha#009 — 量价动量SMA [量价]
```
SMA(((HIGH+LOW)/2-(DELAY(HIGH,1)+DELAY(LOW,1))/2)*(HIGH-LOW)/VOLUME,7,2)
```
> 中间价变化 × 振幅 / 成交量的SMA平滑。

### Alpha#010 — 条件波动率 [波动率] ≈WQ101#001
```
(RANK(MAX(((RET < 0) ? STD(RET, 20) : CLOSE)^2), 5))
```

### Alpha#011 — CLV×成交量 [量价] [技术指标:OBV]
```
SUM(((CLOSE-LOW)-(HIGH-CLOSE))/(HIGH-LOW)*VOLUME,6)
```
> CLV (Close Location Value) × Volume 的6日累积。OBV变种。

### Alpha#012 — 开盘-VWAP偏离 [形态] ≈WQ101#005
```
(RANK((OPEN - (SUM(VWAP, 10) / 10)))) * (-1 * (RANK(ABS((CLOSE - VWAP)))))
```

### Alpha#013 — 几何均值-VWAP [形态] =WQ101#041
```
(((HIGH * LOW)^0.5) - VWAP)
```

### Alpha#014 — 5日动量 [动量]
```
CLOSE - DELAY(CLOSE, 5)
```
> 最简单的5日价格动量。

### Alpha#015 — 隔夜收益 [形态]
```
OPEN / DELAY(CLOSE, 1) - 1
```
> 隔夜跳空收益率。

### Alpha#016 — 量-VWAP排名相关 [量价]
```
(-1 * TSMAX(RANK(CORR(RANK(VOLUME), RANK(VWAP), 5)), 5))
```

### Alpha#017 — VWAP位置幂 [形态]
```
RANK((VWAP - MAX(VWAP, 15)))^DELTA(CLOSE, 5)
```

### Alpha#018 — 5日收益比 [动量]
```
CLOSE / DELAY(CLOSE, 5)
```

### Alpha#019 — 条件动量 [动量]
```
(CLOSE<DELAY(CLOSE,5)?(CLOSE-DELAY(CLOSE,5))/DELAY(CLOSE,5):(CLOSE=DELAY(CLOSE,5)?0:(CLOSE-DELAY(CLOSE,5))/CLOSE))
```
> 下跌时除以前价，上涨时除以现价。非对称动量。

### Alpha#020 — 6日收益率 [动量]
```
(CLOSE - DELAY(CLOSE, 6)) / DELAY(CLOSE, 6) * 100
```

### Alpha#021 — 价格回归斜率（6日）[趋势强度]
```
REGBETA(MEAN(CLOSE, 6), SEQUENCE(6))
```
> **191独有**。6日收盘价均值对时间的线性回归斜率→短期趋势强度。

### Alpha#022 — BIAS偏离SMA [形态] [反转]
```
SMA(((CLOSE-MEAN(CLOSE,6))/MEAN(CLOSE,6)-DELAY((CLOSE-MEAN(CLOSE,6))/MEAN(CLOSE,6),3)),12,1)
```
> BIAS(6日)偏离的变化率的SMA平滑。

### Alpha#023 — RSI波动率版 [技术指标:RSI] [波动率]
```
SMA((CLOSE>DELAY(CLOSE,1)?STD(CLOSE,20):0),20,1) / (SMA((CLOSE>DELAY(CLOSE,1)?STD(CLOSE,20):0),20,1) + SMA((CLOSE<=DELAY(CLOSE,1)?STD(CLOSE,20):0),20,1)) * 100
```
> **191独有**。非标准RSI：上涨日用波动率替代涨幅→捕捉"高波动上涨"。

### Alpha#024 — 5日变化SMA [动量]
```
SMA(CLOSE - DELAY(CLOSE, 5), 5, 1)
```

### Alpha#025 — 衰减动量 [动量] ≈WQ101#039
```
((-1 * RANK((DELTA(CLOSE, 7) * (1 - RANK(DECAYLINEAR((VOLUME/MEAN(VOLUME,20)), 9)))))) * (1 + RANK(SUM(RET, 250))))
```

### Alpha#026 — 均值回归+VWAP相关 [反转]
```
((((SUM(CLOSE, 7) / 7) - CLOSE)) + ((CORR(VWAP, DELAY(CLOSE, 5), 230))))
```

### Alpha#027 — 加权动量WMA [动量]
```
WMA((CLOSE-DELAY(CLOSE,3))/DELAY(CLOSE,3)*100+(CLOSE-DELAY(CLOSE,6))/DELAY(CLOSE,6)*100,12)
```
> **191独有**。3日+6日动量的WMA加权平均。

### Alpha#028 — KDJ变种（3K-2D）[技术指标:KDJ]
```
3*SMA((CLOSE-TSMIN(LOW,9))/(TSMAX(HIGH,9)-TSMIN(LOW,9))*100,3,1) - 2*SMA(SMA((CLOSE-TSMIN(LOW,9))/(TSMAX(HIGH,9)-TSMIN(LOW,9))*100,3,1),3,1)
```
> **191独有**。3K-2D的KDJ组合，强调超买超卖偏离。

### Alpha#029 — 量价动量 [量价] [动量]
```
(CLOSE - DELAY(CLOSE, 6)) / DELAY(CLOSE, 6) * VOLUME
```
> 6日收益率 × 成交量。

### Alpha#030 — Fama-French残差波动 [波动率]
```
WMA((REGRESI(CLOSE/DELAY(CLOSE)-1, MKT, SMB, HML, 60))^2, 20)
```
> **191独有**。FF3残差的平方的WMA→特质波动率(IVOL)的替代计算。需要FF3因子数据。

### Alpha#031 — BIAS(12日) [形态] [反转]
```
(CLOSE - MEAN(CLOSE, 12)) / MEAN(CLOSE, 12) * 100
```
> 12日乖离率。

### Alpha#032 — 高价-量排名相关 [量价] ≈WQ101#015
```
(-1 * SUM(RANK(CORR(RANK(HIGH), RANK(VOLUME), 3)), 3))
```

### Alpha#033 — 低价变化+动量 [动量] ≈WQ101#052
```
((((-1 * TSMIN(LOW, 5)) + DELAY(TSMIN(LOW, 5), 5)) * RANK(((SUM(RET, 240) - SUM(RET, 20)) / 220))) * TSRANK(VOLUME, 5))
```

### Alpha#034 — 均值/现价比 [反转]
```
MEAN(CLOSE, 12) / CLOSE
```
> 12日均线/现价。>1 表示低于均线，<1 表示高于均线。

### Alpha#035 — 加权低价-量衰减 [量价]
```
(MIN(RANK(DECAYLINEAR(DELTA(OPEN, 1), 15)), RANK(DECAYLINEAR(CORR((VOLUME), ((OPEN * 0.65) + (OPEN * 0.35)), 17), 7))) * -1)
```

### Alpha#036 — 量-VWAP排名相关累积 [量价]
```
RANK(SUM(CORR(RANK(VOLUME), RANK(VWAP)), 6), 2)
```

### Alpha#037 — 开盘×收益动量 [动量] ≈WQ101#008
```
(-1 * RANK(((SUM(OPEN, 5) * SUM(RET, 5)) - DELAY((SUM(OPEN, 5) * SUM(RET, 5)), 10))))
```

### Alpha#038 — 高位反转 [反转] =WQ101#023
```
(((SUM(HIGH, 20) / 20) < HIGH) ? (-1 * DELTA(HIGH, 2)) : 0)
```

### Alpha#039 — 加权价格-VWAP衰减 [形态]
```
((RANK(DECAYLINEAR(DELTA((CLOSE), 2), 8)) - RANK(DECAYLINEAR(CORR(((VWAP * 0.3) + (OPEN * 0.7)), SUM(MEAN(VOLUME,180), 37), 14), 12))) * -1)
```

### Alpha#040 — OBV方向比 [技术指标:OBV] [量价]
```
SUM((CLOSE>DELAY(CLOSE,1)?VOLUME:0),26) / SUM((CLOSE<=DELAY(CLOSE,1)?VOLUME:0),26) * 100
```
> 上涨日成交量/下跌日成交量的26日比率。OBV变种。

### Alpha#041 — VWAP动量 [动量]
```
(RANK(MAX(DELTA((VWAP), 3), 5)) * -1)
```

### Alpha#042 — 波动率×高价量相关 [波动率] [量价] =WQ101#040
```
((-1 * RANK(STD(HIGH, 10))) * CORR(HIGH, VOLUME, 10))
```

### Alpha#043 — OBV(6日) [技术指标:OBV]
```
SUM((CLOSE>DELAY(CLOSE,1)?VOLUME:(CLOSE<DELAY(CLOSE,1)?-VOLUME:0)),6)
```
> 6日OBV：上涨日加量，下跌日减量。

### Alpha#044 — 低价-量衰减相关 [量价]
```
(TSRANK(DECAYLINEAR(CORR(((LOW)), MEAN(VOLUME,10), 7), 6), 4) + TSRANK(DECAYLINEAR(DELTA((VWAP), 3), 10), 15))
```

### Alpha#045 — 加权收盘动量×量 [动量] [量价]
```
(RANK(DELTA((((CLOSE * 0.6) + (OPEN * 0.4))), 1)) * RANK(CORR(VWAP, MEAN(VOLUME,150), 15)))
```

### Alpha#046 — 多周期均线比 [形态]
```
(MEAN(CLOSE,3)+MEAN(CLOSE,6)+MEAN(CLOSE,12)+MEAN(CLOSE,24))/(4*CLOSE)
```
> **191独有**。多周期(3/6/12/24日)均线的平均 / 现价。

### Alpha#047 — WR威廉指标 [技术指标:KDJ]
```
SMA((TSMAX(HIGH,6)-CLOSE)/(TSMAX(HIGH,6)-TSMIN(LOW,6))*100,9,1)
```
> 6日WR(Williams %R)的SMA(9,1)平滑。

### Alpha#048 — 连续涨跌方向 [动量] ≈WQ101#030
```
(-1*((RANK(((SIGN((CLOSE-DELAY(CLOSE,1))) + SIGN((DELAY(CLOSE,1)-DELAY(CLOSE,2)))) + SIGN((DELAY(CLOSE,2)-DELAY(CLOSE,3)))))) * SUM(VOLUME,5)) / SUM(VOLUME,20))
```

### Alpha#049 — DTM/DBM方向（上） [技术指标:DMI]
```
SUM(((HIGH+LOW)>=(DELAY(HIGH,1)+DELAY(LOW,1))?0:MAX(ABS(HIGH-DELAY(HIGH,1)),ABS(LOW-DELAY(LOW,1)))),12) / (SUM(...上涨,12)+SUM(...下跌,12))
```
> **191独有**。DMI中间变量DTM/DBM的比率。

### Alpha#050 — DTM/DBM方向差 [技术指标:DMI]
```
Alpha#051 - Alpha#049
```
> **191独有**。下跌方向占比 - 上涨方向占比。

### Alpha#051 — DTM/DBM方向（下） [技术指标:DMI]
```
SUM(下跌,12) / (SUM(下跌,12)+SUM(上涨,12))
```
> **191独有**。DMI下跌方向占比。

### Alpha#052 — CR中间意愿指标 [形态]
```
SUM(MAX(0,HIGH-DELAY((HIGH+LOW+CLOSE)/3,1)),26) / SUM(MAX(0,DELAY((HIGH+LOW+CLOSE)/3,1)-LOW),26) * 100
```
> **191独有**。CR指标：压力/支撑比。

### Alpha#053 — 上涨天数占比 [动量]
```
COUNT(CLOSE>DELAY(CLOSE,1),12)/12*100
```
> **191独有**。12日内上涨天数百分比。

### Alpha#054 — 波动率+日内形态 [波动率] ≈WQ101#018
```
(-1 * RANK((STD(ABS(CLOSE-OPEN)) + (CLOSE-OPEN)) + CORR(CLOSE,OPEN,10)))
```

### Alpha#055 — CR变种 [形态]
```
SUM(16*(CLOSE-DELAY(CLOSE,1)+(CLOSE-OPEN)/2+DELAY(CLOSE,1)-DELAY(OPEN,1))/...,20)
```
> **191独有**。复杂的CR/SAR变种，包含多层条件价格关系。

### Alpha#056 — 开盘位置 vs 量价相关 [量价] ≈WQ101#095
```
(RANK((OPEN - TSMIN(OPEN, 12))) < RANK((RANK(CORR(SUM(((HIGH + LOW) / 2), 19), SUM(MEAN(VOLUME,40), 19), 13))^5)))
```

### Alpha#057 — K值（KDJ的K） [技术指标:KDJ]
```
SMA((CLOSE-TSMIN(LOW,9))/(TSMAX(HIGH,9)-TSMIN(LOW,9))*100,3,1)
```
> **191独有**。标准KDJ中的K值。

### Alpha#058 — 上涨天数占比(20日) [动量]
```
COUNT(CLOSE>DELAY(CLOSE,1),20)/20*100
```
> **191独有**。20日内上涨天数百分比。

### Alpha#059 — 条件累积(20日) [动量]
```
SUM((CLOSE=DELAY(CLOSE,1)?0:CLOSE-(CLOSE>DELAY(CLOSE,1)?MIN(LOW,DELAY(CLOSE,1)):MAX(HIGH,DELAY(CLOSE,1)))),20)
```
> Alpha#003的20日版本。

### Alpha#060 — CLV×成交量(20日) [量价] [技术指标:OBV]
```
SUM(((CLOSE-LOW)-(HIGH-CLOSE))/(HIGH-LOW)*VOLUME,20)
```
> Alpha#011的20日版本。

### Alpha#061 — 衰减量价组合 [量价]
```
(MAX(RANK(DECAYLINEAR(DELTA(VWAP, 1), 12)), RANK(DECAYLINEAR(RANK(CORR((LOW), MEAN(VOLUME,80), 8)), 17))) * -1)
```

### Alpha#062 — 高价-量排名相关 [量价] ≈WQ101#044
```
(-1 * CORR(HIGH, RANK(VOLUME), 5))
```

### Alpha#063 — RSI(6日) [技术指标:RSI]
```
SMA(MAX(CLOSE-DELAY(CLOSE,1),0),6,1) / SMA(ABS(CLOSE-DELAY(CLOSE,1)),6,1) * 100
```
> **191独有**。标准6日RSI。

### Alpha#064 — 衰减量价组合2 [量价]
```
(MAX(RANK(DECAYLINEAR(CORR(RANK(VWAP), RANK(VOLUME), 4), 4)), RANK(DECAYLINEAR(MAX(CORR(RANK(CLOSE), RANK(MEAN(VOLUME,60)), 4), 13), 14))) * -1)
```

### Alpha#065 — BIAS(6日)/现价比 [反转]
```
MEAN(CLOSE, 6) / CLOSE
```
> 6日均线/现价。

### Alpha#066 — BIAS(6日) [形态] [反转]
```
(CLOSE - MEAN(CLOSE, 6)) / MEAN(CLOSE, 6) * 100
```
> 6日乖离率(%)。

### Alpha#067 — RSI(24日) [技术指标:RSI]
```
SMA(MAX(CLOSE-DELAY(CLOSE,1),0),24,1) / SMA(ABS(CLOSE-DELAY(CLOSE,1)),24,1) * 100
```
> **191独有**。标准24日RSI。

### Alpha#068 — 量价动量SMA(15日) [量价]
```
SMA(((HIGH+LOW)/2-(DELAY(HIGH,1)+DELAY(LOW,1))/2)*(HIGH-LOW)/VOLUME,15,2)
```
> Alpha#009的15日版本。

### Alpha#069 — DTM/DBM条件 [技术指标:DMI]
```
(SUM(DTM,20)>SUM(DBM,20) ? (SUM(DTM,20)-SUM(DBM,20))/SUM(DTM,20) : (SUM(DTM,20)=SUM(DBM,20) ? 0 : (SUM(DTM,20)-SUM(DBM,20))/SUM(DBM,20)))
```
> **191独有**。DTM/DBM的条件比较，DMI方向指标。

### Alpha#070 — 成交额波动率 [波动率]
```
STD(AMOUNT, 6)
```
> **191独有**。6日成交额标准差。

### Alpha#071 — BIAS(24日) [反转]
```
(CLOSE - MEAN(CLOSE, 24)) / MEAN(CLOSE, 24) * 100
```
> 24日乖离率。

### Alpha#072 — WR(15日SMA) [技术指标:KDJ]
```
SMA((TSMAX(HIGH,6)-CLOSE)/(TSMAX(HIGH,6)-TSMIN(LOW,6))*100,15,1)
```
> Alpha#047的15日SMA版本。

### Alpha#073 — 衰减相关组合 [复合]
```
((TSRANK(DECAYLINEAR(DECAYLINEAR(CORR((CLOSE), VOLUME, 10), 16), 4), 5) - RANK(DECAYLINEAR(CORR(VWAP, MEAN(VOLUME,30), 4), 3))) * -1)
```

### Alpha#074 — 加权低价-量相关 [量价]
```
(RANK(CORR(SUM(((LOW * 0.35) + (VWAP * 0.65)), 20), SUM(MEAN(VOLUME,40), 20), 7)) + RANK(CORR(RANK(VWAP), RANK(VOLUME), 6)))
```

### Alpha#075 — 逆市上涨比 [基准相对]
```
COUNT(CLOSE>OPEN & BANCHMARKINDEXCLOSE<BANCHMARKINDEXOPEN, 50) / COUNT(BANCHMARKINDEXCLOSE<BANCHMARKINDEXOPEN, 50)
```
> **191独有**。50日内指数下跌日中个股上涨的比例→抗跌能力指标。

### Alpha#076 — 量价冲击 [波动率] [流动性]
```
STD(ABS((CLOSE/DELAY(CLOSE,1)-1))/VOLUME,20) / MEAN(ABS((CLOSE/DELAY(CLOSE,1)-1))/VOLUME,20)
```
> **191独有**。单位成交量带来的价格变化的变异系数→市场冲击不稳定性。

### Alpha#077 — 价格形态+量 [形态] ≈WQ101#077
```
MIN(RANK(DECAYLINEAR(((((HIGH + LOW) / 2) + HIGH) - (VWAP + HIGH)), 20)), RANK(DECAYLINEAR(CORR(((HIGH + LOW) / 2), MEAN(VOLUME,40), 3), 6)))
```

### Alpha#078 — CCI商品通道 [技术指标:CCI]
```
((HIGH+LOW+CLOSE)/3 - MA((HIGH+LOW+CLOSE)/3,12)) / (0.015*MEAN(ABS(CLOSE-MEAN((HIGH+LOW+CLOSE)/3,12)),12))
```
> **191独有**。标准CCI(12日)指标。

### Alpha#079 — RSI(12日) [技术指标:RSI]
```
SMA(MAX(CLOSE-DELAY(CLOSE,1),0),12,1) / SMA(ABS(CLOSE-DELAY(CLOSE,1)),12,1) * 100
```
> **191独有**。12日RSI。

### Alpha#080 — 成交量动量 [流动性]
```
(VOLUME - DELAY(VOLUME, 5)) / DELAY(VOLUME, 5) * 100
```
> 5日成交量变化率。

### Alpha#081 — 成交量SMA [流动性]
```
SMA(VOLUME, 21, 2)
```
> 成交量的21日SMA平滑。

### Alpha#082 — WR(20日SMA) [技术指标:KDJ]
```
SMA((TSMAX(HIGH,6)-CLOSE)/(TSMAX(HIGH,6)-TSMIN(LOW,6))*100,20,1)
```
> Alpha#047的20日SMA版本。

### Alpha#083 — 高价-量协方差 [量价] ≈WQ101#016
```
(-1 * RANK(COVIANCE(RANK(HIGH), RANK(VOLUME), 5)))
```

### Alpha#084 — OBV(20日) [技术指标:OBV]
```
SUM((CLOSE>DELAY(CLOSE,1)?VOLUME:(CLOSE<DELAY(CLOSE,1)?-VOLUME:0)),20)
```
> 20日OBV。

### Alpha#085 — 量比×动量 [量价] [动量]
```
(TSRANK((VOLUME / MEAN(VOLUME,20)), 20) * TSRANK((-1 * DELTA(CLOSE, 7)), 8))
```

### Alpha#086 — 加速度条件 [动量] ≈WQ101#046
```
((0.25 < ...) ? (-1 * 1) : ((... < 0) ? 1 : ((-1 * 1) * (CLOSE - DELAY(CLOSE, 1)))))
```

### Alpha#087 — VWAP变化+形态 [形态]
```
((RANK(DECAYLINEAR(DELTA(VWAP, 4), 7)) + TSRANK(DECAYLINEAR(((((LOW * 0.9) + (LOW * 0.1)) - VWAP) / (OPEN - ((HIGH + LOW) / 2))), 11), 7)) * -1)
```

### Alpha#088 — 20日收益率 [动量]
```
(CLOSE - DELAY(CLOSE, 20)) / DELAY(CLOSE, 20) * 100
```

### Alpha#089 — MACD [技术指标:MACD]
```
2*(SMA(CLOSE,13,2)-SMA(CLOSE,27,2)-SMA(SMA(CLOSE,13,2)-SMA(CLOSE,27,2),10,2))
```
> **191独有**。经典MACD结构：2×(DIF-DEA) = MACD柱状图。

### Alpha#090 — 量-VWAP排名相关 [量价]
```
(RANK(CORR(RANK(VWAP), RANK(VOLUME), 5)) * -1)
```

### Alpha#091 — 收盘位置×量 [量价]
```
((RANK((CLOSE - MAX(CLOSE, 5))) * RANK(CORR((MEAN(VOLUME,40)), LOW, 5))) * -1)
```

### Alpha#092 — 加权价格动量衰减 [动量]
```
(MAX(RANK(DECAYLINEAR(DELTA(((CLOSE * 0.35) + (VWAP * 0.65)), 2), 3)), TSRANK(DECAYLINEAR(ABS(CORR((MEAN(VOLUME,180)), CLOSE, 13)), 5), 15)) * -1)
```

### Alpha#093 — 开盘价条件累积 [形态]
```
SUM((OPEN>=DELAY(OPEN,1)?0:MAX((OPEN-LOW),(OPEN-DELAY(OPEN,1)))),20)
```
> 开盘价下跌日的下影线/跳空累积。

### Alpha#094 — OBV(30日) [技术指标:OBV]
```
SUM((CLOSE>DELAY(CLOSE,1)?VOLUME:(CLOSE<DELAY(CLOSE,1)?-VOLUME:0)),30)
```
> 30日OBV。

### Alpha#095 — 成交额波动率(20日) [波动率]
```
STD(AMOUNT, 20)
```
> **191独有**。20日成交额标准差。

### Alpha#096 — D值（KDJ的D） [技术指标:KDJ]
```
SMA(SMA((CLOSE-TSMIN(LOW,9))/(TSMAX(HIGH,9)-TSMIN(LOW,9))*100,3,1),3,1)
```
> **191独有**。KDJ中D值 = SMA(K, 3, 1)。

### Alpha#097 — 成交量波动率 [波动率]
```
STD(VOLUME, 10)
```

### Alpha#098 — 条件均线反转 [反转] ≈WQ101#024
```
((((DELTA((SUM(CLOSE, 100) / 100), 100) / DELAY(CLOSE, 100)) < 0.05) || ...) ? (-1 * (CLOSE - TSMIN(CLOSE, 100))) : (-1 * DELTA(CLOSE, 3)))
```

### Alpha#099 — 收盘-量协方差 [量价]
```
(-1 * RANK(COVIANCE(RANK(CLOSE), RANK(VOLUME), 5)))
```

### Alpha#100 — 成交量波动率(20日) [波动率]
```
STD(VOLUME, 20)
```

### Alpha#101 — 收盘-量价相关 [量价]
```
((RANK(CORR(CLOSE, SUM(MEAN(VOLUME,30), 37), 15)) < RANK(CORR(RANK(((HIGH * 0.1) + (VWAP * 0.9))), RANK(VOLUME), 11))) * -1)
```

### Alpha#102 — 成交量RSI [流动性]
```
SMA(MAX(VOLUME-DELAY(VOLUME,1),0),6,1) / SMA(ABS(VOLUME-DELAY(VOLUME,1)),6,1) * 100
```
> 成交量的RSI版本。

### Alpha#103 — 低点距今 [形态]
```
((20-LOWDAY(LOW,20))/20)*100
```
> **191独有**。20日内最低价距今天数的百分比。

### Alpha#104 — 高价-量相关变化 [量价] =WQ101#022
```
(-1 * (DELTA(CORR(HIGH, VOLUME, 5), 5) * RANK(STD(CLOSE, 20))))
```

### Alpha#105 — 开盘-量相关 [量价] ≈WQ101#003
```
(-1 * CORR(RANK(OPEN), RANK(VOLUME), 10))
```

### Alpha#106 — 20日动量 [动量]
```
CLOSE - DELAY(CLOSE, 20)
```

### Alpha#107 — 跳空模式 [形态] =WQ101#020
```
(((-1 * RANK((OPEN - DELAY(HIGH, 1)))) * RANK((OPEN - DELAY(CLOSE, 1)))) * RANK((OPEN - DELAY(LOW, 1))))
```

### Alpha#108 — 高价位置幂 [量价]
```
((RANK((HIGH - MIN(HIGH, 2)))^RANK(CORR((VWAP), (MEAN(VOLUME,120)), 6))) * -1)
```

### Alpha#109 — ATR比 [波动率]
```
SMA(HIGH-LOW,10,2) / SMA(SMA(HIGH-LOW,10,2),10,2)
```
> 振幅SMA / 双重SMA。ATR变种。

### Alpha#110 — 上下影比(20日) [形态]
```
SUM(MAX(0,HIGH-DELAY(CLOSE,1)),20) / SUM(MAX(0,DELAY(CLOSE,1)-LOW),20) * 100
```

### Alpha#111 — CLV×量SMA差 [量价] [技术指标:OBV]
```
SMA(VOL*((CLOSE-LOW)-(HIGH-CLOSE))/(HIGH-LOW),11,2) - SMA(VOL*((CLOSE-LOW)-(HIGH-CLOSE))/(HIGH-LOW),4,2)
```
> CLV×Volume的长短期SMA差→OBV-MACD变种。

### Alpha#112 — RSI方向(12日) [技术指标:RSI]
```
(SUM(上涨,12)-SUM(下跌,12)) / (SUM(上涨,12)+SUM(下跌,12)) * 100
```
> 12日涨跌比率→RSI的另一种表达。

### Alpha#113 — 均线×量价×相关 [复合] ≈WQ101#045
```
(-1 * ((RANK((SUM(DELAY(CLOSE, 5), 20) / 20)) * CORR(CLOSE, VOLUME, 2)) * RANK(CORR(SUM(CLOSE, 5), SUM(CLOSE, 20), 2))))
```

### Alpha#114 — 延迟形态×量 [形态] ≈WQ101#083
```
((RANK(DELAY(((HIGH - LOW) / (SUM(CLOSE, 5) / 5)), 2)) * RANK(RANK(VOLUME))) / (((HIGH - LOW) / (SUM(CLOSE, 5) / 5)) / (VWAP - CLOSE)))
```

### Alpha#115 — 加权高价-量幂 [量价]
```
(RANK(CORR(((HIGH * 0.9) + (CLOSE * 0.1)), MEAN(VOLUME,30), 10))^RANK(CORR(TSRANK(((HIGH + LOW) / 2), 4), TSRANK(VOLUME, 10), 7)))
```

### Alpha#116 — 价格回归斜率(20日) [趋势强度]
```
REGBETA(CLOSE, SEQUENCE, 20)
```
> **191独有**。20日收盘价对时间的线性回归斜率→中期趋势强度。

### Alpha#117 — 量×形态×反转 [量价] =WQ101#035
```
((TSRANK(VOLUME, 32) * (1 - TSRANK(((CLOSE + HIGH) - LOW), 16))) * (1 - TSRANK(RET, 32)))
```

### Alpha#118 — 上下影比(累积) [形态]
```
SUM(HIGH-OPEN,20) / SUM(OPEN-LOW,20) * 100
```
> 上影线/下影线的20日累积比。

### Alpha#119 — 衰减量价 [量价]
```
(RANK(DECAYLINEAR(CORR(VWAP, SUM(MEAN(VOLUME,5), 26), 5), 7)) - RANK(DECAYLINEAR(TSRANK(MIN(CORR(RANK(OPEN), RANK(MEAN(VOLUME,15)), 21), 9), 7), 8)))
```

### Alpha#120 — VWAP方向 [形态] =WQ101#042
```
(RANK((VWAP - CLOSE)) / RANK((VWAP + CLOSE)))
```

### Alpha#121 — VWAP位置幂 [量价]
```
((RANK((VWAP - MIN(VWAP, 12)))^TSRANK(CORR(TSRANK(VWAP, 20), TSRANK(MEAN(VOLUME,60), 2), 18), 3)) * -1)
```

### Alpha#122 — 三重SMA趋势 [动量]
```
(SMA(SMA(SMA(LOG(CLOSE),13,2),13,2),13,2) - DELAY(SMA(SMA(SMA(LOG(CLOSE),13,2),13,2),13,2),1)) / DELAY(...)
```
> 三重SMA平滑的对数价格趋势。

### Alpha#123 — 中间价-量 vs 低价-量 [量价]
```
((RANK(CORR(SUM(((HIGH + LOW) / 2), 20), SUM(MEAN(VOLUME,60), 20), 9)) < RANK(CORR(LOW, VOLUME, 6))) * -1)
```

### Alpha#124 — 收盘偏离VWAP/衰减 [形态]
```
(CLOSE - VWAP) / DECAYLINEAR(RANK(TSMAX(CLOSE, 30)), 2)
```

### Alpha#125 — 衰减量价比 [量价]
```
(RANK(DECAYLINEAR(CORR((VWAP), MEAN(VOLUME,80), 17), 20)) / RANK(DECAYLINEAR(DELTA(((CLOSE * 0.5) + (VWAP * 0.5)), 3), 16)))
```

### Alpha#126 — 典型价格 [形态]
```
(CLOSE + HIGH + LOW) / 3
```
> 典型价格(Typical Price)。

### Alpha#127 — 距高点偏离 [反转]
```
(MEAN((100*(CLOSE-MAX(CLOSE,12))/(MAX(CLOSE,12)))^2))^(1/2)
```
> 12日最高价偏离的RMS。

### Alpha#128 — MFI资金流量 [技术指标:RSI] [量价]
```
100-(100/(1+SUM((TP>DELAY(TP,1)?TP*VOLUME:0),14) / SUM((TP<DELAY(TP,1)?TP*VOLUME:0),14)))
```
> **191独有**。MFI(Money Flow Index)资金流量指标。TP=(H+L+C)/3。

### Alpha#129 — 下跌累积 [动量]
```
SUM((CLOSE-DELAY(CLOSE,1)<0?ABS(CLOSE-DELAY(CLOSE,1)):0),12)
```
> 12日内下跌绝对值累积。

### Alpha#130 — 衰减量价比2 [量价]
```
(RANK(DECAYLINEAR(CORR(((HIGH + LOW) / 2), MEAN(VOLUME,40), 9), 10)) / RANK(DECAYLINEAR(CORR(RANK(VWAP), RANK(VOLUME), 7), 3)))
```

### Alpha#131 — VWAP动量幂 [动量]
```
(RANK(DELTA(VWAP, 1))^TSRANK(CORR(CLOSE, MEAN(VOLUME,50), 18), 18))
```

### Alpha#132 — 平均成交额(20日) [流动性]
```
MEAN(AMOUNT, 20)
```
> **191独有**。20日平均成交额。

### Alpha#133 — 高低点位置差 [形态]
```
((20-HIGHDAY(HIGH,20))/20)*100 - ((20-LOWDAY(LOW,20))/20)*100
```
> **191独有**。高点距今% - 低点距今%。

### Alpha#134 — 12日量价动量 [量价]
```
(CLOSE - DELAY(CLOSE, 12)) / DELAY(CLOSE, 12) * VOLUME
```

### Alpha#135 — 滞后收益率SMA [动量]
```
SMA(DELAY(CLOSE/DELAY(CLOSE,20),1),20,1)
```
> 20日收益率的滞后SMA。

### Alpha#136 — 动量加速×量价 [动量] [量价] =WQ101#014
```
((-1 * RANK(DELTA(RET, 3))) * CORR(OPEN, VOLUME, 10))
```

### Alpha#137 — CR/SAR变种(单日) [形态]
```
16*(CLOSE-DELAY(CLOSE,1)+...)/(条件分母) * MAX(ABS(HIGH-DELAY(CLOSE,1)),ABS(LOW-DELAY(CLOSE,1)))
```
> Alpha#055的单日版本。

### Alpha#138 — 加权低价-量衰减 [量价]
```
((RANK(DECAYLINEAR(DELTA((((LOW * 0.7) + (VWAP * 0.3))), 3), 20)) - TSRANK(DECAYLINEAR(TSRANK(CORR(TSRANK(LOW, 8), TSRANK(MEAN(VOLUME,60), 17), 5), 19), 16), 7)) * -1)
```

### Alpha#139 — 开盘-量相关 [量价] =WQ101#006
```
(-1 * CORR(OPEN, VOLUME, 10))
```

### Alpha#140 — 衰减形态 [复合]
```
MIN(RANK(DECAYLINEAR(((RANK(OPEN) + RANK(LOW)) - (RANK(HIGH) + RANK(CLOSE))), 8)), TSRANK(DECAYLINEAR(CORR(TSRANK(CLOSE, 8), TSRANK(MEAN(VOLUME,60), 20), 8), 7), 3))
```

### Alpha#141 — 高价-量排名相关 [量价] ≈WQ101#015
```
(RANK(CORR(RANK(HIGH), RANK(MEAN(VOLUME,15)), 9)) * -1)
```

### Alpha#142 — 复合动量 [动量] ≈WQ101#017
```
(((-1 * RANK(TSRANK(CLOSE, 10))) * RANK(DELTA(DELTA(CLOSE, 1), 1))) * RANK(TSRANK((VOLUME/MEAN(VOLUME,20)), 5)))
```

### Alpha#143 — 递归动量 [动量]
```
CLOSE>DELAY(CLOSE,1) ? (CLOSE-DELAY(CLOSE,1))/DELAY(CLOSE,1)*SELF : SELF
```
> **191独有**。递归因子：上涨时乘以涨幅，否则保持不变。初始值设为1。

### Alpha#144 — 条件量价冲击 [量价]
```
SUMIF(ABS(CLOSE/DELAY(CLOSE,1)-1)/AMOUNT,20,CLOSE<DELAY(CLOSE,1)) / COUNT(CLOSE<DELAY(CLOSE,1),20)
```
> **191独有**。下跌日的平均价格冲击。

### Alpha#145 — 成交量MACD [流动性]
```
(MEAN(VOLUME,9)-MEAN(VOLUME,26))/MEAN(VOLUME,12)*100
```
> **191独有**。成交量的MACD结构。

### Alpha#146 — 条件偏离 [动量]
```
MEAN(RET-SMA(RET,61,2),20)*(RET-SMA(RET,61,2)) / SMA((RET-SMA(RET,61,2))^2,60)
```
> 收益率偏离长期均值的条件波动率。

### Alpha#147 — 价格回归斜率(12日) [趋势强度]
```
REGBETA(MEAN(CLOSE,12), SEQUENCE(12))
```
> **191独有**。12日回归斜率。

### Alpha#148 — 开盘位置 vs 量 [量价]
```
((RANK(CORR((OPEN), SUM(MEAN(VOLUME,60), 9), 6)) < RANK((OPEN - TSMIN(OPEN, 14)))) * -1)
```

### Alpha#149 — 条件回归斜率 [基准相对] [趋势强度]
```
REGBETA(FILTER(CLOSE/DELAY(CLOSE,1)-1, BANCHMARKINDEXCLOSE<DELAY(BANCHMARKINDEXCLOSE,1)), FILTER(INDEX_RET, INDEX_DOWN), 252)
```
> **191独有**。指数下跌日内，个股收益率对指数收益率的回归斜率→下行Beta。

### Alpha#150 — 典型价格×成交量 [量价]
```
(CLOSE + HIGH + LOW) / 3 * VOLUME
```

### Alpha#151 — 20日变化SMA [动量]
```
SMA(CLOSE - DELAY(CLOSE, 20), 20, 1)
```

### Alpha#152 — MACD SMA版 [技术指标:MACD]
```
SMA(MEAN(DELAY(SMA(DELAY(CLOSE/DELAY(CLOSE,9),1),9,1),1),12) - MEAN(DELAY(SMA(DELAY(CLOSE/DELAY(CLOSE,9),1),9,1),1),26), 9, 1)
```
> **191独有**。SMA递归的MACD变种。

### Alpha#153 — 多周期均线均值 [形态]
```
(MEAN(CLOSE,3)+MEAN(CLOSE,6)+MEAN(CLOSE,12)+MEAN(CLOSE,24))/4
```
> 多周期均线的简单平均。

### Alpha#154 — VWAP位置 vs 量 [量价]
```
(((VWAP - MIN(VWAP, 16))) < (CORR(VWAP, MEAN(VOLUME,180), 18)))
```

### Alpha#155 — 成交量MACD柱 [技术指标:MACD] [流动性]
```
SMA(VOLUME,13,2) - SMA(VOLUME,27,2) - SMA(SMA(VOLUME,13,2)-SMA(VOLUME,27,2),10,2)
```
> **191独有**。成交量的MACD柱状图。

### Alpha#156 — 加权价格动量衰减 [动量]
```
(MAX(RANK(DECAYLINEAR(DELTA(VWAP, 5), 3)), RANK(DECAYLINEAR(((DELTA(((OPEN * 0.15) + (LOW * 0.85)), 2) / ((OPEN * 0.15) + (LOW * 0.85))) * -1), 3))) * -1)
```

### Alpha#157 — 嵌套排名 [复合] ≈WQ101#029
```
(MIN(PROD(RANK(RANK(LOG(SUM(TSMIN(RANK(RANK((-1 * RANK(DELTA((CLOSE - 1), 5))))), 2), 1)))), 1), 5) + TSRANK(DELAY((-1 * RET), 6), 5))
```

### Alpha#158 — 价格形态比 [形态]
```
((HIGH-SMA(CLOSE,15,2))-(LOW-SMA(CLOSE,15,2)))/CLOSE
```
> (HIGH-LOW-2×(SMA(15,2)-SMA(15,2)))/CLOSE = 振幅/收盘价。

### Alpha#159 — 多周期价格位置 [形态]
```
加权(6日/12日/24日)收盘价位置组合
```
> **191独有**。多时间窗口的价格位置加权组合。

### Alpha#160 — 下行波动率SMA [波动率]
```
SMA((CLOSE<=DELAY(CLOSE,1)?STD(CLOSE,20):0),20,1)
```
> 下跌日触发的20日波动率SMA。

### Alpha#161 — ATR(12日) [波动率]
```
MEAN(MAX(MAX((HIGH-LOW),ABS(DELAY(CLOSE,1)-HIGH)),ABS(DELAY(CLOSE,1)-LOW)),12)
```
> 12日平均真实波幅(ATR)。

### Alpha#162 — RSI归一化 [技术指标:RSI]
```
(RSI12-MIN(RSI12,12))/(MAX(RSI12,12)-MIN(RSI12,12))
```
> 12日RSI的min-max归一化。

### Alpha#163 — 复合量价 [量价] ≈WQ101#025
```
RANK(((((-1 * RET) * MEAN(VOLUME,20)) * VWAP) * (HIGH - CLOSE)))
```

### Alpha#164 — 条件价格弹性 [形态]
```
SMA((((CLOSE>DELAY(CLOSE,1))?1/(CLOSE-DELAY(CLOSE,1)):1)-MIN(...,12))/(HIGH-LOW)*100,13,2)
```
> **191独有**。价格弹性的条件SMA平滑。

### Alpha#165 — 价格偏离累积 [形态]
```
MAX(SUMAC(CLOSE-MEAN(CLOSE,48)))-MIN(SUMAC(CLOSE-MEAN(CLOSE,48)))/STD(CLOSE,48)
```

### Alpha#166 — 偏度(20日) [波动率]
```
-20*(20-1)^1.5*SUM(RET-MEAN(RET,20),20)/((20-1)*(20-2)*(SUM((RET,20)^2,20))^1.5)
```
> 20日收益率偏度。

### Alpha#167 — 上涨累积 [动量]
```
SUM((CLOSE-DELAY(CLOSE,1)>0?CLOSE-DELAY(CLOSE,1):0),12)
```
> 12日内上涨绝对值累积。

### Alpha#168 — 成交量比 [流动性]
```
(-1*VOLUME/MEAN(VOLUME,20))
```
> 当日/20日均量比取负。

### Alpha#169 — 动量差SMA [技术指标:MACD]
```
SMA(MEAN(DELAY(SMA(CLOSE-DELAY(CLOSE,1),9,1),1),12) - MEAN(DELAY(SMA(CLOSE-DELAY(CLOSE,1),9,1),1),26), 10, 1)
```
> **191独有**。价格变化的MACD-SMA变种。

### Alpha#170 — 流动性形态 [流动性] [形态] ≈WQ101#047
```
((((RANK((1 / CLOSE)) * VOLUME) / MEAN(VOLUME,20)) * ((HIGH * RANK((HIGH - CLOSE))) / (SUM(HIGH, 5) / 5))) - RANK((VWAP - DELAY(VWAP, 5))))
```

### Alpha#171 — 日内形态 [形态] ≈WQ101#054
```
((-1 * ((LOW - CLOSE) * (OPEN^5))) / ((CLOSE - HIGH) * (CLOSE^5)))
```

### Alpha#172 — ADX平均方向指数 [技术指标:DMI]
```
MEAN(ABS(+DI14 - -DI14)/(+DI14 + -DI14)*100, 6)
```
> **191独有**。6日ADX。+DI/-DI基于HD/LD/TR计算。

### Alpha#173 — 三重SMA [动量]
```
3*SMA(CLOSE,13,2) - 2*SMA(SMA(CLOSE,13,2),13,2) + SMA(SMA(SMA(LOG(CLOSE),13,2),13,2),13,2)
```
> 三重SMA组合趋势指标。

### Alpha#174 — 上行波动率SMA [波动率]
```
SMA((CLOSE>DELAY(CLOSE,1)?STD(CLOSE,20):0),20,1)
```
> 上涨日触发的20日波动率SMA。与Alpha#160对称。

### Alpha#175 — ATR(6日) [波动率]
```
MEAN(MAX(MAX((HIGH-LOW),ABS(DELAY(CLOSE,1)-HIGH)),ABS(DELAY(CLOSE,1)-LOW)),6)
```
> 6日ATR。

### Alpha#176 — 价格位置×量相关 [量价]
```
CORR(RANK(((CLOSE - TSMIN(LOW, 12)) / (TSMAX(HIGH, 12) - TSMIN(LOW, 12)))), RANK(VOLUME), 6)
```

### Alpha#177 — 高点距今 [形态]
```
((20-HIGHDAY(HIGH,20))/20)*100
```
> **191独有**。20日内最高价距今天数的百分比。

### Alpha#178 — 量价动量 [量价]
```
(CLOSE - DELAY(CLOSE, 1)) / DELAY(CLOSE, 1) * VOLUME
```
> 1日收益率 × 成交量。

### Alpha#179 — VWAP-量×低价-量 [量价]
```
(RANK(CORR(VWAP, VOLUME, 4)) * RANK(CORR(RANK(LOW), RANK(MEAN(VOLUME,50)), 12)))
```

### Alpha#180 — 条件动量 [动量] ≈WQ101#007
```
((MEAN(VOLUME,20) < VOLUME) ? ((-1 * TSRANK(ABS(DELTA(CLOSE, 7)), 60)) * SIGN(DELTA(CLOSE, 7))) : (-1 * VOLUME))
```

### Alpha#181 — 个股-指数协偏度 [基准相对]
```
SUM(((RET-MEAN(RET,20))-(INDEX_RET-MEAN(INDEX_RET,20)))^2, 20) / SUM((INDEX_RET-MEAN(INDEX_RET,20))^3)
```
> **191独有**。个股收益率偏离与指数收益率偏离的协偏度。

### Alpha#182 — 同步性 [基准相对]
```
COUNT((CLOSE>OPEN & INDEX_CLOSE>INDEX_OPEN) OR (CLOSE<OPEN & INDEX_CLOSE<INDEX_OPEN), 20) / 20
```
> **191独有**。个股与指数同涨同跌的比例→市场联动性。

### Alpha#183 — 价格偏离累积(24日) [形态]
```
MAX(SUMAC(CLOSE-MEAN(CLOSE,24)))-MIN(SUMAC(CLOSE-MEAN(CLOSE,24)))/STD(CLOSE,24)
```

### Alpha#184 — 滞后形态+相关 [形态] ≈WQ101#037
```
(RANK(CORR(DELAY((OPEN - CLOSE), 1), CLOSE, 200)) + RANK((OPEN - CLOSE)))
```

### Alpha#185 — 日内方向 [形态] ≈WQ101#033
```
RANK((-1 * ((1 - (OPEN / CLOSE))^2)))
```

### Alpha#186 — ADX扩展版 [技术指标:DMI]
```
(MEAN(ADX, 6) + DELAY(MEAN(ADX, 6), 6)) / 2
```
> **191独有**。ADX的6日均值和滞后6日均值的平均。

### Alpha#187 — 开盘条件累积 [形态]
```
SUM((OPEN>=DELAY(OPEN,1)?0:MAX((HIGH-OPEN),(OPEN-DELAY(OPEN,1)))),20)
```
> Alpha#093的镜像版。

### Alpha#188 — ATR变化率 [波动率]
```
((HIGH-LOW-SMA(HIGH-LOW,11,2))/SMA(HIGH-LOW,11,2))*100
```
> 振幅偏离SMA振幅的百分比。

### Alpha#189 — 均偏(6日) [波动率]
```
MEAN(ABS(CLOSE-MEAN(CLOSE,6)),6)
```
> 6日平均绝对偏差。

### Alpha#190 — 下行偏差比 [波动率]
```
LOG((COUNT(RET>GEO_RET,20)-1)*SUMIF((RET-GEO_RET)^2,20,RET<GEO_RET) / (COUNT(RET<GEO_RET,20)*SUMIF((RET-GEO_RET)^2,20,RET>GEO_RET)))
```
> **191独有**。上行vs下行偏差的对数比→非对称风险度量。GEO_RET为几何平均收益率。

### Alpha#191 — 量价复合 [量价]
```
((CORR(MEAN(VOLUME,20), LOW, 5) + ((HIGH + LOW) / 2)) - CLOSE)
```
> 均量与低价的相关性 + 中间价 - 收盘价。

---

## 统计摘要

| 分类 | 数量 |
|------|------|
| 与WQ101完全相同或近似 | ~40 个 |
| **191独有因子** | **~60 个** |
| 量价关系 | ~45 个 |
| 动量/反转 | ~35 个 |
| 技术指标(RSI/KDJ/MACD/OBV/DMI/CCI) | ~35 个 |
| 波动率 | ~20 个 |
| 形态 | ~30 个 |
| 基准相对 | 4 个 (#75, #149, #181, #182) |
| 趋势强度 | 4 个 (#21, #116, #147, #149) |
| 流动性 | ~8 个 |
| 需特殊数据(FF3/基准指数) | ~8 个 |
