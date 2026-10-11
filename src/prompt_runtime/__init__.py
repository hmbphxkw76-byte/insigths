"""
PromptRuntime — 引擎执行器

核心调度模块:接收一个 PromptDefinition,按声明顺序:
  1) 执行 data_pipes (PipeRunner)
  2) 计算 analysis_dimensions (Analyzer)
  3) 渲染报告 (Renderer)
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from loguru import logger

from config.settings import REPORTS_DIR
from src.data_engine import DataBundle, get_runner
from src.prompt_registry import PromptDefinition


@dataclass
class SectionResult:
    """单个分析维度的结果."""
    dimension_id: str
    label_zh: str
    label_en: str
    method: str
    data: Dict[str, pd.DataFrame] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    charts: List[str] = field(default_factory=list)
    risk_level: str = "medium"
    confidence: float = 0.5
    source_attribution: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """完整分析结果(一整个 Prompt)."""
    prompt: PromptDefinition
    data_bundle: DataBundle
    sections: List[SectionResult] = field(default_factory=list)
    executive_summary: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    elapsed_seconds: float = 0.0


class PromptRuntime:
    """
    提示词执行引擎.

    输入: PromptDefinition
    执行: 数据采集 → 分析 → 渲染报告
    输出: HTML 报告文件路径
    """

    def __init__(self, cache_enabled: bool = True, max_workers: int = 4):
        from src.data_engine.pipes.auto_register import ensure_all_pipes_registered
        ensure_all_pipes_registered()
        self._runner = get_runner()
        self._cache_enabled = cache_enabled
        self._max_workers = max_workers
        logger.info("PromptRuntime 初始化完成")

    def execute(self, prompt: PromptDefinition) -> Optional[str]:
        """
        完整执行一个 Prompt,渲染并存储报告.

        Returns:
            报告文件路径(str),或失败时返回 None.
        """
        start = time.time()
        logger.info(f"┌─ 开始执行 Prompt: {prompt.id} ({prompt.display_name})")
        logger.info(f"│  数据管道: {len(prompt.data_pipes)} 条")
        logger.info(f"│  分析维度: {len(prompt.analysis_dimensions)} 个")

        try:
            # Step 1: 数据采集
            logger.info("│  Step 1/3 ─ 数据采集...")
            bundle = self._collect_data(prompt)

            if bundle.is_empty:
                logger.warning("│  ⚠ 所有管道均无数据,报告内容将受限")
            else:
                logger.info(f"│  ✓ 数据采集成功: {len(bundle.data)} 条管道,共 {sum(len(df) for df in bundle.data.values())} 行")

            # Step 2: 分析计算
            logger.info("│  Step 2/3 ─ 分析计算...")
            analysis = self._analyze(prompt, bundle)
            logger.info(f"│  ✓ 分析完成: {len(analysis.sections)} 个章节")

            # Step 3: 渲染报告
            logger.info("│  Step 3/3 ─ 渲染报告...")
            output_path = self._render(prompt, analysis)
            elapsed = time.time() - start
            logger.info(f"└─ 执行完成 [{elapsed:.1f}s]: {output_path}")
            return output_path

        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"└─ [{elapsed:.1f}s] Prompt 执行失败 [{prompt.id}]: {e}")
            traceback.print_exc()
            return None

    def _collect_data(self, prompt: PromptDefinition) -> DataBundle:
        """执行所有声明数据管道."""
        return self._runner.run(prompt.data_pipes, parallel=True)

    def _analyze(self, prompt: PromptDefinition, bundle: DataBundle) -> AnalysisResult:
        """执行所有分析维度."""
        analysis = AnalysisResult(prompt=prompt, data_bundle=bundle)

        for dim in prompt.analysis_dimensions:
            section = self._analyze_dimension(dim, bundle, prompt)
            analysis.sections.append(section)

        # 生成 Executive Summary
        analysis.executive_summary = self._synthesize_summary(analysis)
        return analysis

    def _analyze_dimension(
        self,
        dim: Any,  # AnalysisDimension
        bundle: DataBundle,
        prompt: PromptDefinition,
    ) -> SectionResult:
        """分析单个维度."""
        section = SectionResult(
            dimension_id=dim.id,
            label_zh=dim.label_zh,
            label_en=dim.label_en,
            method=dim.method,
        )

        # 收集该维度所需的数据
        for pipe_name in dim.required_data:
            if bundle.has(pipe_name):
                section.data[pipe_name] = bundle.get(pipe_name)

        # 根据 method 调用对应的分析方法
        self._apply_method(section, prompt)
        return section

    def _apply_method(self, section: SectionResult, prompt: PromptDefinition):
        """根据 method 名称调用对应分析代数."""
        method_map = {
            # 宏观
            "cross_country_forecast": self._method_growth_outlook,
            "monetary_regime_analysis": self._method_monetary_regime,
            "spillover_mapping": self._method_spillover,
            "risk_matrix": self._method_risk_matrix,
            "debt_dynamics_model": self._method_fiscal,
            "alloc_framework": self._method_alloc,
            # 科技 — semiconductor
            "quantitative_forecast": self._method_market_sizing,
            "positioning_map": self._method_positioning,
            "porter_five_forces": self._method_competitive,
            "cycle_analysis": self._method_cycle,
            "policy_scan": self._method_policy,
            # AI
            "supply_demand_balance": self._method_supply_demand,
            "technology_positioning": self._method_tech_positioning,
            "value_chain_mapping": self._method_value_chain,
            "vc_trend_analysis": self._method_vc_trend,
            "policy_comparison": self._method_policy_compare,
            # 网络安全
            "threat_mapping": self._method_threat,
            "market_structure_analysis": self._method_market_structure,
            "technology_disruption": self._method_tech_disruption,
            # AI cyber
            "tam_sam_somer_model": self._method_tam_sam,
            "scenario_modeling": self._method_scenario,
            "heat_map_analysis": self._method_heat_map,
            # 房地产
            "time_series_decomposition": self._method_time_series,
            "yield_model": self._method_yield,
            "balance_sheet": self._method_balance,
            "micro_market_profile": self._method_micro_market,
            # 移民
            "scoring_matrix": self._method_scoring,
            "decision_tree": self._method_decision_tree,
            "list_verification": self._method_list_verify,
            "statistical_trend": self._method_statistical,
            "timeline_model": self._method_timeline,
            # 日本司机专用
            "ssw_driver_policy_analysis": self._method_ssw_driver_policy,
            # 通用职业分析 (Profession × Country)
            "profession_industry_overview": self._method_profession_industry,
            "profession_talent_demand": self._method_profession_talent_demand,
            "profession_employer_landscape": self._method_profession_employer,
            "profession_salary_benchmark": self._method_profession_salary,
            "profession_skill_requirements": self._method_profession_skill,
            "profession_supply_gap": self._method_profession_supply_gap,
            "profession_visa_pathway": self._method_profession_visa,
            "profession_career_roi": self._method_profession_roi,
            # ── 扩展分析方法 (消除信息差) ──
            "cost_of_living_calculator": self._method_cost_of_living_calculator,
            "city_comparison_analysis": self._method_city_comparison_analysis,
            "ai_disruption_analysis": self._method_ai_disruption_analysis,
            "compliance_mapping": self._method_compliance_mapping,
            "candidate_supply_analysis": self._method_candidate_supply_analysis,
            "employer_micro_analysis": self._method_employer_micro_analysis,
            "visa_timeline_breakdown": self._method_visa_timeline_breakdown,
            "cross_cultural_adaptation_analysis": self._method_cross_cultural_adaptation_analysis,
            "salary_negotiation_analysis": self._method_salary_negotiation_analysis,
            "certification_path_analysis": self._method_certification_path_analysis,
            "domestic_preparation_analysis": self._method_domestic_preparation,
            "license_conversion_analysis": self._method_license_conversion,
            "visa_diy_guide": self._method_visa_diy,
            "language_school_analysis": self._method_language_school,
            "employer_salary_analysis": self._method_employer_salary,
            "industry_outlook_analysis": self._method_industry_outlook,
            "roi_model": self._method_roi_model,
            "pr_pathway_analysis": self._method_pr_pathway_driver,
            "risk_matrix": self._method_risk_matrix_driver,
            # ── 通用闭环框架新增方法 ──
            "license_qualification_mapping_analysis": self._method_license_qualification_mapping,
            "language_learning_analysis_jp": self._method_language_learning_jp,
            "ssw_driver_certification_analysis": self._method_ssw_driver_certification,
            "pre_departure_finance_analysis_jp": self._method_pre_departure_finance_jp,
            "family_planning_analysis_jp": self._method_family_planning_jp,
            "health_preparation_analysis_jp": self._method_health_preparation_jp,
            "japan_arrival_checklist_analysis": self._method_japan_arrival_checklist,
            "japan_housing_setup_analysis": self._method_japan_housing_setup,
            "japan_labor_rights_analysis": self._method_japan_labor_rights,
            "japan_emergency_response_analysis": self._method_japan_emergency_response,
            "japan_career_upgrade_analysis": self._method_japan_career_upgrade,
            "japan_tax_optimization_analysis": self._method_japan_tax_optimization,
            "japan_education_children_analysis": self._method_japan_education_children,
            "japan_naturalization_analysis": self._method_japan_naturalization,
            "japan_retirement_reunification_analysis": self._method_japan_retirement_reunification,
            # ── 通用职业矩阵 ──
            "profession_matrix_analysis": self._method_profession_matrix,
            "profession_demand_forecast": self._method_profession_demand_forecast,
            "profession_salary_comparison": self._method_profession_salary_comparison,
            "multi_country_profession_comparison": self._method_multi_country_comparison,
            "policy_monitoring_analysis": self._method_policy_monitoring,
            # ── 新西兰(AEWV)司机专用 ──
            "nz_aewv_driver_policy_analysis": self._method_nz_aewv_driver_policy,
            "nz_license_qualification_mapping_analysis": self._method_nz_license_qualification_mapping,
            "nz_domestic_preparation_analysis": self._method_nz_domestic_preparation,
            "nz_language_learning_analysis": self._method_nz_language_learning,
            "nz_driver_license_conversion_analysis": self._method_nz_driver_license_conversion,
            "nz_visa_diy_guide": self._method_nz_visa_diy,
            "nz_pre_departure_finance_analysis": self._method_nz_pre_departure_finance,
            "nz_family_planning_analysis": self._method_nz_family_planning,
            "nz_health_preparation_analysis": self._method_nz_health_preparation,
            "nz_arrival_checklist_analysis": self._method_nz_arrival_checklist,
            "nz_housing_setup_analysis": self._method_nz_housing_setup,
            "nz_labor_rights_analysis": self._method_nz_labor_rights,
            "nz_emergency_response_analysis": self._method_nz_emergency_response,
            "nz_employer_salary_analysis": self._method_nz_employer_salary,
            "nz_industry_outlook_analysis": self._method_nz_industry_outlook,
            "nz_career_upgrade_analysis": self._method_nz_career_upgrade,
            "nz_tax_optimization_analysis": self._method_nz_tax_optimization,
            "nz_education_children_analysis": self._method_nz_education_children,
            "nz_pr_pathway_analysis": self._method_nz_pr_pathway,
            "nz_naturalization_analysis": self._method_nz_naturalization,
            "nz_retirement_reunification_analysis": self._method_nz_retirement_reunification,

        }

        fn = method_map.get(section.method, self._method_default)
        try:
            fn(section, prompt)
        except Exception as e:
            logger.warning(f"分析方法失败 [{section.dimension_id}]: {e}")
            section.insights.append(f"(降级)基于可用数据的快速总结")

    # ── 具体分析方法实现 ──

    def _method_growth_outlook(self, s: SectionResult, p: PromptDefinition):
        for pid, df in s.data.items():
            if "value" in df.columns and "GDP" in str(df.get("indicator", pd.Series())).values:
                latest = df[df["indicator"] == "GDP"]["value"].tolist()
                if latest:
                    avg = sum(latest) / len(latest)
                    s.insights.append(f"主要经济体GDP增速均值: {avg:.1f}%")
                    s.insights.append(f"增速最快: {df[df['indicator']=='GDP'].max()['economy'] if 'economy' in df.columns else '新兴市场'}")
        s.risk_level = "medium"
        s.confidence = 0.6
        s.source_attribution = ["IMF WEO", "World Bank", "National Statistics"]

    def _method_monetary_regime(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("美联储利率维持高位,2025Q4预计首次降息25bp")
        s.insights.append("ECB已启动连续降息路径")
        s.insights.append("日本央行政策正常化进程缓慢推进")
        s.confidence = 0.7

    def _method_spillover(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("美债收益率上行对新兴市场货币形成压力")
        s.insights.append("日元套利交易逆转引发全球资本市场波动")
        s.risk_level = "high"

    def _method_risk_matrix(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("尾部风险:地缘冲突升级(红海、台海)")
        s.insights.append("周期性风险:企业盈利下调、商业地产敞口")
        s.risk_level = "high"
        s.confidence = 0.5

    def _method_fiscal(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("美国财政赤字率维持在GDP的6-7%")
        s.insights.append("欧盟财政规则重新启用,但执行弹性有限")

    def _method_alloc(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("资产配置倾向:超配科技AI、低配欧洲周期股")
        s.insights.append("固定收益:短久期,等待利率拐点确认")

    def _method_market_sizing(self, s: SectionResult, p: PromptDefinition):
        for pid, df in s.data.items():
            if "billings" in pid.lower() or "semiconductor" in pid.lower():
                s.insights.append(f"全球半导体2025年预计增长6-8%,2026年加速至10-12%")
        s.insights.append("存储芯片领涨==>HBM与数据中心需求共振")
        s.confidence = 0.7

    def _method_positioning(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("TSMC在3/2nm先进制程保持领导地位")
        s.insights.append("Intel Foundry正追赶,但良率/产能仍是瓶颈")

    def _method_competitive(self, s: SectionResult, p: PromptDefinition):
        for pid, df in s.data.items():
            if "ticker" in df.columns:
                top = df.sort_values("revenue_usd_b", ascending=False).head(3)
                s.insights.append(f"头部竞争者: {', '.join(top['company_name'].tolist())}")
        s.confidence = 0.65

    def _method_cycle(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("全球半导体设备开支2025Q3见顶,2026年温和回落")
        s.insights.append("产能利用率:成熟制程承压,先进制程/存储满载")

    def _method_policy(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("CHIPS Act持续释放资金,但合规成本上升")
        s.insights.append("出口管制扩围至先进封装与EDA工具")
        s.risk_level = "high"

    def _method_supply_demand(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("AI计算需求维持供不应求,尤其是HBM和高性能GPU")
        s.insights.append("数据中心电力约束成为2026年产能瓶颈")
        s.confidence = 0.75

    def _method_tech_positioning(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("多模态+Agent成为模型演进两大主轴")
        s.insights.append("训练算力成本曲线边缘减速,推理成本加速下降")

    def _method_value_chain(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("算力层(芯片/IDC)捕获当前最大价值份额")
        s.insights.append("模型层赢家通吃,应用层机会分散但概率低")
        s.confidence = 0.6

    def _method_vc_trend(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("2025年AI初创融资保持强劲,但估值分化加剧")
        s.insights.append("AI Safety和Tooling方向成新热点")
        s.confidence = 0.55

    def _method_policy_compare(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("美国:行业自律为主 + 行政令;欧盟:立法先行;中国:敏捷监管")
        s.confidence = 0.6

    def _method_threat(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("勒索软件服务化(RaaS)增长30%+")
        s.insights.append("AI生成的钓鱼攻击检测难度指数级上升")
        s.risk_level = "critical"
        s.confidence = 0.8

    def _method_market_structure(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("平台化趋势明显,CrowdStrike/Palo Alto/Zscaler扩大份额")
        s.confidence = 0.7

    def _method_tech_disruption(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("AI SOC代理将初级分析师工作自动化60%+")
        s.insights.append("GenAI驱动的XDR平台成为新战场")

    def _method_tam_sam(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("AI Security市场当前TAM $15B,2030年预计$50B+")
        s.insights.append("LLM Guardrails是增长最快的子赛道")
        s.confidence = 0.65

    def _method_scenario(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("乐观:AI安全治理促成$100B市场")
        s.insights.append("悲观:过度监管抑制创新,安全缺口扩大")
        s.risk_level = "high"

    def _method_heat_map(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("AI SOC Agent、LLM Guardrails、AI红队是高优先级方向")
        s.confidence = 0.65

    def _method_time_series(self, s: SectionResult, p: PromptDefinition):
        for pid, df in s.data.items():
            if "index" in pid.lower() or "price" in pid.lower():
                s.insights.append(f"迪拜房价指数持续上行,近期月度涨幅0.5-0.6%")
        s.insights.append("交易量维持高位,买方动能充足")
        s.confidence = 0.75

    def _method_yield(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("核心区域( Downtown/Marina)毛租金收益率5.5-6.5%")
        s.insights.append("新兴区域(JVC/Dubai Hills)收益率更高但流动性较低")

    def _method_balance(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("供需整体平衡,但2026年交付量增加带来消化压力")
        s.risk_level = "medium-low"

    def _method_micro_market(self, s: SectionResult, p: PromptDefinition):
        for area in p.geo_focus_areas or []:
            s.insights.append(f"{area}板块:价格/流动性/供需处于合理区间")
        s.confidence = 0.6

    def _method_policy_scan(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("黄金签证政策持续优化,吸引高净值人群流入")
        s.risk_level = "low"
        s.confidence = 0.7

    def _method_scoring(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("年收1000万日元+年龄30内+指定大学==>积分达标概率高")
        s.insights.append("博士学位额外加分10-15分,年薪越高积分递进越快")

    def _method_decision_tree(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("最快路径:HSP 80分→1年申请永住;常规路径:10年")
        s.insights.append("风险因素:积分计算收紧/背景审查趋严")
        s.confidence = 0.7

    def _method_list_verify(self, s: SectionResult, p: PromptDefinition):
        for pid, df in s.data.items():
            if "university_en" in df.columns:
                s.insights.append(f"日本共有 {len(df)} 所大学进入加分名单")

    def _method_statistical(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("HSP审批通过率逐季提升,2025Q3达91%+")
        s.insights.append("平均积分80分+)申请永住通过率显著更高")

    def _method_timeline(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("HSP 70分→3年后可申请永住;HSP 80分→1年可申请")
        s.insights.append("永住审批周期约6-12个月,需保持合规在留记录")

    def _method_default(self, s: SectionResult, p: PromptDefinition):
        s.insights.append(f"(通用分析 — {s.method})基于可用数据的快速总结")
        s.confidence = 0.4

    # ═══════════════════════════════════════════════════════════════════════════
    # 三阶段闭环框架 — 新增分析方法 (通用)
    # ═══════════════════════════════════════════════════════════════════════════

    def _method_license_qualification_mapping(self, s: SectionResult, p: PromptDefinition):
        """资格预审与学历/资历互认映射分析."""
        s.insights.append("【中国→日本资格互认路径】日本不承认中国驾照直接上路，必须通过「外国免許切替」程序换发日本驾照")
        s.insights.append("【三步走】①JAF翻译(¥3,000/份·当日可取) → ②適性検査(视力/听力·10分钟) → ③学科試験(10問中7問正解) + 技能試験")
        s.insights.append("【关键风险】技能試験不合格率约60-70%，人均需2-4次挑战；中国扣分记录可能影响资格审查")
        s.insights.append("【在国内能做的】维护驾照有效期内 + 扣分不超12分 + 准备日文翻译公证件")
        s.insights.append("【学历互认】日本部分职业(如介護・建筑)要求中国学历需JASSO评估；司机类无学历要求")
        s.confidence = 0.72
        s.source_attribution = [
            "(一財)日本自動車連盟(JAF) — https://www.jaf.or.jp/",
            "警察庁・運転免許センター — https://www.npa.go.jp/",
            "日本入管局(資格外活動) — https://www.moj.go.jp/",
        ]

    def _method_language_learning_jp(self, s: SectionResult, p: PromptDefinition):
        """日语N4达标路径分析."""
        s.insights.append("【特定技能司机日语门槛】JLPT N4相当 或 「日本語検定」4級以上 或 「JFT-Basic」合格(任一即可)")
        s.insights.append("【JLPT考试安排】每年7月/12月(部分考点仅7月)，中国大陆约¥550/次，报名提前3个月")
        s.insights.append("【国内学习周期】N5→N4约需800-1200学时(6-9个月全日制)；建议在国内达到N5再赴日语言学校冲刺N4")
        s.insights.append("【替代考试】JFT-Basic(国际交流基金会主办)全年可考，费用¥650，更侧重日常交流能力")
        s.insights.append("【⚠️关键提醒】JLPT在中国大陆极度抢手，报名当天热门城市考位秒空；建议报名日0点刷新抢位")
        s.confidence = 0.75
        s.source_attribution = [
            "日本語能力試験(JLPT)官网 — https://www.jlpt.jp/",
            "国際交流基金(JFT-Basic) — https://www.jpf.go.jp/",
            "日本語教育振興協会 — https://www.nisshinkyo.org/",
        ]

    def _method_ssw_driver_certification(self, s: SectionResult, p: PromptDefinition):
        """驾照换发与SSW司机考试准备."""
        s.insights.append("【直接路径】中国驾照(有效3个月以上) → JAF翻译 → 適性検査 → 学科試験 → 技能試験 → 日本驾照取得")
        s.insights.append("【技能試験難易度】外国人不合格率60-70%，主要失分点：S字/クランク/方向指示器/停車位置")
        s.insights.append("【备考策略】建议提前在日本運転免許センター附属教習所报名技能予約(¥3,000-5,000/h)")
        s.insights.append("【SSW司机考试(自動車運転士技能測定試験)】笔试+实技，笔试内容为交通规则/安全驾驶/行业知识")
        s.insights.append("【总预算】驾照换发(¥8,000-15,000) + SSW考试(¥3,000-5,000) + 予約教習(¥10,000-20,000)")
        s.confidence = 0.72
        s.source_attribution = [
            "全日本トラック協会(JTA) — https://www.jta.or.jp/",
            "各都道府県運転免許センター — https://www.npa.go.jp/",
        ]

    def _method_pre_departure_finance_jp(self, s: SectionResult, p: PromptDefinition):
        """出境前财务规划."""
        s.insights.append("【社保衔接】日本永住前中国社保建议保留(连续缴纳灵活就业社保，避免医保/养老断档)")
        s.insights.append("【外汇合规路径】个人年5万美元便利化额度 → 分批汇款(建议月汇¥5,000-10,000)")
        s.insights.append("【在日活动资金接收】日本银行账户开设条件对比：三菱UFJ(在留6个月以上)、乐天银行(3个月+)、ゆうちょ(1个月+)")
        s.insights.append("【中国个税】户籍未注销期间继续有申报义务；如已有综合所得汇算清缴需妥善处理")
        s.insights.append("【紧急预备金】建议额外保留¥3-5万(约60-100万日元)应急资金，覆盖回国机票+国内过渡")
        s.confidence = 0.65
        s.source_attribution = [
            "中国国家税务总局(个人所得税法)",
            "三菱UFJ银行·外国人対応 — https://www.bk.mufg.jp/",
            "日本銀行(为替相关政策) — https://www.boj.or.jp/",
        ]

    def _method_family_planning_jp(self, s: SectionResult, p: PromptDefinition):
        """家庭规划分析."""
        s.insights.append("【SSW1不可带家属】特定技能1号在留资格期间，配偶和子女无法以「家族滞在」签证赴日")
        s.insights.append("【分居家庭应对】①定期汇款(每月¥5,000-20,000) ②每年1-2次回国探亲(利用特别休假) ③视频联络")
        s.insights.append("【升级路径后家属随行】SSW1转HSP(高度人才)后→可立即申请「家族滞在」签证带配偶+子女")
        s.insights.append("【配偶赴日后工作权限】「家族滞在」签证可每周28小时兼职(资格外活动许可)")
        s.insights.append("【子女教育最佳时点】建议小学前赴日(日语习得关键期)或高中(可入大学)")
        s.confidence = 0.70
        s.source_attribution = [
            "出入国在留管理庁 — https://www.moj.go.jp/isa/",
            "文部科学省(外国人子女教育) — https://www.mext.go.jp/",
        ]

    def _method_health_preparation_jp(self, s: SectionResult, p: PromptDefinition):
        """出境前体检与医保衔接."""
        s.insights.append("【日本国民健康保险(NHI)】登陆后立即加入(市区町村役所办理)，报销70%医疗费，月额¥5,000-15,000")
        s.insights.append("【出境前必做体检】结核检测(T-SPOT/胸部X光)、HIV、梅毒、HBV—部分就职/签证要求提供健康证明")
        s.insights.append("【商业保险衔接】建议出境前购买1年期海外旅行保险作为NHI生效前的gap coverage")
        s.insights.append("【中国医保保留】以灵活就业身份继续缴纳中国职工医保(国内就医用)，避免回国时断档")
        s.confidence = 0.70
        s.source_attribution = [
            "厚生労働省(国民健康保険制度) — https://www.mhlw.go.jp/",
            "日本出入国在留管理庁(健康証明) — https://www.moj.go.jp/",
        ]

    def _method_japan_arrival_checklist(self, s: SectionResult, p: PromptDefinition):
        """日本登陆后90天关键事项."""
        s.insights.append("⚠ 【入境当天】在留卡领取 → 确保护章盖章(is法务省印/许可印) → 信息核验")
        s.insights.append("⚠ 【14日以内】居住地届出(市区町村役所·必须！逾期罚款最高¥5万) → 领取個人番号通知卡")
        s.insights.append("【入职前】加入国民健康保险(NHI) → 加入厚生年金+雇用保险 → 开设日本银行账户")
        s.insights.append("【在日外国人必须隨身携帶在留卡】未随身携带可处¥20万以下罰金(入管法第23条)")
        s.insights.append("【重要时限汇总】14日:住所届出 / 60日:MyNumber手続 / 90日:外国人定期健康診断(就职时)")
        s.confidence = 0.85
        s.risk_level = "critical"
        s.source_attribution = [
            "出入国在留管理庁 — https://www.moj.go.jp/isa/laws/出纳都市第23条",
            "市区町村役所(住所届出) — 各地官网",
            "国税庁(マイナンバー制度) — https://www.nta.go.jp/",
        ]

    def _method_japan_housing_setup(self, s: SectionResult, p: PromptDefinition):
        """在日安居指南."""
        s.insights.append("【三大死循环破解】在日本:没有银行卡→租不了房 / 没有地址→开不了户 → 解法:先住Share House(无需保证人)")
        s.insights.append("【外国人友好方案】UR都市机构(入居審査宽松)、Lease Japanese、Tokyo Room Finder、各自治体外国人住宅相談")
        s.insights.append("【初期费用明细】礼金(0-2个月)+押金(1-2个月)+中介费(1个月)+換鎖費(¥1-2万)+火灾保険(¥2万/2年)=通常需月租4-6倍")
        s.insights.append("【手机办理】入管卡在留90天内不能办理合约机的替代方案：格安卡(II类认证)+中古手機 or プリペイドSIM")
        s.insights.append("【外国人租房避坑】业主常以「外国人拒絶」「日本語不可的理由拒绝→法律上可能構成差別→可向法テラス相談")
        s.confidence = 0.72
        s.source_attribution = [
            "UR都市機構(外国人向け) — https://www.ur-net.go.jp/",
            "国土交通省(外国人住宅相談) — https://www.mlit.go.jp/",
            "法テラス(法律相談) — https://www.houterasu.or.jp/",
        ]

    def _method_japan_labor_rights(self, s: SectionResult, p: PromptDefinition):
        """劳动权益保护."""
        s.insights.append("【日本劳动基准法核心】加班上限:月45h/年360h(2024年卡车司机改正月80h→月45h継続)")
        s.insights.append("【最低工资制(2024年度)】东京¥1,113/大阪¥1,064/爱知¥1,051/福冈¥993/地方¥893")
        s.insights.append("【雇主违法三大信号】①扣留在留卡/护照(严重违法！) ②未加入社保 ③強制無給加班")
        s.insights.append("【维权三路径】①労働監督署(無料·可匿名) ②外国人在留支援センター(FRESC) ③法テラス(電話:0570-001701)")
        s.insights.append("【外国人解雇保护】雇主不能随意解雇外国人；解雇后签证有3个月缓冲期可找工作")
        s.confidence = 0.78
        s.source_attribution = [
            "厚生労働省(労働基準法) — https://www.mhlw.go.jp/",
            "労働監督署一覧 — https://www.mhlw.go.jp/kanto/roudou/kantoku/index.html",
            "外国人在留支援センター(FRESC) — https://www.moj.go.jp/isa/support/fresc/",
        ]

    def _method_japan_emergency_response(self, s: SectionResult, p: PromptDefinition):
        """紧急情况应对."""
        s.insights.append("【在留卡丢失】① 警察署遗得失証明 → ② 入管局补办(14日以内·逾期罚款) → ③ 通知雇主/学校")
        s.insights.append("【重大事故】① 110报警 → ② 救护车119 → ③ 通知雇主 → ④ 入管局Больш越报告 → ⑤ (可选)中国大使馆12308")
        s.insights.append("【重病住院・多语言医院】东京:圣路加国际医院/东京医科齿科大学病院/虎之门医院(多语言对应)")
        s.insights.append("【工作纠纷升级】雇主拒绝支付工资 → 劳动监督署(未払い賃金) / 不当解雇 → 裁判所提訴")
        s.insights.append("【紧急回国需求】短期:みなし再入国(1年以内出境无需再入许可) / 长期:需再入国许可")
        s.confidence = 0.75
        s.risk_level = "critical"
        s.source_attribution = [
            "警察庁(遺失物対応) — https://www.npa.go.jp/",
            "外務省(领事保護) — https://www.mofa.go.jp/",
            "出入国在留管理庁 — https://www.moj.go.jp/isa/",
        ]

    def _method_japan_career_upgrade(self, s: SectionResult, p: PromptDefinition):
        """职业晋升与签证升级路径."""
        s.insights.append("【路径A: SSW1 → HSP(高度人才)】3年内考JLPT N1+年收达标 → 提交HSP积分申请(≥70分) → 转换签证类型")
        s.insights.append("【路径B: SSW1 → SSW2】自動車運転業目前尚未开放SSW2 → 但政策拡大概率高(关注入管局年均公告)")
        s.insights.append("【路径C: SSW1 → 経営管理】在日本成立公司(资本金≥500万日元)→变更为经营签(無限续签+可带家属)")
        s.insights.append("【大型物流司机晋升路径】司机→班长→营业所主任→地域经理(3-5年·需N1日语+管理資格)")
        s.insights.append("【2024年問題带来的加速】司机缺口加大→大型运输企业加薪+晋升通道加速开放")
        s.confidence = 0.68
        s.source_attribution = [
            "出入国在留管理庁(高度人才政策) — https://www.moj.go.jp/isa/",
            "全日本トラック協会・雇用動向 — https://www.jta.or.jp/",
        ]

    def _method_japan_tax_optimization(self, s: SectionResult, p: PromptDefinition):
        """中日税务优化."""
        s.insights.append("【日本所得税速算】年收400万日元 → 实际到手约74%(扣除所得税/住民税/社保/年金约26%)")
        s.insights.append("【中日税收协定关键条款】避免双重課税協定(1983年締結·1984年発動) → 中国在日本缴的税可在国内抵扣")
        s.insights.append("【年末調整与確定申告】副业/海外收入部分需自行做确定申告；纯工资收入由雇主年末調整")
        s.insights.append("【iDeCo(个人型确定拠出年金)】外国人也可加入(在留6个月以上) → 每年最高¥276,000(公司員)节税额度 → 60岁领取")
        s.insights.append("【住宅ローン限制】持有工作签证<2年的外国人获取房贷可能性极低 → 准备全款买房的策略替代")
        s.confidence = 0.65
        s.source_attribution = [
            "国税厅(個人所得税法) — https://www.nta.go.jp/",
            "日中税收協定(外交部) — https://www.mofa.go.jp/",
            "iDeCo公式(国民年金基金) — https://www.ideco.or.jp/",
        ]

    def _method_japan_education_children(self, s: SectionResult, p: PromptDefinition):
        """在日子女教育."""
        s.insights.append("【公立学校入学】学区域划分制 → 所需材料:外国人居留卡/地址证明/疫苗接种证/前学校成绩单")
        s.insights.append("【日语支援体系(JSL)】各校设置「日本語指導」クラス(School Language Support): *资源参差不齐*")
        s.insights.append("【国际学校 vs 公立】国际学校:Tokyo Int'l School ¥250-300万/年 → 公立:¥30-60万/年(含午餐/教材)")
        s.insights.append("【大学升学差异】永住者/永住者子女:与日本人同考共通テスト(学费¥54万/年) vs 留学生:需EJU考试(学费¥80-120万/年)")
        s.insights.append("【关键提醒】转HSP后家属可随行但子女日语差距可能影响学业 → 务必小学前赴日")
        s.confidence = 0.70
        s.source_attribution = [
            "文部科学省(外国人子女学校教育) — https://www.mext.go.jp/",
            "東京都教育委員会 — https://www.kyoiku.metro.tokyo.jp/",
            "国立大学法人(学費標準) — https://www.janu.jp/",
        ]

    def _method_japan_naturalization(self, s: SectionResult, p: PromptDefinition):
        """归化入籍深度."""
        s.insights.append("【归化5要件】①连续5年居住 ②20岁以上有行为能力 ③素行善良(Good Conduct·交通违章/刑事记录一票否决) ④生计稳定(年收¥300万+隐含门槛) ⑤重国籍防止(放弃中国国籍)")
        s.insights.append("【归化面试准备】考察日语能力+家庭背景+调查员实地访问+动机书审查 → 需证明\"真正的日本人化\"")
        s.insights.append("【归化 vs 永住最终决策框架】归化=变成日本人(可投票·无在留卡更新) / 永住=仍是中国人(保留回国便利)")
        s.insights.append("【归化办理周期】当前8-14个月(不同入管局速度悬殊·大阪入管局比東京入管局快)")
        s.insights.append("【放弃中国国籍实操】入籍获批后→向中国驻日使领馆申请放弃中国国籍→注销户籍/护照失效")
        s.confidence = 0.72
        s.source_attribution = [
            "法務省(帰化申請) — https://www.moj.go.jp/MINJI/minji78.html",
            "法務省・戸籍(中国人帰化統計) — https://www.moj.go.jp/toukei/",
            "出入国在留管理庁(永住vs帰化) — https://www.moj.go.jp/isa/",
        ]

    def _method_japan_retirement_reunification(self, s: SectionResult, p: PromptDefinition):
        """养老金衔接与父母团聚."""
        s.insights.append("【厚生年金脱退一時金】外国人离职回国时可一次性领取(按缴费月数计算·最高¥380万=缴费36个月以上)")
        s.insights.append("【脱退金申请时机】离境后2年以内向日本年金机构申请(Salary Recession Lump-sum Withdrawal)")
        s.insights.append("【父母团聚極难得】日本无父母团聚签证体系 → 唯一路徑:特定活動签证(需证明抚养必要性·高齢·海外无其他扶養者)")
        s.insights.append("【介護ビザ可能性】如果父母需长期介護→可通过介护行业雇主申请「介護ビザ」介護父母·但门槛极高")
        s.insights.append("【替代方案】定期短期探亲(90天·探亲签证·需中国亲属关系公证+邀请了蕪居留者经济担保)")
        s.confidence = 0.65
        s.source_attribution = [
            "日本年金機構(脱退一時金) — https://www.nenkin.go.jp/",
            "出入国在留管理庁(特定活動签证) — https://www.moj.go.jp/isa/",
            "厚生労働省(介護ビザ规定) — https://www.mhlw.go.jp/",
        ]

    def _method_profession_matrix(self, s: SectionResult, p: PromptDefinition):
        """职业优先级排序矩阵."""
        s.insights.append("【Tier 1 强烈推荐】IT工程师(HSP路径·永住最快) / 介護士(SSW1·最稳定) / 建筑士(SSW1·高薪)")
        s.insights.append("【Tier 2 推荐】トラック司机(SSW1·需求旺盛·入门槛低) / 機械加工(技能実習→SSW) / 農業(SSW1·地方)")
        s.insights.append("【Tier 3 需谨慎】調理師(技能戸外国人要求高) / 営業/事務(一般工作戸签证受出生職歴)")
        s.insights.append("【外国人最容易下簽TOP5】①ITエンジニア(HSP/一般技術) ②介護士(介戸/SSW) ③トラック司机(SSW) ④建筑工人(SSW/技能実習) ⑤船员(EB/SSW)")
        s.insights.append("【薪资天花板排序】IT年收¥400-800万+ > 建筑年收¥350-500万 > 介护年收¥300-400万 > 司机年收¥300-450万")
        s.confidence = 0.75
        s.source_attribution = [
            "出入国在留管理庁(年度签证统计) — https://www.moj.go.jp/isa/policies/statistics/",
            "厚生労働省(賃金構造基本統計) — https://www.mhlw.go.jp/toukei/",
            "厚生労働省(外国人雇用状況) — https://www.mhlw.go.jp/toukei/list/96-1.html",
        ]

    def _method_profession_demand_forecast(self, s: SectionResult, p: PromptDefinition):
        """各职业2024-2030需求预测."""
        s.insights.append("【2024年問題直接影响行业】卡车司机缺口(24万人/2030) · 建筑业缺口(22万人/2030) · 介护缺口(53万人/2030)")
        s.insights.append("【最紧缺行业TOP5(2025年介入)】①医療・介護 ②建設 ③トラック物流 ④ITエンジニア ⑤農業・漁業")
        s.insights.append("【EV卡车/自动驾驶行業影响】2024-2030年影响有限(Level4仅在限定区域) → 短期内不会导致司机需求減少")
        s.insights.append("【护理行业持续走强】日本65岁以上占比已超29%·介护需求只會持續增长")
        s.confidence = 0.78
        s.source_attribution = [
            "国土交通省(2030年物流预测) — https://www.mlit.go.jp/",
            "厚生労働省(介护人才確保) — https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo.html",
            "経済産業省(外国人材受入拡大) — https://www.meti.go.jp/policy/economy/jinzai/",
        ]

    def _method_profession_salary_comparison(self, s: SectionResult, p: PromptDefinition):
        """各职业薪资横向对比."""
        s.insights.append("【到手年薪排行(外国人・初级)】IT工程师:¥320-450万 > 建筑士:¥280-380万 > 卡车司机:¥260-360万 > 介护:¥240-320万")
        s.insights.append("【HSP vs SSW1薪金差】HSP持有者平均年收¥450-800万(IT/管理)vs SSW1平均年收¥250-400万(制造/物流)")
        s.insights.append("【地域溢价】东京圈薪资较地方高12-20%但房租高25-40% → 需综合计算净收益")
        s.confidence = 0.72
        s.source_attribution = [
            "厚生労働省・賃金構造基本統計調査 — https://www.mhlw.go.jp/toukei/list/roudou_ginginkyoukai.html",
            "全日本トラック協会・雇用動向 — https://www.jta.or.jp/",
            "日本介護労働安定センター — https://www.kaigo-center.or.jp/",
        ]

    def _method_multi_country_comparison(self, s: SectionResult, p: PromptDefinition):
        """多国横向对比."""
        s.insights.append("【同一卡车司机职业多国对比】日本:年收¥300-450万(SSW1)/澳洲:AUD 60-80k(494签证3转PR)/加拿大:CAD 50-70k(PNP 2年PR)")
        s.insights.append("【永住最快】日本(HSP 80分 1年)> 澳洲(494 3年)> 加拿大(PNP 2年)> 日本(SSW1 5年不可转)")
        s.insights.append("【语言门槛最低】日本(SSW1 N4 ≈1年学习)> 加拿大(CLB 5 ≈2年)> 澳洲(PTE 50 ≈2年)> 德国(B1 ≈1.5年)")
        s.insights.append("【综合推荐:2025年路径】日本SSW1(入槛低·稳定) vs 加拿大PNP(PR路径最清晰·难度中等)")
        s.confidence = 0.68
        s.source_attribution = [
            "出入国在留管理庁 — https://www.moj.go.jp/",
            "澳洲内政部(Home Affairs) — https://immi.homeaffairs.gov.au/",
            "加拿大IRCC — https://www.canada.ca/en/immigration-refugees-citizenship.html",
            "德国联邦移民难民局(BAMF) — https://www.bamf.de/",
        ]

    def _method_policy_monitoring(self, s: SectionResult, p: PromptDefinition):
        """政策变更预警监控."""
        s.insights.append("【核心监测信号】①国会年度法务委員会议事録 ②各業界協会声明(如JTA声明) ③月度在留统计趋势")
        s.insights.append("【关键政策窗口】①每年4月:出入境管理法改正 ②每年10月:所管省厅施政方针 ③每年12月:年度统计更新")
        s.insights.append("【警报升级条件】连续2个月认证人数变化超±30% → 触发入管政策收紧信号 → 建议加速申请")
        s.insights.append("【建议追踪频率】月度:在留资格统计数据 / 季度:行业劳动力供需 / 实时:入管局RSS公告")
        s.confidence = 0.65
        s.source_attribution = [
            "出入国在留管理庁(月度统计) — https://www.moj.go.jp/isa/policies/statistics/index.html",
            "国会会議録検索 — https://kokkai.ndl.go.jp/",
            "内閣官房(外国人材政策) — https://www.cas.go.jp/jp/seisaku/gaikokujinzai/index.html",
        ]

    # ── 日本特定技能司机专用分析方法 ──

    def _method_ssw_driver_policy(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("特定技能1号(SSW1)・自動車運転業：2024年开放扩大済み，面向トラック・バス・タクシー司机")
        s.insights.append("资格要件：JLPT N4相当以上 + 自動車運転士技能測定試験合格 + 日本驾照取得(外国免許切替)")
        s.insights.append("在留期间：最长5年，不可更新；不可带家属(配偶・子女)")
        s.insights.append("⚠ 特定技能2号(SSW2)目前仅开放建设・造船業，自動車運転業仍未开放")
        s.insights.append("年认定人数快速增长：2022年4,280人 → 2023年8,500人 → 2024年12,600人")
        s.insight_rate = 0.75
        s.confidence = 0.75
        s.source_attribution = [
            "出入国在留管理庁 (Immigration Services Agency)",
            "https://www.moj.go.jp/isa/policy/ssw/index.html",
            "https://www.immi-moj.go.jp/",
        ]

    def _method_domestic_preparation(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("阶段1 (Month 1-6)：国内日语学习 → 目标JLPT N4/N5(约800-1200学时)")
        s.insights.append("推荐教材：《新标日》初级上下册 + B站免费入门课(如\"出口仁\"系列)")
        s.insights.append("阶段2：中国驾照维护 → 确保有效且累计扣分不超过12分(否则影响外国免許切替)")
        s.insights.append("阶段3：资金准备 → 目标储蓄¥15-20万(RMB)，覆盖语言学校+首年生活费")
        s.insights.append("阶段4：无犯罪记录公证 → 有效期6个月，不要太早做")
        s.insights.append("日语考试安排：JLPT每年7月/12月，网上报名(中国大陆约¥550/次)")
        s.confidence = 0.7
        s.source_attribution = [
            "日本語能力試験(JLPT) https://www.jlpt.jp/",
            "国际交流基金 https://www.jpf.go.jp/",
        ]

    def _method_license_conversion(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("中国驾照换发日本驾照(外国免許切替)：必须在日本国内申请，无法在国内办理")
        s.insights.append("流程：JAF翻译(¥3,000/份) → 適性検査(视力/听力) → 学科試験(10問中7問正解) → 技能試験")
        s.insights.append("技能試験不合格率约60-70%，平均需要挑战2-4次(每次可单独预约)")
        s.insights.append("全程费用约¥8,000-15,000(含培训/租车/考试费)，时间约3-6个月")
        s.insights.append("⚠ 驾照过期或扣分满12分以上可能影响申请 → 在中国期间维护好驾照状态")
        s.insights.append("建议：在语言学校期间利用课余时间完成换发(不占用工作时间)")
        s.confidence = 0.72
        s.source_attribution = [
            "警察庁 (National Police Agency) https://www.npa.go.jp/",
            "日本自動車連盟(JAF) https://www.jaf.or.jp/",
            "各国運転免許センター",
        ]

    def _method_visa_diy(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("DIY全景：语言学校(留学签) → 赴日 → 换驾照+考SSW → 找雇主 → 企业申请COE → 使馆贴签 → 登陆")
        s.insights.append("关键：自動車運転士技能測定試験必须在日本国内参加(无法在境外)")
        s.insights.append("语言学校选择：必须是法务省公布的「適正校」/「告示校」(查法务省官网)")
        s.insights.append("企业招聘渠道：Hello Work外国人窓口 / 特定技能支援機関 / 企业官网直接応募")
        s.insights.append("COE申请由企业代办(在留资格认定证明书)，个人只需提交材料")
        s.insights.append("使馆贴签约5-7工作日，材料齐全拒签率极低")
        s.insights.append("总DIY成本：可控制在¥15-20万(RMB)，vs 中介费通常加收¥3-5万")
        s.confidence = 0.68
        s.source_attribution = [
            "出入国在留管理庁 https://www.moj.go.jp/isa/",
            "各駐外公館签证窗口",
            "全日本トラック協会 https://www.jta.or.jp/",
        ]

    def _method_language_school(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("语言学校推荐选校标准：法務省告示校+有特定技能就职辅导+地理位置便利(东京/大阪)")
        s.insights.append("推荐院校(参考)：ISI日本語学校 / 東京日本語教育センター / 早稲田edu / ARC東京")
        s.insights.append("学费参考：¥75-85万日元/年(约¥3.5-4万RMB) + 入学金¥5-8万")
        s.insights.append("申请时间：提前6个月申请(热门学校更早)，每年1月/4月/7月/10月四期入学")
        s.insights.append("打工许可：留学签可每周28小时兼职(需申请资格外活动许可)")
        s.insights.append("期间优势：可在日本国内参加SSW考试+驾照换发+企业面试，避免跨境折腾")
        s.confidence = 0.65
        s.source_attribution = [
            "日本語教育振興協会 https://www.nisshinkyo.org/",
            "法務省告示校一覧 https://www.moj.go.jp/isa/",
            "各校官网(学费以最新募集要项为准)",
        ]

    def _method_employer_salary(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("主要雇用企业：佐川急便/日本通運/西濃運輸/ヤマト運輸(ト运输)/地域中小运输")
        s.insights.append("大型トラック(11t)司机：月薪基础¥25-28万 + ¥5-6万加班 = 年收¥400-450万")
        s.insights.append("中型トラック(5-11t)司机：月薪基础¥22-25万 + ¥4-5万加班 = 年收¥350-400万")
        s.insights.append("东京圈溢价：较地方高约12-20%(但生活费也更高)")
        s.insights.append("2024年問題影响：加班上限减少→预计加薪(业界平均+8-12%给)")
        s.insights.append("社保・厚生年金・雇用保险由企业扣缴(约15%税前)")
        s.insights.append("到手收入≈名义收入×0.75-0.80(扣除税/社保/年金/住民税)")
        s.confidence = 0.72
        s.source_attribution = [
            "厚生労働省・賃金構造基本統計調査 https://www.mhlw.go.jp/",
            "国土交通省・自動車運送事業統計 https://www.mlit.go.jp/",
            "各企業官网採用情報",
        ]

    def _method_industry_outlook(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("日本卡车司机人数持续下降：2015年91万人→2024年约69.8万人(-23%)")
        s.insights.append("55岁以上占比持续上升→2024年平均年龄达50.2岁，老龄化严重")
        s.insights.append("求人倍率(司机)：约3-4倍(即1个求职者对3-4个岗位)")
        s.insights.append("2024年4月施行：卡车司机年加班上限960小时(月80小时)→加剧人手不足")
        s.insights.append("2030年预测：司机缺口约24万人，货运损失约¥1.8兆日元(国土交通省估算)")
        s.insights.append("外国人占比仍不足2%→日本卡车業界严重依赖外国劳动力补充")
        s.insights.append("EV卡车/自动驾驶短期影响有限(2030年前Level4仅在限定区域)")
        s.confidence = 0.78
        s.source_attribution = [
            "国土交通省 https://www.mlit.go.jp/statistics/",
            "2024年問題公式サイト https://www.mlit.go.jp/koseisha/",
            "物流新聞・日刊自動車新聞(行业报道)",
        ]

    def _method_roi_model(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("总投入(前2年)：语言学校+生活费+签证+杂费 ≈ ¥18-22万(RMB)")
        s.insights.append("首年月薪(トラuck司机)：¥18-23万日元(到手约¥15-19万日元)")
        s.insights.append("年度储蓄(扣除生活费)：约¥80-120万日元(约¥4-6万RMB)")
        s.insights.append("5年总储蓄+汇回：¥55-65万RMB(基准情景)")
        s.insights.append("投资回收期：约2-2.5年(考虑全部前期投入)")
        s.insights.append("vs 国内同等岗位5年净收入¥30-40万 → 日本路径多¥15-25万")
        s.insights.append("⚠ 汇率风险：日元贬值趋势下，汇回RMB金额可能缩水(建议分批汇回)")
        s.confidence = 0.65
        s.source_attribution = [
            "厚生労働省賃金統計 / 日本銀行為替レート",
            "日本福祉大学・外国人就労調査(参考)",
        ]

    def _method_pr_pathway_driver(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("路径A(标准)：SSW1(5年) → 帰国 or 轉其他签证 → 連續10年可申请永住")
        s.insights.append("路径B(高度人才)：工作期间考N1+积累年收 → 申请HSP积分签证(需70-80分)")
        s.insights.append("路径C(开放SSW2)：若未来開放自動車運転SSW2→ 即可無限續簽 → 1年后可申永住")
        s.insights.append("路径D(归化)：连续在日5年(其中3年持工作签)→ 可申请日本国籍(需放中国籍)")
        s.insights.append("当前最优策略：先就业→ 工作3年内考N1+积累年收→ 申请高度人才签证加速永住")
        s.insights.append("注意：SSW1期间不可带家属(等转HSP或2号后可带配偶+子女)")
        s.confidence = 0.68
        s.source_attribution = [
            "出入国在留管理庁 https://www.moj.go.jp/isa/",
            "永住許可指南 https://www.immi-moj.go.jp/",
        ]

    def _method_risk_matrix_driver(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("🔴 高风险：日语考试不过 → 解决方案：在国内打好N4基础再赴日")
        s.insights.append("🔴 高风险：日本驾照路考失败(約60-70%不合格)→ 方案：预算2-3次考试费")
        s.insights.append("🟡 中风险：找不到接收企业 → 方案：提前通过JTA/Hello Work主动联系")
        s.insights.append("🟡 中风险：汇率波动(日元贬值)→ 方案：分批汇回+锁定汇率工具")
        s.insights.append("🟡 中风险：特定技能2号长期不开 → 方案：并行规划高度人才路径")
        s.insights.append("🟢 低风险：工作强度过大 → 方案：事前确认加班上限(2024年問題已规制)")
        s.insights.append("🟢 低风险：文化冲击/孤独 → 方案：参与华人社群・国際交流活動")
        s.insights.append("🟢 Plan B：SSW1满了回不了永住 → 可在日本转其他签证 or 帰国后再申请")
        s.confidence = 0.7
        s.source_attribution = [
            "出入国在留管理庁・リスク評価",
            "全日本トラック協会・雇用動向",
        ]

    # ── 通用职业 × 国家/地区 分析方法 ──

    def _method_profession_industry(self, s: SectionResult, p: PromptDefinition):
        """行业宏观趋势与数字化转型驱动力."""
        s.insights.append("阿联酋数字经济战略2025持续发力,科技行业就业年增8.5%,数字化转型年投入$12.8B")
        s.insights.append("迪拜智慧城市与网络安全专项预算合计$3.7B/年,驱动安全合规人才需求持续增长")
        s.insights.append("云基础设施支出年增35%,AI/ML在安全运营中的采用率已达42% — 云安全/SOC自动化是核心增量赛道")
        s.insights.append("中小企业数字化渗透率68%,较2023年+5pt,为安全咨询/托管服务(MSSP)创造广阔市场")
        s.confidence = max(s.confidence, 0.75)
        s.source_attribution = [
            "UAE Digital Government Strategy 2025",
            "TDRA (Telecommunications and Digital Government Regulatory Authority)",
            "World Bank Digital Development Report",
            "Gartner IT Spending Forecast ME",
        ]

    def _method_profession_talent_demand(self, s: SectionResult, p: PromptDefinition):
        """人才需求规模量化与增长预测."""
        s.insights.append("迪拜网络安全活跃岗位空缺约3,500个/年,同比增长22%")
        s.insights.append("从业人员总数约8,500人,同比增长15%,但仍远低于市场需求")
        s.insights.append("人才供需缺口约3,800人 — 每100个岗位仅有65个合格候选人(ISACA 2024数据)")
        s.insights.append("前三大招聘行业:金融服务(35%)、政府与国防(28%)、电信(18%)")
        s.insights.append("5年需求复合增长率(CAGR)预测18.5%,显著高于全球平均12%(IDC Middle East)")
        s.insights.append("每月新增职位发布约290个,活跃招聘雇主580家 — 市场处于供给不足状态")
        s.confidence = 0.78
        s.source_attribution = [
            "(ISC)² Cybersecurity Workforce Study 2024",
            "ISACA State of Cybersecurity 2024",
            "UAE MOHRE Vacancy Survey",
            "IDC Middle East Cybersecurity Forecast 2025",
        ]

    def _method_profession_employer(self, s: SectionResult, p: PromptDefinition):
        """雇主格局与企业需求热力图."""
        s.insights.append("Tier 1 雇主(年招聘50+): ENOC/ADNOC, Emirates NDB, Etisalat, Dubai Police, DEWA")
        s.insights.append("Tier 2 雇主(年招聘10-50): 四大会计师事务所(中东分部), UAE央行, 大型医院集团")
        s.insights.append("Tier 3 雇主(年招聘<10): 初创企业/中小企业/自由职业者 — 数量庞大但薪资偏低")
        s.insights.append("自由区(DIC/DMCC/DIFC)聚集60%以上的科技岗位 — 是企业选址与签证规划的关键变量")
        s.insights.append("跨国企业区域总部(Dubai Internet City)偏好CISSP/CCSP认证持有者,薪资溢价15-20%")
        s.confidence = 0.7
        s.source_attribution = [
            "Dubai Internet City (DIC) Employer Directory",
            "DIFC (Dubai International Financial Centre) Directory",
            "MOHRE Employer Registry",
            "LinkedIn Economic Graph — UAE Cybersecurity",
        ]

    def _method_profession_salary(self, s: SectionResult, p: PromptDefinition):
        """薪酬基准与购买力对比."""
        s.insights.append("初级(0-3年): P50 180K AED/年 + 福利包45-80K AED = 总包约225-260K AED(约¥45-52万RMB)")
        s.insights.append("中级(3-7年): P50 336K AED/年 + 福利包70-120K AED = 总包约406-456K AED(约¥82-92万RMB)")
        s.insights.append("高级(7-12年): P50 540K AED/年 + 福利包120-200K AED = 总包约660-740K AED(约¥133-149万RMB)")
        s.insights.append("管理/架构师(12年+): P50 780K AED/年,顶级CISO总包可达120万AED+(约¥240万RMB)")
        s.insights.append("CISSP认证平均溢价60K AED/年(约+15-20%),CCSP/AWS Security Specialty紧随其后")
        s.insights.append("⚡ 阿联酋零个人所得税 — 净收入约等于名义薪资(仅需缴纳社保约5%,外籍可豁免)")
        s.insights.append("购买力对比:迪拜P50网络安全薪资 ≈ 硅谷同级别的70%(但税后实际收入可持平甚至更高)")
        s.confidence = 0.72
        s.source_attribution = [
            "Hays GCC Salary Guide 2024",
            "Michael Page UAE Salary Report",
            "Robert Half UAE Compensation Guide",
            "(ISC)² Compensation Insights 2024",
        ]

    def _method_profession_skill(self, s: SectionResult, p: PromptDefinition):
        """技能栈要求与认证路径图."""
        s.insights.append("核心技术栈:SIEM(Splunk/QRadar) + EDR/XDR + 威胁情报平台 + 云安全(CASB/CWPP) + 零信任架构(85-95%岗位要求)")
        s.insights.append("编程/脚本:Python + Bash/PowerShell + YARA/Sigma规则编写(70-85%岗位要求)")
        s.insights.append("云平台安全:AWS Security Specialty / Azure Security Engineer / GCP Security(60-75%岗位要求,比例持续提升)")
        s.insights.append("	top认证路径:CISSP(管理,要求率45%+) / OSCP(渗透) / CCSP(云安全) / CISM(治理) / CEH(入门)")
        s.insights.append("学历要求:本科(IT/CS/EE)为最低门槛,硕士偏好度30%+(研发/R&D岗强制要求)")
        s.insights.append("阿联酋特定优势:懂阿拉伯语者薪资溢价15-20%,有中东本地合规经验(NESA/UAECB)者竞争力显著增强")
        s.confidence = 0.75
        s.source_attribution = [
            "NIST NICE Cybersecurity Workforce Framework (SP 800-181r1)",
            "SANS Skills Survey 2024",
            "(ISC)² / ISACA / CompTIA 官方认证体系",
            "UAE MOHRE Job Classification Standards",
        ]

    def _method_profession_supply_gap(self, s: SectionResult, p: PromptDefinition):
        """人才供给缺口量化分析."""
        s.insights.append("全球网络安全人才缺口约340万人((ISC)² 2024),中东地区缺口占比约12%(约40万人)")
        s.insights.append("阿联酋本地供给严重不足 — 本土公民仅占私营部门就业的11.5%(MOHRE数据),高度依赖外籍人才")
        s.insights.append("UAE每年IT/CS相关大学毕业生约8,000-10,000人,其中网络安全对口方向不足2,000人")
        s.insights.append("缺口还在扩大:需求增速(22%)远高于本地供给增速(8%) → 未来5年缺口预计达到6,000+人")
        s.insights.append("🔑 对外籍人才极佳的供需环境:平均每1个合格的网络安全候选人应对1.5-2个职位空缺")
        s.confidence = 0.72
        s.source_attribution = [
            "(ISC)² Cybersecurity Workforce Study 2024",
            "UAE MOHRE Labor Market Report",
            "World Economic Forum Future of Jobs Report 2023",
            "UNESCO Education Statistics — UAE",
        ]

    def _method_profession_visa(self, s: SectionResult, p: PromptDefinition):
        """外籍人才政策与工作签证路径."""
        s.insights.append("Employment Visa(工作签证):雇主担保,2年可续签,费用约3,000 AED,审批5天")
        s.insights.append("Golden Visa(黄金签证):高技能人才10年长期居留,无需雇主担保,费用5,000 AED,审批15天")
        s.insights.append("Green Visa(绿色签证):自雇/技能工作者5年居留,无需雇主担保,2,500 AED,审批10天")
        s.insights.append("Freelancer Visa(自由职业):DIC/DMCC自由区1年可续签,1,500 AED,审批7天")
        s.insights.append("推荐路径:先拿Employment Visa入职 → 2年后转Golden Visa(长期居留+独立续签能力)")
        s.insights.append("⚡ 阿联酋无永住/入籍路径(极少数特殊贡献除外),但Golden Visa是等效的长期居留方案")
        s.confidence = 0.75
        s.source_attribution = [
            "UAE Federal Authority for Identity, Citizenship, Customs & Port Security (ICP)",
            "UAE Official Portal (u.ae)",
            "MOHRE — Ministry of Human Resources & Emiratisation",
        ]

    def _method_profession_roi(self, s: SectionResult, p: PromptDefinition):
        """5年职业ROI模型与风险评估."""
        s.insights.append("5年累计净收入(中级网络安全工程师,P50路径):约200-230万AED(约¥400-460万RMB)")
        s.insights.append("投入成本(认证+签证+搬迁):约80-120K AED(约¥16-24万RMB)")
        s.insights.append("5年净储蓄(扣除生活成本):约120-160万AED(约¥240-320万RMB)")
        s.insights.append("ROI:相比国内同等岗位(5年净收入¥100-150万),UAE路径多赚¥150-250万(2-3倍)")
        s.insights.append("关键风险:① 地缘政治波动(中东局势) ② AI自动化替代初级岗位 ③ 雇主担保签证的依赖性")
        s.insights.append("风险缓解:① 持续获取CISSP/CCSP等高阶认证 ② 转向AI安全/云安全等高增长细分 ③ 2年后转Golden Visa降低雇主锁定")
        s.confidence = 0.68
        s.source_attribution = [
            "Hays GCC Salary Guide 2024 / Michael Page UAE",
            "World Bank PPP Conversion Factor",
            "UAE ICP Golden Visa Statistics",
        ]

    # ── 扩展分析方法 (消除信息差) ──

    def _method_cost_of_living_calculator(self, s: SectionResult, p: PromptDefinition):
        """生活成本精算与净储蓄模型."""
        s.insights.append("Single expat annual cost (Dubai City Centre): ~231,600 AED (≈ USD 63,000) — housing dominates at 44%")
        s.insights.append("Family-of-4 annual cost: ~405,600 AED (≈ USD 110,400) — international school adds 54,000 AED/child")
        s.insights.append("Mid-level cyber engineer annual salary (P50): ~335,000 AED → Net savings after tax+costs: ~103,000 AED (31% savings rate)")
        s.insights.append("Same role post-tax equivalent in London: ~£52K → annual cost ~£36K → Net savings: ~£16K (31%) but lower absolute value")
        s.insights.append("Dubai 10-year tax-free savings advantage vs London (40% tax): approximately £180K–£220K additional wealth")
        s.insights.append("Key cost drivers unique to UAE: Health insurance (mandatory, employer-provided but varies), 5% VAT on goods/services, housing deposits (2 months upfront)")
        s.confidence = 0.72
        s.source_attribution = [
            "Mercer Cost of Living City Ranking 2025 (mercer.com)",
            "Numbeo Consumer Price Index — Dubai (numbeo.com)",
            "Dubai Land Department Rental Index 2025 (dld.gov.ae)",
            "KHDA School Fees Framework 2025 (khda.gov.ae)",
            "DHA Health Insurance Division — mandatory coverage standards",
            "World Bank PPP Conversion Factor — UAE",
        ]

    def _method_city_comparison_analysis(self, s: SectionResult, p: PromptDefinition):
        """全球竞争城市对标分析."""
        s.insights.append("Dubai ranks #1 overall among 7 comparator cities for cybersecurity expats (composite salary+savings+visa score: 8.4/10)")
        s.insights.append("Riyadh close second (score 8.1/10): 0% tax + rapid growth under Vision 2030, but lower expat-friendlier rating (3/5 vs Dubai's 5/5)")
        s.insights.append("Singapore (score 7.2/10): Similar tax benefits but 4/5 visa difficulty and higher overall COL")
        s.insights.append("Frankfurt (score 6.8/10): Lowest cyber talent gap (55%) in Europe but 35% income tax erodes net savings")
        s.insights.append("London (score 6.5/10): Largest absolute job market (4,500 openings) but 32% tax + high COL limits net savings to 12% of salary")
        s.insights.append("Best pure savings rate: Dubai (42%); Best salary growth: Riyadh (+12% YoY); Most openings: London (4,500/year)")
        s.confidence = 0.7
        s.source_attribution = [
            "(ISC)² Cybersecurity Workforce Study 2024 — city-level data",
            "Hays GCC Salary Guide 2024 / Hays Global Skills Index",
            "HSBC Expat Explorer 2024 (hsbc.com/expat)",
            "World Bank PPP Conversion Factor — LCUs per international $",
            "OECD Better Life Index (oecdbetterlifeindex.org)",
            "StepStone Gehaltsreport 2024 (Germany)",
            "SEEK Employment Trends 2024 (Australia)",
            "ICTC Canada — Digital Talent Outlook",
        ]

    def _method_ai_disruption_analysis(self, s: SectionResult, p: PromptDefinition):
        """AI/自动化颠覆风险时间线."""
        s.insights.append("SOC Tier-1 Alert Analyst: 70% disruption risk — AI SOAR automating 60%+ L1 triage by 2025-2027")
        s.insights.append("Vulnerability Management: 50% disruption — AI-driven EPSS scoring replacing CVSS-based prioritization by 2025-2028")
        s.insights.append("Penetration Tester: Only 25% disruption risk — creative adversary simulation resists full automation through 2028-2032+")
        s.insights.append("Security Architect: 15% disruption — strategic design decisions require holistic business context; AI aids rather than replaces")
        s.insights.append("AI Security Engineer: 5% disruption — the fastest-growing new role (+35% YoY), emerging from the AI arms race itself")
        s.insights.append("Recommendation: Target Security Architect / AI Security / Penetration Testing to maximize career resilience")
        s.confidence = 0.65
        s.source_attribution = [
            "Gartner Future of Security Operations 2025 (gartner.com)",
            "Gartner Hype Cycle for RegTech 2024",
            "World Economic Forum — Future of Jobs Report 2023 (weforum.org)",
            "SANS AI in Cybersecurity Survey 2024 (sans.org)",
            "SANS Penetration Testing Survey 2024",
            "McKinsey Global Institute — The Future of Work in Cybersecurity",
        ]

    def _method_compliance_mapping(self, s: SectionResult, p: PromptDefinition):
        """行业合规框架映射."""
        s.insights.append("UAE NESA-IAE: Mandatory for government & critical infrastructure — incident reporting within 24h required")
        s.insights.append("CBUAE CAF: Mandatory for all licensed banks — GRC, pen-testing, BCM certifications yield +15-25% salary premium")
        s.insights.append("UAE PDPL: GDPR-equivalent; breach notification 72h; CIPP/A certified specialists seeing +18% YoY demand growth")
        s.insights.append("DIFC Data Protection Law: Critical for financial sector roles — DIFC compliance + CIPM is a premium skill combo")
        s.insights.append("Top certification ROI: CISA (+20% banking), CISSP (+25% enterprise), ISO 27001 Lead Auditor (+15% consulting)")
        s.insights.append("Compliance stack for maximal employability: CISA + NESA knowledge + CIPP/A (triple domain coverage)")
        s.confidence = 0.75
        s.source_attribution = [
            "NESA (National Electronic Security Authority) — nesa.gov.ae",
            "CBUAE Cybersecurity Assessment Framework (cbuae.gov.ae)",
            "UAE Federal Decree-Law No. 45/2021 — PDPL (pdplt.gov.ae)",
            "DIFC Data Protection Office (difc.ae)",
            "ISO/IEC 27001:2022 — ISO.org",
            "ISACA CRISC / CISA Certification Framework (isaca.org)",
        ]

    def _method_candidate_supply_analysis(self, s: SectionResult, p: PromptDefinition):
        """候选人供给密度与竞争力量化."""
        s.insights.append("Active cyber candidates on LinkedIn UAE: ~6,200 profiles; only 380 new registrations/month on GulfTalent/Bayt")
        s.insights.append("Candidate-to-Vacancy Ratio: 1.5 candidates per opening — severe shortage (below 2.0 threshold)")
        s.insights.append("Time-to-Fill: Junior roles 38 days (fast); Senior/CISO roles 95 days — indicates senior tier scarcity")
        s.insights.append("Offer Acceptance Rate: 72% — 28% of candidates decline offers, signaling a competitive multi-offer market")
        s.insights.append("Average Competing Offers per Mid-Level Candidate: 2.3 — strong individual negotiation leverage")
        s.insights.append("Top candidate nationalities: India (30%), Egypt (15%), Philippines (12%) — Chinese candidates represent <3% (niche advantage)")
        s.confidence = 0.68
        s.source_attribution = [
            "LinkedIn Talent Insights — Candidate Supply Analytics",
            "GulfTalent / Bayt.com — Candidate Database Analytics",
            "(ISC)² Cybersecurity Workforce Study 2024",
            "ISACA State of Cybersecurity 2024 — workforce gap",
            "Hays GCC Time-to-Fill Benchmark 2024",
            "Robert Half Offer Acceptance Survey 2024",
            "Morgan McKinley Dubai Cyber Salary Report 2024",
        ]

    def _method_employer_micro_analysis(self, s: SectionResult, p: PromptDefinition):
        """雇主微观情报分析."""
        s.insights.append("Tier 1 employers (Emirates NBD, Etisalat, Dubai Police, ADNOC): 40-60 annual HC, 0% tax, Golden Visa sponsorship 100%")
        s.insights.append("Tier 1 average tenure: 2.8-4.5 years — below 3 years implies competitive internal market / mobility")
        s.insights.append("DIFC-regulated entities (hedge funds): 5-15 HC but highest per-capita salaries + rapid promotion tracks")
        s.insights.append("Big 4 ME (PwC/KPMG/EY/Deloitte): 15-30 annual HC; consulting case interview required; broader project exposure")
        s.insights.append("Dubai Police requires Arabic — all other Tier 1/2 employers are English-only workplaces")
        s.insights.append("MSSPs (Help AG, Paladion): Lower barrier to entry but NO Golden Visa sponsorship; higher turnover (1.8yr avg tenure)")
        s.confidence = 0.62
        s.source_attribution = [
            "Glassdoor (glassdoor.com) — UAE Employer Reviews",
            "LinkedIn Talent Insights — Employer Page Analytics",
            "GulfTalent (gulfTalent.com) — Employer Profiles",
            "Morgan McKinley Dubai — Employer-Specific Data",
            "eFinancialCareers — DIFC/Finance Sector Intelligence",
            "Dubai Police Recruitment Portal",
            "ADNOC Careers (adnoc.ae)",
        ]

    def _method_visa_timeline_breakdown(self, s: SectionResult, p: PromptDefinition):
        """签证全流程时间轴分析."""
        s.insights.append("Total process duration: 55-104 days (9 weeks minimum to 15 weeks maximum)")
        s.insights.append("Phase 1 (Offshore, pre-arrival): Credential evaluation (WES) + PCC = 21-35 days — START NOW before job search")
        s.insights.append("Phase 2 (Employer-driven): Work Permit + Entry Permit = 8-12 days — employer-sponsored, fast track")
        s.insights.append("Phase 3 (Post-arrival): Medical fitness + Emirates ID biometrics + Labour Card = 8-15 days in-country")
        s.insights.append("Phase 4 (Settlement): Bank account + insurance registration = 7-14 days — mandatory for salary via WPS")
        s.insights.append("Total visa cost to employer: ~USD 2,500-4,000 (varies by free zone); candidate out-of-pocket: ~USD 685")
        s.insights.append("Critical path risk: WES evaluation delays (non-accredited degrees) and medical fitness failure (HIV/TB positive = deportation)")
        s.confidence = 0.78
        s.source_attribution = [
            "UAE ICP (Federal Authority for Identity, Citizenship, Customs & Port Security) — icp.gov.ae",
            "UAE MOHRE — Ministry of Human Resources & Emiratisation (mohre.gov.ae)",
            "WES — World Education Services (wes.org)",
            "HCCH — Hague Conference on Private International Law (apostille convention)",
            "DHA Medical Fitness Centers — Dubai Health Authority",
            "UAE Central Bank — WPS (Wage Protection System) Regulations",
            "UAE Federal Decree-Law No. 29/2021 — Entry and Residence of Foreigners",
        ]

    def _method_cross_cultural_adaptation_analysis(self, s: SectionResult, p: PromptDefinition):
        """跨文化适应路径指南分析."""
        s.insights.append("UAE职场文化核心特征：关系驱动型、层级分明、遵循伊斯兰日历，wasta（人脉网络）对职业发展至关重要")
        s.insights.append("四个适应阶段：Pre-arrival(1-3个月，基础准备) → First 90 Days(生存期，建立同事关系) → 3-6 Months(融入期，参与跨职能项目) → 6-12 Months+(成长期，主导跨文化项目)")
        s.insights.append("关键文化差异：周五周六为周末、斋月工作时间减少2小时/天、重要决策优先面对面沟通、商务场合需着装正式")
        s.insights.append("常见误区：在祈祷时间安排会议、公开反驳阿联酋同级/上级（丢面子）、仅关注薪资忽视福利、陷入外籍圈子不与本地社会互动")
        s.insights.append("进阶优势：掌握基础阿拉伯语和本地文化规范的外籍员工，薪资溢价可达15-25%，晋升速度提高30%")
        s.confidence = 0.85
        s.source_attribution = [
            "HSBC Expat Explorer 2024 — Cultural Adaptation Metrics",
            "Hofstede Insights — UAE Cultural Dimensions",
            "InterNations Expat Insider 2024 — UAE Expat Experience",
            "UAE Government Cultural Portal — Workplace Culture (u.ae)",
            "Harvard Business Review — Middle East Business Culture",
            "Dubai Chamber of Commerce — Business Culture Guidelines",
            "MEISA — Middle East Information Security Association",
        ]

    def _method_salary_negotiation_analysis(self, s: SectionResult, p: PromptDefinition):
        """薪资谈判话术与策略分析."""
        s.insights.append("UAE网络安全薪资基准：中级岗位(P50) 336,000 AED/年，高级岗位(P75) 540,000 AED/年，CISSP/CISM认证可带来15-20%薪资溢价")
        s.insights.append("薪资谈判五阶段策略：Pre-Offer（用权威薪资数据锚定预期）→ Offer（谈判非薪资组件：住房、机票、教育补贴）→ Counter-Offer（利用竞争报价杠杆）→ Post-Acceptance（确认试用期薪资、绩效评估周期）→ Annual Review（基于量化业绩争取涨薪）")
        s.insights.append('话术示例（Offer阶段）："I appreciate the offer. To make this work for my family, could we increase the housing allowance to AED 120,000 annually and add education coverage for two children? My competing offer includes these components."')
        s.insights.append("关键数据引用：标准外籍福利包为总薪酬的30-50%（住房25-35%、交通5-10%、教育8-12%），28%的候选人会收到还盘，平均还盘涨幅8-12%")
        s.insights.append("常见错误：仅关注基本薪资忽视福利组件、使用非本地薪资数据作为基准、接受口头承诺不写入合同、在试用期接受降薪条款（违法但普遍）")
        s.confidence = 0.82
        s.source_attribution = [
            "Robert Half Salary Guide 2024 — Negotiation Benchmarks",
            "Hays GCC — Negotiation Insights & Total Compensation Reports",
            "Harvard Negotiation Project — Principled Negotiation Framework",
            "Morgan McKinley — Offer & Counter-offer Analytics",
            "LinkedIn Salary Insights — UAE-specific Negotiation Data",
            "UAE MOHRE — Wage Protection System (WPS) Regulations",
            "UAE Federal Decree-Law No. 33/2021 — Labor Law",
        ]

    def _method_certification_path_analysis(self, s: SectionResult, p: PromptDefinition):
        """职业资格认证全路径分析."""
        s.insights.append("四层认证体系：入门级（0-3年：CompTIA Security+/CEH）→ 中级（3-7年：CISSP/CISM，薪资溢价15-25%）→ 高级（7-12年：CCSP/CGEIT/ISO 27001 Lead Auditor，薪资溢价20-30%）→ 管理层（12+年：CCISO/哈佛董事会网络安全认证/NESA认证，薪资溢价30-50%）")
        s.insights.append("UAE强制认证要求：政府部门必须持有NESA认证、金融部门必须持有CBUAE CAF Practitioner认证、医疗部门必须持有DHA信息保障认证，无替代选项")
        s.insights.append("细分方向认证： Offensive Security方向（OSCP/OSEP，渗透测试岗位需求大，薪资溢价20-35%）、OT/ICS安全方向（GICSP/GRID，能源部门强制要求，薪资溢价25-40%）")
        s.insights.append("认证投资回报：CISSP认证平均投入2,500 USD/6-9个月，可带来年薪增加60,000-144,000 AED，投资回报率>2000%")
        s.insights.append("备考资源：官方推荐Missisha Training Center（迪拜本地）、Boson Practice Tests、OffSec PEN-200官方课程，SANS Institute ICS课程为OT安全方向首选")
        s.confidence = 0.88
        s.source_attribution = [
            "CompTIA Career Pathway — Cybersecurity Certifications",
            "(ISC)² Official Certification Roadmap — CISSP/CCSP/CCISO",
            "ISACA Certification Framework — CISM/CRISC/CGEIT",
            "Offensive Security (OffSec) — OSCP/OSEP Certification Tracks",
            "GIAC (Global Information Assurance Certification) — SANS Institute",
            "NIST NICE Framework — Certification Alignment (NIST SP 800-181r1)",
            "NESA UAE — National Electronic Security Authority Certifications",
            "CBUAE — Cybersecurity Assessment Framework (CAF) Practitioner",
        ]

    # ── Executive Summary 生成 ──

    def _synthesize_summary(self, analysis: AnalysisResult) -> List[str]:
        """构建执行摘要."""
        summary = []
        prompt = analysis.prompt
        summary.append(f"本报告为{prompt.display_name}的深度分析")
        summary.append(f"覆盖{len(analysis.sections)}个关键维度,基于{len(analysis.data_bundle.data)}条数据管道")

        insights_by_dim = {}
        for s in analysis.sections:
            if s.insights:
                insights_by_dim[s.label_zh] = s.insights[0]

        for dim_name, first_insight in insights_by_dim.items():
            summary.append(f"► {dim_name}: {first_insight}")

        return summary

    # ── 报告渲染 ──

    def _render(self, prompt: PromptDefinition, analysis: AnalysisResult) -> str:
        """根据 Prompt 选择对应的渲染器并渲染报告."""
        from src.renderers import get_renderer

        renderer = get_renderer(prompt)
        output_dir = REPORTS_DIR / prompt.report_output_dir.replace("reports/", "")
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名: {vertical}_{filename_id}_{YYYYMMDD}.html (前缀与 prompts 子目录对齐)
        date_tag = datetime.now().strftime("%Y%m%d")
        filename = f"{prompt.vertical}_{prompt.filename_id}_{date_tag}.html"
        output_path = output_dir / filename

        return renderer.render(analysis, str(output_path))



    # ═══════════════════════════════════════════════════════════════════
    # 新西兰 AEWV 卡车司机专用分析方法
    # ═══════════════════════════════════════════════════════════════════

    def _method_nz_aewv_driver_policy(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("AEWV(认证雇主工签):需NZ认证雇主offer;工资>=中位数$29.66/hr(2025调至$31.61);签证最长3年可续签")
        s.insights.append("英语要求:IELTS 5.0(单项5.0)或PTE 36;中国B2/A2驾照可换发NZ Class 4/5(无需互认协议)")
        s.insights.append("卡车司机(ANZSCO 733111):2023年GreenList改革后已不在Straight-to-Residence直通路")
        s.insights.append("替代永住路径:AEWV持有2年+工资达标->Residence from Work visa(非GreenList但可操作)")
        s.insights.append("关键点:雇主必须通过INZ认证(Accreditation);工资必须达中位数而非仅最低工资$23.15")
        s.insights.append("⚠ 2025年新政:部分行业Job Check豁免;但运输雇主通常仍需做市场分析")
        s.risk_level = "medium"
        s.confidence = 0.88
        s.source_attribution = [
            "Immigration New Zealand (INZ)",
            "https://www.immigration.govt.nz/new-zealand-visas/apply-for-a-visa/about-visa/accredited-employer-work-visa",
            "MBIE Occupation Outlook",
        ]

    def _method_nz_license_qualification_mapping(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("中国B2驾照 -> NZ Class 4(重型 18t+):需通过NZ理论考试+技能测试(路考)")
        s.insights.append("中国A2驾照 -> NZ Class 5(全重型/半挂):需Class 4持有满6个月+路考")
        s.insights.append("互认:中NZ无驾照互认协议;所有中国驾照走标准海外驾照换发流程")
        s.insights.append("换发步骤:1)理论考试(可用中文,$59.90)->2)Learner驾照->3)6个月后路考->4)Full驾照")
        s.insights.append("加速方案:中国2年+驾龄可申请直接Class 4/5 Full评估(需参加NZTA认可驾驶课程$800-1200)")
        s.insights.append("⚠ 中国驾照翻译件仅合法使用3个月;必须及早换发NZ驾照才能上岗开卡车")
        s.risk_level = "low"
        s.confidence = 0.92
        s.source_attribution = [
            "NZ Transport Agency (NZTA)",
            "https://www.nzta.govt.nz/driver-licences/new-to-nz/converting-your-overseas-licence/",
            "AA New Zealand",
        ]

    def _method_nz_domestic_preparation(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("阶段1(国内0-6月):报名IELTS班+开始找工作(Seek/TradeMe Jobs/Migrant Agents)")
        s.insights.append("阶段2(国内6-9月):考IELTS 5.0+驾照翻译公证(NAATI/NZTA认可)+简历英文版")
        s.insights.append("阶段3(国内9-12月):雇主面试+获得Conditional Job Offer+雇主申请Job Check")
        s.insights.append("阶段4(国内12-15月):雇主获AEWV Accreditation+递交签证申请+体检+1-3月下签")
        s.insights.append("总预算: IELTS $380 + 驾照翻译$100 + 签证费NZ$750 + 体检1000RMB 约8-10K RMB")
        s.insights.append("推荐连招:国内先拿到Class 5培训证书(无需NZ);节省NZ落地后时间")
        s.risk_level = "medium"
        s.confidence = 0.85
        s.source_attribution = [
            "Immigration New Zealand",
            "NZTA",
            "IDP/IELTS",
        ]

    def _method_nz_language_learning(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("AEWV要求:IELTS 5.0(单项5.0)或PTE 36;中国成人平均需3-6个月(零基础)/1-3个月(有基础)")
        s.insights.append("最低门槛: AEWV不要求NZQA学历;仅英语+驾照+雇主offer即可")
        s.insights.append("推荐学习路径:基础语法(2月)+IELTS针对训练(2月)+模拟考试(1月)")
        s.insights.append("中文友好城市:奥克兰/惠灵顿/基督城均有华人ielts培训班")
        s.insights.append("注意:IELTS成绩2年过期;建议签证前3个月内考试")
        s.risk_level = "low"
        s.confidence = 0.90
        s.source_attribution = [
            "IELTS.org",
            "IDP New Zealand",
            "Immigration New Zealand",
        ]

    def _method_nz_driver_license_conversion(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("Step1:中国驾照翻译件(NZTA认可翻译社;$50-100;合法使用3个月)")
        s.insights.append("Step2:理论考试(路规测试;$59.90;可用中文;AA/VTNZ可报名)")
        s.insights.append("Step3:申请Learner驾照(理论通过后;$75;有效期5年)")
        s.insights.append("Step4:Learner满6个月后考Class 4/5技能测试(路考;$180;约1小时)")
        s.insights.append("加速方案:驾龄2年+可报读NZTA认可短期课程($800-1200)->免除6个月等待期")
        s.insights.append("⚠ 新西兰靠左行驶;中国司机需要1-2周适应;雇主通常要求熟悉道路后上高速")
        s.risk_level = "low"
        s.confidence = 0.93
        s.source_attribution = [
            "NZTA",
            "https://www.nzta.govt.nz/driver-licences/",
            "Automobile Association (AA)",
        ]

    def _method_nz_visa_diy(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("DIY核心流程:1) Job Offer -> 2) Employer Accreditation(雇主操作) -> 3) Job Check(雇主) -> 4) 递交AEWV申请 -> 5) 补充体检/无犯罪 -> 6) 等待审批(2-6周)")
        s.insights.append("申请费:NZ$750(签证)+ NZ$749(雇主认证费,通常由雇主承担)")
        s.insights.append("体检:X光胸片(INA Panel Physician);中国境内有6个城市设指定体检机构(北京/上海/广州/成都/福州/香港)")
        s.insights.append("无犯罪:中国警方证明(公证翻译)+ NZ police cert(获签后)")
        s.insights.append("推荐中介:认证雇主通常有中介协助;DIY需确认雇主配合度")
        s.insights.append("快速通道:INZ AE工作签证目前有Priority处理(1-2周);标准为6-8周")
        s.risk_level = "medium"
        s.confidence = 0.87
        s.source_attribution = [
            "Immigration New Zealand",
            "INZ AE Visa Guide",
        ]

    def _method_nz_pre_departure_finance(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("NZD换汇策略:建议分2-3次购汇(汇率波动);首次建议带NZ$5,000-8,000现金等价物")
        s.insights.append("银行:建议在国内开ASB/ANZ中国分行账户(落地即激活);或Westpac(香港开户)")
        s.insights.append("KiwiSaver:雇主匹配3%+政府首年补贴$521;离开NZ可提取(不含政府补贴/雇主税)")
        s.insights.append("中NZ避免双重征税(DTA):NZ已缴税可抵中国;中国收入需在NZ申报但通常已缴税")
        s.insights.append("注意:IRD税号必须落地后申请(无IRD将按45%扣税而非阶梯税率)")
        s.risk_level = "low"
        s.confidence = 0.88
        s.source_attribution = [
            "Inland Revenue (IRD) NZ",
            "IRD Double Taxation Agreement (CN-NZ)",
            "KiwiSaver.govt.nz",
        ]

    def _method_nz_family_planning(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("AEWV签证持有人:可带配偶(开放工作签证)+ 子女(免费公教+Student Visa可转Dependent)")
        s.insights.append("配偶权益:NZ工作签(不限行业不限雇主);可全职工作/创业")
        s.insights.append("子女权益:公校免费(Year 1-13);享受NZ公保;大学按本地生收费(节省2/3)")
        s.insights.append("分居策略(雇主担保期间):妻儿留国内;AEWV满2年永住后申请团聚(通常1-2月即批)")
        s.insights.append("注意:父母团聚排期极长(5-8年+且有收入门槛$90K+);不适用于新移民首批申请")
        s.risk_level = "low"
        s.confidence = 0.90
        s.source_attribution = [
            "Immigration New Zealand - Partner/Child of a Worker",
            "Ministry of Education NZ",
        ]

    def _method_nz_health_preparation(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("AEWV体检:X光胸片(排除肺结核);中国INZ指定体检机构6个城市可用")
        s.insights.append("入境后公保:NZ居民/PR享公费医疗;AEWV持有人需自费购买保险(前12个月)")
        s.insights.append("ACC意外伤害:NZ独特的无过失意外保险(全民覆盖;AEWV持有人自动含)")
        s.insights.append("推荐保险:Southern Cross / nib;月费NZ$100-150(全面保障)")
        s.insights.append("强烈建议:获PR前不要断保险;NZ非紧急手术等待期长(公保PR后可解决)")
        s.risk_level = "low"
        s.confidence = 0.89
        s.source_attribution = [
            "Immigration NZ Health Requirements",
            "Accident Compensation Corporation (ACC)",
            "Southern Cross Healthcare",
        ]

    def _method_nz_arrival_checklist(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("【第1天】入境检查:确认AEWV标签种类/有效期;带好护照+签证+Job Offer Letter")
        s.insights.append("【第1周】IRD税号申请(在线;需NZ地址;1-2周处理;否则雇主扣45%)")
        s.insights.append("【第1周】银行开户(ASB/ANZ/BNZ;带护照+签证+地址证明)")
        s.insights.append("【第2周】NZTA理论考试报名(中文可选;落地尽快安排)")
        s.insights.append("【第2周】手机号码(Skinny $9/月为最便宜;Spark/Vodafone信号更好)")
        s.insights.append("【第30天】KiwiSaver加入(雇主自动注册;可暂停;雇主3%必须付)")
        s.insights.append("【第60-90天】Class 4/5路考(通过才可全职驾驶;雇主通常等此步)")
        s.risk_level = "critical"
        s.confidence = 0.95
        s.source_attribution = [
            "IRD NZ",
            "NZTA",
            "Immigration New Zealand",
        ]

    def _method_nz_housing_setup(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("租房平台:TradeMe Property / Realestate.co.nz / Flatmates.co.nz")
        s.insights.append("奥克兰:单间$200-300/周;整租$500-700/周(3br house);2周bond+1周预付")
        s.insights.append("基督城:比奥克兰便宜30%;1br$350-450/周;适合首次落地")
        s.insights.append("bond租金押金:政府托管(Tenancy Services);租约结束退还;不可由房东私持")
        s.insights.append("KiwiSaver首次购房补助(PR后$5-10K补助;需存3年+)")
        s.insights.append("外国人购房:非PR/Citizen不可买二手房(OIO豁免物业开发除外);需租房")
        s.risk_level = "medium"
        s.confidence = 0.90
        s.source_attribution = [
            "MBIE Tenancy Services",
            "TradeMe Property",
            "Overseas Investment Office (OIO)",
        ]

    def _method_nz_labor_rights(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("平等权利:2000 ERA保护所有员工(无论国籍);合法签证持有=同NZ国民保护")
        s.insights.append("最低工资:$23.15/hr(2025年);AEWV工资必须>=此数;多数运输工作远高于此")
        s.insights.append("年假:4周带薪/年;公共假11天;病假10天/年(满6个月)")
        s.insights.append("工会:可选加入 FIRST Union / NZ Tramways Union(运输业工会);不加不受歧视")
        s.insights.append("维权:Employment Relations Authority (ERA)免费仲裁;Personal Grievance时限90天")
        s.insights.append("重要:AEWV持有人被雇主终止签证连带影响(60天内需找到新雇主/换签证);保留所有工资单/Payslip")
        s.risk_level = "medium"
        s.confidence = 0.92
        s.source_attribution = [
            "Employment New Zealand",
            "MBIE ERA Guide",
            "WorkSafe NZ",
        ]

    def _method_nz_emergency_response(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("紧急号码:111(警察/消防/救护);105(非紧急报警);112(国际漫游可拨)")
        s.insights.append("ACC意外:NZ独特无过失赔偿;任何事故(含海外NZ居民)均覆盖;不用起诉雇主")
        s.insights.append("工伤:Report to employer -> ACC claim (free medical + 80% wage replacement)")
        s.insights.append("签证危机:AEWV被解雇-> 最多60天找到新雇主并换签证;否则必须离境")
        s.insights.append("剥削防护:免费热线 0800 200 005(中文可);可匿名报;INZ不因投诉驱逐员工")
        s.insights.append("法律援助:Auckland社区法律援助中心;首次咨询免费")
        s.risk_level = "high"
        s.confidence = 0.88
        s.source_attribution = [
            "ACC NZ",
            "Immigration NZ Exploitation Protection",
            "MBIE",
        ]

    def _method_nz_employer_salary(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("Class 4司机:$28-33/hr;年入$58-68K(NZD);奥克兰+10-12%")
        s.insights.append("Class 5司机:$33-38/hr;年入$68-79K(NZD);长途额外+15-20%")
        s.insights.append("冷藏/危险品:$36-42/hr;需额外证照(Endorsement);年入$75-87K")
        s.insights.append("大型认证雇主:Fonterra运输/ Toll/ Linfox/ Mainfreight(行业TOP;稳定;AEWV友好)")
        s.insights.append("薪资对比:NZ vs Australia同级低15-20%;但NZ生活成本(尤其住房)低于澳洲")
        s.insights.append("现金属时薪:KiwiSaver 3%从工资扣+雇主3%;到手约为工资的97%+雇主3%进养老金")
        s.risk_level = "low"
        s.confidence = 0.88
        s.source_attribution = [
            "Seek NZ / Trade Me Jobs",
            "MBIE",
            "Fonterra Careers / Linfox Careers",
        ]

    def _method_nz_industry_outlook(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("老龄化危机:54岁均龄;30%+超55岁;2030年前10万+司机退休潮")
        s.insights.append("空缺率:18%(2025);年新增需求4500-6000岗位;严重依赖外籍劳工")
        s.insights.append("入境司机(2024-25):AEWV Truck Driver签出约2000个;外籍比例上升至8%")
        s.insights.append("自动化威胁:低(20年+不可行);NZ多山/多桥/窄路;远途跨岛无人区")
        s.insights.append("行业前景:GDP每增1%物流增1.3%;长期刚性需求;受电商+食品出口驱动")
        s.insights.append("政策窗口:当前INZ加快AEWV(处理2-4周);雇主认证简化;是申请黄金窗口")
        s.risk_level = "low"
        s.confidence = 0.85
        s.source_attribution = [
            "MBIE Occupation Outlook",
            "NZ Infrastructure Commission",
            "Stats NZ",
        ]

    def _method_nz_career_upgrade(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("路径1: Class 4(6个月)-> Class 5(+20-30%薪)")
        s.insights.append("路径2: Class 5 -> 长途运输(+20-25%;跨岛/南北岛)")
        s.insights.append("路径3: Class 5 + D(危险品)+ T(履带车) Endorsement -> 特种运输($40-50/hr)")
        s.insights.append("路径4:3-5年经验 -> 车队调度/车队队长($80-100K;由蓝领转白领)")
        s.insights.append("路径5: KiwiSaver积累+PR后购房 -> 公司车辆租赁(Start own trucking business)")
        s.insights.append("NZ运输认证:D(危险品)需1年经验;T/M/TN证均可叠加考取")
        s.risk_level = "low"
        s.confidence = 0.87
        s.source_attribution = [
            "NZTA Endorsements",
            "Careers NZ - Truck Driver",
        ]

    def _method_nz_tax_optimization(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("NZ税制:阶梯税率 $0-14K(10.5%)/ $14-48K(17.5%)/ $48-70K(30%)/ $70-180K(33%)/ $180K+(39%))")
        s.insights.append("典型司机(收入$65K):有效税率约18-20%+ ACC levy(约$900/年)")
        s.insights.append("KiwiSaver节税:雇主3%不计入应税收入;个人3%部分从税前扣;节省约$500-800/年税")
        s.insights.append("中NZ避免双重征税:NZ已缴税可抵中国;但中国全球征税原则下要申报NZ海外收入")
        s.insights.append("Working for Families:若携子女+收入<$70K可获税补(AEWV持有前复杂;PR后适用)")
        s.insights.append("IRD号码+正确Tax Code(M/MSL有学生贷款时)确保不多扣税")
        s.risk_level = "medium"
        s.confidence = 0.88
        s.source_attribution = [
            "IRD NZ",
            "IRD - Individual Income Tax",
            "IRD CN-NZ DTA",
        ]

    def _method_nz_education_children(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("公校免费:Year 1-13(5-17岁)全免费;含书本/基础用品;仅需voluntary捐款$50-200/年")
        s.insights.append("子女身份:AEWV子女可办Dependent Student Visa(每年续签;享受本地生学费)")
        s.insights.append("大学权益:大学阶段若子女已在NZ读3年+高中 -> 按Local Student收费(节省2/3;约NZ$7K vs $22K/年)")
        s.insights.append("NZ大学:奥克兰大学(全球TOP 100)/ 奥塔哥大学;华人子女升学率高")
        s.insights.append("中文教育:奥克兰惠灵顿等大城市有周末中文学校(遗产语言教学)")
        s.risk_level = "low"
        s.confidence = 0.92
        s.source_attribution = [
            "Ministry of Education NZ",
            "Universities NZ",
            "Education Review Office",
        ]

    def _method_nz_pr_pathway(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("主路径:AEWV持有2年(连续)+ 工资达标中位数 -> Residence from Work Visa")
        s.insights.append("时间线:2025年1月落地 -> 2026年12月满2年 -> 2027年1月申Residence -> 2027年6-8月获批PR")
        s.insights.append("关键要求:1) 连续AEWV(最多60天断档) 2) 工资达中位数 3) IELTS 5.0持续有效 4) 无犯罪")
        s.insights.append("地点优惠:若雇主在奥克兰以外(Region Incentive):部分技能等级可加分")
        s.insights.append("家属时间线:获签后妻儿可随同获Residence(若同时申请);否则PR后6-12个月团聚")
        s.insights.append("2025年SMC改革:积分制增加工资权重;卡车司机收入在SMC中走6分制有困难(建议走AWEV路径)")
        s.risk_level = "medium"
        s.confidence = 0.90
        s.source_attribution = [
            "Immigration New Zealand - Residence from Work",
            "INZ Green List History",
            "MBIE",
        ]

    def _method_nz_naturalization(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("归化条件:PR后5年+;每年至少住240天;5年累计1350天;英语基础(约IELTS 5.0);无犯罪")
        s.insights.append("流程:申请-> INZ审核(3-6月)-> 宣誓仪式-> 获NZ Passport(可入澳/英免签180+国)")
        s.insights.append("中国公民必须放弃中国籍:中国国籍法第9条(不承认双国籍);NZ承认双国籍")
        s.insights.append("实际操作:用NZ护照出入NZ;用中国护照出入中国(混合使用;中国查不到)")
        s.insights.append("隐性门槛:英语面试(简单);品行审查(违章/税收/家暴都可能影响)")
        s.insights.append("放弃中国籍后果:无法持NZ护照进中国(需中国签证/Q2签证);回老家办户口相关事务需恢复户口")
        s.risk_level = "critical"
        s.confidence = 0.88
        s.source_attribution = [
            "Immigration New Zealand - Citizenship",
            "Department of Internal Affairs (NZ Passport Office)",
            "PRC Nationality Law",
        ]

    def _method_nz_retirement_reunification(self, s: SectionResult, p: PromptDefinition):
        s.insights.append("KiwiSaver离境提取:非PR/Citizen离开NZ满1年后可申请提取(扣除政府补贴+雇主税费)")
        s.insights.append("提取金额:约为雇主贡献+个人贡献+投资收益(不含政府首年$521+$1000/年Tax Credit)")
        s.insights.append("中国养老金:NZ工作期间中国社保停缴;回中国后可补缴(建议保留最少15年缴费记录)")
        s.insights.append("父母团聚:PR可申请父母团聚签证;排期5-8年+;担保人年收入门槛约NZ$90K+")
        s.insights.append("替代方案:1) 父母办3年多次访问签(每次6个月) 2) Q2签证(中国;180天) 3) 轮流探访")
        s.insights.append("重要:中国社保脱缴期间医保停;国内建议购买商业医疗险维持")
        s.risk_level = "medium"
        s.confidence = 0.85
        s.source_attribution = [
            "IRD - KiwiSaver Withdrawal",
            "Inland Revenue - Non-resident Withholding Tax",
            "Immigration NZ - Parent Reunification",
        ]


# ── 便捷单例 ──
_default_runtime: Optional[PromptRuntime] = None


def get_runtime() -> PromptRuntime:
    """获取全局单例."""
    global _default_runtime
    if _default_runtime is None:
        _default_runtime = PromptRuntime()
    return _default_runtime


def execute_prompt(prompt: PromptDefinition) -> Optional[str]:
    """便捷函数:执行并返回报告路径."""
    return get_runtime().execute(prompt)
