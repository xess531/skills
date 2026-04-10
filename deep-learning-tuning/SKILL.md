---
name: deep-learning-tuning
description: Use when tuning deep learning model hyperparameters, diagnosing training issues (loss divergence, overfitting, underfitting, instability), choosing optimizers, batch sizes, learning rates, or regularization strategies. Also use when designing systematic tuning experiments or reviewing training curves. Triggers include mentions of IC, sharpe, overfitting, learning rate, dropout, weight decay, warmup, batch size, or any hyperparameter discussion. Also triggers for CNN-specific tuning (kernel size, channels, pooling, BN), Transformer-specific tuning (attention heads, FFN dimension, positional encoding, warmup schedule), mixed CNN-Transformer architectures, model compression (pruning, distillation, quantization), and automated hyperparameter search (Optuna, Hyperopt, Bayesian optimization).
---

# 深度学习调参专家 (Deep Learning Tuning Expert)

> 基于 [Google Research Deep Learning Tuning Playbook](https://github.com/google-research/tuning_playbook) + 12 篇中文文档整合

## 核心原则

**不要猜测，要验证。** 所有调参决策必须基于实验证据，遵循控制变量法，系统化地最大化模型性能。

---

## 知识模块索引

本 Skill 的详细知识按专题拆分存放在 `references/` 目录下。**根据用户问题的具体领域，读取对应的 reference 文件获取完整知识。**

### 模块路由表

| # | 文件 | 内容概要 | 何时读取 |
|---|------|----------|----------|
| 01 | `references/01-methodology.md` | **科学调参方法论**：增量调优循环、超参三分类（科学/干扰/固定）、搜索策略、模型选择、决策框架、实验管理、调参者忠告 | 用户刚开始调参项目、问"怎么系统化调参"、需要实验设计方法论时 |
| 02 | `references/02-optimizer-lr-bs.md` | **优化器 + LR + BS**：Adam/AdamW/SGD 选择、学习率衰减与 warmup、批量大小选择、训练步数确定 | 用户问优化器选择、学习率调整、batch size 设置、训练时长时 |
| 03 | `references/03-regularization.md` | **正则化 + 初始化 + 交互效应**：Dropout/WD/数据增强/Label Smoothing、1Cycle Policy、LR Range Test、权重初始化、超参数交互矩阵 | 用户讨论过拟合/欠拟合、正则化参数选择、初始化问题、参数之间联动关系时 |
| 04 | `references/04-training-advanced.md` | **高级训练技巧**：EMA/SWA 权重平均、FP16/BF16 混合精度、数据增强（Mixup/CutMix等）、梯度裁剪与监控 | 用户想优化训练过程、使用混合精度、数据增强策略、梯度处理时 |
| 05 | `references/05-diagnosis-debugging.md` | **训练诊断与调试**：Loss 异常百科（NaN/不动/震荡/spike）、梯度异常、过拟合/欠拟合判断、不稳定性修复、训练曲线解读、偏差-方差框架 | 用户遇到训练问题（loss异常、不收敛、过拟合等）、需要诊断训练曲线时 |
| 06 | `references/06-cnn-tuning.md` | **CNN 专项**：架构参数速查（卷积核/通道/深度/Pooling）、Bag of Tricks、CNN Batch Size 注意事项、可视化诊断、目标检测/CV 技巧 | 用户做 CNN 相关调参、讨论卷积核大小/通道数/BN 等 CNN 特有问题时 |
| 07 | `references/07-transformer-tuning.md` | **Transformer 专项**：核心超参（d_model/heads/FFN/layers）、Noam Schedule 与 Warmup 策略、CNN vs Transformer 差异对照表、微调策略（全量/冻结/LoRA） | 用户做 Transformer 相关调参、讨论 warmup/attention heads/微调策略时 |
| 08 | `references/08-hybrid-compression.md` | **混合架构 + 模型压缩**：CNN+Transformer 混合设计模式、特征融合 Q/K/V 来源、结构化剪枝/量化/蒸馏/UPDP 流程与超参 | 用户讨论混合架构设计、模型压缩/部署优化、剪枝/蒸馏参数时 |
| 09 | `references/09-auto-search.md` | **自动超参搜索**：网格/随机/准随机/贝叶斯对比、两阶段搜索策略、Optuna/Hyperopt/Ray Tune 工具推荐、搜索空间定义技巧 | 用户想做自动化调参、问搜索策略选择、或想用 Optuna 等工具时 |
| 10 | `references/10-sop-checklist.md` | **调参 SOP**：完整 6 步 Checklist（数据检查→Sanity Check→Baseline→搜索→验证→确认）、快速排错流程图 | 用户要一个调参操作清单、或快速排查特定训练问题时 |
| 11 | `references/11-appendix-references.md` | **附录速查表**：超参搜索范围表、LR 调度器对比、Normalization 选择指南、激活函数选择指南、完整参考文献列表 | 需要快速查询具体超参范围、选 LR scheduler / Norm / 激活函数、或查找参考文献时 |

---

## 使用指引

1. **用户问题明确属于某一模块** → 直接读取对应 reference 文件，用其中的知识回答
2. **用户问题跨多个模块** → 读取所有相关 reference 文件，综合回答
3. **用户刚开始调参、不确定方向** → 先读 `01-methodology.md` 和 `10-sop-checklist.md`
4. **用户遇到训练问题** → 先读 `05-diagnosis-debugging.md`，再根据问题类型读取专项文件
5. **用户问"某某参数怎么设"** → 先读 `11-appendix-references.md` 查范围，再读专项文件了解原理

---

## 快速决策表（常驻记忆）

| 问题 | 首先尝试 | 然后尝试 | 详见 |
|------|----------|----------|------|
| 模型不收敛 | 降低 LR / 检查代码 | 增加 warmup / 梯度裁剪 | `05` |
| 过拟合 | 增加 dropout / weight decay | 增加数据 / 数据增强 | `03` `05` |
| 欠拟合 | 增大模型 / 降低正则化 | 提高 LR / 训练更久 | `03` `05` |
| 训练太慢 | 增大 batch size | 混合精度 | `02` `04` |
| 结果不稳定 | 多 seed 验证 | 增加 warmup | `01` |
| IC/指标不提升 | 检查特征/数据质量 | 尝试不同架构 | `01` |
| CNN 专项问题 | 查 CNN 架构参数速查表 | Bag of Tricks 逐项试 | `06` |
| Transformer 专项 | 检查 warmup 是否足够 | 调 d_model/heads/layers | `07` |
| 想做自动调参 | 先准随机探索 | 再贝叶斯精调 | `09` |
| 要部署/压缩 | 量化(INT8) 最简单 | 结构化剪枝+蒸馏 | `08` |

---

## 调参优先级排序（常驻记忆）

```
1. 模型架构（决定性能上限）
2. 学习率（最重要的单个超参数）
3. 训练数据量和质量
4. 批量大小（影响训练效率）
5. 训练步数 / epochs
6. 学习率衰减策略
7. 正则化参数（dropout, weight decay）
8. 优化器高级参数（β₁, β₂, ε）
9. 其他（label smoothing, 数据增强强度等）
```
