# Insights 项目 Vibe Coding 宪法规范

> **版本**: v1.7  
> **生效日期**: 2026-10-12  
> **适用范围**: 本仓库所有代码、配置、数据管道、渲染器、文档及 AI 辅助开发活动  
> **跨工具兼容**: 本规范独立于任何 IDE (CatPaw / CodeBuddy / Cursor 等) 和任何 AI 模型 (LongCat / HY 等),具有工具无关性

---

## 第一部分:宪法框架 (Constitutional Framework)

### 1.1 最高原则 (Supreme Principles)

```
╔══════════════════════════════════════════════════════════════════════════╗
║                         最高原则 — 不可违反                               ║
║              (本宪法独立于任何 IDE 与 AI 模型,工具无关)                    ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  原则零: 架构核心 — Prompt 为中心 (Prompt-First Architecture)             ║
║  ─────────────────────────────────────────────────────────────────────   ║
║  整个系统的最小设计单元不是"模块"或"函数",而是 Prompt。                   ║
║  所有代码设计和实施必须服务于 Prompt 的定义、解析、编排、执行与输出。       ║
║  代码仅负责解析和执行 Prompt 中声明的意图,不得脱离 Prompt 独立运行。        ║
║                                                                          ║
║  原则一: 数据来源 — 英文权威机构优先                                      ║
║  ─────────────────────────────────────                                   ║
║  所有数据采集必须来自英文主流权威机构或官方网站。                           ║
║  严禁使用任何中文网站、UGC 平台作为数据来源。                              ║
║  ★ 来源可验证性:每条信息来源必须附带可点击的官方 URL,                       ║
║  确保用户可一键验证数据真实性,从机制上减少幻觉。                            ║
║                                                                          ║
║  原则二: 日本例外 — 日语官网可采但中文输出                                 ║
║  ─────────────────────────────────────                                   ║
║  针对日本主题相关内容,允许搜索并参照日语语言的官方网站                      ║
║  (如 e-Gov Japan、厚生劳动省、经济产业省、国土交通省等)。                  ║
║  日语官网仅为数据采集来源,最终输出必须为中文。                              ║
║                                                                          ║
║  原则三: 中文输出 — 终端用户统一中文                                       ║
║  ─────────────────────────────────────                                   ║
║  所有最终报告、分析结论、用户界面文本统一以中文显示给终端用户。              ║
║  禁止在最终输出中出现未翻译的外文片段(公司名/专有名词除外)。                ║
║                                                                          ║
║  原则四: 工具无关性 — 宪法约束跨 IDE/跨模型统一                            ║
║  ─────────────────────────────────────                                   ║
║  本宪法框架的规则适用于所有开发环境,无论使用何种 IDE 或 AI 模型。           ║
║  每次切换 IDE 或模型后,必须首先加载并确认本宪法,方可开始开发。              ║
║  开发产物(代码/配置/文档)不得包含特定 IDE 或模型的私有格式依赖。            ║
║                                                                          ║
║  原则五: 反幻觉约束 — 事实零虚构 (Zero Fabrication)                       ║
║                                                                          ║
║  原则六: 反时间幻觉约束 — 日期感知报告生成 (Date-Aware Reporting)        ║
║  ─────────────────────────────────────                                   ║
║  所有 Prompt 报告必须基于 ReportContext.report_date 作为唯一时间基准。     ║
║  禁止硬编码未来年份 / 禁止使用 datetime.now() 替代 analysis.context。    ║
║  渲染器必须统一使用 analysis.context.format_date() 生成元数据。            ║
║  ─────────────────────────────────────                                   ║
║  禁止 AI 生成任何无法溯源至权威来源的事实性声明。                           ║
║  数据缺失时必须显式标注"暂无数据"或"—",严禁推断填充或编造数值。          ║
║  分析推断必须明确标注逻辑前提和置信度,与原始事实严格分离。                   ║
║  每条数值必须附带时间范围、单位和来源机构,缺失任一要素则不呈现。            ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### 1.2 Prompt-First 架构约束 (Architectural Constraints)

> **原则零的衍生约束**: 以下规则是"Prompt 为中心"原则在所有开发活动中的具体体现。

#### 1.2.1 代码服务于 Prompt 的规则

| 规则 | 说明 | 违反判定 |
|------|------|---------|
| **代码不可脱离 Prompt 独立运行** | 所有 DataPipe、Analyzer、Renderer 必须由 Prompt YAML 驱动,不接受硬编码逻辑 | 存在不从 Prompt 注入参数而被直接调用的管道 |
| **新增分析意图 = 新增 Prompt YAML** | 扩展业务功能时,第一选择是添加/修改 Prompt 定义,而非常规代码修改 | 为简单需求修改核心引擎代码 |
| **Prompt 定义即文档** | Prompt YAML 是唯一可信的业务逻辑来源,代码注释应引用 Prompt 字段解释意图 | 代码逻辑与 Prompt YAML 不一致且无说明 |
| **配置与代码解耦** | Prompt 中声明的 data_pipes / analysis_dimensions / report 决定系统的全部行为 | 行为由代码中的条件分支而非 Prompt 配置决定 |

#### 1.2.2 开发优先级

当面临实现选择时,按以下优先级决策:

```
优先级 1: 是否让 Prompt YAML 更清晰地表达意图?           ← 最高
优先级 2: 是否让代码更好地执行 Prompt 声明的逻辑?         ← 次高
优先级 3: 是否让引擎层更通用,以支持更多 Prompt 变体?      ← 中等
优先级 4: 是否让特定 Prompt 的执行效率更高?               ← 较低
```

#### 1.2.3 Prompt 完整性检查

```python
def validate_prompt_centric_design():
    """验证系统设计是否符合 Prompt-First 原则。"""
    # 1. 每个 DataPipe 必须至少被一个 Prompt 的 data_pipes 引用
    # 2. 每个 Renderer 必须至少被一个 Prompt 的 report.template 引用
    # 3. Engine 层代码不得包含业务硬编码 (所有业务参数从 Prompt 注入)
    # 4. 所有 CLI 命令最终归结为: 解析 Prompt → 执行 Prompt → 输出报告
    ...
```

### 1.3 数据来源分级体系

| 级别 | 来源类型 | 典型示例 | 处理方式 |
|------|---------|---------|---------|
| **A 级** | 英文权威机构 | World Bank, IMF, OECD, 各国政府英文门户、央行、FBISTAT, BLS | 直接写入 DataPipe,优先采集 |
| **B 级** | 英文专业机构 | Gartner, IDC, McKinsey, BCG, Forrester, PitchBook, Crunchbase | 预留 Hook,支持 CSV 快照导入 |
| **C 级** | 英文商业数据 | Bloomberg, Reuters, Financial Times, SEC EDGAR | 封装为可选 Pipe,缺失时降级 |
| **D 级** | 国家特定语言 | 日本日语官网 (e-Gov, MHLW, MLIT, MOJ/NPA) | **仅限日本主题**,输出必须为中文 |
| **F 级** | **严禁使用** | 任何中文网站(知乎、微博、百度等)、任何 UGC 平台 | 绝对禁止,违反即拒绝执行 |

### 1.4 日本例外规则 (Japan-Specific Exception)

```yaml
# 日本例外适用条件 — 必须同时满足以下全部条件
country_specific_exception_JP:
  适用条件:
    - 主题域涉及日本国 (country_code = "JP")
    - 数据内容在日本官方机构英文版本中存在信息滞后或不完整
    - 日语官网提供的信息比英文版本更及时、更准确
  允许行为:
    - 搜索日语语言的官方网站采集数据
    - 从日语 PDF/公告中提取数值信息
  禁止行为:
    - 将日语原文直接输出到最终报告
    - 引用日语网站作为分析结论的唯一依据 (需交叉验证)
    - 将日本例外逻辑套用于其他国家
  输出要求:
    - 所有日语采集的数据必须翻译为中文
    - 报告附录保留原始日语来源 URL 备查
```

### 1.5 跨 IDE/跨模型保障机制 (Cross-Tool Compliance)

> **原则四的衍生约束**: 确保宪法框架在任何 AI 辅助开发环境中都得到严格执行。

#### 1.5.1 宪法文件的物理布局

宪法文件必须放置在仓库的固定位置,确保任何 IDE 的 AI 上下文都能自动发现:

```
insights/docs/
├── vibe_coding_constitution.md      # ★ 完整版宪法规范 (本文)
└── constitution/
    ├── CONSTITUTION_MINI.md         # ★ 压缩版宪法 (供 AI System Prompt 注入)
    └── constitution.version         # 宪法版本号文件
```

#### 1.5.2 模型切换时的强制加载协议

当开发环境发生以下任一变更时,必须执行初始化协议:

| 变更类型 | 触发条件 | 必须执行的动作 |
|---------|---------|---------------|
| 切换 AI 模型 | 从 LongCat 切换到 HY,或反之 | 重新加载 `CONSTITUTION_MINI.md` 并发送确认 |
| 切换 IDE | 从 CatPaw 切换到 CodeBuddy,或反之 | 在首轮对话中粘贴宪法摘要,要求模型确认 |
| 新建项目会话 | 开启全新对话/会话 | 在发送首条指令前,先加载宪法文件 |
| 长时间断开后恢复 | 会话间隔 >24 小时 | 重新发送宪法确认提示词 |

#### 1.5.3 宪法确认提示词 (通用模板)

以下提示词可在任何 IDE/模型中使用,用于在开发前强制加载宪法:

```
在开始任何开发工作之前,请先阅读并确认你已理解 docs/constitution/CONSTITUTION_MINI.md 中的全部宪法原则。
确认后将以下声明作为首条回复:
"已加载 Insights 项目宪法框架 v{version},确认遵守: (1)Prompt为中心 (2)英文权威数据源 (3)日本例外中文输出 (4)工具无关性"
```

#### 1.5.4 开发产物标准 (避免 IDE/模型锁定)

确保所有开发产物为纯文本/标准格式,避免 IDE 或模型的私有锁定:

| 产物 | 标准格式 | 禁止使用的格式 |
|------|---------|---------------|
| Prompt 定义 | YAML (UTF-8) | IDE 专有注释格式 |
| DataPipe 代码 | Python .py (UTF-8) | 模型生成的非标准语法 |
| 配置文件 | .yaml / .toml / .py | IDE 专有配置块 |
| 报告模板 | HTML + CSS (标准) | 框架绑定 (如 React/Vue)提交产物 |
| 文档 | Markdown (.md) | 仅 IDE 可读的二进制/专有格式 |

---

## 第二部分:架构分层与目录规范

### 2.1 分层架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                        用户 / 调度器                                │
│    "迪拜AI网络安全"  "全球宏观经济" "日本高度人才" "中东房地产"     │
└────────────────┬────────────────────────────────────────────────────┘
                 │ 关键词 / Prompt
                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Prompt Registry (提示词注册表)                     │  ◄── 配置层
│    macro_global   tech_ai   realestate_dubai   visa_japan_hsp      │
│    ├─ definition      ├─ definition     ├─ definition   ├─ ...    │
│    ├─ data_pipes      ├─ data_pipes     ├─ data_pipes   ├─ ...    │
│    ├─ analysis_spec   ├─ analysis_spec  ├─ analysis_sp  ├─ ...    │
│    └─ report_schema   └─ report_schema  └─ report_sch   └─ ...    │
└────────────────┬────────────────────────────────────────────────────┘
                 │ 解析后的执行计划
                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Prompt Runtime (提示词执行引擎)                   │  ◄── 引擎层
│                                                                     │
│  ┌───────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ DataPipe  │  │  Analyzer  │  │  Synthesizer│  │  Renderer  │  │
│  │ (数据采集)│  │  (分析计算)│  │  (综合归纳) │  │  (报告渲染)│  │
│  └───────────┘  └────────────┘  └────────────┘  └────────────┘  │
└────────────────┬────────────────────────────────────────────────────┘
                 │ 渲染后的报告
                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Report Store (报告仓库)                          │  ◄── 产物层
│    reports/tech/     reports/macro/     reports/career/            │
│    reports/realestate/    reports/studyabroad/                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构规范

```
insights/
├── main.py                          # CLI 入口
├── config/
│   └── settings.py                  # 全局路径配置(极简,仅目录常量)
│
├── prompts/                         # ⭐ Prompt 定义目录(核心配置)
│   ├── prompt_schema.yaml           # Prompt YAML Schema 校验定义
│   ├── macro/                       # 宏观经济赛道
│   ├── tech/                        # 科技行业赛道
│   ├── realestate/                  # 房地产赛道
│   ├── studyabroad/                 # 留学赛道
│   └── career/                      # 就业与移民赛道
│
├── src/
│   ├── prompt_registry/             # 提示词注册与匹配引擎
│   │   └── __init__.py              # PromptRegistry
│   │
│   ├── prompt_runtime/              # 提示词执行引擎
│   │   └── __init__.py              # PromptRuntime
│   │
│   ├── data_engine/                 # 数据引擎
│   │   ├── __init__.py              # DataPipe, PipeRunner, DataBundle
│   │   └── pipes/                   # 各主题域管道实现
│   │       ├── auto_register.py     # 自动注册器
│   │       ├── career/              # 海外就业·签证移民管道
│   │       ├── macro/               # 宏观经济管道
│   │       ├── realestate/          # 房地产管道
│   │       ├── studyabroad/         # 留学管道
│   │       └── tech/                # 科技管道
│
│   └── renderers/                   # 报告渲染器族
│       ├── __init__.py              # RendererFactory
│       ├── career/                  # 签证/职业/移民渲染器
│       ├── macro/                   # 宏观仪表盘
│       ├── realestate/              # 地产分析
│       ├── studyabroad/             # 留学分析
│       └── tech/                    # 麦肯锡风格科技渲染器
│
├── data/
│   └── store/                       # Pipe 引擎 Parquet 缓存仓库
│
├── docs/
│   ├── vibe_coding_constitution.md  # ★ 完整版宪法规范
│   └── constitution/
│       ├── CONSTITUTION_MINI.md     # ★ 压缩版宪法 (AI System Prompt 注入用)
│       └── constitution.version     # 宪法版本号追踪
│
└── reports/                         # 分析报告输出
    ├── career/
    ├── macro/
    ├── realestate/
    ├── studyabroad/
    └── tech/
```

### 2.3 主题域 (Vertical) 对齐规则

**核心约束**: `prompts/`、`src/data_engine/pipes/`、`src/renderers/` 三个目录的子目录名称必须一一对应。

| Vertical | ID 前缀 | prompts 子目录 | pipes 子目录 | renderers 子目录 |
|---------|---------|---------------|-------------|-----------------|
| 宏观经济 | `macro_` | `macro/` | `macro/` | `macro/` |
| 科技行业 | `tech_` | `tech/` | `tech/` | `tech/` |
| 房地产 | `realestate_` / `re_` | `realestate/` | `realestate/` | `realestate/` |
| 留学 | `studyabroad_` | `studyabroad/` | `studyabroad/` | `studyabroad/` |
| 就业移民 | `visa_` / `profession_` | `career/` | `career/` | `career/` |

---

## 第三部分: Prompt YAML 编写规范

### 3.1 最小必要字段

每个 Prompt YAML 必须包含以下强制字段:

```yaml
id: tech_xxx                         # 唯一标识符 (小写字母+下划线)
version: 1                            # 定义版本
enabled: true                         # 是否启用

data_source_policy:                   # ★ 数据来源合规策略 (强制)
  mode: english_authoritative_only    # 固定值,不可修改
  allowed_sources:                    # 允许的来源白名单
    - World Bank
    - IMF
  forbidden_sources:                  # 严禁的来源黑名单
    - 任何中文网站
    - 任何 UGC 平台
  output_language: zh                 # 固定值:中文输出
  country_specific_exceptions:        # 国家特定例外 (可选)
    JP:
      enabled: true
      language: ja
      official_sources:
        - e-Gov Japan
        - 厚生劳动省
      note: 仅限数据采集,输出仍为中文

label:
  zh: "中文显示名称"
  en: "English Display Name"

triggers:                             # 触发关键词列表
  - "关键词1"
  - "keyword2"

data_pipes:                           # 数据管道声明
  - pipe: pipe_id_name
    params:
      key: value

analysis_dimensions:                  # 分析维度
  - id: dimension_id
    label_zh: "维度中文名"
    label_en: "Dimension English Name"
    method: analysis_method
    required_data: [pipe_id_name]

report:
  template: template_name             # 渲染模板名
  output_dir: reports/tech            # 输出目录
  style:
    primary_color: "#0b2545"
    accent_color: "#c8a24b"

schedule:
  cadence: monthly
  time: "08:00"

quality:
  min_data_freshness_days: 30
  min_sources_per_section: 2
  anti_hallucination:                        # ★ 反幻觉配置 (强制)
    mode: strict                             # strict = 缺失数据显示"—",不推断填充
    require_data_period: true                # 每条数据必须标注时间范围
    require_unit: true                       # 数值必须带单位
    distinguish_inference: true              # 推断必须与事实分离呈现
    min_confidence_for_inference: medium     # 低于 medium 的推断不输出
```

### 3.2 `data_source_policy` 编写细则

#### 3.2.1 通用主题 (非日本)

```yaml
data_source_policy:
  mode: english_authoritative_only
  allowed_sources:
    - World Bank API (api.worldbank.org)
    - IMF Data (data.imf.org)
    - OECD Stats (stats.oecd.org)
    - U.S. Bureau of Labor Statistics (bls.gov)
    - U.S. Federal Reserve (federalreserve.gov)
    - European Central Bank (ecb.europa.eu)
    - 各国政府英文门户网站
  forbidden_sources:
    - 任何中文网站
    - 任何 UGC 平台 (知乎、Reddit、Twitter 等)
    - 未经验证的第三方博客
  output_language: zh
```

#### 3.2.2 日本主题

```yaml
data_source_policy:
  mode: english_authoritative_only
  allowed_sources:
    - Ministry of Justice Japan (moj.go.jp/isa/)
    - Immigration Services Agency of Japan (immi-moj.go.jp)
    - Ministry of Health, Labour and Welfare (mhlw.go.jp)
    - Ministry of Economy, Trade and Industry (meti.go.jp)
    - Ministry of Land, Infrastructure, Transport and Tourism (mlit.go.jp)
    - National Police Agency (npa.go.jp)
    - Japan Statistics Bureau (stat.go.jp)
    - World Bank
    - OECD
  forbidden_sources:
    - 任何中文网站
    - 任何 UGC 平台
  output_language: zh
  country_specific_exceptions:
    JP:
      enabled: true
      language: ja
      official_sources:
        - e-Gov Japan (e-gov.go.jp)
        - 厚生劳动省 (mhlw.go.jp)
        - 経済産業省 (meti.go.jp)
        - 国土交通省 (mlit.go.jp)
        - 法務省入管庁 (moj.go.jp/isa/)
      note: |
        日本例外规则:
        - 日语官网信息更新更及时时使用
        - 仅限数据采集来源
        - 最终输出必须为中文
        - 附录保留日语来源 URL 备查
```

### 3.3 YAML 禁止事项

| 禁止项 | 说明 | 后果 |
|--------|------|------|
| `allowed_sources` 包含中文网站 | 严禁任何中文域名出现在白名单 | 拒绝加载该 Prompt |
| `output_language` 非 `zh` | 输出语言必须为中文 | 拒绝加载该 Prompt |
| `mode` 非 `english_authoritative_only` | 数据源模式固定 | 拒绝加载该 Prompt |
| 日本例外套用于其他国家 | JP 例外不可扩展至其他国 | 拒绝加载该 Prompt |
| `data_pipes` 为空 | 至少声明一条管道 | 警告,但允许加载 |

---

## 第四部分: DataPipe 开发规范

### 4.1 DataPipe 基类约定

```python
from src.data_engine import DataPipe
import pandas as pd

class YourCustomPipe(DataPipe):
    """
    管道说明 — 清晰描述采集内容
    
    数据来源:
      - 来源机构英文名称 (official_url)
      - 来源机构英文名称 (official_url)
    """

    pipe_id = "your_custom_pipe"      # ★ 必须唯一,与 YAML 中 pipe 字段对应

    def collect(self, params: Dict) -> pd.DataFrame:
        """
        核心采集方法 — 返回结构化 DataFrame
        
        Args:
            params: Prompt YAML 中声明的 params
            
        Returns:
            pd.DataFrame: 采集到的结构化数据
        """
        # 实现数据采集逻辑
        ...

    def source_attribution(self) -> List[str]:
        """声明数据来源 (引用追踪) — 返回来源机构名+URL"""
        return [
            "机构英文名称",
            "https://official.url",
        ]
```

### 4.2 数据来源合规检查清单

在编写 `collect()` 方法时,必须确认:

- [ ] 所有数据来源于 A/B/C 级英文权威机构或 D 级(仅限日本主题)
- [ ] API 请求使用官方 API 端点 (如 `data.worldbank.org`, `data.imf.org`)
- [ ] 网页抓取目标为官方机构 `.gov` `.go.jp` `.int` 或公认的 `.org` 权威机构
- [ ] 不涉及任何中文域名网站的请求
- [ ] `source_attribution()` 返回真实可访问的 URL
- [ ] DataFrame 中包含 `source_url` 列,逐条记录数据来源

### 4.3 管道注册规范

```python
# 方式一: 装饰器注册 (推荐,用于新建管道)
from src.data_engine import register_pipe

@register_pipe
class NewDataPipe(DataPipe):
    pipe_id = "new_data_pipe"
    def collect(self, params: Dict) -> pd.DataFrame:
        ...

# 方式二: auto_register.py 显式导入 (用于现有管道批量管理)
# 在 src/data_engine/pipes/auto_register.py 的 _ALL_STATIC_PIPE_CLASSES 列表中添加
```

### 4.4 缓存与降级策略

```python
class RobustPipe(DataPipe):
    pipe_id = "robust_pipe"
    
    def collect(self, params: Dict) -> pd.DataFrame:
        # 策略: 优先 API → 降级缓存 → 降级模拟数据
        try:
            return self._fetch_from_api(params)
        except NetworkError:
            logger.warning(f"[{self.pipe_id}] API 不可用,尝试使用缓存")
            try:
                return self._load_from_cache(params)
            except NoCacheError:
                logger.warning(f"[{self.pipe_id}] 无可用缓存,使用模拟数据")
                return self._generate_fallback_data()
    
    def _fetch_from_api(self, params) -> pd.DataFrame:
        """从官方 API 采集 — 主路径"""
        ...
    
    def _load_from_cache(self, params) -> pd pd.DataFrame:
        """从本地 Parquet 缓存加载 — 降级路径"""
        ...
    
    def _generate_fallback_data(self) -> pd.DataFrame:
        """生成降级数据 (标注为模拟) — 最后手段"""
        ...
```

---

## 第五部分: Renderer 开发规范

### 5.1 渲染器注册

```python
# src/renderers/tech/mckinsey_style.py
from src.renderers import BaseRenderer

class McKinseyTechRenderer(BaseRenderer):
    template_name = "mckinsey_tech"   # ★ 与 Prompt YAML 中 report.template 对应
    
    def render(self, analysis: Dict, prompt) -> str:
        """
        渲染报告为 HTML
        
        Args:
            analysis: 分析结果字典
            prompt: PromptDefinition 实例
            
        Returns:
            HTML 字符串
        """
        ...
```

### 5.2 中文输出强制规范

```python
class compliantRenderer(BaseRenderer):
    
    def render(self, analysis: Dict, prompt) -> str:
        # ★ 所有面向用户的文本必须为中文
        sections = self._build_sections(analysis)
        
        # 正确做法
        title = "执行摘要"
        conclusion = "基于上述分析,我们认为..."
        
        # 错误做法 (禁止)
        # title = "Executive Summary"
        # conclusion = "Based on the analysis above, we believe..."
        
        # 允许保留原文的例外: 公司名称、股票代码、专有名词
        # 例如: "NVIDIA Corporation (NVDA)", "GPT-5", "MMLU"
        
        return self._assemble_html(title, sections, conclusion)
```

### 5.3 来源引用规范 (强制可点击)

> **★ 核心规则**: 每份报告中的**每一个来源**必须能**直接点击**打开对应的官方网页,方便用户验证信息真实性,从机制上减少幻觉。

#### 5.3.1 来源链接实现规范

```python
# src/renderers/source_links.py 中维护权威来源 URL 映射表 (SOURCE_URL_MAP)
# 所有 Renderer 渲染来源时必须使用 render_source_ul_as_html() 或 render_source_list_as_html()

# 正确做法: 使用 source_links 工具函数渲染来源
from src.renderers.source_links import render_source_ul_as_html, render_source_list_as_html

sources = ["Gartner — Market Guide for AI Security (Sept 2025)", "IDC — MEA Forecast"]
html = render_source_ul_as_html(sources)
# → <li>Gartner — Market Guide... — <a href="https://www.gartner.com/en">...</a></li>

# 错误做法: 直接输出纯文本
# html = ''.join(f'<li>{s}</li>' for s in sources)  # ← 违反规范!
```

#### 5.3.2 URL 匹配优先级

解析来源字符串时,按以下优先级确定 URL:

1. **内嵌 URL**: 来源字符串本身含 `https://...(URL)`,直接使用
   - 示例: `"(一財)日本自動車連盟(JAF) — https://www.jaf.or.jp/"`
2. **映射表查询**: 根据来源机构名称匹配 `SOURCE_URL_MAP`
   - 内置映射表涵盖 Gartner/IDC/Frost & Sullivan/McKinsey/CrowdStrike 等 50+ 权威机构
   - 新增映射在 `src/renderers/source_links.py` 维护
3. **纯文本 fallback**: 映射表中找不到时,保持纯文本(无链接下划线)

#### 5.3.3 HTML 渲染输出要求

```html
<!-- 报告末尾 "来源与方法论" 章节 -->
<ul class="source-list">
  <li>Gartner — Market Guide for AI Security (Sept 2025) — 
      <a href="https://www.gartner.com/en" target="_blank" rel="noopener noreferrer">https://www.gartner.com/en</a>
  </li>
  <li>出入国在留管理庁 — 
      <a href="https://www.moj.go.jp/isa/" target="_blank" rel="noopener noreferrer">https://www.moj.go.jp/isa/</a>
  </li>
</ul>

<!-- 章节内来源脚注 -->
<div class="source-section-label">
  来源: 
  <a href="https://..." target="_blank" rel="noopener noreferrer">Gartner — ...</a> | 
  <a href="https://..." target="_blank" rel="noopener noreferrer">IDC — ...</a>
</div>
```

#### 5.3.4 链接样式规范

所有来源链接必须使用统一的视觉样式:
- **未访问**: 蓝色 (#1565c0) + 点状下划线 (dotted),与正文区分
- **悬停 (hover)**: 深色 (#0b2545) + 实线下划线
- **新开窗口**: `target="_blank" rel="noopener noreferrer"`
- **无链接时**: 纯文本显示(无下划线误导用户)

#### 5.3.5 渲染器适配清单

| 渲染器 | 文件 | 当前状态 |
|--------|------|---------|
| McKinseyTechV2Renderer | `renderers/tech/mckinsey_v2.py` | ✅ 已适配 (使用 source_links) |
| McKinseyTechRenderer | `renderers/tech/mckinsey_style.py` | ✅ 已适配 (使用 source_links) |
| ProfessionAnalyzerRenderer | `renderers/career/profession_analyzer.py` | ✅ 已适配 (使用 source_links) |
| MacroDashboardRenderer | `renderers/macro/dashboard.py` | ⏳ 待适配 (硬编码来源) |
| RealEstateDashboard | `renderers/realestate/dashboard.py` | ⏳ 待适配 (硬编码来源) |
| VisaTrackerRenderer | `renderers/career/visa_tracker.py` | ⏳ 待适配 |

> **递增要求**: 每新建/修改一个 Renderer,必须使用 `source_links` 模块渲染所有来源。

### 5.4 职业 (Career) 赛道 URL 文件命名与路由规范

> **★ 核心规则**: 职业/签证赛道的报告文件名和页面标题必须使用 **小写英文前缀** 标识目标国家/地区，避免 `[[country]]` 占位符泄漏或中文/混乱名称出现。

#### 5.4.1 国家/地区前缀命名规则

| 目标 | 前缀 (slug) | 示例报告文件名 | 示例页面标题 |
|------|------------|----------------|-------------|
| 迪拜/阿联酋 | `dubai` | `career_dubai_ai_security_engineer_20261012.html` | Dubai AI Security Engineer 人才深度分析 |
| 日本 | `japan` | `career_japan_it_engineer_20261012.html` | Japan IT Engineer 人才深度分析 |
| 德国 | `germany` | `career_germany_auto_engineer_20261012.html` | Germany Auto Engineer 人才深度分析 |
| 新加坡 | `singapore` | `career_singapore_data_analyst_20261012.html` | Singapore Data Analyst 人才深度分析 |
| 澳洲/澳大利亚 | `australia` | `career_australia_accountant_20261012.html` | Australia Accountant 人才深度分析 |
| 新西兰 | `nz` | `career_nz_driver_20261012.html` | NZ Driver 人才深度分析 |
| 英国 | `uk` | `career_uk_finance_20261012.html` | UK Finance 人才深度分析 |
| 加拿大 | `canada` | `career_canada_nurse_20261012.html` | Canada Nurse 人才深度分析 |
| 美国 | `us` | `career_us_software_engineer_20261012.html` | US Software Engineer 人才深度分析 |

#### 5.4.2 模板变量解析规则

`profession_country.yaml` 中使用 `[[country]]` 和 `[[profession]]` 作为模板占位符，必须在 **执行时** 替换为实际小写英文值：

```python
# src/utils/career_naming.py 中实现 resolve_career_title()
def resolve_career_title(keyword: str) -> Tuple[str, str]:
    """
    将用户输入的关键词映射为 (country_slug, profession_slug)。
    
    返回值:
        country_slug:   "dubai" / "japan" / "germany" / ...
        profession_slug: "ai-security-engineer" / "it-engineer" / ...
    
    示例:
        "迪拜AI安全工程师" → ("dubai", "ai-security-engineer")
        "日本IT"          → ("japan", "it-engineer")
        "Germany automotive" → ("germany", "automotive-engineer")
    """
    ...
```

#### 5.4.3 报告文件命名规范

```
reports/career/career_{country_slug}_{profession_slug}_{YYYYMMDD}.html
```

- 所有字母 **小写**
- 多单词用 **连字符** (`-`) 连接
- 日期使用 ISO 短格式 (`YYYYMMDD`)
- 禁止出现中文字符、空格、大写字母

#### 5.4.4 标题渲染规范

报告 HTML `<title>` 和 `<h1>` 显示格式:

```html
<!-- 正确 -->
<title>Dubai AI Security Engineer 人才需求与就业前景深度分析</title>
<h1>Dubai AI Security Engineer 人才需求与就业前景深度分析</h1>

<!-- 错误 — 占位符泄漏 -->
<title>[[country]][[profession]]人才需求与就业前景深度分析</title>

<!-- 错误 — 混乱格式 -->
<title>阿联酋・迪拜 AI安全工程师 人才分析</title>
```

#### 5.4.5 PromptRegistry 集成要求

当通过 `--keyword` 触发 `profession_country` 类模板 Prompt 时，`PromptRegistry.resolve()` 必须在返回 `PromptDefinition` 前调用 `resolve_career_title()` 填充 `label_zh` 和 `label_en` 中的 `[[country]]` / `[[profession]]` 占位符。

```python
# src/prompt_registry/__init__.py — resolve() 方法中
if matched_prompt.id.startswith("profession_"):
    from src.utils.career_naming import resolve_career_title
    country_slug, profession_slug = resolve_career_title(keyword)
    matched_prompt = _fill_career_template(matched_prompt, country_slug, profession_slug)
```

### 5.6 反时间幻觉规范 (Date-Aware Reporting — **全Prompt通用**) ★v1.7新增

> **★ 原则六衍生规范**: 以下规则是"日期感知报告生成"原则在 **所有垂直赛道 (macro/career/studyabroad/realestate/tech)** 的具体体现。时间幻觉是报告可信度的慢性毒素,必须从架构层面彻底根除。

#### 5.6.1 适用范围 (无一例外)

| 垂直赛道 | 日期敏感元素 | 强制约束 |
|---------|------------|---------|
| **宏观 (macro)** | GDP预测/政策利率/通胀展望 | 使用 `ctx.year_str(offset)` 动态生成年份;引用IMF/WorldBank/OECD报告时标注报告发布年份 |
| **留学 (studyabroad)** | 申请截止日期/开学时间 | 必须标注以官网最新公布为准;不得硬编码"2025年9月入学" |
| **职业移民 (career)** | 签证政策/工资中位数/认证要求 | 政策生效日期+信息来源URL;时效性数据须标注"截至{report_date}" |
| **房地产 (realestate)** | 房价指数/租金回报率/交易量 | 历史数据标注时间区间(如 2020-2024 实际值);预测标注基准年 |
| **科技 (tech)** | TAM预测/融资数据/技术路线图 | 区分"已发布/已验证"与"预测/推测";标注数据来源的采集/发布时间 |

#### 5.6.2 渲染器日期规范 (Renderer Date Policy)

```python
# ❌ 违规写法 — 使用系统当前时间(每次生成报告会产生不同日期)
from datetime import datetime
meta = f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

# ✅ 正确写法 — 使用 ReportContext 保证整份报告时间一致
meta = f"生成时间: {analysis.context.format_date('%Y-%m-%d %H:%M')}"
```

**强制规则**:
1. 所有 6 个渲染器 (visa_tracker / japan_driver / migration_lifecycle / profession_analyzer / mckinsey_style / mckinsey_v2 / real_estate_dashboard / japan_economy) **禁止导入 `from datetime import datetime`** 用于报告生成
2. 所有日期元数据字段必须来自 `ReportContext.format_date()` 或 `ReportContext.date_tag()`
3. 文件名的 YYYYMMDD 标签必须使用 `analysis.context.date_tag()` 生成
4. 报告内所有"今年/明年/去年"必须使用 `ctx.this_year / ctx.next_year / ctx.year_str(-1)` 等动态值

#### 5.6.3 分析方法日期规范

所有 `_method_*` 函数的签名必须包含 `ctx: ReportContext = None` 参数:

```python
# ✅ 正确签名
def _method_xxx(self, s: SectionResult, p: PromptDefinition, ctx: ReportContext = None):
    c = ctx or ReportContext()  # 容错:若无上下文则创建默认
    s.insights.append(f"【数据覆盖】{c.this_year}年度实际值 + {c.next_year}年度预测")
    s.source_attribution.append(f"IMF WEO {c.quarter_str(0, 2)} — https://...")
```

#### 5.6.4 Prompt YAML 时间声明

Prompt YAML 字段中 **hardcode 未来年份的位置** 必须通过动态生成:

```yaml
# ❌ 错误示例
analysis_dimensions:
  - id: growth_forecast
    label_zh: "2025-2030年美国经济增长展望"  # 硬编码 → 时间幻觉

# ✅ 正确示例
analysis_dimensions:
  - id: growth_forecast
    label_zh: ""  # 运行时由 _method 函数动态生成
```

**规则**: Prompt YAML 的 `label_zh` 和 `label_en` 中不得包含具体年份(如"2025"/"2026")。所有时间相关的显示值必须由分析方法在运行时动态生成。

#### 5.6.5 时间幻觉检查清单 (Submit前必检)

```markdown
Report QA Checklist (时间幻觉专项):
□ 所有渲染器已移除 datetime.now() 调用
□ 文件名 YYYYMMDD 与报告内元数据日期一致
□ 报告生成的年份 ≤ report_date.year (不得引用"未来发布"的数据)
□ 所有预测性陈述已标注 "(E)" / "预测" / "estimated" 后缀
□ 申请类信息已标注"以[官网名]最新公布为准"
□ 使用 format_relative_year() / year_str() 生成相对年份
```

#### 5.6.6 违规拦截机制

```python
# 建议在 PromptRuntime.execute() 末尾增加时间幻觉检测
def _detect_time_hallucination(analysis: AnalysisResult) -> List[str]:
    """检测报告中的时间幻觉."""
    violations = []
    report_year = analysis.context.report_year
    for section in analysis.segments:
        for insight in section.insights:
            # 检测硬编码的未来年份 (如 2027/2028/2029/2030)
            future_years = [str(y) for y in range(report_year + 1, report_year + 10)]
            if any(y in insight for y in future_years):
                if "(E)" not in insight and "预测" not in insight:
                    violations.append(f"[{section.dimension_id}] 可能的时间幻觉: {insight[:50]}")
    return violations
```

---

### 5.5 反幻觉防控规范 (Anti-Hallucination Best Practices)

> **★ 原则五衍生规范**: 以下规则是"事实零虚构"原则在所有数据采集、分析、渲染活动中的具体体现。AI 幻觉是报告质量的最大威胁,必须从架构层面建立防线。

#### 5.4.1 幻觉定义与分类

本项目将 AI 幻觉划分为三级,每级有对应的防控策略:

| 幻觉级 | 说明 | 典型表现 | 防控策略 |
|--------|------|---------|---------|
| **L1 数据捏造** | 完全编造不存在的数值 | "市场规模达到 3,247 亿美元"(实际不存在该数据) | DataPipe 强校验 + 来源绑定 |
| **L2 过度推断** | 基于少量事实做出缺乏依据的推论 | "由于 A 增长 10%,预计 B 必然增长 15%" | 推断标注 + 置信度评分 |
| **L3 来源混淆** | 将不同来源/时间/范围的数值错误拼接 | 将 2024 年数据标注为 2025 年,或将估算值标注为实测值 | 元数据追踪 + 单位校验 |

#### 5.4.2 数据采集层防幻觉规则

```python
class AntiHallucinationDataPipe(DataPipe):
    """
    防幻觉数据管道基类 — 所有 DataPipe 必须遵守此约定
    """
    
    def collect(self, params: Dict) -> pd.DataFrame:
        df = self._fetch_data(params)
        
        # 规则 1: 每条数据必须带来源 URL
        assert "source_url" in df.columns, "缺失 source_url 列 — 违反反幻觉原则"
        
        # 规则 2: 每条数据必须有时间戳/时间范围
        assert "data_period" in df.columns, "缺失 data_period 列 — 无法判断数据时效性"
        
        # 规则 3: 数值必须带单位
        assert "unit" in df.columns or self._infer_unit(df) is not None
        
        # 规则 4: 缺失值用 NaN/None 表示,绝不使用"合理推断值"填充
        df = df.where(pd.notnull(df), None)
        
        return df
    
    def source_attribution(self) -> List[str]:
        """必须返回含 URL 的来源声明 — 见 source_links.SOURCE_URL_MAP"""
        raise NotImplementedError("每个 Pipe 必须声明真实可访问的来源 URL")
```

#### 5.4.3 三条铁律 (不可违反)

**铁律一: 无来源 ≠ 数据**

```python
# ❌ 违反铁律: 没有来源时就编造一个"合理"数值
market_size = 324.7  # 324.7 亿美元 — 从哪来的?

# ✅ 正确做法: 返回缺失标记,渲染层显示"—"或"暂无数据"
market_size = None  # DataPipe 未获取到该指标
```

**铁律二: 推断 ≠ 事实**

```python
# ❌ 违反铁律: 将分析推断呈现为确定事实
"中东网络安全市场将增长 20%" — 这是 AI 推断,不是数据来源陈述

# ✅ 正确做法: 标注推断来源和逻辑链
"基于 Frost & Sullivan 2024 基准增长率 12% + MEA数字化转型加速 (+~8pp),推断中值 20% (置信度: 中等)"
```

**铁律三: 估算 ≠ 精确**

```python
# ❌ 违反铁律: 将区间估算呈现为精确数字
"市场规模 = 324.7 亿美元" — 精确到小数点后 1 位,实际是区间估算

# ✅ 正确做法: 保留精度与数据来源一致
"市场规模 ≈ 320-330 亿美元 (来源: Gartner, 2025Q2, 区间估算)"
```

#### 5.4.4 数据元数据强制字段

DataPipe 输出的 DataFrame 必须包含以下元数据列,作为渲染层判断"该数值是否可信"的依据:

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `source_url` | str | ✅ | 数据点对应的可访问 URL | `https://www.gartner.com/...` |
| `data_period` | str | ✅ | 数据涵盖的时间范围 | `2025Q1`, `FY2024`, `截至 2025-06` |
| `unit` | str | ✅ | 数值单位 | `亿美元`, `%`, `千人` |
| `data_type` | str | ✅ | 数据类型: `actual`(实测) / `estimate`(估算) / `forecast`(预测) | `actual` |
| `confidence` | str | 建议 | 置信度: `high` / `medium` / `low` | `high` |
| `caveat` | str | 可选 | 附加说明/注意事项 | `不含消费级市场` |
| `retrieval_date` | str | ✅ | DataPipe 实际采集日期(ISO 8601) | `2025-10-12` |

#### 5.4.5 渲染层防幻觉呈现规则

```python
class AntiHallucinationRenderer(BaseRenderer):
    
    def _render_data_point(self, row: Dict) -> str:
        """
        渲染单个数值点 — 必须包含: 数值 + 单位 + 时间范围 + 来源链接
        """
        # 正确: 所有要素齐全
        return (
            f'<span class="data-value">{row["value"]}</span> '
            f'<span class="data-unit">{row["unit"]}</span> '
            f'<span class="data-period">({row["data_period"]})</span> '
            f'<span class="data-source">{render_source_as_html(row["source"])}</span>'
        )
        
        # 缺少任何要素 = 该数值不应呈现,替换为"—"
        if not all([row.get("value"), row.get("unit"), row.get("source")]):
            return '<span class="data-missing">—</span>'
    
    def _render_inference(self, statement: str, logic: str, confidence: str) -> str:
        """
        渲染推断性结论 — 必须与事实明确区分
        """
        confidence_colors = {"high": "#2e7d32", "medium": "#f57c00", "low": "#c62828"}
        return (
            f'<div class="inference-box" style="border-left: 3px solid {confidence_colors[confidence]};">'
            f'  <div class="inference-label">分析推断 (置信度: {confidence})</div>'
            f'  <div class="inference-statement">{statement}</div>'
            f'  <div class="inference-logic">逻辑依据: {logic}</div>'
            f'</div>'
        )
```

#### 5.4.6 Prompt YAML 反幻觉约束

每个 Prompt YAML 必须在 `quality` 节点下声明反幻觉策略:

```yaml
quality:
  min_data_freshness_days: 30
  min_sources_per_section: 2
  anti_hallucination:                        # ★ 反幻觉配置 (强制)
    mode: strict                             # strict = 缺失数据显示"—",不推断填充
    require_data_period: true                # 每条数据必须标注时间范围
    require_unit: true                       # 数值必须带单位
    distinguish_inference: true              # 推断必须与事实分离呈现
    min_confidence_for_inference: medium     # 低于 medium 的推断不输出
```

#### 5.4.7 幻觉风险检查清单 (提交前自检)

```markdown
Report QA Checklist (反幻觉专项):
  □ 每个数值都有可点击的来源链接
  □ 每个数值都标注了时间范围/数据期
  □ 每个数值都标注了单位
  □ 实测/估算/预测有明确区分
  □ 推断性结论有置信度标注和逻辑依据
  □ 无来源的数据点已标注"—"而非空格或隐藏
  □ 没有将区间估算呈现为精确数字
  □ 没有跨来源拼接的数据(除非标注为交叉验证后的综合)
  □ AI 生成的段落没有冒充引用(如"据 Gartner 报道"但无法提供具体报告名+URL)
```

#### 5.4.8 检测与拦截机制

建议在系统层面增加以下自动化检测:

```python
class HallucinationDetector:
    """
    幻觉检测器 — 在报告生成后自动扫描潜在幻觉信号
    """
    
    def check_report(self, html: str, source_registry: List[str]) -> List[str]:
        warnings = []
        
        # 检测 1: 含有具体数值但无来源链接的段落
        unfumbered = self._find_values_without_source(html)
        if unfumbered:
            warnings.append(f"发现 {len(unfumbered)} 个无来源数值: {unfnumbered[:3]}...")
        
        # 检测 2: 引用了来源名称但不在 source_registry 中
        orphan_refs = self._find_orphaned_references(html, source_registry)
        if orphan_refs:
            warnings.append(f"发现悬空来源引用: {orphan_refs}")
        
        # 检测 3: 数值精度异常 (如 GDP 精确到个位)
        precision_anomalies = self._check_precision_anomalies(html)
        if precision_anomalies:
            warnings.append(f"精度异常: {precision_anomalies}")
        
        return warnings
```

---

## 第六部分: 编码与命名规范

### 6.1 文件命名

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| Prompt YAML | `{vertical}_{topic}.yaml` | `tech_ai.yaml`, `visa_japan_hsp.yaml` |
| DataPipe | `{domain}_pipes.py` | `tech_pipes.py`, `japan_visa_pipes.py` |
| Renderer | `{style}_renderer.py` 或 `{style}.py` | `mckinsey_style.py`, `dashboard.py` |
| 配置文件 | `settings.py` | `config/settings.py` |

### 6.2 代码标识符命名

| 元素 | 规则 | 示例 |
|------|------|------|
| Prompt ID | `小写_数字_下划线` | `tech_ai`, `visa_japan_hsp`, `study_abroad_jp` |
| Pipe ID | `小写_数字_下划线` | `ai_compute_demand`, `japan_immigration_policy` |
| 类名 | `PascalCase` + 后缀 | `JapanSSWPolicyPipe`, `McKinseyTechRenderer` |
| 方法/函数 | `snake_case` | `collect()`, `source_attribution()` |
| 常量 | `UPPER_SNAKE_CASE` | `OFFICIAL_SOURCES`, `DEFAULT_CACHE_TTL` |

### 6.3 编码强制性要求

1. **文件编码**: 所有 `.py` 文件使用 UTF-8 编码
2. **Windows 控制台兼容**: `main.py` 必须包含 UTF-8 stdout 重配置
3. **中文字符串**: 代码中的中文字符串使用双引号包裹
4. **注释**: 所有公开类和方法必须有 docstring (中英文均可,优先中文)
5. **类型标注**: 所有函数参数和返回值必须有类型标注

---

## 第七部分: 质量护栏与验证

### 7.1 Prompt 加载时校验

PromptRegistry 在加载每个 YAML 时必须执行以下校验:

```python
def _validate_prompt(raw: Dict, path: Path) -> List[str]:
    """返回错误列表,为空则通过."""
    errors = []
    
    # 强制字段检查
    for field in ["id", "data_source_policy", "data_pipes", "analysis_dimensions", "report"]:
        if field not in raw:
            errors.append(f"缺少强制字段: {field}")
    
    # 数据来源合规检查
    policy = raw.get("data_source_policy", {})
    if policy.get("mode") != "english_authoritative_only":
        errors.append("data_source_policy.mode 必须为 english_authoritative_only")
    if policy.get("output_language") != "zh":
        errors.append("data_source_policy.output_language 必须为 zh")
    
    # 禁止来源检查
    forbidden = policy.get("forbidden_sources", [])
    if "任何中文网站" not in str(forbidden):
        errors.append("forbidden_sources 必须包含中文网站")
    
    # 日本例外仅限 JP
    exceptions = policy.get("country_specific_exceptions", {})
    for country_code in exceptions:
        if country_code != "JP":
            errors.append(f"不支持 {country_code} 的国家特定例外")
    
    return errors
```

### 7.2 数据管道运行时验证

```python
def validate_pipe_output(df: pd.DataFrame, pipe_id: str) -> bool:
    """验证管道输出是否符合规范."""
    if df is None or df.empty:
        logger.warning(f"[{pipe_id}] 输出为空")
        return False
    
    # 日本主题管道检查: source_url 应包含 .go.jp 域名
    if "japan" in pipe_id:
        if "source_url" not in df.columns:
            logger.warning(f"[{pipe_id}] 日本管道缺少 source_url 列")
    
    return True
```

### 7.3 报告渲染后验证

```python
def validate_report_output(html: str, prompt_id: str) -> bool:
    """验证最终 HTML 报告是否符合中文输出规范."""
    # 检查是否包含大量未翻译的英文段落 (排除代码块/URL/专有名词)
    # 允许的英文: 公司名(NVIDIA)、产品名(GPT-5)、股票代码(NVDA)
    ...
```

### 7.4 健康检查集成

```bash
# 系统健康检查应包含数据来源合规扫描
python main.py --health
# 预期输出:
# [OK] PromptRegistry: X prompts loaded
# [OK] DataEngine: Y pipes ready  
# [OK] All Prompt data_source_policy validated (english_authoritative_only + zh output)
# [OK] No forbidden sources detected in any Prompt definition
```

---

## 第八部分: 扩展新赛道工作流

### 8.1 新增主题 Prompt (无需修改代码)

```bash
# 1. 在 prompts/{vertical}/ 下新建 YAML 文件
# 2. 定义完整的 Prompt (含 data_source_policy)
# 3. 运行验证
python main.py --show {new_prompt_id}
python main.py --keyword {trigger_word} --run
```

### 8.2 新增 DataPipe (需编写代码)

```bash
# 1. 在 src/data_engine/pipes/{vertical}/ 下新建或编辑管道文件
# 2. 实现 DataPipe 子类 (含 source_attribution)
# 3. 在 auto_register.py 中注册
# 4. 运行验证
python main.py --health
```

### 8.3 新增 Renderer (需编写代码)

```bash
# 1. 在 src/renderers/{vertical}/ 下新建渲染器
# 2. 继承 BaseRenderer,实现 render()
# 3. 在 renderers/__init__.py 的工厂中注册
# 4. 通过 Prompt YAML 的 report.template 引用
```

---

## 第九部分: 违规与处理

### 9.1 违规行为分级

| 级别 | 违规行为 | 处理方式 |
|------|---------|---------|
| **严重** | 使用中文网站作为数据来源 | 拒绝 Prompt 加载,标记为 invalid |
| **严重** | 输出语言配置为非 zh | 拒绝 Prompt 加载,标记为 invalid |
| **严重** | 在新 IDE/模型中未执行宪法确认 | 停止开发,要求重新加载宪法 |
| **严重** | 编造/捏造数据 (无来源的数值) | 拒绝发布报告,追溯 DataPipe 源码 |
| **严重** | 将 AI 推断呈现为确定事实 (冒充数据) | 拒绝发布,标注为"幻觉风险"需修正 |
| **一般** | DataPipe 未实现 source_attribution | 警告,允许加载但报告标注"来源未声明" |
| **一般** | 推断未标注置信度/逻辑依据 | 警告,不修正不得发布 |
| **一般** | 实测/估算/预测类型混淆 | 警告,标注后方可发布 |
| **一般** | 区间估算以精确数字呈现 (精度欺诈) | 警告,须标注"约"/"区间" |
| **一般** | 日本例外规则套用于非 JP 国家 | 拒绝该条例外,其余正常加载 |
| **轻微** | 注释/文档中包含非规范内容 | 警告,建议修正 |

### 9.2 自检脚本

每次提交前应运行:

```bash
# 1. 健康检查
python main.py --health

# 2. 数据来源合规验证 (应输出所有 Prompt 的合规状态)
python main.py --validate-sources

# 3. 基准测试 (确保所有 Prompt 可执行)
python main.py --benchmark
```

---

## 第十部分: 跨 IDE/跨模型操作指南

### 10.1 IDE 配置对照表

| IDE | 宪法加载方式 | 配置文件位置 |
|-----|------------|-------------|
| **CatPaw** | 仓库根目录放置 `.catpaw/rules/constitution.md` 软链 | `.catpaw/rules/` |
| **CodeBuddy** | 仓库根目录放置 `.codebuddy/rules/constitution.md` 软链 | `.codebuddy/rules/` |
| **Cursor** | `.cursor/rules/constitution.mdc` 配置 | `.cursor/rules/` |
| **通用方案** | 在 AI 首轮对话中发送宪法确认提示词 | 无需配置文件 |

### 10.2 宪法确认协议 (任何 IDE/模型通用)

```
【协议名称】: 宪法确认协议 (Constitution Acknowledgment Protocol)
【触发时机】: 
  - 首次在新 IDE 中打开项目
  - 切换 AI 模型后首次对话
  - 新建会话/对话轮次

【执行步骤】:
  1. 读取 docs/constitution/CONSTITUTION_MINI.md
  2. 确认以下 4 条最高原则:
     ✔ Prompt 为中心
     ✔ 英文权威数据源 (日本例外:日语采集+中文输出)
     ✔ 中文输出为首要
     ✔ 工具无关性
  3. 回复确认声明:
     "已确认 Insights 宪法框架,将在后续开发中严格遵守。"

【协议失败处理】:
  - 如果模型无法读取宪法文件 --> 手动粘贴宪法摘要
  - 如果模型拒绝确认 --> 切换回已确认的模型/会话
```

### 10.3 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 模型不认识项目约定 | 新会话/新模型未加载宪法 | 发送宪法确认提示词 |
| 代码生成使用了中文数据源 | 模型未遵守原则一 | 在提示词中显式声明"仅使用英文权威数据源" |
| 报告输出为英文 | 模型未遵守原则三 | 在提示词中显式声明"最终输出必须为中文" |
| IDE 私有格式污染 | 开发产物包含 IDE 锁定信息 | 检查并转换为标准格式(见 1.5.4) |
| 不同 IDE 生成的代码风格不同 | 模型默认风格差异 | 在宪法中明确代码规范(第六部分)覆盖默认风格 |

### 10.4 模型能力适配策略

| 模型特点 | 适配策略 |
|---------|---------|
| **长上下文模型** (如 HY) | 直接注入完整宪法到 System Prompt |
| **短上下文模型** | 注入压缩版 `CONSTITUTION_MINI.md`,完整文档按需读取 |
| **强指令遵循模型** | 在 System Prompt 中声明宪法为"不可违反" |
| **弱指令遵循模型** | 在每条开发指令前附加"宪法约束:仅英文数据源+中文输出" |

---

## 附录

### A. 常用英文权威数据来源清单

| 机构 | 域名 | 数据内容 |
|------|------|---------|
| World Bank | data.worldbank.org | 全球发展指标、GDP、人口 |
| IMF | data.imf.org | 财政、债务、汇率、WE |
| OECD | stats.oecd.org | 就业、教育、创新、贸易 |
| U.S. BLS | bls.gov | 美国就业、通胀、工资 |
| U.S. Fed | federalreserve.gov | 利率、货币供应、金融稳定 |
| ECB | ecb.europa.eu | 欧元区货币政策、金融稳定 |
| UN Data | data.un.org | 联合国各机构综合数据 |
| WTO | wto.org | 国际贸易统计 |

### B. 日本官方日语网站清单 (D 级来源,仅限日本主题)

| 机构 | 域名 | 数据内容 |
|------|------|---------|
| e-Gov Japan | e-gov.go.jp | 日本政府综合门户 |
| 厚生劳动省 | mhlw.go.jp | 劳动、工资、社保 |
| 経済産業省 | meti.go.jp | 产业政策、贸易 |
| 国土交通省 | mlit.go.jp | 基建、交通、物流 |
| 法務省入管局 | moj.go.jp/isa/ | 移民、签证、国籍 |
| 警察庁 | npa.go.jp | 交通安全、驾照 |
| 総務省統計局 | stat.go.jp | 日本统计年鉴 |

### C. Prompt YAML 模板

```yaml
id: {vertical}_{topic}
version: 1
enabled: true

data_source_policy:
  mode: english_authoritative_only
  allowed_sources:
    - 来源1
    - 来源2
  forbidden_sources:
    - 任何中文网站
    - 任何 UGC 平台
  output_language: zh

label:
  zh: "中文标题"
  en: "English Title"

triggers:
  - "关键词"

data_pipes:
  - pipe: pipe_name
    params:
      key: value

analysis_dimensions:
  - id: dim_id
    label_zh: "维度名"
    label_en: "Dimension Name"
    method: method_name
  required_data: [pipe_name]

report:
  template: template_name
  output_dir: reports/{vertical}

schedule:
  cadence: monthly
  time: "08:00"

quality:
  min_data_freshness_days: 30
  min_sources_per_section: 2
  anti_hallucination:
    mode: strict
    require_data_period: true
    require_unit: true
    distinguish_inference: true
    min_confidence_for_inference: medium
```

### D. AI 系统提示词模板 (压缩版宪法,可直接注入)

以下内容可直接复制到任何 AI IDE 的 System Prompt / 自定义指令中:

```markdown
## Insights 项目宪法框架 v1.4 - 不可违反

### 架构原则
- **Prompt 为中心**: 所有代码服务于 Prompt YAML 的定义、解析、执行
- 新增分析意图 = 新增 Prompt YAML,不修改核心引擎代码

### 数据源原则
- **仅英文权威**: World Bank / IMF / OECD / 各国政府英文门户 / 央行 / BLS / Fed / ECB
- **日本例外**: 日语官网可采集(信息更及时),但输出必须翻译为中文
- **严禁**: 任何中文网站(知乎/微博/百度等)、任何 UGC 平台
- **来源可点击**: 每条信息必须附带可点击官方 URL

### 反幻觉原则 (事实零虚构)
- 缺失数据绝不编造,用"—"代替
- 推断必须标注置信度 (high/medium/low) 和逻辑依据
- 每条数值必备三要素: 来源URL + 时间范围 + 单位
- 实测/估算/预测明确区分呈现
- 区间估算不得伪装成精确数字

### 输出原则
- **中文输出**: 所有报告/界面文本统一中文(公司名/专有名词除外)

### 工具无关性
- 所有产物使用标准格式 (YAML/Python/Markdown/HTML)
- 不依赖任何 IDE 或模型的私有格式
```

### E. pre-commit 钩子配置建议

```yaml
# .pre-commit-config.yaml (建议配置)
repos:
  - repo: local
    hooks:
      - id: constitution-check
        name: Constitution Compliance Check
        entry: python scripts/check_constitution.py
        language: system
        always_run: true
        pass_filenames: false
```

---

> **文档维护**: 本规范为项目开发的"宪法"文件,任何修改需经项目负责人审核。
> **持续改进**: 随着项目演进和规范执行情况,定期更新本文件。
> **v1.7 变更**: 新增原则六(反时间幻觉约束 — 日期感知报告生成全Prompt通用);第 5.6 节「反时间幻觉规范」详细规定适用范围、渲染器日期规范、分析方法签名规范、Prompt YAML 时间声明约束、时间幻觉检查清单及违规拦截机制;渲染器统一迁移至 analysis.context.format_date();宪法压缩版同步升级。
> **v1.6 变更**: 压缩版新增「反时间幻觉约束」原则(仅覆盖宏观 Prompt);宪法压缩版升级至 v1.6。
> **v1.5 变更**: 第 5.4 节新增「职业赛道路由命名规范」— 国家/地区使用小写英文前缀 (dubai/japan/germany 等),报告文件命名格式 `career_{country}_{profession}_{YYYYMMDD}.html`,模板占位符 `[[country]]`/`[[profession]]` 在 resolve 阶段自动填充。反幻觉章节重编号为 5.5。
> **v1.4 变更**: 新增原则五(反幻觉约束 — 事实零虚构);第 5.4 节(现 5.5)「反幻觉防控规范」详细规定三条铁律、元数据强制字段、渲染层防幻觉呈现规则、Prompt YAML 反幻觉配置、幻觉风险检查清单及自动化检测机制。  
> **v1.3 变更**: 原则一增强 — 新增来源可点击强制规范 (所有报告来源必须附带可点击 URL,引入 `src/renderers/source_links.py` 模块 + SOURCE_URL_MAP 映射表);第 5.3 节全面升级为「来源引用规范 (强制可点击)」;宪法压缩版同步更新。  
> **v1.2 变更**: 新增原则四(工具无关性)、第十部分(跨 IDE/跨模型操作指南)、附录 D (AI 系统提示词模板)、附录 E (pre-commit 钩子)。
