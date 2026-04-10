# 模块四：深度学习端到端模型综述

> 量化选股领域主流深度学习架构详解、模型选型指南、损失函数选型。

---

## 1. CNN 系列

### 1.1 AlphaNet（华泰证券）

**核心论文**：《AlphaNet：因子挖掘神经网络》

**架构**：
```
输入 [N_stocks, T_days, F_features]
  → Alpha Layer 1: MLP + tanh → hidden_dim 个非线性因子（[-1, 1]）
  → Alpha Layer 2: MLP + tanh → 高阶非线性特征
  → Output Layer: 加权聚合 → 预测未来收益
```

**三种损失函数对比**：

| 损失函数 | 定义 | 优点 | 缺点 |
|----------|------|------|------|
| **MSE** | mean((pred - target)²) | 标准回归 | 与投资目标不对齐 |
| **IC Loss** | -corr(pred, target) | 直接优化 IC | 对异常值敏感 |
| **CCC Loss** | 一致性相关系数 | 兼顾相关性+一致性 | 优化难度较高 |

**因子正交化正则**：
```python
orth_loss = ||F'F - I||²  # F 为因子矩阵
total_loss = main_loss + λ * orth_loss  # λ 通常 0.01-0.1
```

**关键实验**：
- IC Loss 在 IC 绝对值和多头超额上最优
- CCC Loss 在稳定性（IR）上最优
- 非线性模型改善主要来自**多头端**
- 中证 1000（小市值）表现最佳

### 1.2 多尺度 CNN 架构

```
输入 [B, T, C]
  → Branch 1: Conv1d(k=3, s=2)  → 日级模式（游资快进快出）
  → Branch 2: Conv1d(k=10, s=5) → 周级模式（连续放量）
  → Branch 3: Conv1d(k=20, s=10)→ 月级模式（月线突破）
  → 序列拼接 + CLS Token → Transformer 融合 → 预测
```

**关键设计决策**：

| 设计点 | 推荐 | 理由 |
|--------|------|------|
| Conv1d vs Conv2d | Conv1d | 金融特征无空间结构 |
| 融合方式 | 序列拼接 | AdaptivePool 丢失高频细节 |
| 聚合 | CLS Token | 比 Mean Pooling 更灵活 |
| Stem | Pointwise (k=1) | 保留完整时间分辨率 |

---

## 2. Transformer 系列

### 2.1 CTTS（东北证券）

**核心**：CNN 提取局部特征 + Transformer 全局建模

```
输入 [B, T, F]
  → Conv1d Block → 局部特征 [B, T', d_model]
  → Positional Encoding
  → Transformer Encoder (N 层, H 头)
  → Pooling → MLP Head → 预测
```

**结论**：CNN + Transformer > 单独任一组件。

### 2.2 PatchTST（IBM，ICLR 2023）

**核心创新**：时序切 patch → 降低复杂度

```
输入 [B, T, C] → 切 patch → [B, N_patch, patch_len × C]
每通道独立通过 Transformer（Channel Independence），共享参数
```

**配置建议**：
- 60 日窗口：patch_len=5, stride=5
- 120 日窗口：patch_len=10, stride=10
- 可多尺度：同时 patch_len=5 和 20

**vs 传统 Transformer**：Token 数从 60 降到 12，注意力复杂度从 O(3600) 降到 O(144)。

### 2.3 iTransformer（清华/蚂蚁，ICLR 2024）

**核心创新**：倒置 Transformer——交换时间维和变量维。

```python
class iTransformer(nn.Module):
    def __init__(self, seq_len, n_vars, d_model, n_heads, n_layers):
        self.embed = nn.Linear(seq_len, d_model)  # 时序 → 向量
        self.encoder = TransformerEncoder(d_model, n_heads, n_layers)
        self.head = nn.Linear(d_model, 1)
    
    def forward(self, x):  # x: [B, T, C]
        x = x.permute(0, 2, 1)  # [B, C, T]
        x = self.embed(x)       # [B, C, d_model]
        x = self.encoder(x)     # Attention on C (变量间)
        x = x.mean(dim=1)       # [B, d_model]
        return self.head(x)     # [B, 1]
```

**为什么适合金融**：变量间关系（成交量→价格）比时间长距离依赖更重要。

---

## 3. GRU / RNN 系列

### 3.1 CrossGRU（华创证券）

**核心创新**：GRU 时序 + 交叉注意力截面交互

**三部分**：
1. **时序 GRU**：每只股票独立 → h_i ∈ R^d
2. **截面交互**：CrossAttn(h_i, H_market) → 融合市场信息
3. **门控残差**：α = sigmoid(W @ h_i); output = α*h_cross + (1-α)*h_individual

**表现**：5d RankIC=10.9%，10d=11.7%，Top 组年化+39%，最大回撤 8%。

### 3.2 LSTM vs GRU

A 股 60 日窗口场景，GRU 和 LSTM 效果几乎无差异，GRU 因参数少通常略优。

---

## 4. 强化学习 + 因子挖掘

### 4.1 T2RL/TFAC（西南证券）

**两阶段**：

**Stage 1 TFAC**：Transformer + Actor-Critic
```python
reward = sign(predicted_return) * actual_return  # 方向准确奖励
```
RankIC=11.19%，多头年化 33.61%

**Stage 2 TFSAC**：SAC 学习候选池权重分配，奖励=收益-交易成本

---

## 5. MLP / 无注意力架构

### 5.1 TSMixer（Google，NeurIPS 2023）

纯 MLP：Temporal MLP → Feature MLP → Residual+LN，堆叠 N 层。参数极小，训练极快。

### 5.2 ModernTCN（2024）

大核 DWConv(k=51) + Pointwise + GELU + LN。纯卷积，单层覆盖整个 60 日窗口。

### 5.3 DLinear（2023）

极简线性基线：Trend-Seasonal 分解 → Linear(T, 1)。如果 DLinear IC 接近复杂模型，说明线性信号已很强。

---

## 6. TabNet（Google，AAAI 2021）

序列注意力做稀疏特征选择：多步 Sparsemax → 每步选不同特征子集 → 累加决策。

**在选股中**：输入 100+ 截面因子 → 自动特征选择 → 输出特征重要性（因子归因）。

**局限**：不建模时序；离散特征处理不如 GBDT。

---

## 7. GNN 选股

### 7.1 图构建方式

| 图类型 | 方法 | 稳定性 |
|--------|------|--------|
| 行业关系图 | 同行业/板块相连 | 高 |
| 供应链图 | 上下游相连 | 中 |
| 收益相关图 | 相关性>θ 相连 | 低 |
| 自适应图 | 可学习邻接矩阵 | 取决训练 |

### 7.2 主流模型

- **HIST**（浙大 KDD'22）：预定义概念 + 隐式概念双通道
- **AlphaSAGE**：GraphSAGE + 股票关系图
- **RSR**：关系感知 GNN + ListwiseLoss

---

## 8. 自动化因子挖掘

### 8.1 AlphaForge（广发证券）

生成-预测网络：因子生成器(梯度优化) → 因子预测器(IC预测) → 动态加权合成。比 GP 收敛更快、因子更稳定。

**因子算子库**：ts_mean/std/rank/corr, cs_rank/zscore, add/sub/mul/div/log, if_then, ts_argmax/decay_linear 等。

### 8.2 LLM + MCTS

LLM 生成候选因子表达式 → MCTS(UCB+LLM变异+快速IC回测) → Top-K 高 IC 因子。

### 8.3 Microsoft RD-Agent

AI 驱动闭环：多臂老虎机→决定优化因子/模型→LLM修改代码→回测→反馈更新。

---

## 9. 模型选型指南

### 9.1 按数据场景

| 数据场景 | 推荐模型 | 理由 |
|----------|----------|------|
| 日频量价 + 短窗口(30-60d) | CNN 多尺度 / GRU / PatchTST | 局部+全局 |
| 日频量价 + 长窗口(120-250d) | PatchTST / iTransformer | 长距离依赖 |
| 截面因子值(100+因子) | TabNet / LightGBM | 特征选择+非线性 |
| 日频 + 截面交互 | CrossGRU / GNN | 时序+截面联合 |
| 分钟级高频 | ModernTCN / TSMixer | 计算效率优先 |
| 因子挖掘+组合闭环 | T2RL / RD-Agent | 端到端 |

### 9.2 按研究阶段

| 阶段 | 推荐 | 理由 |
|------|------|------|
| 基线 | DLinear + MLP | 确认信号存在 |
| 探索 | GRU / LSTM | 简单时序模型 |
| 深入 | CNN-Transformer / PatchTST | 更强表达力 |
| 前沿 | iTransformer / CrossGRU / GNN | 新范式 |
| 自动化 | AlphaForge / RD-Agent | 提升效率 |

### 9.3 复杂度经验法则

```
低信噪比(IC<0.03) → 简单模型优于复杂模型
中信噪比(0.03<IC<0.06) → 中等复杂度最优
高信噪比(IC>0.06) → 复杂模型有空间

参数量：
  <100 万样本 → <100K 参数
  100-500 万样本 → 100K-1M 参数
  >500 万样本 → 1M-10M 参数
```

### 9.4 金融时序 vs NLP 的差异

| 维度 | NLP | 金融时序 |
|------|-----|----------|
| 信噪比 | 高 | 极低 |
| 数据量 | 海量 | 有限 |
| 分布稳定性 | 稳定 | 体制转换 |
| 标签质量 | 清晰 | 含噪 |

**应对**：避免复杂大模型；弱学习器集成；Transformer 做融合器而非预测器；必须 Warmup。

---

## 10. 损失函数选型

| 损失函数 | 适用场景 | 优缺点 |
|----------|----------|--------|
| **MSE** | 通用回归 | 标准但与投资目标不对齐 |
| **SmoothL1** | 标签噪声大 | 需调 β |
| **IC Loss** | 因子挖掘（**推荐**） | 直接对齐投资目标 |
| **CCC Loss** | 稳定性优先 | IC 绝对值可能略低 |
| **RankIC Loss** | 排序优先 | 梯度不连续需近似 |
| **Listwise/Pairwise** | 直接优化排序 | 实现复杂 |

**推荐路径**：MSE/SmoothL1 跑通 → IC Loss → CCC/RankIC Loss（如 IC 波动大）。

---

## 11. 参考文献

| 来源 | 标题 | 关键词 |
|------|------|--------|
| 华泰证券 | AlphaNet | CNN, IC Loss, 因子正交化 |
| 东北证券 | CTTS | CNN-Transformer |
| 华创证券 | CrossGRU | 截面交互, 市场隐变量 |
| 华创证券 | PatchTST/TSMixer/ModernTCN 对比 | 新架构对比 |
| 西南证券 | T2RL/TFAC | RL + 因子挖掘 |
| 清华/蚂蚁 | iTransformer (ICLR 2024) | 倒置 Transformer |
| IBM | PatchTST (ICLR 2023) | Patch + Channel Independence |
| Google | TabNet (AAAI 2021) | 稀疏特征选择 |
| Google | TSMixer (NeurIPS 2023) | 纯 MLP |
| 浙大 | HIST (KDD 2022) | 双通道 GNN |
| 广发证券 | AlphaForge | 梯度优化因子生成 |
| Microsoft | RD-Agent | AI 驱动闭环 |
