# Insights — Prompt-Driven Intelligence Engine

## 系统概述

以**提示词（Prompt）**为核心驱动力的多主题域深度分析引擎。
系统自动采集英文权威数据源，覆盖宏观经济、海外留学、境外就业、房地产行业以及科技/AI/网络安全等领域，
根据提示词配置生成专业的中文分析报告。

**核心理念**：配置即代码（Config as Code）。所有分析意图、数据管道、报告格式均由 YAML 定义，代码仅负责解析和执行。

---

## 目录结构

```
insights/
├── main.py                  # CLI 入口（关键词驱动）
├── README.md                # 本文档
├── requirements.txt         # Python 依赖
│
├── config/
│   └── settings.py          # 全局路径配置（极简，仅保留目录常量）
│
├── prompts/                 # ⭐ Prompt 定义目录（核心配置）
│   ├── prompt_schema.yaml   # Prompt YAML Schema 说明
│   ├── macro/               # 宏观经济分析
│   │   └── macro_global.yaml
│   ├── tech/                # 科技行业（AI / 网络安全 / 半导体）
│   │   ├── tech_ai.yaml
│   │   ├── tech_ai_cybersecurity.yaml
│   │   ├── tech_cybersecurity.yaml
│   │   ├── tech_dubai_ai_cybersecurity.yaml
│   │   └── tech_semiconductor.yaml
│   ├── realestate/          # 房地产
│   │   └── re_dubai.yaml
│   ├── studyabroad/         # 留学分析
│   │   ├── study_abroad_au.yaml      # 澳洲
│   │   ├── study_abroad_ca.yaml      # 加拿大
│   │   ├── study_abroad_de.yaml      # 德国
│   │   ├── study_abroad_fr_engineering.yaml
│   │   ├── study_abroad_gb_master.yaml
│   │   ├── study_abroad_hk.yaml      # 香港
│   │   ├── study_abroad_jp.yaml      # 日本
│   │   ├── study_abroad_nz.yaml      # 新西兰
│   │   ├── study_abroad_sg.yaml      # 新加坡
│   │   ├── study_abroad_uk.yaml      # 英国
│   │   ├── study_abroad_us.yaml      # 美国
│   │   └── ... (更多国家与学位层次)
│   └── career/              # 海外就业与职业移民
│       ├── visa_japan_driver.yaml     # 日本驾驶签证
│       ├── visa_japan_hsp.yaml        # 日本高度人才
│       ├── visa_nz_driver.yaml        # 新西兰驾驶签证
│       ├── profession_country.yaml    # 职业清单国家对比
│       ├── visa_profession_matrix.yaml
│       └── _template_lifecycle.yaml   # 移民生命周期模板
│
├── src/                     # 源代码（全部围绕 Prompt 展开）
│   ├── __init__.py
│   ├── prompt_registry/     # Prompt 注册与匹配引擎
│   │   └── __init__.py      # PromptRegistry: 加载 YAML → 关键词匹配
│   ├── prompt_runtime/      # 执行引擎（采集→分析→渲染）
│   │   └── __init__.py      # PromptRuntime: 调度三阶段流水线
│   ├── data_engine/         # 数据管道引擎
│   │   ├── __init__.py      # DataPipe, PipeRunner, DataBundle
│   │   └── pipes/           # 各主题域的 DataPipe 实现
│   │       ├── auto_register.py
│   │       ├── career/      # 海外就业·签证移民管道
│   │       │   ├── extra_pipes.py
│   │       │   ├── japan_visa_pipes.py
│   │       │   ├── migration_pipes.py
│   │       │   ├── nz_visa_pipes.py
│   │       │   └── profession_pipes.py
│   │       ├── macro/       # 宏观经济管道
│   │       │   └── macro_pipes.py
│   │       ├── realestate/  # 海外房地产管道
│   │       │   └── realestate_pipes.py
│   │       ├── studyabroad/ # 留学分析管道
│   │       │   └── study_abroad_pipes.py
│   │       └── tech/        # 科技(AI/网络安全/半导体)管道
│   │           ├── cyber_pipes.py
│   │           └── tech_pipes.py
│   └── renderers/           # 报告渲染器（按主题域划分）
│       ├── __init__.py      # RendererFactory
│       ├── career/          # 签证/职业/移民生命周期报告
│       │   ├── japan_driver.py
│       │   ├── migration_lifecycle.py
│       │   ├── profession_analyzer.py
│       │   └── visa_tracker.py
│       ├── macro/           # 宏观经济仪表盘
│       │   └── dashboard.py
│       ├── realestate/      # 房地产深度分析
│       │   └── dashboard.py
│       ├── studyabroad/     # 留学申请分析
│       │   └── __init__.py
│       └── tech/            # AI/网络安全/半导体 (麦肯锡风格)
│           └── mckinsey_style.py
│
├── data/                    # 数据目录
│   └── store/               # Pipe 引擎 parquet 仓库（运行时自动生成）
│
├── reports/                 # 分析报告输出
│   ├── career/              # 海外职业移民生命周期
│   ├── macro/               # 宏观经济
│   ├── realestate/          # 房地产
│   ├── studyabroad/         # 留学
│   └── tech/                # 科技
│
└── docs/                    # 架构文档
    └── architecture_prompt_driven.md
```

---

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 查看所有已注册的 Prompt
python main.py --list

# 查看某赛道 Prompt
python main.py --vertical tech --list

# 执行半导体分析（模糊匹配关键词）
python main.py --keyword 半导体 --run

# 执行科技赛道全部 Prompt
python main.py --vertical tech --run

# 直接指定 Prompt ID 执行
python main.py --prompt tech_ai --run

# 查看 Prompt 详情
python main.py --show tech_semiconductor

# 健康检查
python main.py --health

# 基准测试（跑一遍所有 Prompt）
python main.py --benchmark
```

---

## 数据源原则

系统严格遵循以下数据源策略（定义于 `prompt_schema.yaml`）：

1. **英文权威优先**：所有数据采集必须来自英文权威机构（World Bank, IMF, 各国政府英文门户等）
2. **中文输出**：最终报告统一以中文显示给终端用户
3. **国家特定例外**：针对日本相关资料，允许参照日本日语语言官方网站（因信息更新更及时），但输出仍为中文

---

## 架构设计

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  prompts/    │────▶│  PromptRegistry  │────▶│  PromptRuntime  │
│  *.yaml      │     │  (加载 + 匹配)    │     │  (执行引擎)      │
└──────────────┘     └──────────────────┘     └────────�────────┘
                                                       │
                                           �───────────�───────────�
                                           ▼           ▼           ▼
                                      ┌────────┐ ┌─────────� ┌──────────┐
                                      │DataPipe│ │Analyzer │ │Renderer  │
                                      │(采集)  │ │(计算)   │ │(渲染HTML)│
                                      └────────┘ └─────────┘ └──────────�
```

### 主题域(Vertical)划分

| 垂直域 | 目录 | 数据管道 | 渲染器 | 典型 Prompt |
|--------|------|----------|--------|-------------|
| **macro** | `pipes/macro/`, `renderers/macro/` | 宏观经济数据采集 | `MacroDashboardRenderer` | `macro_global` |
| **tech** | `pipes/tech/`, `renderers/tech/` | 科技/AI/网络安全数据采集 | `McKinseyTechRenderer` | `tech_ai`, `tech_semiconductor` |
| **realestate** | `pipes/realestate/`, `renderers/realestate/` | 房地产数据采集 | `RealEstateDashboardRenderer` | `re_dubai` |
| **career** | `pipes/career/`, `renderers/career/` | 签证/职业数据采集 | `VisaTrackerRenderer`, `JapanDriverRenderer` | `visa_japan_hsp`, `visa_nz_driver` |
| **studyabroad** | `pipes/studyabroad/`, `renderers/studyabroad/` | 留学数据采集 | `McKinseyTechRenderer` | `study_abroad_us`, `study_abroad_uk` |

### 核心组件

1. **PromptDefinition** (`prompt_registry`): Prompt YAML 的结构化表示，包含触发词、数据管道列表、分析维度、报告模板
2. **PipeRunner** (`data_engine`): 并行执行声明的 DataPipe，支持 Parquet 缓存与失败降级
3. **PromptRuntime** (`prompt_runtime`): 三阶段调度 — 采集 → 分析 → 渲染
4. **RendererFactory** (`renderers`): 根据 Prompt 的 `report_template` 字段选择对应渲染器

### Prompt YAML 结构

```yaml
id: tech_semiconductor
label:
  zh: 全球半导体行业深度分析
en: Global Semiconductor Industry Analysis
triggers: [半导体, chip, semiconductor, 晶圆, foundry]
horizon:
  type: future_years
  value: 5
geo:
  region_zh: "全球"
  region_en: "Global"
data_pipes:
  - pipe: semiconductor_sales
  - pipe: company_earnings
analysis_dimensions:
  - id: market_sizing
    label_zh: "市场规模与预测"
    method: quantitative_forecast
report:
  template: mckinsey_tech
  output_dir: reports/tech
schedule:
  cadence: monthly
  time: "08:00"
```

---

## 报告命名规则

生成的报告文件命名格式：

```
{vertical}_{prompt_id}_{YYYYMMDD}.html
```

示例：
- `tech_tech_semiconductor_20261011.html`
- `macro_macro_global_20261011.html`

---

## 设计原则

1. **纯 Prompt-Driven**：所有分析意图由 `prompts/*.yaml` 声明，代码仅负责解析与执行
2. **配置与代码解耦**：新增行业/赛道仅需添加 YAML + DataPipe，无需修改核心代码
3. **目录结构清晰**：config / prompts / src / data / reports 各司其职
4. **管道化数据源**：每个 DataPipe 是独立、可组合、可缓存的数据采集单元
5. **多赛道渲染器**：针对不同行业定制 HTML 模板与可视化风格
6. **主题域对齐**：`src/data_engine/pipes/` 与 `src/renderers/` 的子目录与 `prompts/` 主题域一一对应，便于动态扩展
