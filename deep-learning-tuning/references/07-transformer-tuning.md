# Transformer 专项调参指南

> 来源：Transformer 原论文 Warmup 策略、CSDN/掘金 Transformer 超参经验、d2l.ai

## 一、Transformer 核心超参数

| 参数 | 典型值 | 调参经验 |
|------|--------|----------|
| **d_model（嵌入维度）** | 256 / 512 / 768 / 1024 | 越大表示能力越强，但过拟合风险和计算开销也增大 |
| **num_heads（注意力头数）** | 4 / 8 / 16 | 必须能整除 d_model；头数增多可捕捉多样特征，但过多会冗余 |
| **d_ff（FFN 维度）** | 通常 = 4 × d_model | 经典比例 4:1；也有 8/3 × d_model (LLaMA) 的变体 |
| **num_layers（层数）** | 6 / 12 / 24 | 从少量层开始，逐步增加观察验证集性能；过深可能梯度消失 |
| **dropout** | 0.1 ~ 0.3 | 应用于：attention 权重、FFN 后、embedding 后、残差连接 |
| **d_k（头维度）** | d_model / num_heads | 通常不单独调，由前两者决定 |

---

## 二、Transformer Warmup 策略（关键！）

**原版 Transformer LR Schedule（Noam Schedule）：**

```
lr = d_model^(-0.5) × min(step^(-0.5), step × warmup_steps^(-1.5))
```

**行为：**
- 前 `warmup_steps` 步：LR 线性增长
- 之后：LR 按 step^(-0.5) 衰减

**为什么 Transformer 必须 Warmup：**
- Adam 的自适应学习率在训练初期方差估计不准确（RAdam 论文证明）
- Transformer 没有 BN，对初始化更敏感，初期梯度较大
- Warmup 让优化器有时间"热身"，积累准确的梯度统计

**Warmup 步数推荐：**

| 模型规模 | warmup_steps | 说明 |
|----------|-------------|------|
| 小模型（d=256, L=6） | 1000 ~ 4000 | 可以较短 |
| 中模型（d=512, L=12） | 4000 ~ 10000 | 原版 Transformer 用 4000 |
| 大模型（d≥1024, L≥24） | 10000+ | 更大模型需要更长 warmup |

---

## 三、Transformer vs CNN 调参差异

| 维度 | CNN | Transformer |
|------|-----|-------------|
| **Normalization** | Batch Norm（默认） | Layer Norm / RMS Norm |
| **LR Schedule** | Step Decay / Cosine | **必须 Warmup** + Cosine/Inverse Sqrt |
| **初始化** | He (Kaiming) | 截断正态 + 缩放因子（GPT 用 1/√(2N)） |
| **位置信息** | 卷积天然带位置 | 需要位置编码（正弦/可学习/RoPE） |
| **Batch Size 敏感度** | 高（BN 依赖 batch） | 低（LN 不依赖 batch） |
| **Dropout 位置** | Conv 后 / FC 后 | Attention、FFN、Embedding、残差 |
| **深度扩展** | 残差连接 + BN | 残差连接 + LN + Pre-Norm 更稳定 |
| **过拟合倾向** | 中等 | 高（参数量大，小数据易过拟合） |

---

## 四、Transformer 微调策略

| 策略 | 适用场景 | 操作 |
|------|----------|------|
| **全量微调** | 数据充足 + 计算充足 | 所有参数可训练，LR 比预训练小 10~100 倍 |
| **冻结底层** | 数据较少 | 冻结前 N 层，只训练后几层 + 分类头 |
| **逐层解冻** | 稳定性优先 | 先训分类头 → 逐层向下解冻，每层用更小 LR |
| **LoRA / Adapter** | 超大模型 | 只训练少量额外参数，原始权重冻结 |
| **区分 LR** | 通用 | 底层用更小 LR，顶层用更大 LR |
