# 关键词(提示词)驱动的行业深度分析系统 — 架构设计方案

> **核心理念**: 整个代码架构的最小设计单元不是"模块"或"函数",而是 **Prompt(提示词)**. 每一个 Prompt 代表一种分析意图,系统围绕 Prompt 的定义、解析、编排、执行与输出而构建.
>
> **设计原则**: 添加一个新的分析维度,只需要添加一个新的 Prompt 定义文件;无需修改核心引擎.

---

## 一、架构总体视图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        用户 / 调度器                                │
│    "迪拜AI网络安全"  "全球宏观经济" "日本高度人才" "中东房地产"     │
└────────────────┬────────────────────────────────────────────────────┘
                 │ 关键词 / Prompt
                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Prompt Registry(提示词注册表)                      │  ◄── 配置层
│    macro_global   tech_ai   realestate_dubai   visa_japan_hsp      │
│    ├─ definition      ├─ definition     ├─ definition   ├─ ...    │
│    ├─ data_pipes      ├─ data_pipes     ├─ data_pipes   ├─ ...    │
│    ├─ analysis_spec   ├─ analysis_spec  ├─ analysis_sp  ├─ ...    │
│    └─ report_schema   └─ report_schema  └─ report_sch   └─ ...    │
└────────────────┬────────────────────────────────────────────────────┘
                 │ 解析后的执行计划(ExecutionPlan)
                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Prompt Runtime(提示词执行引擎)                    │  ◄── 引擎层
│                                                                     │
│  ┌───────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ DataPipe  │  │  Analyzer  │  │  Synthesizer│  │  Renderer  │  │
│  │ (数据管)  │  │  (分析器)  │  │  (综合器)  │  │  (渲染器)  │  │
│  └───────────┘  └────────────┘  └────────────┘  └────────────┘  │
└────────────────┬────────────────────────────────────────────────────┘
                 │ 渲染后的报告
                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Report Store(报告仓库)                           │  ◄── 产物层
│    reports/industry/{YYYY-MM}/{prompt_id}/{date}_{prompt_id}.html  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 二、核心抽象:Prompt 作为一等公民

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
  template: mckinsey_vertical     # 麦肯锡垂直行业8章节
  output_dir: reports/industry/tech
  style:
    primary_color: "#0b2545"
    accent_color: "#c8a24b"

# 调度
schedule:
  cadence: weekly                 # weekly / monthly / quarterly / event-driven
  day: monday
  time: "08:00"
  enabled: true

# 质量护栏
quality:
  min_data_freshness_days: 7      # 数据不得老化超过7天
  min_sources_per_section: 2      # 每章至少引用2个来源
  required_disclaimers:
    - "market_forecast"
    - "not_investment_advice"
```

### 2.2 四大行业赛道的 Prompt 清单

```yaml
# prompts/ 目录结构
prompts/
├── macro/                              # 宏观经济系列
│   ├── macro_global.yaml               # 全球经济宏观总览
│   ├── macro_us.yaml                   # 美国经济深度
│   ├── macro_cn.yaml                   # 中国经济深度
│   ├── macro_eu.yaml                   # 欧洲/欧盟经济深度
│   └── macro_jp.yaml                   # 日本经济深度
├── tech/                               # 科技行业系列
│   ├── tech_ai_global.yaml             # 全球AI行业
│   ├── tech_ai_dubai.yaml              # 迪拜/中东AI行业
│   ├── tech_semiconductor.yaml         # 全球半导体
│   ├── tech_cybersecurity.yaml         # 网络安全
│   ├── tech_cloud.yaml                 # 云计算
│   └── tech_fintech.yaml               # 金融科技
├── realestate/                         # 房地产系列
│   ├── re_dubai.yaml                   # 迪拜地产
│   ├── re_abudhabi.yaml                # 阿布扎比地产
│   ├── re_saudi.yaml                   # 沙特地产
│   ├── re_tokyo.yaml                   # 东京地产
│   └── re_singapore.yaml               # 新加坡地产
└── migration/                          # 海外移民系列
    ├── visa_japan_hsp.yaml             # 日本高度人才
    ├── visa_japan_bm.yaml              # 日本经营管理
    ├── visa_canada_exprss.yaml         # 加拿大EE
    ├── visa_australia_gsm.yaml         # 澳洲技术移民
    ├── visa_uk_skilled.yaml            # 英国技术工签
    └── visa_sg_ep.yaml                 # 新加坡EP
```

---

## 三、分层架构设计

### 3.1 配置层:Prompt Registry

**职责**:加载、索引、匹配、管理所有 Prompt 定义.

```python
# src/prompt_registry/__init__.py
class PromptRegistry:
    """提示词注册表:所有提示词的发现、注册、匹配与生命周期管理."""

    def __init__(self, prompts_dir: Path):
        self.prompts_dir = prompts_dir
        self._registry: Dict[str, PromptDefinition] = {}
        self._trigger_index: Dict[str, List[str]] = {}  # 关键词 → [prompt_id, ...]
        self._load_all()

    # ── 核心接口 ──
    def register(self, definition: PromptDefinition) -> None: ...
    def resolve(self, keyword: str) -> PromptDefinition:
        """根据用户输入的关键词,解析并返回最佳匹配的 Prompt."""
        ...
    def resolve_multi(self, keywords: List[str]) -> List[PromptDefinition]:
        """支持多关键词组合,返回多个 Prompt 的合并执行计划."""
        ...
    def list_by_vertical(self, vertical: str) -> List[PromptDefinition]: ...
    def list_enabled(self) -> List[PromptDefinition]: ...
    def get(self, prompt_id: str) -> PromptDefinition: ...

    # ── 内部实现 ──
    def _load_all(self): ...
    def _build_trigger_index(self): ...
    def _fuzzy_match(self, keyword: str) -> List[Tuple[str, float]]: ...
```

### 3.2 引擎层:Prompt Runtime

**职责**:接收一个已解析的 Prompt,执行其数据管道 → 分析 → 综合 → 渲染的全流程.

```python
# src/prompt_runtime/__init__.py
class PromptRuntime:
    """提示词执行引擎:一个 Prompt 配置 → 一份完整的深度分析报告."""

    def __init__(self, registry: PromptRegistry, data_engine: DataEngine):
        self.registry = registry
        self.data_engine = data_engine
        self.pipe_runner = PipeRunner(data_engine)
        self.analyzer = Analyzer()
        self.synthesizer = Synthesizer()
        self.renderer_factory = RendererFactory()

    # ── 主入口 ──
    def execute(self, prompt_id: str | PromptDefinition, context: dict = None) -> ReportArtifact:
        """主执行方法:一个 Prompt → 一份报告."""
        prompt = self._resolve_prompt(prompt_id, context)

        # Phase 1: 数据采集(并行)
        bundle = self.pipe_runner.run(prompt.data_pipes)

        # Phase 2: 多维分析
        analyses = {}
        for dim in prompt.analysis_dimensions:
            analyses[dim.id] = self.analyzer.analyze(dim, bundle)

        # Phase 3: 综合合成
        synthesis = self.synthesizer.synthesize(
            analyses, prompt.analysis_dimensions, bundle
        )

        # Phase 4: 报告渲染
        renderer = self.renderer_factory.get(prompt.report.template)
        report = renderer.render(synthesis, prompt)

        return report

    def execute_pipeline(self, prompt_ids: List[str]) -> List[ReportArtifact]:
        """批量执行多个 Prompt(并行或串行,按需指定)."""
        ...
```

### 3.3 数据层:Data Engine + Pipe Runner

**职责**:提供统一的数据访问接口;Pipe Runner 根据 Prompt 中的 `data_pipes` 声明,按需执行对应的数据采集管道.

```python
# src/data_engine/__init__.py
class DataEngine:
    """统一数据引擎:为上层提供跨数据源的访问抽象."""

    def __init__(self):
        self.sources: Dict[str, DataSource] = {}
        self.cache = DataCache()

    def register_source(self, name: str, source: DataSource): ...
    def fetch(self, pipe_id: str, params: dict, use_cache=True) -> DataBundle: ...
    def health_check(self, pipe_id: str) -> SourceHealth: ...

# src/data_engine/pipe.py
class PipeRunner:
    """管道执行器:将 Prompt 中的 data_pipes 声明转化为实际数据."""

    def __init__(self, engine: DataEngine):
        self.engine = engine
        self._pipe_registry: Dict[str, DataPipe] = {}

    def register_pipe(self, pipe_id: str, pipe_factory: Callable): ...
    def run(self, pipe_declarations: List[dict]) -> DataBundle:
        """并行执行所有声明的数据管道,组装为 DataBundle."""
        ...

# 数据管道的具体实现 —— 每种数据源一个 Pipe 类
class DataPipe(ABC):
    """单个数据管道的抽象基类."""
    @abstractmethod
    def collect(self, params: dict) -> pd.DataFrame: ...
    @abstractmethod
    def validate(self, data: pd.DataFrame) -> ValidationResult: ...
    @abstractmethod
    def source_attribution(self) -> List[str]: ...

# ── 具体管道实现 ──
class GatnerMagicQuadrantPipe(DataPipe): ...      # Gartner MQ
class IDCSpendingPipe(DataPipe): ...              # IDC 支出指南
class DLDTransactionsPipe(DataPipe): ...           # 迪拜土地局
class SECFilingPipe(DataPipe): ...                # SEC EDGAR
class NewsAPIPipe(DataPipe): ...                  # 新闻API(Reuters/Bloomberg)
class LinkedInJobsPipe(DataPipe): ...              # LinkedIn 职位
class IMFIndicatorPipe(DataPipe): ...             # IMF 宏观指标
class JapanImmigrationPipe(DataPipe): ...          # 日本入管局政策
class WorldBankPipe(DataPipe): ...                # 世界银行
```

### 3.4 渲染层:Renderer + Template Registry

**职责**:将综合后的分析结果渲染为最终报告(HTML/Markdown/PDF).

```python
# src/renderers/__init__.py
class Renderer(ABC):
    @abstractmethod
    def render(self, synthesis: SynthesisResult, prompt: PromptDefinition) -> ReportArtifact: ...

class RendererFactory:
    _renderers: Dict[str, Renderer] = {}

    def register(self, name: str, renderer: Renderer): ...
    def get(self, name: str) -> Renderer: ...

# ── 四种核心Renderer(对应四个行业赛道) ──

class McKinseyTechRenderer(Renderer):
    """麦肯锡风格 — 科技行业."""
    # 8章节: 概览/趋势/竞争/人才/区域/监管/投资/建议
    ...

class MacroDashboardRenderer(Renderer):
    """宏观经济仪表盘风格."""
    # 跨国比较表/趋势图/政策日历/风险矩阵
    ...

class RealEstateRenderer(Renderer):
    """地产行业专属."""
    # 价格指数时序/租金收益率/供需平衡/政策时间线/项目案例
    ...

class VisaTrackerRenderer(Renderer):
    """移民政策追踪."""
    # 签证路径图/评分计算器/政策变更时间线/案例解读
    ...
```

### 3.5 产物层:Report Store + Archive

**职责**:报告的持久化、检索、归档.

```python
# src/report_store/__init__.py
class ReportStore:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def save(self, artifact: ReportArtifact) -> Path: ...
    def list_reports(self, prompt_id: str = None, date_range=None) -> List[ReportMeta]: ...
    def get_latest(self, prompt_id: str) -> ReportArtifact: ...
    def archive_by_year(self, year: int, dry_run: bool): ...
```

---

## 四、完整执行流程:从一个关键词到一份报告

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
      ├── [2.3] Synthesizer.synthesize(analyses, dimensions, bundle)
      │         → SynthesisResult(章节化+可视化数据+来源)
      │
      └── [2.4] McKinseyTechRenderer.render(synthesis, prompt_def)
                → ReportArtifact(HTML文件, 写入 report_store)
      │
      ▼
[3] 输出: reports/industry/tech/2026-10/20261014_tech_ai_dubai.html
```

---

## 五、调度与运维架构

### 5.1 调度器:以 Prompt 为粒度调度

```python
# src/schedulers/__init__.py
class PromptScheduler:
    """基于 cron 的任务调度器,以 Prompt 为调度单元."""

    def __init__(self, registry: PromptRegistry, runtime: PromptRuntime):
        self.registry = registry
        self.runtime = runtime
        self.scheduler = AsyncIOScheduler()

    def build_schedule(self):
        """扫描所有 enabled=True 的 Prompt,按其 schedule 字段注册 cron 任务."""
        for prompt in self.registry.list_enabled():
            self.scheduler.add_job(
                self._run_prompt,
                trigger=CronTrigger(
                    day_of_week=prompt.schedule.get("day", "*"),
                    hour=prompt.schedule.get("time", "08:00").split(":")[0],
                ),
                args=[prompt.id],
                id=prompt.id,
            )

    def _run_prompt(self, prompt_id: str):
        """执行单个 Prompt 的完整报告链路."""
        artifact = self.runtime.execute(prompt_id)
        # 推送通知(钉钉/飞书/邮件)
        ...
```

### 5.2 CLI 入口

```bash
# ── 即时分析(关键词驱动) ──
python main.py run "迪拜AI网络安全"                    # 单次生成
python main.py run "全球宏观经济" --as macro           # 指定赛道
python main.py run "日本高度人才" --date 2027-01       # 指定时间切片

# ── 批量调度 ──
python main.py schedule --list                         # 查看所有定时任务
python main.py schedule --run macro_global             # 手动触发某个 Prompt
python main.py schedule --run-all                      # 执行所有到期任务

# ── Prompt 管理 ──
python main.py prompt --list                           # 列出所有 Prompt
python main.py prompt --show tech_ai_dubai             # 查看 Prompt 详情
python main.py prompt --validate tech_ai_dubai         # 校验数据管道健康
python main.py prompt --test tech_ai_dubai             # 试跑(不渲染,只验管道)

# ── 报告管理 ──
python main.py report --list                           # 列出所有报告
python main.py report --latest tech_ai_dubai           # 查看最新报告
python main.py report --diff tech_ai_dubai --weeks 4   # 四周对比变化

# ── 数据管道管理 ──
python main.py pipe --list                             # 列出所有管道
python main.py pipe --status                           # 管道健康状态
python main.py pipe --test idc_spending --params '{"category":"AI"}'
```

---

## 六、扩展示例:新增一个行业赛道

假设需要新增"中东房地产"(目前只有零散的 tracker):

```yaml
# 步骤1: 新增 Prompt 定义文件 prompts/realestate/re_dubai.yaml
id: re_dubai
version: 1
label: { zh: "迪拜房地产市场月度深度分析", en: "Dubai Real Estate Monthly Deep-dive" }
triggers: ["迪拜房地产", "迪拜房产", "Dubai real estate", "Dubai property", "阿联酋地产"]
horizon: { type: months, value: 12 }
geo: { region_zh: 迪拜, region_en: Dubai, country_code: AE, peers: [Abu Dhabi, Singapore, London] }

data_pipes:
  - pipe: dld_transactions
    params: { property_type: "Residential" }
  - pipe: valustrat_index
    params: { index: "Dubai Residential Price" }
  - pipe: mortgage_rates
    params: { country: "UAE", source: "UAE Central Bank" }
  - pipe: population_growth
    params: { source: "Dubai Statistics Center" }
  - pipe: news_reuters
    params: { keywords: ["Dubai property", "DLD", "real estate"] }

analysis_dimensions:
  - id: price_trend
    label_zh: 价格与交易量趋势
    method: time_series_decomposition
    required_data: [dld_transactions, valustrat_index]
  - id: rental_yield
    label_zh: 租金收益率与投资回报
    method: yield_model
    required_data: [dld_transactions, mortgage_rates]
  - id: supply_demand
    label_zh: 供需平衡表
    method: balance_sheet
    required_data: [dld_transactions, population_growth]
  - id: policy_risk
    label_zh: 政策与监管风险
    method: policy_scan
    required_data: [news_reuters]

report:
  template: realestate_vertical
  output_dir: reports/industry/realestate

schedule:
  cadence: monthly
  day: monday
  time: "08:00"
```

**完成!不需要修改任何代码** —— 只需要:
1. 新建 `prompts/realestate/re_dubai.yaml`
2. 在 `data_engine` 中确保 `dld_transactions` / `valustrat_index` 等管道已实现
3. PromptRegistry 在启动时自动加载

---

## 七、四大赛道的 Renderer 设计

### 7.1 McKinseyTechRenderer (科技行业)
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

### 7.3 RealEstateRenderer (房地产)
```
封面 → 城市地产速览(Dashboard)
  ├─ 1. 价格指数时序(可自行上传/12月/5年)
  ├─ 2. 租金收益率(各商圈分层)
  ├─ 3. 供需平衡表(新增供应 vs 吸纳量)
  ├─ 4. 投资交易追踪(大宗交易/外资动向)
  ├─ 5. 按揭成本与可负担性
  ├─ 6. 政策时间线(限购/税收/土地)
  ├─ 7. 重点商圈画像(Downtown, DIFC, D Marina...)
  └─ 8. 12个月展望与配置权重
```

### 7.4 VisaTrackerRenderer (移民政策)
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

## 九、迁移路线图

### Phase 1:Prompt Registry + Runtime 骨架(1周)
- [ ] 实现 `PromptRegistry` (YAML 加载/索引/匹配)
- [ ] 实现 `PromptRuntime` (骨架,数据管道 stub)
- [ ] 实现 `PipeRunner` + 3-4 个核心 Pipe
- [ ] 实现 CLI 入口 `run` 命令
- [ ] 验证: `python main.py run "迪拜AI网络安全"` 端到端跑通

### Phase 2:行业数据采集管道(1-2周)
- [ ] 实现 10+ 个具体 Pipe 类
- [ ] 数据缓存与老化机制
- [ ] 管道健康检查状态页
- [ ] 验证:每个 Prompt 的数据管道 100% 可运行

### 3.3 渲染层(1周)
- [ ] 实现 RendererFactory
- [ ] 实现 McKinseyTechRenderer
- [ ] 实现 MacroDashboardRenderer
- [ ] 实现 RealEstateRenderer
- [ ] 实现 VisaTrackerRenderer
- [ ] 验证:四条赛道各产出一份可信报告

### Phase 4:调度与运维(3-5天)
- [ ] 实现 PromptScheduler (cron 调度)
- [ ] 实现 ReportStore 与归档
- [ ] CLI 实现 schedule/report 命令
- [ ] 验证:s + 定时触达

### Phase 5:Prompt 库扩展(持续)
- [ ] 填充 prompts/ 目录至 20+ 个 Prompt 定义
- [ ] 新增行业赛道(消费/医疗/新能源...)
- [ ] 优化触发词匹配精度
- [ ] 沉淀 Prompt 模板(pattern library)

---

## 十、关键设计决策记录

### 决策 1:为什么 Prompt 定义为 YAML 配置而非代码?
**答案**: 让分析师/业务人员可以独立维护 Prompt 的定义、数据管道、报告结构,无需程序员介入.代码只负责执行引擎.这解决了"业务逻辑频繁变更"与"代码发布流程沉重"的矛盾.

### 决策 2:为什么不用通用 LLM 端到端?
**答案**: 行业报告的可信度依赖可验证的数据来源与可复现的分析框架.完全依赖 LLM 会引入幻觉风险,且无法保证引用准确性.采用"结构化数据管道 + 规则分析 + LLM 辅助综合"路径:数据与分析是确定性的,LLM 只负责语言润色与逻辑衔接.

### 决策 3:为什么四个赛道用不同 Renderer 而非统一模板?
**答案**: 每个赛道的"分析范式"本质不同.科技行业是"趋势×竞争×技术",宏观经济是"指标×跨国×政策",房地产是"价格×供需×项目",移民是"路径×政策×案例".用统一模板会强行扭曲某一类信息,导致报告不可读.每种 Renderer 为该赛道的"原生长句"服务.

### 决策 4:如何处理外部付费数据?
**答案**: -
 公有数据(官方统计局/央行/入管局/IMF/WorldBank):直接写入 Pipe
 低估数据(IDC/Gartner):预留 Hook,支持导入 CSV 快照
 付费 API(LinkedIn/NewsAPI):封装为可选 Pipe,缺失时降级(跳过该 section,不阻塞报告生成)
 这套"PIPE_DEGRADED"策略已在设计中预留.

---

## 十一、总结:新架构下的代码组织

```text
intelligence/
├── prompts/                         # ◄── 提示词定义库(新的"一等公民")
│   ├── macro/
│   │   ├── macro_global.yaml
│   │   ├── macro_us.yaml
│   │   └── ...
│   ├── tech/
│   │   ├── tech_ai_dubai.yaml
│   │   └── ...
│   ├── realestate/
│   │   └── re_dubai.yaml
│   └── migration/
│       └── visa_japan_hsp.yaml
│
├── src/
│   ├── prompt_registry/             # 提示词注册与匹配
│   │   ├── __init__.py             #  PromptRegistry
│   │   ├── loader.py               #  YAML加载器
│   │   ├── matcher.py              #  模糊关键词匹配
│   │   └── validator.py            #  Prompt 定义校验
│   │
│   ├── prompt_runtime/              # 提示词执行引擎
│   │   ├── __init__.py             #  PromptRuntime
│   │   ├── executor.py             #  执行协调
│   │   ├── analyzer.py             #  多维分析
│   │   ├── synthesizer.py          #  章节综合
│   │   └── cache.py                #  执行缓存
│   │
│   ├── data_engine/                 # 数据引擎 + 管道
│   │   ├── __init__.py             #  DataEngine
│   │   ├── pipe.py                 #  PipeRunner + DataPipe ABC
│   │   ├── pipes/                  #  具体管道实现
│   │   │   ├── gartner.py
│   │   │   ├── idc.py
│   │   │   ├── dld.py
│   │   │   ├── sec.py
│   │   │   ├── news_api.py
│   │   │   ├── linkedin.py
│   │   │   ├── imf_indicator.py
│   │   │   ├── japan_immigration.py
│   │   │   └── worldbank.py
│   │   ├── cache.py
│   │   └── health.py
│   │
│   ├── renderers/                   # 报告渲染器族
│   │   ├── __init__.py             #  RendererFactory
│   │   ├── base.py                 #  Renderer ABC
│   │   ├── tech_mckinsey.py        #  科技(麦肯锡)
│   │   ├── macro_dashboard.py      #  宏观(仪表盘)
│   │   ├── realestate.py           #  房地产(价格+周期)
│   │   └── visa_tracker.py         #  移民(路径+政策)
│   │
│   ├── schedulers/                  # 调度器
│   │   ├── __init__.py             #  PromptScheduler
│   │   └── cron.py                 #  Cron 触发
│   │
│   ├── report_store/                # 报告仓库
│   │   ├── __init__.py
│   │   ├── repository.py
│   │   └── archive.py
│   │
│   └── utils/
│       ├── plotting.py
│       └── llm_client.py           # LLM 辅助
│
├── main.py                          # CLI 入口(重构为 prompt-driven)
├── config/
│   └── settings.py                  # 保留(宏观保留为数据底座)
│
└── reports/
    └── industry/                    # 行业报告输出
        ├── tech/
        ├── macro/
        ├── realestate/
        └── migration/
```

---

> **设计仓促使**:从"流程驱动"到"提示词驱动",本质上是将系统的"变化点"从代码(compiled artifact)转移到了配置(Human-readable YAML). 每次业务扩展 = 添加/修改一个 Prompt 定义,不经代码发布. 这就是 Prompt-Driven Architecture 的工程价值.
