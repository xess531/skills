# llm-wiki-init

> 一键创建 Karpathy-style LLM Wiki 个人知识库。

## 这是什么

一个 WorkBuddy Skill，帮你在 3 分钟内搭建一个完整的 AI 驱动个人知识库。你负责收集资料，LLM 负责整理、关联、维护一切。

基于 [Andrej Karpathy 的 LLM Wiki 范式](https://gist.github.com/karpathy/1dd0294ef9567971c1e4348a90d69285)：**让 LLM 把知识「编译」成持久的 Wiki，而非每次临时检索（RAG）。**

## 使用方法

在 WorkBuddy 中说：

```
帮我创建一个知识库
```

Skill 会问你 2 个问题，然后自动生成所有文件。

## 它会生成什么

一个完整的 Obsidian Vault，包含：

```
<你的知识库>/
├── AGENT.md                 ← LLM 的规则主文件
├── AGENT-schema.md          ← 页面格式规范
├── AGENT-workflows.md       ← 操作流程（ingest/query/lint）
├── AGENT-writing.md         ← 写作规范 + 标签体系
├── README.md                ← 使用指南
├── raw/                     ← 原始资料（你收集，LLM 只读）
│   └── <每个域>/            │   articles/ papers/ transcripts/ data/ assets/
├── wiki/                    ← 知识 Wiki（LLM 维护，你阅读）
│   ├── index.md             ← 总索引
│   ├── log.md               ← 操作日志
│   ├── hot.md               ← 会话热缓存
│   ├── <每个域>/            │   entities/ concepts/ sources/ comparisons/ maps/
│   └── maps/dashboard.md   ← Dataview 仪表盘
└── templates/
    └── web-clipper.md       ← 浏览器剪藏模板
```

## 核心概念

### 三层架构

| 层 | 目录 | 谁负责 | 作用 |
|----|------|--------|------|
| 原始资料 | `raw/` | **你** | 不可变的事实锚点，LLM 只读不写 |
| 知识 Wiki | `wiki/` | **LLM** | 结构化知识页面，所有论述可追溯到 raw |
| 规则 Schema | `AGENT*.md` | **共同** | 定义结构和工作流，越用越精确 |

### 五种 Wiki 页面

| 类型 | 回答什么问题 | 举例 |
|------|------------|------|
| **Entity（实体）** | "这是谁/什么？" | 公司、人物、工具、模型 |
| **Concept（概念）** | "这怎么理解？" | 理论、框架、方法论 |
| **Source（来源）** | "这篇文章讲了什么？" | 每篇原始资料的摘要，1:1 对应 |
| **Comparison（对比）** | "A 和 B 有什么区别？" | 两个概念/工具的系统对比 |
| **Map（导航）** | "这个主题下有什么？" | 某个大主题的页面全景 |

### 三个核心操作

| 操作 | 你说 | 发生什么 |
|------|------|---------|
| **Ingest** | "帮我 ingest 这篇文章" | LLM 读原文 → 创建 source + 更新 concept/entity → 更新索引 |
| **Query** | "React Hooks 有哪些最佳实践？" | LLM 查索引 → 读相关页面 → 综合回答 + 引用来源 |
| **Lint** | "lint" | LLM 做健康检查：矛盾、孤立页面、stub、缺失引用 |

### 域（Domain）

知识库按领域分区管理。可以是知识领域（前端开发、产品设计），也可以是项目（项目A、项目B）。不分领域的话会默认创建一个 `general` 通用域。每个域在 `raw/` 和 `wiki/` 下各有独立子目录。一个概念可以**跨域**存在。

### hot.md（会话热缓存）

LLM 每次会话结束前自动更新的状态快照（~500 词），记录当前焦点、未解决问题、最近操作。下次会话开始时 LLM 自动读取，不用你重新交代背景。

## 日常使用流程

```
1. 看到好文章 → Web Clipper 剪藏到 raw/ 对应域
2. 自动 ingest（如果设了定时任务），或手动说"帮我 ingest"
3. 想问什么就问 → LLM 从 wiki 中查找并综合回答
4. 每 1-2 周说 "lint" 做个体检
```

## 推荐：设置自动化定时 Ingest

在 WorkBuddy 的「自动化」中添加定时任务，让知识库每天自动处理新剪藏的文章：

| 配置项 | 填写内容 |
|--------|---------|
| 名称 | Wiki 自动 Ingest |
| 工作空间 | 选择知识库文件夹 |
| 执行频率 | 每天 09:00 |
| 星期 | 全选 |

提示词：

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

## 环境要求

- **WorkBuddy**（必须）— 知识库通过 WorkBuddy 的 memory 机制自动加载规则
- **Obsidian**（必须）— 浏览和阅读知识库
- **Obsidian Dataview 插件**（推荐）— 驱动仪表盘的动态查询
- **Obsidian Web Clipper**（推荐）— 浏览器一键剪藏文章到 raw/

> ⚠️ 本知识库默认配合 WorkBuddy 使用。如果使用其他 AI 工具（Claude Code、Cursor 等），AGENT.md 可能无法被自动加载，需要手动配置。

## 致谢

- [Andrej Karpathy](https://x.com/karpathy) — LLM Wiki 范式提出者
- [Karpathy-LLM-Wiki-Stack](https://github.com/ScrapingArt/Karpathy-LLM-Wiki-Stack) — 社区最完整的工程化参考
