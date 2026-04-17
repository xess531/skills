# AGENT-workflows.md — 核心工作流

> 执行 Ingest / Query / Lint 操作时读取本文件。

## 1. Ingest（摄入）

当人类说 `ingest <filepath>` 或将新文件放入 `raw/` 后：

1. **读取**完整的原始文档
2. **判域**：根据文件路径或内容判定所属域（可能跨域）
3. **讨论**：输出 2-3 条核心要点 + 值得关注的论断 + 判定的域，等待人类确认
4. 人类确认后，执行以下步骤：
   - 在对应域的 `wiki/<domain>/sources/` 创建来源摘要页
   - 更新或创建对应域的 `wiki/<domain>/entities/` 页面
   - 更新或创建对应域的 `wiki/<domain>/concepts/` 页面
   - **跨域检查**：扫描其他域中是否有相关页面需要更新
   - 检查与已有内容的**矛盾**，用 `> ⚠️ 矛盾` 标注
   - 更新所有受影响页面的交叉引用（`[[wiki link]]` 格式）
   - 更新 `wiki/index.md`（在对应域分区下添加）
   - 追加到 `wiki/log.md`
5. **报告**：创建了什么、更新了什么、有没有矛盾、有没有跨域更新

## 2. Query（查询）

当人类提问时：

1. 先读 `wiki/index.md` 定位相关页面（可能跨域）
2. 读取相关页面
3. 综合回答，**必须引用来源**（格式：`(来源: [[wiki/<domain>/sources/xxx]])`）
4. 如果回答有价值，建议是否反哺为 wiki 新页面
5. **域内查询**：人类可以用 `query ai: "问题"` 限定域内搜索

### 查询反哺规则

当 Query 回答满足以下条件时，LLM 应**主动提议**将其存为 wiki 页面：

1. **对比分析** → 存入 `wiki/<domain>/comparisons/`
   - 触发条件：回答中包含 ≥2 个概念/工具的系统对比
   - 示例："RAG 和 LLM Wiki 哪个好？" → `comparisons/rag-vs-llm-wiki.md`

2. **综合洞察** → 存入 `wiki/<domain>/maps/`
   - 触发条件：回答整合了 ≥3 个已有页面的信息
   - 示例："AI Agent 领域的全景是什么？" → `maps/agent-tech-landscape.md`

3. **反哺页面的 frontmatter 标注**：
   ```yaml
   filed_from_query: true
   query_date: YYYY-MM-DD
   ```

不要过度反哺——只有真正新增知识的回答才存，简单的事实查询不存。

## 3. Lint（健康检查）

当人类说 `lint` 或 `lint <domain>` 时，执行以下检查清单：

### P0 — 数据完整性

1. 遍历 `wiki/**/*.md`，检查必填 frontmatter 字段是否齐全
2. 检查所有 `sources:` 路径指向的 raw 文件是否存在
3. 检查 `source_count` 是否与 `sources` 列表长度一致
4. 检查 `related:` 路径指向的 wiki 文件是否存在

### P1 — 知识图谱健康

5. 🔗 孤立页面（无任何其他页面的 `related` 指向它）
6. 🔍 高频引用但无独立页面：在 ≥3 个页面中被提到但没有自己的 wiki 页面
7. 🌐 跨域孤立：`domain` 标注多域但只在一个域有 related 链接
8. 📏 概念膨胀：单个概念页超过 3000 字，应考虑拆分

### P2 — 内容质量

9. 📝 Stub 页面（status: stub 且创建超过 7 天）
10. ❗ 页面间矛盾（新来源推翻旧结论）
11. ⏰ 过时检查：confidence: low 且超过 30 天未更新
12. 📥 `raw/` 里未摄入的文件
13. ❓ 缺失页面（被 `[[引用]]` 但不存在）

### 输出格式

```markdown
# Wiki Lint Report — YYYY-MM-DD

## 域统计
| 域 | 页面数 | 来源数 | Stubs | 矛盾 |
|...|...|...|...|...|

## P0 — 数据完整性 (N issues)
- ...

## P1 — 知识图谱健康 (N issues)
- ...

## P2 — 内容质量 (N issues)
- ...

## Suggested Next Steps
- ...
```

支持 `lint ai` 只检查 AI 域，`lint` 检查全部。
