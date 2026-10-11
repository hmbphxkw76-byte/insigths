# 留学申请分析模块 — 提示词与数据采集设计

## 模块概述

本模块提供面向高中毕业生的留学申请全景分析功能，覆盖 **8个主要留学目标国** 的本科申请路径。
与科技、房地产、宏观经济等分析模块并列，由 `intustry_pipeline.yaml` 统一调度。

## 目录结构

```
prompts/studyabroad/
├── README.md                          # 本文件 — 设计说明
├── module_config.yaml                 # 模块索引配置（各国Prompt注册 + 数据源URL清单）
├── template_generic.yaml              # 通用参数化模板（快速新增国家时使用）
│
├── study_abroad_fr_engineering.yaml   # 🇫🇷 法国工程师学院(Grande École)
├── study_abroad_jp.yaml               # 🇯🇵 日本本科留学
├── study_abroad_de.yaml               # 🇩🇪 德国本科留学
├── study_abroad_uk.yaml               # 🇬🇧 英国本科留学
├── study_abroad_au.yaml               # 🇦🇺 澳洲本科留学
├── study_abroad_ca.yaml               # 🇨🇦 加拿大本科留学
├── study_abroad_us.yaml               # 🇺🇸 美国本科留学
└── study_abroad_sg.yaml               # 🇸🇬 新加坡本科留学
```

## 报告结构（8维度统一框架）

所有国家的留学分析 Prompt 生成 **8章节统一报告**：

| # | 维度 | 内容说明 |
|---|------|---------|
| 1 | **教育体系架构** | 该国高等教育体系独特性、学位层级、与中国的差异 |
| 2 | **申请路径全景图** | 所有合法入学路径、对比决策树、适合人群画像 |
| 3 | **院校筛选与认证** | 中国教育部认可名单 + 该国本土认证体系 |
| 4 | **费用全拆解** | 学费(本/国际) + 生活费 + 隐性成本 + 奖学金 |
| 5 | **时间轴规划** | 从现在起的倒计时甘特图 + 关键deadline |
| 6 | **签证与居留** | 最新签证政策、毕业后工签、转永居路径 |
| 7 | **就业与职业发展** | 留目标国就业数据 + 回国发展路径 |
| 8 | **风险与避坑** | TOP 10高风险决策点 + 常见中介话术辟谣 |

## 参数化模板使用

新增目标国时，复制 `template_generic.yaml`，替换占位符：

```bash
cp template_generic.yaml study_abroad_xx.yaml
# 编辑占位符: {COUNTRY} → 国家中文, {COUNTRY_EN} → 国家英文, {COUNTRY_CODE} → ISO代码
```

占位符清单：
- `{COUNTRY}` — 国家中文名
- `{COUNTRY_EN}` — 国家英文名
- `{COUNTRY_CODE}` — ISO 3166-1 alpha-2 代码
- `{KEY_TRIGGERS}` — 触发关键词列表
- `{TOP_INSTITUTIONS}` — 目标国家Top院校列表
- `{TUITION_RANGE}` — 学费区间
- `{LIVING_COST}` — 月生活费区间
- `{VISA_TYPE}` — 主要学生签证类型
- `{PEER_COUNTRIES}` — 对标国家

## 自动数据采集

各数据管道（`src/data_engine/pipes/study_abroad_pipes.py`）从以下 **官方权威来源** 自动采集：

### 法国
| 来源 | URL | 数据类型 |
|------|-----|---------|
| CTI - 法国工程师职衔委员会 | https://www.cti-commission.fr | 认证院校名单 |
| Campus France 中文站 | https://chine.campusfrance.org | 项目列表 |
| France-Visas | https://france-visas.gouv.fr | 签证政策 |
| INSEE | https://www.insee.fr/en | 经济/生活数据 |

### 日本
| 来源 | URL | 数据类型 |
|------|-----|---------|
| JASSO 日本学生支援机构 | https://www.jasso.go.jp/en | 统计/EJU/SGU |
| MEXT 文部科学省 | https://www.mext.go.jp/en | 政策/法规 |
| JPSS Japan Study Support | https://www.jpss.jp/en | 院校搜索 |
| 出入国在留管理庁 | https://www.moj.go.jp/isa | 签证/在留 |

### 德国
| 来源 | URL | 数据类型 |
|------|-----|---------|
| DAAD 德国学术交流中心 | https://www.daad.de/en | 项目数据库 |
| APS 留德审核部 | https://www.aps.org.cn/zh | 学历审核 |
| TU9 德国理工大学联盟 | https://www.tu9.de | 联盟院校 |

### 英国
| 来源 | URL | 数据类型 |
|------|-----|---------|
| UCAS | https://www.ucas.com | 申请系统 |
| British Council Study UK | https://www.britishcouncil.org | 留学信息 |
| UK Gov Student Visa | https://www.gov.uk/student-visa | 签证政策 |
| HESA 高等教育统计局 | https://www.hesa.ac.uk | 统计数据 |

### 澳洲
| 来源 | URL | 数据类型 |
|------|-----|---------|
| Study Australia | https://www.studyaustralia.gov.au | 官方指南 |
| Home Affairs Australia | https://immi.homeaffairs.gov.au | 签证政策 |
| CRICOS | https://cricos.education.gov.au | 注册院校 |

### 加拿大
| 来源 | URL | 数据类型 |
|------|-----|---------|
| EduCanada | https://www.educanada.ca | 官方指南 |
| IRCC | https://www.canada.ca/en/immigration-refugees-citizenship | 签证/移民 |

### 美国
| 来源 | URL | 数据类型 |
|------|-----|---------|
| Common App | https://www.commonapp.org | 申请系统 |
| EducationUSA | https://educationusa.state.gov | 官方指南 |
| US State Dept (Study Visas) | https://travel.state.gov | 签证政策 |
| USCIS (OPT/H-1B) | https://www.uscis.gov | 工作许可 |

### 新加坡
| 来源 | URL | 数据类型 |
|------|-----|---------|
| ICA | https://www.ica.gov.sg | 签证/PR |
| MOE Singapore | https://www.moe.gov.sg | 学费补贴 |
| NUS Admissions | https://www.nus.edu.sg/osa | 录取信息 |

## 调度计划

| 国家 | 频率 | 月份 | 优先级 |
|------|------|------|--------|
| 🇫🇷 法国工程师 | 季度 | 1/4/7/10 | critical |
| 🇯🇵 日本 | 季度 | 1/4/7/10 | high |
| 🇩🇪 德国 | 季度 | 2/5/8/11 | high |
| 🇬🇧 英国 | 季度 | 1/4/7/10 | high |
| 🇦🇺 澳洲 | 季度 | 2/5/8/11 | high |
| 🇨🇦 加拿大 | 季度 | 3/6/9/12 | high |
| 🇺🇸 美国 | 季度 | 1/4/7/10 | high |
| 🇸🇬 新加坡 | 季度 | 3/6/9/12 | medium |

## 与中国教育部涉外监管的衔接

报告在"院校筛选与认证"章节 **必须** 包含：
- 中国教育部涉外监管信息网查询：https://jsj.moe.gov.cn
- 留学服务中心学历认证：https://zwfw.cscse.edu.cn
- ⚠️ 提醒用户：认证结果以教育部官方回复为准

## 数据质量规则

1. 所有数据必须标注 【数据来源】和【数据年份】
2. 政策引用必须标注 【官方来源URL】
3. 对不确定信息明确标注 ⚠️ 并提供核实方式
4. 对"中介夸大宣传"主动辟谣
5. 使用对比表格、决策树可视化提高可读性
6. 关键术语保留原文（法语/德语/日语等），附中文解释

## 与已有模块的关系

```
intelligence/
├── reports/
│   ├── industry/           ← 科技/AI网络/半导体行业报告
│   ├── monthly/            ← 月度宏观经济报告
│   ├── weekly/             ← 周报
│   ├── daily/              ← 日报
│   └── studyabroad/        ← 🎓 留学分析报告（本模块新增）
│       ├── fr_engineering/
│       ├── japan_undergraduate/
│       ├── germany_undergraduate/
│       ├── uk_undergraduate/
│       ├── australia_undergraduate/
│       ├── canada_undergraduate/
│       ├── us_undergraduate/
│       └── singapore_undergraduate/
```
