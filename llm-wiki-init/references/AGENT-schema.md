# AGENT-schema.md — Frontmatter 规范 & 页面类型

> 创建或更新 wiki 页面时读取本文件。

## Frontmatter 规范

所有 wiki 页面必须包含以下 YAML frontmatter：

```yaml
---
type: entity | concept | source | comparison | map
domain: [general]               # 所属域列表，跨域页面标注多个
title: "页面标题"
aliases: [别名1, 别名2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - raw/<domain>/articles/xxx.md
  - raw/<domain>/papers/xxx.md
source_count: 3
related:
  - wiki/<domain>/concepts/xxx.md
  - wiki/<domain>/entities/xxx.md
tags: [tag1, tag2]
status: active | stub | needs-update | deprecated
confidence: high | medium | low
---
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `type` | ✅ | 页面类型 |
| `domain` | ✅ | 所属域列表，如 `[general]` 或 `[tech, work]` |
| `title` | ✅ | 页面标题 |
| `aliases` | ❌ | 别名，方便搜索 |
| `created` | ✅ | 创建日期 |
| `updated` | ✅ | 最后更新日期 |
| `sources` | ✅ | 原始来源列表（指向 `raw/` 中的文件） |
| `source_count` | ✅ | 来源数量（必须与 sources 列表长度一致） |
| `related` | ✅ | 相关页面链接（支持跨域） |
| `tags` | ✅ | 分类标签 |
| `status` | ✅ | `active` / `stub` / `needs-update` / `deprecated` |
| `confidence` | ✅ | `high`（≥2来源交叉验证且结论一致）/ `medium`（1-2来源，信息基本可靠）/ `low`（单来源且无法独立验证） |

## 页面类型模板

### entity（实体）

人物、公司、模型、工具、数据集。

必须包含：
- 简介
- 关键事实/参数
- 与其他实体的关系
- 时间线（如适用）

### concept（概念）

理论、框架、方法论、指标、技术。

必须包含：
- 定义
- 核心原理
- 优缺点
- 应用场景
- 与相关概念的对比

### source（来源摘要）

每个摄入的原始资料一篇（1:1 对应）。

必须包含：
- 元信息（作者/日期/来源）
- 3-5 条核心要点
- 关键引用（原文）
- 与已有知识的关联

### comparison（对比分析）

两个或多个概念/工具/方法的对比。

必须包含：
- 对比维度表格
- 各自优劣
- 适用场景
- 结论

可选 frontmatter 字段：
```yaml
filed_from_query: true    # 标记来自查询而非 ingest
query_date: YYYY-MM-DD
```

### map（主题导航）

某个大主题下所有相关页面的入口。

必须包含：
- 主题概述
- 页面分类列表
- 阅读路径建议
