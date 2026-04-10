# 附录：速查表与参考文献

## 附一：常用超参数搜索范围参考

| 超参数 | 搜索范围（对数尺度） | 备注 |
|--------|----------------------|------|
| Learning Rate | 1e-5 ~ 1e-1 | 最关键的超参 |
| Weight Decay | 1e-6 ~ 1e-2 | 与 LR 协调 |
| Dropout | 0.0 ~ 0.5 | 线性尺度 |
| Batch Size | 32 ~ 4096 | 2 的幂次 |
| Warmup Steps | 0 ~ 总步数×10% | 整数 |
| Hidden Size | 32 ~ 1024 | 2 的幂次 |
| Num Layers | 1 ~ 12 | 整数 |
| β₁ (Adam) | 0.85 ~ 0.99 | 线性尺度 |
| β₂ (Adam) | 0.99 ~ 0.9999 | 对数尺度 |
| ε (Adam) | 1e-8 ~ 1e-5 | 对数尺度 |
| Label Smoothing | 0.0 ~ 0.2 | 线性尺度 |
| Gradient Clip | 0.1 ~ 10.0 | 对数尺度 |

---

## 附二：学习率调度器全面对比

| 调度器 | 公式/行为 | 优点 | 缺点 | 推荐场景 |
|--------|-----------|------|------|----------|
| **恒定 (Constant)** | LR 不变 | 简单，快速探索 | 后期收敛慢 | 调参初期 / 短实验 |
| **Step Decay** | 每 N 步 ×γ | 简单直观 | 需手动设 N 和 γ | 经典 CNN 训练 |
| **Cosine Annealing** | 余弦曲线平滑衰减到 0 | 平滑，不需要太多调参 | 不适合需要长尾探索的任务 | **默认推荐** |
| **Cosine + Warmup** | 先线性升温再余弦衰减 | 稳定性好，适合大 LR | 需设 warmup 步数 | Transformer / 大模型 |
| **Linear Decay** | 线性衰减到 0 | 简单可预测 | 衰减速度均匀，不够灵活 | NLP 任务常用 |
| **Polynomial Decay** | 多项式衰减 | 可调次数控制衰减曲线 | 多一个需调的参数 | 需要精细控制时 |
| **1Cycle** | 升→降→退火 | 超收敛，自带正则效果 | 需 LR range test | 追求快速训练 |
| **Cyclical LR** | 周期性三角波 | 自动探索 LR 范围 | 调周期和边界值麻烦 | 不确定最优 LR 时 |
| **Reduce on Plateau** | 验证 loss 停滞时降 LR | 自适应 | 反应滞后，不适合自动化 | 交互式训练 |
| **Exponential Decay** | LR × γ^step | 快速衰减 | 后期 LR 可能过小 | 短训练 / 微调 |

**推荐默认组合：Cosine Annealing + Linear Warmup**

---

## 附三：Normalization 层选择指南

| 技术 | 沿哪个维度归一化 | 适用场景 | 注意事项 |
|------|------------------|----------|----------|
| **Batch Norm (BN)** | Batch 维度 | CNN 默认选择 | 小 batch 时统计不稳定；推理需要 running stats |
| **Layer Norm (LN)** | 特征维度 | Transformer / RNN 默认 | 对 batch size 不敏感 |
| **Instance Norm (IN)** | 单样本空间维度 | 风格迁移 | 去除实例级别的统计信息 |
| **Group Norm (GN)** | 分组特征 | 小 batch CNN | BN 在小 batch 下的替代品 |
| **RMS Norm** | 特征维度（仅缩放） | 大语言模型 | LN 的简化版，去掉了中心化 |

**选择规则：**
- CNN + 大 batch → **Batch Norm**
- CNN + 小 batch（<16）→ **Group Norm**
- Transformer / Attention → **Layer Norm** 或 **RMS Norm**
- BN 在残差连接中的位置：推荐 **Pre-Norm**（`x + f(Norm(x))`）

---

## 附四：激活函数选择指南

| 激活函数 | 公式 | 优点 | 缺点 | 推荐场景 |
|----------|------|------|------|----------|
| **ReLU** | max(0, x) | 简单高效，不饱和 | Dying ReLU 问题 | CNN 默认 |
| **Leaky ReLU** | max(αx, x), α=0.01 | 解决 Dying ReLU | α 需要调 | ReLU 有问题时 |
| **PReLU** | max(αx, x), α 可学习 | 自适应 | 多一个参数 | 计算机视觉 |
| **GELU** | x·Φ(x) | 平滑，Transformer 标配 | 计算量稍大 | **Transformer 默认** |
| **SiLU (Swish)** | x·σ(x) | 平滑，效果好 | 计算量稍大 | 现代架构 |
| **Mish** | x·tanh(softplus(x)) | 非常平滑 | 计算最慢 | 实验性 |
| **Tanh** | (eˣ-e⁻ˣ)/(eˣ+e⁻ˣ) | 零中心化 | 饱和区梯度消失 | RNN/LSTM |
| **Sigmoid** | 1/(1+e⁻ˣ) | 输出 (0,1) | 饱和 + 非零中心 | 仅用于输出层概率 |

---

## 附五：参考文献与推荐资源

### 核心论文

| 文献 | 核心贡献 | 链接 |
|------|----------|------|
| **Google Deep Learning Tuning Playbook** | 系统化调参方法论，超参分类与实验设计 | [GitHub](https://github.com/google-research/tuning_playbook) |
| **Leslie Smith - A Disciplined Approach to NN Hyperparameters (2018)** | 1Cycle Policy, LR Range Test, Cyclical Momentum | [arXiv:1803.09820](https://arxiv.org/abs/1803.09820) |
| **He et al. - Bag of Tricks for Image Classification (CVPR 2019)** | 训练技巧组合拳，ResNet 从 75.3→79.29% | [Paper](https://arxiv.org/abs/1812.01187) |
| **Loshchilov & Hutter - Decoupled Weight Decay (2019)** | AdamW，解耦权重衰减 | [arXiv:1711.05101](https://arxiv.org/abs/1711.05101) |
| **Loshchilov & Hutter - SGDR (2017)** | 余弦退火 + 热重启 | [arXiv:1608.03983](https://arxiv.org/abs/1608.03983) |
| **Bag of Freebies for Object Detection (2019)** | 不改结构提升检测性能的训练技巧 | [arXiv:1902.04103](https://arxiv.org/abs/1902.04103) |
| **UPDP - Unified Progressive Depth Pruner (2024)** | CNN 与 ViT 通用深度剪枝，ConvNeXt 几乎无损加速 40% | [智源社区](https://hub.baai.ac.cn/view/34440) |

### 进阶论文

| 文献 | 核心贡献 |
|------|----------|
| **Liu et al. - On the Variance of the Adaptive LR and Beyond (RAdam, 2020)** | 解释 Adam warmup 的必要性，提出 RAdam |
| **Zhang et al. - Lookahead Optimizer (2019)** | 慢权重 + 快权重结合，更稳定的收敛 |
| **Izmailov et al. - Averaging Weights Leads to Wider Optima (SWA, 2018)** | 权重平均找到更平坦的 loss 最小值 |
| **Morales-Brotons et al. - EMA of Weights in Deep Learning (2024)** | EMA 的系统性研究，证明 EMA 解不同于 last-iterate |
| **Zhang et al. - Mixup (2018)** | 样本混合正则化 |
| **Yun et al. - CutMix (2019)** | 区域混合正则化 |
| **Glorot & Bengio - Xavier Initialization (2010)** | Sigmoid/Tanh 网络的初始化理论 |
| **He et al. - Kaiming Initialization (2015)** | ReLU 网络的初始化理论 |
| **Vaswani et al. - Attention Is All You Need (2017)** | Transformer 原版论文，Noam LR Schedule |

### 方法论 / Playbook 级

| 资源 | 内容 | 链接 |
|------|------|------|
| **Tuning Playbook 中文版** | 系统调参手册完整中文翻译 | [GitHub](https://github.com/schrodingercatss/tuning_playbook_zh_cn) |
| **深度学习调优指南·系统性优化模型** | 工程视角重述 playbook，超参三分类讲解清晰 | [腾讯云](https://cloud.tencent.com/developer/article/2322933) |
| **通用深度学习模型调优方法** | 偏差/方差分析 + 调优三阶段逻辑 | [博客园](https://www.cnblogs.com/chenzhenhong/p/13437132.html) |

### CNN 侧参考

| 资源 | 内容 | 链接 |
|------|------|------|
| **CNN 超参数优化和可视化技巧详解** | 卷积核/通道/BS/Dropout + 可视化诊断 | [阿里云](https://developer.aliyun.com/article/496231) |
| **目标检测算法优化技巧** | MixUp/多尺度/Label Smoothing/同步BN | [博客园](https://www.cnblogs.com/pprp/p/12544099.html) |

### Transformer 侧参考

| 资源 | 内容 | 链接 |
|------|------|------|
| **Transformer 超参数选择和调整经验** | 嵌入维度/头数/层数/Warmup/搜索策略 | [CSDN](https://blog.csdn.net/njhhuuuby/article/details/131609945) |
| **d2l.ai Transformer 章节** | 架构实现 + 训练配置详解 | [d2l](https://zh.d2l.ai/chapter_attention-mechanisms/transformer.html) |

### 自动调参 / 工具

| 资源 | 内容 | 链接 |
|------|------|------|
| **超参数自动化调优详解** | 网格/随机/贝叶斯 + Hyperopt 实战 | [火山引擎](https://developer.volcengine.com/articles/7389520244877819930) |
| **Optuna + HuggingFace Transformers** | 官方调参教程 | [HuggingFace](https://huggingface.co/learn/cookbook/en/optuna_hpo_with_transformers) |

### 混合架构 / 压缩

| 资源 | 内容 | 链接 |
|------|------|------|
| **CNN + Transformer 混合特征融合 (MHAFF)** | 双分支融合设计 + Q/K/V 来源实验 | [火山引擎](https://developer.volcengine.com/articles/7487815625499213865) |
| **UPDP 统一渐进深度剪枝** | CNN 与 ViT 通用，渐进训练策略 | [智源社区](https://hub.baai.ac.cn/view/34440) |

### 通用实用资源

| 资源 | 类型 | 链接 |
|------|------|------|
| **Conchylicultor/Deep-Learning-Tricks** | GitHub 技巧汇总 | [GitHub](https://github.com/Conchylicultor/Deep-Learning-Tricks) |
| **CS230 Stanford - Initialization & Regularization** | 教程讲义 | [PDF](https://cs230.stanford.edu/section/4/Section4.pdf) |
| **PyTorch LR Scheduler 文档** | 官方 API | [Docs](https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate) |
| **炼丹宝典 (cnblogs)** | 中文调参 tricks 汇总 | [链接](https://www.cnblogs.com/shona/p/12667950.html) |
| **深度学习调参技巧超参数调优秘籍** | 常见问题排错 | [极市](https://www.cvmart.net/community/detail/5648) |
