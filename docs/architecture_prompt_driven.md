# 关键词(提示词)驱动的行业深度分析系统 — 架构设计方案

> **核心理念**: 整个代码架构的最小设计单元不是"模块"或"函数",而是 **Prompt(提示词)**. 每一个 Prompt 代表一种分析意图,系统围绕 Prompt 的定义、解析、编排、执行与输出而构建.
>
> **设计原则**: 添加一个新的分析维度,只需要添加一个新的 Prompt 定义文件;无需修改核心引擎.

---

## 一、架构总体视图

```
�─────────────────────────────────────────────────────────────────────┐
│                        用户 / 调度器                                │
│    "迪拜AI网络安全"  "全球宏观经济" "日本高度人才" "中东房地产"     │
└────────────────�────────────────────────────────────────────────────┘
                 │ 关键词 / Prompt
                 ▼
┌─────────────────────────────────────────────────────────────────────�
│                    Prompt Registry(提示词注册表)                      │  ◄── 配置层
│    macro_global   tech_ai   realestate_dubai   visa_japan_hsp      │
│    ├─ definition      ├─ definition     ├─ definition   ├─ ...    │
│    ├─ data_pipes      ├─ data_pipes     ├─ data_pipes   ├─ ...    │
│    ├─ analysis_spec   ├─ analysis_spec  ├─ analysis_sp  ├─ ...    │
│    └─ report_schema   └─ report_schema  └─ report_sch   └─ ...    │
└────────────────┬────────────────────────────────────────────────────�
                 │ 解析后的执行计划(ExecutionPlan)
                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Prompt Runtime(提示词执行引擎)                    │  �── 引擎层
│                                                                     │
│  ┌───────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ DataPipe  │  │  Analyzer  │  │  Synthesizer│  │  Renderer  │  │
│  │ (数据管)  │  │  (分析器)  │  │  (综合器)  │  │  (渲染器)  │  │
│  └───────────�  └────────────┘  └────────────┘  └────────────┘  │
└────────────────┬────────────────────────────────────────────────────┘
                 │ 渲染后的报告
                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Report Store(报告仓库)                           │  ◄── 产物层
│    reports/tech/     reports/macro/     reports/career/            │
│    reports/realestate/    reports/studyabroad/                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 二、核心抽象: Prompt 作为一等公民

### 2.1 Prompt 的定义结构

每个提示词是一个 **声明式 YAML/JSON 配置**,它完整描述了一类分析任务的方方面面:

```yaml
# prompts/tech_ai_dubai.yaml
id: tech_ai_dubai
version: 1
label:
  zh: 迪拜AI与网络安全行业深度分析
  en: AI & Cybersecurity Industry in Dubai — Deep-dive

# 触发词:用户输入哪些关键词应激活此 Prompt
triggers:
  - "迪拜AI"
  - "迪拜网络安全"
  - "Dubai AI cybersecurity"
  - "UAE artificial intelligence"
  - "中东AI"        # 同义扩展

# 时间窗口
horizon:
  type: future_years
  value: 5

# 地域锚点
geo:
  region_zh: 迪拜
  region_en: Dubai
  country_code: AE
  peers:            # 对标区域(用于对比分析)
    - Singapore
    - Tel Aviv
    - Riyadh
    - London

# 数据来源合规策略 (强制字段)
data_source_policy:
  mode: english_authoritative_only
  allowed_sources:
    - World Bank
    - IMF
    - UAE Government Portals
    - Gartner
    - IDC
  forbidden_sources:
    - 任何中文 UGC 平台
  output_language: zh
  country_specific_exceptions:
    JP:
      enabled: true
      language: ja
      official_sources:
        - e-Gov Japan
        - 厚生劳动省
      note: 仅限数据采集，输出仍为中文

# 数据管道:此 Prompt 需要哪些数据
data_pipes:
  - pipe: gartner_mq          # Gartner 魔力象限(科技行业定位)
    params:
      sector: "AI Platforms"
      region: "MEA"
  - pipe: idc_spending        # IDC 支出预测(市场规模)
    params:
      category: "Cybersecurity"
      geography: "UAE"
  - pipe: dld_transactions    # 迪拜土地局地产数据(办公楼/园区需求)
    params:
      property_type: "Office"
  - pipe: sec_filings         # SEC 财报(巨头资本开支)
    params:
      tickers: [NVDA, MSFT, GOOGL, PANW, CRWD]
  - pipe: news_reuters        # Reuters 新闻(定性信号)
    params:
      keywords: ["AI", "cybersecurity", "UAE", "Dubai"]
  - pipe: linkedin_jobs       # LinkedIn 职位发布(人才供需)
    params:
      skills: ["AI Security", "ML Ops", "Threat Intel"]
      location: "Dubai"

# 分析维度:什么角度切入(对应报告章节)
analysis_dimensions:
  - id: market_sizing
    label_zh: 市场规模与增长
    label_en: Market Sizing & Growth
    method: quantitative_forecast
    required_data: [idc_spending, gartner_mq]
  - id: competitive_landscape
    label_zh: 竞争格局
    label_en: Competitive Landscape
    method: positioning_map
    required_data: [gartner_mq, sec_filings]
  - id: talent_dynamics
    label_zh: 人才供需
    label_en: Talent Supply/Demand
    method: gap_analysis
    required_data: [linkedin_jobs]
  - id: regulatory_risk
    label_zh: 监管与合规风险
    label_en: Regulatory & Compliance Risk
    method: policy_scan
    required_data: [news_reuters]
  - id: investment_thesis
    label_zh: 投资框架与情景推演
    label_en: Investment Thesis & Scenarios
    method: three_scenario_model
    required_data: [idc_spending, sec_filings]

# 报告模板:使用哪个 Renderer
report:
  template: mckinsey_tech
  output_dir: reports/tech
  format:
    type: html
    sections:
      - executive_summary
      - market_sizing
      - competitive_landscape
      - talent_dynamics
      - regulatory_risk
      - investment_thesis
      - strategic_recommendations

# 调度
schedule:
  cadence: weekly
  day_of_week: monday
  time: "08:00"
  timezone: "UTC"

# 质量护栏
quality:
  min_data_freshness_days: 7      # 数据不得老化超过7天
  min_sources_per_section: 2      # 每章至少引用2个来源
  required_disclaimers:
    - "market_forecast"
    - "not_investment_advice"
```

### 2.2 五大主题域的 Prompt 清单

```yaml
# prompts/ 目录结构 (与 src/pipes/ 和 src/renderers/ 子目录对齐)
prompts/
├── macro/                              # 宏观经济系列
│   └── macro_global.yaml               # 全球经济宏观总览
├── tech/                               # 科技行业系列
│   ├── tech_ai.yaml                    # 全球AI行业
│   ├── tech_ai_cybersecurity.yaml      # AI+网络安全交叉
│   ├── tech_cybersecurity.yaml         # 网络安全
│   ├── tech_dubai_ai_cybersecurity.yaml# 迪拜/中东AI网络安全
│   └── tech_semiconductor.yaml         # 全球半导体
├── realestate/                         # 房地产系列
│   └── re_dubai.yaml                   # 迪拜地产
├── studyabroad/                        # 留学系列
│   ├── study_abroad_au.yaml            # 澳洲留学
│   ├── study_abroad_ca.yaml            # 加拿大留学
│   ├── study_abroad_de.yaml            # 德国留学
│   ├── study_abroad_fr_engineering.yaml# 法国工程
│   ├── study_abroad_gb_master.yaml     # 英国硕士
│   ├── study_abroad_hk.yaml            # 香港留学
│   ├── study_abroad_jp.yaml            # 日本留学
│   ├── study_abroad_nz.yaml            # 新西兰留学
│   ├── study_abroad_sg.yaml            # 新加坡留学
│   ├── study_abroad_uk.yaml            # 英国留学
│   ├── study_abroad_us.yaml            # 美国留学
│   └── template_generic.yaml           # 通用留学模板
└── career/                             # 海外就业与职业移民系列
    ├── visa_japan_driver.yaml          # 日本驾驶签证
    ├── visa_japan_hsp.yaml             # 日本高度人才
    ├── visa_nz_driver.yaml             # 新西兰驾驶签证
    ├── profession_country.yaml         # 职业清单国家对比
    ├── visa_profession_matrix.yaml     # 签证-职业矩阵
    └── _template_lifecycle.yaml        # 移民生命周期模板
```

---

## 三、分层架构设计

### 3.1 配置层: Prompt Registry

**职责**: 加载、索引、匹配、管理所有 Prompt 定义.

**实际位置**: `src/prompt_registry/__init__.py`

```python
class PromptRegistry:
    """提示词注册表:所有提示词的发现、注册、匹配与生命周期管理."""

    def __init__(self, prompts_dir: Path):
        self.prompts_dir = prompts_dir
        self._registry: Dict[str, PromptDefinition] = {}
        self._trigger_index: Dict[str, List[str]] = {}  # 关键词 → [prompt_id, ...]
        self._load_all()

    # ── 核心接口 ──
    def resolve(self, keyword: str, vertical: str = None) -> Optional[PromptDefinition]:
        """根据用户输入的关键词,解析并返回最佳匹配的 prompt."""
        ...
    def resolve_multi(self, keywords: List[str], vertical: str = None) -> List[PromptDefinition]:
        """支持多关键词组合,返回多个 Prompt."""
        ...
    def list_by_vertical(self, vertical: str) -> List[PromptDefinition]: ...
    def list_enabled(self) -> List[PromptDefinition]: ...
    def get(self, prompt_id: str) -> PromptDefinition: ...
    def summary(self) -> Dict: ...

    # ── 内部实现 ──
    def _load_all(self): ...          # 自动发现 prompts/ 下所有 YAML
    def _build_trigger_index(self): ... # 构建关键词倒排索引
    def _parse_prompt(self, raw: Dict, path: Path) -> Optional[PromptDefinition]: ...
```

**Vertical 自动推断逻辑**:

Prompt 的 `vertical` 属性由其 ID 前缀自动推断:

| ID 前缀 | 推断的 Vertical | 目录 |
|---------|----------------|------|
| `tech_` | `tech` | `prompts/tech/` |
| `realestate_` / `re_` | `realestate` | `prompts/realestate/` |
| `macro_` | `macro` | `prompts/macro/` |
| `visa_` / `profession_` | `career` | `prompts/career/` |
| `studyabroad_` | `studyabroad` | `prompts/studyabroad/` |
| `industry_` | `industry` | (兼容) |

### 3.2 引擎层: Prompt Runtime

**职责**: 接收一个已解析的 Prompt,执行其数据管道 → 分析 → 综合 → 渲染的全流程.

**实际位置**: `src/prompt_runtime/__init__.py`

```python
class PromptRuntime:
    """提示词执行引擎:一个 Prompt 配置 → 一份完整的深度分析报告."""

    def __init__(self, cache_enabled: bool = True, max_workers: int = 4):
        self._runner = get_runner()  # PipeRunner
        ...

    def execute(self, prompt: PromptDefinition) -> Optional[str]:
        """
        完整执行一个 Prompt,渲染并存储报告.

        Returns:
            报告文件路径(str),或失败时返回 None.
        """
        # Step 1: 数据采集 (并行执行所有声明的 DataPipe)
        bundle = self._collect_data(prompt)

        # Step 2: 分析计算 (遍历 analysis_dimensions)
        analysis = self._analyze(prompt, bundle)

        # Step 3: 渲染报告 (根据 vertical/template 选择 Renderer)
        output_path = self._render(prompt, analysis)

        return output_path
```

**PromptRuntime 还内置了**:
- `_collect_data(prompt)`: 调用 PipeRunner 并行采集,返回 `DataBundle`
- `_analyze(prompt, bundle)`: 根据 `analysis_dimensions` 声明的 method 执行分析
- `_render(prompt, analysis)`: 通过 RendererFactory 选择 Renderer 并渲染 HTML
- `_generate_report(prompt, analysis)`: 生成报告并写入 `output_dir`
- `_write_html(...)`: 实际文件写入逻辑

### 3.3 数据层: Data Engine + Pipe Runner

**职责**: 提供统一的数据访问接口; Pipe Runner 根据 Prompt 中的 `data_pipes` 声明,按需执行对应的数据采集管道.

**实际位置**: `src/data_engine/__init__.py` 与各主题域管道目录

```python
# src/data_engine/__init__.py
class DataBundle:
    """数据采集结果容器 — 承载所有管道采集到的数据."""
    data: Dict[str, pd.DataFrame]
    metadata: Dict[str, Dict[str, Any]]
    errors: Dict[str, str]

class DataPipe(ABC):
    """单个数据管道的抽象基类."""
    pipe_id: str = ""

    @abstractmethod
    def collect(self, params: Dict) -> pd.DataFrame: ...
    def validate(self, data: pd.DataFrame) -> bool: ...
    def source_attribution(self) -> List[str]: ...
    def cache_key(self, params: Dict) -> str: ...

class PipeRunner:
    """管道执行器:将 Prompt 中的 data_pipes 声明转化为实际数据."""

    def register(self, pipe_id: str, factory: Callable[..., DataPipe]): ...
    def register_pipe(self, pipe_cls: type): ...  # 装饰器注册
    def run_single(self, pipe_id: str, params: Dict = None) -> pd.DataFrame: ...
    def run(self, pipe_declarations: List[Any], parallel: bool = True) -> DataBundle: ...
```

**主题域管道目录结构 (src/data_engine/pipes/)**:

```
pipes/
├── auto_register.py     # 自动注册所有管道 (ensure_all_pipes_registered)
├── career/              # 海外就业·签证移民管道
│   ├── __init__.py      # 导出所有 career 管道类
│   ├── extra_pipes.py   # 扩展管道
│   ├── japan_visa_pipes.py
│   ├── migration_pipes.py
│   ├── nz_visa_pipes.py
│   └── profession_pipes.py
├── macro/               # 宏观经济管道
│   ├── __init__.py
│   └── macro_pipes.py
├── realestate/          # 海外房地产管道
│   ├── __init__.py
│   └── realestate_pipes.py
├── studyabroad/         # 留学分析管道
│   ├── __init__.py
│   └── study_abroad_pipes.py
└── tech/                # 科技(AI/网络安全/半导体)管道
    ├── __init__.py
    ├── cyber_pipes.py
    └── tech_pipes.py
```

**管道自动注册机制 (`auto_register.py`)**:

```python
def ensure_all_pipes_registered():
    """确保所有内置数据管道已注册到全局 PipeRunner."""
    from src.data_engine.pipes import career as _career    # noqa: F401
    from src.data_engine.pipes import macro as _macro      # noqa: F401
    from src.data_engine.pipes import realestate as _realestate  # noqa: F401
    from src.data_engine.pipes import studyabroad as _studyabroad # noqa: F401
    from src.data_engine.pipes import tech as _tech        # noqa: F401
```

每个主题域子目录的 `__init__.py` 通过导入模块触发各管道的装饰器注册,实现"零配置"自动发现.

### 3.4 渲染层: Renderer + Renderer Factory

**职责**: 将综合后的分析结果渲染为最终报告(HTML).

**实际位置**: `src/renderers/__init__.py` 与各主题域渲染器目录

```python
# src/renderers/__init__.py
class RendererFactory:
    """渲染器工厂."""

    @staticmethod
    def get_renderer(prompt: PromptDefinition) -> Renderer:
        """根据 Prompt 选择渲染器实例."""
        # 1. 优先匹配 report_template
        # 2. 回退: 基于 vertical 猜测
        ...

    @staticmethod
    def register(template_name: str, cls: type): ...
```

**渲染器注册表 (模板名 → 渲染器类)**:

| 模板名 | 渲染器类 | 垂直域 | 说明 |
|--------|---------|--------|------|
| `visa_tracker` | `VisaTrackerRenderer` | career | 签证政策追踪 |
| `japan_driver` | `JapanDriverRenderer` | career | 日本驾驶签证 |
| `migration_lifecycle` | `MigrationLifecycleRenderer` | career | 移民生命周期 |
| `profession_analyzer` | `ProfessionAnalyzerRenderer` | career | 职业清单分析 |
| `macro_dashboard` | `MacroDashboardRenderer` | macro | 宏观经济仪表盘 |
| `real_estate_dashboard` | `RealEstateDashboardRenderer` | realestate | 房地产深度分析 |
| `mckinsey_tech` | `McKinseyTechRenderer` | tech/studyabroad | 麦肯锡风格科技报告 |

**渲染器目录结构 (src/renderers/)**:

```
renderers/
├── __init__.py          # RendererFactory, 导出各渲染器类
├── career/              # 签证/职业/移民生命周期渲染器
│   ├── __init__.py
│   ├── japan_driver.py
│   ├── migration_lifecycle.py
│   ├── profession_analyzer.py
│   └── visa_tracker.py
├── macro/               # 宏观经济仪表盘
│   ├── __init__.py
│   └── dashboard.py
├── realestate/          # 房地产深度分析
│   ├── __init__.py
│   └── dashboard.py
├── studyabroad/         # 留学申请分析
│   └── __init__.py      # alias McKinseyTechRenderer
└── tech/                # AI/网络安全/半导体
    ├── __init__.py
    └── mckinsey_style.py
```

---

## 四、完整执行流程: 从一个关键词到一份报告

```
用户输入: "生成迪拜AI网络安全行业5年深度分析"
      │
      ▼
[1] PromptRegistry.resolve("迪拜AI网络安全")
      │ 模糊匹配 → tech_ai_dubai → PromptDefinition
      ▼
[2] PromptRuntime.execute(prompt_def)
      │
      ├── [2.1] PipeRunner.run(prompt_def.data_pipes)
      │         ├─ gartner_mq("AI Platforms", "MEA")
      │         ├─ idc_spending("Cybersecurity", "UAE")
      │         ├─ dld_transactions("Office", "Dubai")
      │         ├─ sec_filings([NVDA, MSFT, GOOGL, ...])
      │         ├─ news_reuters(["AI","cybersecurity","UAE"])
      │         └─ linkedin_jobs(["AI Security","ML Ops"], "Dubai")
      │         → DataBundle(6个DataFrame + 元数据)
      │
      ├── [2.2] Analyzer.analyze_each(prompt_def.analysis_dimensions, bundle)
      │         → {market_sizing: AnalysisResult,
      │            competitive_landscape: AnalysisResult, ...}
      │
      └── [2.3] RendererFactory.get_renderer(prompt_def)
                → McKinseyTechRenderer.render(analysis, prompt_def)
                → HTML 报告文件
      │
      ▼
[3] 输出: reports/tech/20261011_tech_ai_dubai.html
```

---

## 五、CLI 入口

**实际位置**: `main.py`

```bash
# ── 即时分析(关键词驱动) ──
python main.py --keyword 半导体 --run                    # 模糊匹配+执行
python main.py --prompt tech_ai --run                    # 直接指定 ID
python main.py --vertical tech --run                     # 执行某赛道全部
python main.py --vertical studyabroad --run              # 执行留学赛道

# ── Promppt 管理 ──
python main.py --list                                    # 列出所有 Prompt
python main.py --vertical tech --list                    # 列出某赛道
python main.py --show tech_ai                            # 查看 Prompt 详情

# ── 系统运维 ──
python main.py --health                                  # 健康检查
python main.py --benchmark                               # 基准测试: 跑一遍所有
```

---

## 六、扩展示例: 新增一个行业赛道

假设需要新增"区域经济"(宏观经济的子维度):

### 步骤 1: 新增 Prompt 定义文件

新建 `prompts/macro/macro_regional_asia.yaml`:

```yaml
id: macro_regional_asia
version: 1
label:
  zh: 亚洲区域经济与贸易深度分析
  en: Asia Regional Economic & Trade Deep-dive
triggers: [亚洲经济, 亚太经济, 东盟, Asia economy, ASEAN]
horizon:
  type: future_years
  value: 5
geo:
  region_zh: 亚洲
  region_en: Asia
  country_code: ""
  peers:
    - China
    - Japan
    - South Korea
    - India
    - ASEAN

data_source_policy:
  mode: english_authoritative_only
  allowed_sources:
    - World Bank
    - IMF
    - ADB
    - ASEAN Secretariat
  forbidden_sources: []
  output_language: zh

data_pipes:
  - pipe: worldbank_indicator
    params: { indicator: "NY.GDP.MKTP.CD" }
  - pipe: imf_weo
    params: { region: "Asia" }

analysis_dimensions:
  - id: trade_flows
    label_zh: 区域贸易流向
    method: network_analysis
    required_data: [worldbank_indicator]

report:
  template: macro_dashboard
  output_dir: reports/macro

schedule:
  cadence: quarterly
  time: "08:00"

quality:
  min_data_freshness_days: 90
  min_sources_per_section: 2
```

### 步骤 2: 实现对应的数据管道 (如需要)

新建 `src/data_engine/pipes/macro/regional_pipes.py`:

```python
from src.data_engine import register_pipe, DataPipe

@register_pipe
class WorldBankIndicatorPipe(DataPipe):
    pipe_id = "worldbank_indicator"

    def collect(self, params: Dict) -> pd.DataFrame:
        # 实现 World Bank API 数据采集
        ...

@register_pipe
class IMFWEO pip e(DataPipe):
    pipe_id = "imf_weo"

    def collect(self, params: Dict) -> pd.DataFrame:
        # 实现 IMF World Economic Outlook 数据采集
        ...
```

并在 `src/data_engine/pipes/macro/__init__.py` 中导入:

```python
from src.data_engine.pipes.macro.regional_pipes import (
    WorldBankIndicatorPipe,
    IMFWEOPipe,
)
```

### 步骤 3: 无需修改核心代码

PromptRegistry 在启动时自动发现新 YAML, PipeRunner 自动注册新管道(通过 auto_register).

---

## 七、各主题域的 Renderer 设计

### 7.1 McKinseyTechRenderer (科技行业 + 留学)
```
封面 → 执行摘要(5 bullet核心结论)
  ├─ 1. 市场规模与增长 ← IDC 数据 + 3情景CAGR
  ├─ 2. 竞争格局 ← Gartner MQ + 份额时序
  ├─ 3. AI/技术影响 ← 技术成熟度曲线
  ├─ 4. 人才供需 ← LinkedIn 数据 + 薪酬分位
  ├─ 5. 区域对标 ← vs 新加坡/以色列/伦敦
  ├─ 6. 监管风险 ← 政策扫描矩阵
  ├─ 7. 投资框架 ← 三情景推演
  └─ 8. 战略建议 ← 政府/企业/投资者三视角
```

### 7.2 MacroDashboardRenderer (宏观经济)
```
封面 → 全球宏观一页纸(核心指标快照)
  ├─ 1. 超级经济体比较 ← 美/欧/中/日/英 GDP-CPI-利率-失业率
  ├─ 2. 央行政策日历 ← 下次决议日期 + 市场定价
  ├─ 3. 增长引擎分解 ← 消费/投资/净出口贡献
  ├─ 4. 通胀动力 ← 核心/非核心, 服务/商品
  ├─ 5. 财政空间 ← 债务/GDP, 财政赤字, 融资成本
  ├─ 6. 风险矩阵 ← 地缘/金融/气候/科技
  └─ 7. 配置建议 ← 6个月战术资产轮动
```

### 7.3 RealEstateDashboardRenderer (房地产)
```
封面 → 城市地产速览(Dashboard)
  ├─ 1. 价格指数时序(可自行上传/12月/5年)
  ├─ 2. 租金收益率(各商圈分层)
  ├─ 3. 供需平衡表(新增供应 vs 吸纳量)
  ├─ 4. 投资交易追踪(大宗交易/外资动向)
  ├─ 5. 按揭成本与可负担性
  ├─ 6. 政策时间线(限购/税收/土地)
  ├─ 7. 重点商圈画像(Downtown, DIFC...)
  └─ 8. 12个月展望与配置权重
```

### 7.4 VisaTrackerRenderer / JapanDriverRenderer / MigrationLifecycleRenderer (移民签证)
```
封面 → 签证路径决策树
  ├─ 1. 当前政策快照(评分表/打分解释)
  ├─ 2. 一年政策变更时间线
  ├─ 3. 各路径对比(时间/成本/成功率/风险)
  ├─ 4. 资格自测(结构化问答)
  ├─ 5. 加分明细核对表(大学/工作经验/年收入)
  ├─ 6. 常见陷阱与拒签原因
  ├─ 7. 材料清单与时间规划
  └─ 8. 下次的政策窗口预测
```

---

## 八、数据源策略

### 8.1 数据来源分级

| 级别 | 来源类型 | 示例 | 处理方式 |
|------|---------|------|---------|
| **A 级** | 英文权威机构 | World Bank, IMF, 各国政府英文门户、央行 | 直接写入 Pipe |
| **B 级** | 英文专业机构 | Gartner, IDC, McKinsey, BCG | 预留 Hook,支持 CSV 快照导入 |
| **C 级** | 付费/可选 API | LinkedIn API, NewsAPI | 封装为可选 Pipe,缺失时降级 |
| **D 级** | 国家特定语言 | 日本日语官网 | 仅限数据采集,输出必须为中文 |

### 8.2 降级策略

任意 Pipe 失败不影响报告生成: 对应章节显示"数据暂缺",其他章节正常渲染. 这确保了系统的鲁棒性.

### 8.3 缓存策略

- PipeRunner 支持 Parquet 缓存 (`data/store/`)
- 默认缓存有效期: 24 小时 (可配置)
- 缓存键由 `pipe_id + md5(params)` 构成
- 同时支持降级: 网络失败时尝试使用过期缓存

---

## 九、配置管理

### 9.1 全局配置 (config/settings.py)

```python
# 极简目录配置,不含业务逻辑
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
PIPE_STORE_DIR = DATA_DIR / "store"
```

报告输出目录完全由 Prompt YAML 的 `report.output_dir` 字段驱动, Renderer 按需 `mkdir`.

### 9.2 Prompt YAML 配置项速查

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识符 (小写字母+下划线) |
| `version` | integer | 定义版本 |
| `label.zh/en` | string | 显示名称 |
| `triggers` | list[string] | 触发关键词 |
| `horizon.type/value/unit` | object | 时间窗口 |
| `geo.region_zh/en` | string | 地域名称 |
| `geo.country_code` | string | 国家代码 |
| `geo.peers` | list[string] | 对标区域 |
| `data_pipes[].pipe` | string | 管道 ID (必须) |
| `data_pipes[].params` | object | 管道参数 |
| `analysis_dimensions[].id` | string | 维度 ID |
| `analysis_dimensions[].method` | string | 分析方法 |
| `analysis_dimensions[].required_data` | list | 所需管道 |
| `report.template` | string | 渲染模板名 |
| `report.output_dir` | string | 输出目录 |
| `report.format.type` | enum | `html`/`markdown`/`pdf` |
| `schedule.cadence` | enum | `daily`/`weekly`/`monthly`/`quarterly` |
| `quality.min_data_freshness_days` | integer | 数据最大老化天数 |

---

## 十、关键设计决策记录

### 决策 1: 为什么 Prompt 定义为 YAML 配置而非代码?
**答案**: 让分析师/业务人员可以独立维护 Prompt 的定义、数据管道、报告结构,无需程序员介入. 代码只负责执行引擎. 这解决了"业务逻辑频繁变更"与"代码发布流程沉重"的矛盾.

### 决策 2: 为什么 src/ 子目录与 prompts/ 主题域对齐?
**答案**: 1) 同一主题域的管道和渲染器放在一起,便于查找; 2) 新增主题域只需在 prompts/ 和 src/pipes/、src/renderers/ 下添加同名子目录; 3) 避免"一个管道文件跨越多个目录"的混乱.

### 决策 3: 五个主题域为什么用不同 Renderer 而非统一模板?
**答案**: 每个主题域的"分析范式"本质不同. 科技行业是"趋势×竞争×技术",宏观经济是"指标×跨国×政策",房地产是"价格×供需×项目",移民签证是"路径×政策×案例",留学是"申请×院校×专业×就业". 用统一模板会强行扭曲某一类信息.

### 决策 4: 是否使用 LLM 端到端?
**答案**: 行业报告的可信度依赖可验证的数据来源与可复现的分析框架. 采用"结构化数据管道 + 规则分析"路径,确保数据与分析的确定性.

### 决策 5: 如何处理 Vertical 自动推断?
**答案**: 通过 ID 前缀映射实现零配置分类. 设计师只需遵循命名约定 (`tech_`, `macro_`, `career_`, `studyabroad_`, `realestate_`), 无需额外维护分类字段.

---

## 十一、总结: 当前代码组织

```text
insights/
├── prompts/                         # ◄── 提示词定义库(一等公民)
│   ├── macro/                       # 宏观经济
│   ├── tech/                        # 科技(AI/网络安全/半导体)
│   ├── realestate/                  # 房地产
│   ├── studyabroad/                 # 留学
│   └── career/                      # 就业与职业移民
│
├── src/
│   ├── prompt_registry/             # 提示词注册与匹配
│   │   └── __init__.py
│   │
│   ├── prompt_runtime/              # 提示词执行引擎
│   │   └── __init__.py
│   │
│   ├── data_engine/                 # 数据引擎 + 管道
│   │   ├── __init__.py              # DataPipe, PipeRunner, DataBundle
│   │   └── pipes/                   # 具体管道实现 (按主题域分组)
│   │       ├── auto_register.py     # 自动注册器
│   │       ├── career/              # 签证/职业管道
│   │       ├── macro/               # 宏观管道
│   │       ├── realestate/          # 地产管道
│   │       ├── studyabroad/         # 留学管道
│   │       └── tech/                # 科技管道
│   │
│   └── renderers/                   # 报告渲染器族 (按主题域分组)
│       ├── __init__.py              # RendererFactory
│       ├── career/                  # 移民/职业渲染器
│       ├── macro/                   # 宏观仪表盘
│       ├── realestate/              # 地产分析
│       ├── studyabroad/             # 留学分析
│       └── tech/                    # 麦肯锡风格科技
│
├── main.py                          # CLI 入口
├── config/settings.py               # 目录配置
└── reports/                         # 报告输出
    ├── career/
    ├── macro/
    ├── realestate/
    ├── studyabroad/
    └── tech/
```

> **架构演进**: 从"流程驱动"到"提示词驱动",本质上是将系统的"变化点"从代码(compiled artifact)转移到了配置(Human-readable YAML). 每次业务扩展 = 添加/修改一个 Prompt 定义,不经代码发布. 这就是 Prompt-Driven Architecture 的工程价值.
>
> **主题域对齐**: 新增主题域只需在 `prompts/`、`src/data_engine/pipes/`、`src/renderers/` 下添加同名子目录,实现"配置-管道-渲染"三位一体的清晰组织.
