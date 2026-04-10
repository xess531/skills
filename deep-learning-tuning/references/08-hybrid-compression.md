# CNN + Transformer 混合架构与模型压缩

> 来源：火山引擎 MHAFF 论文解读、腾讯云 CNN→Transformer 演进文章、智源社区 UPDP 论文

## 一、混合架构设计模式

| 模式 | 结构 | 适用场景 |
|------|------|----------|
| **CNN backbone + Transformer head** | CNN 提取局部特征 → Transformer 做全局建模 | 最常见，兼顾效率和效果 |
| **Transformer backbone + CNN head** | ViT 提取特征 → CNN 做精细预测 | 检测/分割 |
| **双分支融合** | CNN 分支 + Transformer 分支 → 注意力融合 | 需要同时捕捉局部+全局特征 |
| **交替堆叠** | Conv-Attention-Conv-Attention... | 现代架构（如 CoAtNet） |

---

## 二、混合架构调参要点

| 要点 | 说明 |
|------|------|
| **各分支独立 LR** | CNN 分支和 Transformer 分支最优 LR 通常不同 |
| **迁移学习** | 两个分支分别用各自的预训练权重初始化（如 ResNet + ViT-ImageNet） |
| **融合层设计** | 注意力融合 > 拼接 > 加法（注意力融合可动态加权，但计算量更大） |
| **输入适配** | CNN 输入通常 224×224；ViT 需要分 patch（如 16×16） |
| **正则化策略** | CNN 侧用 BN + Dropout；Transformer 侧用 LN + Dropout |
| **Warmup** | 混合架构也需要 warmup，主要受 Transformer 分支影响 |

---

## 三、特征融合 Q/K/V 来源选择

当用多头注意力融合 CNN 和 Transformer 特征时：

| Q 来源 | K 来源 | V 来源 | 效果 |
|--------|--------|--------|------|
| Transformer | CNN | Transformer | **最优**（让 Transformer 的全局视角引导融合） |
| CNN | Transformer | CNN | 次优 |
| CNN | CNN | Transformer | 较差 |

---

## 四、模型压缩技术概览

| 技术 | 原理 | 精度损失 | 加速倍数 | 适用 |
|------|------|----------|----------|------|
| **结构化剪枝** | 移除整个通道/层/注意力头 | 中 | 1.5~3× | CNN + Transformer |
| **非结构化剪枝** | 移除单个权重（稀疏化） | 低 | 需特殊硬件 | 研究用 |
| **量化（INT8/INT4）** | 降低权重精度 | 低~中 | 2~4× | 部署 |
| **知识蒸馏** | 小模型学大模型的输出 | 低 | 取决于学生模型 | 通用 |
| **深度剪枝（UPDP）** | 移除残差块/Transformer 层 | 低（渐进式训练） | 1.2~1.4× | CNN + ViT |

---

## 五、UPDP 流程与超参推荐

```
超网络训练（10 epochs）→ 子网搜索（遗传算法）→ 渐进式子网训练 → 重参化合并
```

| 模型 | 子网训练 Epochs | 渐进参数 K | 特殊操作 |
|------|-----------------|-----------|----------|
| ResNet34 | 150 | 3 | epoch 100 时将剪枝块 3×3 Conv 改为 1×1 |
| MobileNetV2 | 450 | 3 | 直接渐进训练，跳过超网搜索 |
| ConvNeXtV1 | 450 | 4.5 | 剪枝块 7×7 DWConv → 3×3 以加速 |
| DeiT (ViT) | 450 | 6 | 标准流程 |

---

## 六、压缩阶段调参注意

- **蒸馏温度 T**：通常 4~20，T 越大输出越"软"，T=4 是常见默认
- **蒸馏 α**：hard label loss 和 soft label loss 的权重比，通常 α=0.5~0.9
- **量化后微调**：通常 5~20 epoch，LR 为原训练的 1/10~1/100
- **剪枝后重训练**：需要比原始训练更长的 epoch 数来恢复精度
