# IntelKB — Prompt-Driven Intelligence Engine

## 系统概述

以**提示词（Prompt）**为核心驱动力的行业深度分析引擎。
用户通过自然语言关键词触发分析任务，系统自动完成 **数据采集 → 分析计算 → 报告渲染** 全流程。

**核心理念**：配置即代码（Config as Code）。所有分析意图、数据管道、报告格式均由 YAML 定义，代码仅负责解析和执行。

---

## 目录结构

```
intelligence/
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
│   ├── tech/                # 科技行业（半导体 / AI / 网络安全）
│   │   ├── tech_semiconductor.yaml
│   │   ├── tech_ai.yaml
│   │   ├── tech_cybersecurity.yaml
│   │   └── tech_ai_cybersecurity.yaml
│   ├── realestate/          # 房地产
│   │   └── re_dubai.yaml
│   ├── studyabroad/         # 留学分析
│   │   ├── study_abroad_au.yaml
│   │   ├── study_abroad_ca.yaml
│   │   ├── study_abroad_de.yaml
│   │   └── ...
│   └── migration/           # 移民签证
│       └── visa_japan_hsp.yaml
│
├── src/                     # 源代码（全部围绕 Prompt 展开）
│   ├── __init__.py
│   ├── prompt_registry/     # Prompt 注册与匹配引擎
│   │   └── __init__.py      # PromptRegistry: 加载 YAML → 关键词匹配
│   ├── prompt_runtime/      # 执行引擎（采集→分析→渲染）
│   │   └── __init__.py      # PromptRuntime: 调度三阶段流水线
│   ├── data_engine/         # 数据管道引擎
│   │   ├── __init__.py      # PipeRunner: 并行执行、Parquet 缓存
│   │   └── pipes/           # 各行业的 DataPipe 实现
│   │       ├── auto_register.py
│   │       ├── macro_pipes.py
│   │       ├── tech_pipes.py
│   │       ├── cyber_pipes.py
│   │       ├── realestate_pipes.py
│   │       ├── migration_pipes.py
│   │       └── study_abroad_pipes.py
│   └── renderers/           # 报告渲染器
│       ├── __init__.py      # RendererFactory
│       ├── mckinsey_tech.py # 麦肯锡风格（科技/AI/半导体）
│       ├── macro_dashboard.py
│       ├── real_estate.py
│       └── visa_tracker.py
│
├── data/                    # 数据目录
│   └── store/               # Pipe 引擎 parquet 仓库（运行时自动生成）
│
├── reports/                 # 分析报告输出
│   ├── industry/            # 职业/行业分析
│   └── career/              # 海外职业移民生命周期
│
├── docs/                    # 架构文档
│   └── architecture_prompt_driven.md
│
└── logs/                    # 运行日志
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

## 架构设计

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  prompts/    │────▶│  PromptRegistry  │────▶│  PromptRuntime  │
│  *.yaml      │     │  (加载 + 匹配)    │     │  (执行引擎)      │
└──────────────┘     └──────────────────┘     └────────┬────────┘
                                                       │
                                           ┌───────────┼───────────┐
                                           ▼           ▼           ▼
                                      ┌────────┐ ┌─────────┐ ┌──────────┐
                                      │DataPipe│ │Analyzer │ │Renderer  │
                                      │(采集)  │ │(计算)   │ │(渲染HTML)│
                                      └────────┘ └─────────┘ └──────────┘
```

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
  output_dir: reports/industry
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
