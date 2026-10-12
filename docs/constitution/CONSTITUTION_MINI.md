# Insights 项目宪法框架 (压缩版)

> **版本**: v1.4 | **用途**: AI System Prompt 注入 | **跨 IDE/模型通用**

---

## 五条最高原则 (不可违反)

### 原则零: Prompt 为中心
- 系统的最小设计单元是 **Prompt**,不是模块或函数
- 所有代码服务于 Prompt YAML 的定义、解析、编排、执行
- 新增分析意图 = 新增/修改 Prompt YAML,不修改核心引擎

### 原则一: 英文权威数据源
- **仅使用**: World Bank / IMF / OECD / 各国政府英文门户 / 央行 / BLS / Fed / ECB / Gartner / IDC
- **日本例外**: 日语官网可采集(信息更及时),但**输出必须翻译为中文**
- **严禁**: 任何中文网站(知乎/微博/百度等)、任何 UGC 平台
- **★ 来源可点击**: 报告中每个来源必须附带可点击官方 URL (使用 `src/renderers/source_links.py`),确保用户可即时验证数据真实性、减少幻觉

### 原则三: 中文输出
- 所有报告、分析结论、用户界面文本统一为**中文**
- 例外: 公司名(NVIDIA)、产品名(GPT-5)、股票代码(NVDA)可保留原文

### 原则四: 工具无关性
- 所有产物使用**标准格式** (YAML / Python / Markdown / HTML / CSS)
- 不依赖任何 IDE 或模型的私有格式

### 原则五: 反幻觉约束 (事实零虚构)
- **禁止**生成任何无法溯源至权威来源的事实性声明
- **数据缺失时**显式标注 "暂无数据" / "—",绝不用"合理推断"填充
- **推断 ≠ 事实** — 分析推断必须标注逻辑前提和置信度 (high/medium/low) 并与事实分离呈现
- **估算 ≠ 精确** — 区间估算不得以精确数字呈现,保留与来源一致的精度
- **每条数值必备三要素**: 来源 URL + 时间范围 + 单位,缺失则不渲染

---

## 数据来源分级

| 级别 | 类型 | 处理 |
|------|------|------|
| A | 英文权威机构 (World Bank/IMF/OECD) | 直接写入 DataPipe |
| B | 英文专业机构 (Gartner/IDC/McKinsey) | 预留 Hook,CSV 导入 |
| C | 英文商业数据 (Bloomberg/Reuters) | 可选 Pipe,缺失降级 |
| D | 日语官网 (仅限日本主题) | 可采集,输出必须中文 |
| F | 中文网站/UGC平台 | **绝对禁止** |

---

## 日本例外规则

- 适用条件: country_code="JP" 且日语官网信息比英文更及时
- 允许: 从日语官网采集数据
- 禁止: 日语原文直接输出、套用于其他国家
- 输出: 必须翻译为中文,附录保留日语 URL

---

## Prompt YAML 必须包含

- `data_source_policy.mode` = `english_authoritative_only`
- `data_source_policy.output_language` = `zh`
- `data_source_policy.forbidden_sources` 包含"任何中文网站"
- `data_pipes` 至少声明一条管道
- `analysis_dimensions` 每个维度声明 `required_data`
- `report.template` 对应已注册的 Renderer

---

## 代码规范

- 编码: UTF-8 | 中文: 双引号包裹 | 类型标注: 必须
- 命名: Prompt/Pipe ID = `snake_case` | 类名 = `PascalCase` | 常量 = `UPPER_SNAKE_CASE`
- DataPipe: 必须实现 `source_attribution()` 返回真实 URL
- Renderer: `template_name` 必须与 Prompt YAML 中 `report.template` 对应

---

## 跨 IDE/模型操作指南

**切换 IDE 或模型后,首轮对话必须**:
1. 读取本文件
2. 确认五条最高原则 (含反幻觉约束)
3. 回复: "已确认 Insights 宪法框架 v1.4,将在后续开发中严格遵守"

**IDE 特定配置**:
- CatPaw: `.catpaw/rules/constitution.md` → 软链到本文件
- CodeBuddy: `.codebuddy/rules/constitution.md` → 软链到本文件
- Cursor: `.cursor/rules/constitution.mdc` → 引用本文件
- 通用方案: 首轮对话粘贴本文件内容

---

## 违规处理

| 级别 | 行为 | 处理 |
|------|------|------|
| 严重 | 使用中文网站数据源 | 拒绝执行 |
| 严重 | 输出语言非中文 | 拒绝执行 |
| 严重 | 未执行宪法确认 | 停止开发 |
| 严重 | 编造/捏造数据 (无来源的数值) | 拒绝发布报告,追溯 DataPipe |
| 一般 | DataPipe 缺少 source_attribution | 警告 |
| 一般 | 推断未标注置信度/逻辑依据 | 警告,不修正不得发布 |
| 一般 | 实测/估算/预测类型混淆 | 警告,标注后方可发布 |
| 轻微 | 格式/注释不规范 | 建议修正 |

---

> **本文件为 docs/vibe_coding_constitution.md 的压缩版**  
> **完整版路径**: `docs/vibe_coding_constitution.md`
