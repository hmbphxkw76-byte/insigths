# Insights 项目宪法框架 (压缩版)

> **版本**: v1.7 | **用途**: AI System Prompt 注入 | **跨 IDE/模型通用**

---

## 六条最高原则 (不可违反)

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

### 原则六: 反时间幻觉约束 (日期感知报告生成 — **全Prompt通用**) ★v1.7更新
- **适用范围**: **所有 Prompt (macro/career/studyabroad/realestate/tech/...)** 无一例外 — 报告日期是唯一时间基准
- **渲染器统一使用 `analysis.context.format_date()`**: 所有渲染器不得使用 `datetime.now()` / `datetime.today()`,必须统一从 `ReportContext` 获取日期
- **文件名日期标签**: 使用 `analysis.context.date_tag()` 生成 `YYYYMMDD` 后缀,确保文件名与报告内元数据一致
- **禁止硬编码预测年份**: 分析管道中的 `insights` 不得硬编码未来年份(如"2026年预测"),必须使用 `ctx.this_year` / `ctx.next_year` / `ctx.year_str(offset=N)` 等动态函数生成
- **来源年份可追溯**: `source_attribution` 中的URL可包含年份,但须是已发布的报告年份(≤ report_date.year),不得引用"未来发布"的数据源
- **"今年/明年/N年后"规范**: 
  - 今年 = report_date.year
  - 明年 = report_date.year + 1  
  - N年后 = report_date.year + N
  - 须使用 `format_relative_year()` 或 `ReportContext.year_str(offset)` 进行自动转换
- **日本财政年度特别规则**: 4月1日开始的财政年度标识使用 `ctx.current_fy` / `ctx.next_fy`
- **留学/签证/房地产/科技 领域额外约束**:
  - 申请截止日期: 必须标注"以[机构名]官网最新公布为准",不得硬编码日期
  - 政策有效期: 必须引用政策原文中的生效日期 + 信息来源URL
  - 预测性陈述(如市场增速/TAM预测): 必须标注"截至{report_date}的预测"并区分基准年/预测年
  - 历史数据引用: 必须标注数据覆盖的时间区间(如 2020-2024 实际值 / 2025-2027 预测值)
- **违规判定**: 任何 Prompt 报告中出现与 `analysis.context.report_date` 不一致的时间引用 → 视为时间幻觉,须立刻修正

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
3. 回复: "已确认 Insights 宪法框架 v1.5,将在后续开发中严格遵守"

**IDE 特定配置**:
- CatPaw: `.catpaw/rules/constitution.md` → 软链到本文件
- CodeBuddy: `.codebuddy/rules/constitution.md` → 软链到本文件
- Cursor: `.cursor/rules/constitution.mdc` → 引用本文件
- 通用方案: 首轮对话粘贴本文件内容

---

## 职业赛道 URL 命名规范

- 国家/地区前缀使用 **小写英文 slug**: `dubai` / `japan` / `germany` / `singapore` / `australia` / `nz` / `uk` / `us`
- 报告文件名: `career_{country_slug}_{profession_slug}_{YYYYMMDD}.html`
- `[[country]]` / `[[profession]]` 占位符在 PromptRegistry.resolve() 阶段自动填充
- 工具函数: `src/utils/career_naming.py` → `resolve_career_title()` / `build_career_filename()`
- 禁止出现中文、大写字母、空格、占位符泄漏 (`career_country_xxx.html` 已废弃)

---

## 违规处理

| 级别 | 行为 | 处理 |
|------|------|------|
| 严重 | 使用中文网站数据源 | 拒绝执行 |
| 严重 | 输出语言非中文 | 拒绝执行 |
| 严重 | 未执行宪法确认 | 停止开发 |
| 严重 | 编造/捏造数据 (无来源的数值) | 拒绝发布报告,追溯 DataPipe |
| 严重 | 时间幻觉 (报告日期后仍引用过期的预测年份) | 拒绝发布,追溯分析方法 |
| 严重 | 渲染器使用 datetime.now() 而非 analysis.context | 拒绝发布,追溯渲染器 |
| 一般 | DataPipe 缺少 source_attribution | 警告 |
| 一般 | 推断未标注置信度/逻辑依据 | 警告,不修正不得发布 |
| 一般 | 实测/估算/预测类型混淆 | 警告,标注后方可发布 |
| 一般 | 硬编码年份而非使用 ReportContext | 警告,须重构后方可发布 |
| 轻微 | 格式/注释不规范 | 建议修正 |

---

> **本文件为 docs/vibe_coding_constitution.md 的压缩版**  
> **完整版路径**: `docs/vibe_coding_constitution.md`
