---
name: llm-wiki-init
description: |
  一键创建 Karpathy-style LLM Wiki 个人知识库。
  触发词：创建知识库、搭建知识库、初始化知识库、新建知识库、llm wiki、karpathy wiki、建一个wiki、帮我搭知识库
---

# LLM Wiki 初始化工具

> 一次性脚手架。问 2 个问题，生成完整的 Karpathy-style LLM Wiki 知识库，然后退场。

## 你是什么

一键知识库生成器。产出一个完整可用的个人知识库：目录结构 + 规则文件 + 模板 + Obsidian 配置指引。跑一次就够了。

## 重要提示（必须告知用户）

在开始之前，**必须提示用户**：

> ⚠️ 本知识库默认配合 **WorkBuddy** 使用。知识库的规则文件（AGENT.md 等）通过 WorkBuddy 的 memory 机制自动加载。如果你使用其他工具（Claude Code、Cursor 等），AGENT.md 可能无法被自动触发，需要手动配置加载方式。

## 执行流程

### Step 1：收集信息（只问 2 个问题）

**问题 1**：知识库叫什么名字？想放在哪里？

- 默认路径：`~/Desktop/<名字>`
- 示例：`~/Desktop/my-knowledge`

**问题 2**：你想管理哪些领域？

提示用户：
> 可以是不同的知识领域（如 前端开发、产品设计、心理学），也可以是不同的项目（如 项目A、项目B）。
> 每个领域给一个英文 ID 和一句话描述。如果你不确定怎么命名，告诉我你关注什么，我来推荐。
> 如果不需要分领域，直接跳过就好，我会默认创建一个 `general` 通用目录。

示例输入：
```
tech: 技术学习，编程、架构、工具链
work: 工作，项目管理、方案设计、职业发展
life: 生活，阅读、健身、旅行、个人思考
```

**如果用户描述模糊**，根据描述推荐域 ID 和名称，让用户确认。比如用户说"我平时主要看技术文章，偶尔也记记读书笔记"，推荐：
```
tech: 技术学习
reading: 阅读笔记
```

**如果用户不指定领域**（比如说"不分"、"先不管"、"随便"），默认使用单域：
```
general: 通用知识库
```

**如果用户一句话就给了所有信息，不要再追问，直接执行。**

### Step 2：创建目录结构

对每个域 `<domain>`，创建：

```bash
mkdir -p <path>/raw/<domain>/articles
mkdir -p <path>/raw/<domain>/papers
mkdir -p <path>/raw/<domain>/transcripts
mkdir -p <path>/raw/<domain>/data
mkdir -p <path>/raw/<domain>/assets
mkdir -p <path>/wiki/<domain>/entities
mkdir -p <path>/wiki/<domain>/concepts
mkdir -p <path>/wiki/<domain>/sources
mkdir -p <path>/wiki/<domain>/comparisons
mkdir -p <path>/wiki/<domain>/maps
```

另外创建：
```bash
mkdir -p <path>/wiki/maps
mkdir -p <path>/templates
mkdir -p <path>/assets
mkdir -p <path>/.workbuddy/memory
```

### Step 3：生成固定文件（直接从 references/ 复制）

从 Skill 的 `references/` 目录复制以下文件到知识库根目录：

- `references/AGENT-schema.md` → `<path>/AGENT-schema.md`
- `references/AGENT-workflows.md` → `<path>/AGENT-workflows.md`

### Step 4：生成动态文件

以下文件根据用户输入的域信息**现场生成**：

#### 4.1 AGENT.md（主规则文件）

按照 `references/AGENT-template-spec.md` 中定义的结构生成，填入：
- 域表格（用户定义的所有域 ID、名称、覆盖范围）
- 目录结构树（反映实际域）
- 变更日志初始条目

#### 4.2 AGENT-writing.md（写作规范 + 标签体系）

- 写作规范部分是固定的（从 `references/AGENT-writing-fixed.md` 复制）
- 标签体系部分是**动态的**：根据每个域的描述，为每个域生成 6-10 个合理的标签
- 标签规则：小写英文、用连字符分隔、每个标签带中文注释

#### 4.3 README.md

生成完整的使用指南，包含：
- 项目简介（基于 Karpathy LLM Wiki 范式）
- 日常使用三动作：收集 → 提问 → 体检
- 知识库结构说明（反映实际域）
- Web Clipper 配置（每个域一个模板）
- Obsidian 配置步骤
- 核心原则

#### 4.4 wiki/index.md

为每个域生成一个空分区：
```markdown
## <域emoji> <域中文名> (`<domain_id>`)

_暂无内容。_

---
```

#### 4.5 wiki/log.md

```markdown
---
type: log
title: "操作日志"
updated: <today>
---

# Wiki 操作日志

---

## [<today>] init | 知识库初始化

- 操作: 创建知识库目录结构 + 规则文件 + 模板
- 域: <所有域列表>
- 状态: 知识库就绪，等待首次 ingest
```

#### 4.6 wiki/hot.md

```markdown
---
type: meta
title: "会话热缓存"
updated: <today>
---

# 🔥 会话热缓存

> 本文件由 LLM 在每次会话结束前自动更新，新会话开始时静默读取。约 500 词上限。

## 当前焦点

- 知识库刚初始化，所有域为空
- 等待用户添加第一篇原始资料到 raw/ 目录

## 未解决问题

_暂无_

## 最近决策

_暂无_

## 最近操作

- [<today>] 知识库初始化

## 活跃页面

_暂无_

## 知识库统计快照

- Raw: 0 篇
- Wiki: 0 知识页 + 3 管理页（index/log/hot）
- 域: <每个域> 空
```

#### 4.7 wiki/maps/dashboard.md

为每个域生成一个 Dataview 查询块：
```markdown
## <域emoji> <域中文名>最新

\```dataview
TABLE type, title, updated, confidence
FROM "wiki/<domain>"
SORT updated DESC
LIMIT 10
\```
```

加上固定的全局查询（跨域页面、待处理资料、Stub 页面、按标签分布）。

#### 4.8 templates/web-clipper.md

```markdown
---
type: raw-article
title: "{{title}}"
url: "{{url}}"
author: "{{author}}"
published: "{{published}}"
clipped: {{date}}
domain: ""
tags: [unprocessed]
---

# {{title}}

> 来源: [{{url}}]({{url}})
> 作者: {{author}}
> 发布日期: {{published}}
> 剪藏日期: {{date}}

---

{{content}}
```

#### 4.9 .workbuddy/memory/MEMORY.md ⚠️ 最关键的文件

> **这个文件是整个知识库能正常运转的启动引擎。** 没有它，WorkBuddy 后续会话不会自动读取 AGENT.md，知识库规则形同虚设。**必须确保此文件被正确生成到 `<path>/.workbuddy/memory/MEMORY.md`。**

```markdown
# MEMORY.md — 长期记忆

## 项目性质

这是一个基于 Karpathy LLM Wiki 范式的个人知识库（Obsidian Vault）。

## 会话启动规则（必须遵守）

**每次新会话开始时，在做任何事之前，按顺序读取以下文件：**

1. `wiki/hot.md` — 会话热缓存（当前焦点、未解决问题、最近操作）
2. `AGENT.md` — Wiki 规则主文件（身份、架构、核心安全规则）
3. `wiki/index.md` — 总索引（知识库全貌）

根据用户要求的操作类型，按需加载子模块：
- 执行 ingest/query/lint → 读 `AGENT-workflows.md`
- 创建/更新 wiki 页面 → 读 `AGENT-schema.md`
- 撰写 wiki 内容 → 读 `AGENT-writing.md`

**每次会话结束前，更新 `wiki/hot.md`。**

## Schema 架构

| 文件 | 用途 |
|------|------|
| AGENT.md | 主文件：身份、多域架构、会话规则、安全规则 |
| AGENT-schema.md | Frontmatter 规范 + 页面类型模板 |
| AGENT-workflows.md | Ingest / Query / Lint 工作流 |
| AGENT-writing.md | 写作规范 + 标签体系 |

## 核心原则

- `raw/` 不可变——绝不修改、重命名、删除
- `wiki/` 由 LLM 维护，人类阅读
- 所有论述必须可追溯到 raw/ 来源
- 永不删除 wiki 页面——过时页面标记 `status: deprecated`
- `wiki/hot.md` 是唯一 LLM 可主动写入的 wiki 文件
```

### Step 5：输出配置指引

生成完所有文件后，输出以下指引：

---

**🎉 知识库创建完成！**

**接下来让它跑起来：**

**1. 打开 Obsidian**
- 打开 Obsidian → "Open folder as vault" → 选择 `<path>`

**2. 安装 Dataview 插件**
- 设置 → 社区插件 → 关闭安全模式 → 浏览 → 搜索 "Dataview" → 安装并启用
- 这个插件驱动仪表盘（`wiki/maps/dashboard.md`）的动态查询

**3. 配置 Web Clipper（推荐）**
- 浏览器安装 [Obsidian Web Clipper](https://obsidian.md/clipper) 扩展
- 扩展设置 → General → Vaults → 输入 `<知识库名>`
- Templates → Default → Folder 改为 `raw/<第一个域>/articles`
- （推荐）为每个域创建一个模板：

| 模板名 | Folder 路径 |
|--------|-------------|
<为每个域生成一行>

**4. 设置自动化定时 Ingest（强烈推荐）**

在 WorkBuddy 中设置一个自动化任务，**每天定时自动摄入新文章**，这样你只需要用 Web Clipper 剪藏，剩下的全自动完成。

设置方法：打开 WorkBuddy → 左侧栏 "自动化" → "添加自动化任务"，按以下配置填写：

| 配置项 | 填写内容 |
|--------|---------|
| **名称** | Wiki 自动 Ingest |
| **工作空间** | 选择你的知识库文件夹 `<path>` |
| **提示词** | 见下方 |
| **执行频率** | 每天 |
| **时间** | 09:00（或你喜欢的时间） |
| **星期** | 周一到周日全选 |

**提示词模板**（直接复制粘贴）：

```
先读取 wiki/hot.md 和 AGENT.md 了解当前状态。

然后扫描 raw/ 目录下所有 .md 文件，对比 wiki/index.md 和 wiki/log.md 中已摄入的记录，找出尚未被 ingest 的新文件。

如果没有新文件，简要报告"今日无新资料"并更新 wiki/hot.md，然后结束。

如果有新文件，按照 AGENT-workflows.md 中的 Ingest 流程逐篇处理：
1. 读取全文，判定所属域
2. 创建 source 摘要页
3. 更新或创建相关的 concept 和 entity 页面
4. 检查矛盾，更新交叉引用
5. 更新 wiki/index.md 和 wiki/log.md

全部完成后更新 wiki/hot.md。
```

> 💡 设置后，你只需要日常用 Web Clipper 剪藏文章到 `raw/` 目录，知识库会每天自动整理和更新。

**5. 开始使用**
```
1. 浏览器看到好文章 → Web Clipper 剪藏到对应域
2. 每天自动 ingest（如果设了自动化），或手动说 "帮我 ingest 没处理的文章"
3. 想问什么就问 → "wiki 里关于 xxx 有什么？"
4. 每隔一两周说 "lint" 做个体检
```

---

### 完成标志

所有文件生成完毕 + 配置指引输出 = **结束**。这个 Skill 只跑这一次。
