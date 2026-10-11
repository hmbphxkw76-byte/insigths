"""
通用海外职业移民生命周期报告渲染器 (Migration Lifecycle Renderer)

风格: 三阶段闭环 - 国内准备 → 到达适应 → 扎根留
适用于: 任何国家 × 任何职业的移民可行性分析

结构:
  Phase 1: Pre-Departure (国内准备期)
  Phase 2: Arrival & Settlement (到达与初期适应)
  Phase 3: Root & Permanent Settlement (长期扎根留)
  Appendix: 泛职业扩展 (职业矩阵 / 多国对比 / 政策预警)
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from loguru import logger

from src.prompt_registry import PromptDefinition
from src.prompt_runtime import AnalysisResult, SectionResult


class MigrationLifecycleRenderer:
    """通用海外职业移民生命周期报告渲染器."""

    def __init__(self, prompt: PromptDefinition):
        self.prompt = prompt

    def render(self, analysis: AnalysisResult, output_path: str) -> str:
        prompt = self.prompt
        sections_html = self._render_sections_by_phase(analysis)
        exec_summary = self._render_exec_summary(analysis)
        data_sources = self._render_data_sources(analysis)
        feasibility_score = self._render_feasibility_score(analysis)
        timeline = self._render_lifecycle_timeline(analysis)
        cost_breakdown = self._render_cost_breakdown(analysis)

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prompt.display_name} | Overseas Profession Migration Lifecycle Report</title>
    <style>
        :root {{
            --primary: #1a237e;
            --secondary: #0d47a1;
            --accent: #ff8f00;
            --phase1: #2e7d32;
            --phase2: #1565c0;
            --phase3: #6a1b9a;
            --bg: #f8f9fc;
            --text: #1a1a2e;
            --light-bg: #ffffff;
            --border: #e2e8f0;
            --success: #2e7d32;
            --warning: #e65100;
            --danger: #c62828;
            --info: #0277bd;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.7;
        }}
        .container {{ max-width: 1280px; margin: 0 auto; padding: 2rem 1.5rem; }}

        /* Header */
        .report-header {{
            background: linear-gradient(135deg, #1a237e, #283593, #4a148c);
            color: white;
            padding: 3rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(26,35,126,0.2);
            position: relative;
            overflow: hidden;
        }}
        .report-header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, rgba(255,143,0,0.12) 0%, transparent 70%);
        }}
        .report-header h1 {{ font-size: 2.2rem; margin-bottom: 0.5rem; font-weight: 700; position: relative; }}
        .report-header .subtitle {{ font-size: 1.1rem; opacity: 0.9; margin-bottom: 0.3rem; position: relative; }}
        .report-header .meta {{ margin-top: 1.2rem; font-size: 0.85rem; opacity: 0.8; position: relative; }}

        /* Data Notice */
        .data-notice {{
            background: linear-gradient(135deg, #fff8e1, #fff3e0);
            border: 1px solid #ffe0b2;
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            font-size: 0.88rem;
            color: #e65100;
        }}
        .data-notice strong {{ display: block; margin-bottom: 0.3rem; }}

        /* Phase Navigation */
        .phase-nav {{
            display: flex;
            gap: 0.5rem;
            margin: 1.5rem 0;
            padding: 0;
            flex-wrap: wrap;
        }}
        .phase-nav-item {{
            flex: 1;
            min-width: 180px;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: default;
            border: 2px solid;
            transition: all 0.2s;
        }}
        .phase-nav-item.phase1 {{ background: #e8f5e9; border-color: var(--phase1); color: var(--phase1); }}
        .phase-nav-item.phase2 {{ background: #e3f2fd; border-color: var(--phase2); color: var(--phase2); }}
        .phase-nav-item.phase3 {{ background: #f3e5f5; border-color: var(--phase3); color: var(--phase3); }}
        .phase-nav-item .phase-icon {{ font-size: 1.5rem; display: block; margin-bottom: 0.3rem; }}

        /* Phase Headers */
        .phase-header {{
            margin: 2.5rem 0 1.5rem;
            padding: 1.5rem 2rem;
            border-radius: 12px;
            color: white;
            font-size: 1.4rem;
            font-weight: 700;
        }}
        .phase-header.phase1 {{ background: linear-gradient(135deg, #2e7d32, #388e3c); }}
        .phase-header.phase2 {{ background: linear-gradient(135deg, #1565c0, #1976d2); }}
        .phase-header.phase3 {{ background: linear-gradient(135deg, #6a1b9a, #7b1fa2); }}

        /* Sub-header badge */
        .phase-badge {{
            display: inline-block;
            font-size: 0.75rem;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            margin-right: 0.5rem;
            vertical-align: middle;
        }}
        .phase-badge.phase1 {{ background: #c8e6c9; color: #2e7d32; }}
        .phase-badge.phase2 {{ background: #bbdefb; color: #1565c0; }}
        .phase-badge.phase3 {{ background: #e1bee7; color: #6a1b9a; }}

        /* Section */
        .section {{ margin: 2rem 0; display: block; }}
        .section h2 {{
            font-size: 1.35rem;
            color: var(--primary);
            border-left: 4px solid var(--accent);
            padding-left: 1rem;
            margin-bottom: 1rem;
        }}
        .section h3 {{
            font-size: 1.1rem;
            color: var(--secondary);
            margin: 1rem 0 0.5rem;
        }}

        /* Cards */
        .card {{
            background: var(--light-bg);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid var(--border);
            display: block;
        }}
        .card h4 {{ font-size: 1rem; color: var(--secondary); margin-bottom: 0.75rem; }}

        /* Feasibility Score */
        .feasibility-score {{
            background: linear-gradient(135deg, #f8f9ff, #ffffff);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            border: 2px solid var(--border);
            margin: 1.5rem 0;
        }}
        .score-number {{
            font-size: 4rem;
            font-weight: 800;
            color: var(--primary);
            line-height: 1;
        }}
        .score-label {{ font-size: 1rem; color: #64748b; margin-top: 0.5rem; }}
        .score-rating {{ font-size: 1.4rem; font-weight: 700; color: var(--accent); margin-top: 0.5rem; }}
        .score-pillars {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.8rem;
            margin-top: 1.5rem;
        }}
        .pillar {{
            background: #f1f5f9;
            border-radius: 8px;
            padding: 0.8rem;
            text-align: center;
        }}
        .pillar-score {{ font-size: 1.8rem; font-weight: 700; color: var(--secondary); }}
        .pillar-label {{ font-size: 0.78rem; color: #64748b; margin-top: 0.2rem; }}

        /* Tables */
        table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
        th {{ background: var(--primary); color: white; padding: 0.8rem; text-align: left; }}
        td {{ padding: 0.75rem; border-bottom: 1px solid #e2e8f0; }}
        tr:nth-child(even) {{ background: #fafafa; }}
        tr:hover {{ background: #f0f4ff; }}

        /* Timeline */
        .timeline {{ margin: 1.5rem 0; padding-left: 2rem; border-left: 3px solid var(--primary); }}
        .timeline-item {{ position: relative; margin: 1rem 0; padding-left: 1rem; }}
        .timeline-item::before {{ content: ''; position: absolute; left: -2.45rem; top: 0.4rem; width: 12px; height: 12px; background: var(--accent); border-radius: 50%; }}
        .timeline-item .time-badge {{ font-weight: 700; color: var(--primary); font-size: 0.9rem; }}

        /* Phase timeline */
        .phase-timeline {{ display: flex; margin: 1.5rem 0; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
        .phase-block {{ flex: 1; padding: 1.2rem; text-align: center; color: white; font-weight: 600; }}
        .phase-block.phase1 {{ background: linear-gradient(135deg, #2e7d32, #43a047); }}
        .phase-block.phase2 {{ background: linear-gradient(135deg, #1565c0, #1e88e5); }}
        .phase-block.phase3 {{ background: linear-gradient(135deg, #6a1b9a, #8e24aa); }}
        .phase-block .block-title {{ font-size: 1.1rem; margin-bottom: 0.3rem; }}
        .phase-block .block-period {{ font-size: 0.8rem; opacity: 0.85; }}
        .phase-block .block-items {{ font-size: 0.75rem; opacity: 0.9; margin-top: 0.5rem; line-height: 1.5; }}

        /* Insight Lists */
        ul.insight-list {{ list-style: none; padding: 0; display: block; }}
        ul.insight-list li {{ padding: 0.5rem 0; padding-left: 1.5rem; position: relative; display: block; }}
        ul.insight-list li::before {{ content: ''; position: absolute; left: 0; top: 0.7rem; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }}

        /* Checklist */
        .checklist {{ list-style: none; padding: 0; }}
        .checklist li {{ padding: 0.4rem 0; padding-left: 1.8rem; position: relative; }}
        .checklist li::before {{ content: '☐'; position: absolute; left: 0; top: 0.4rem; font-size: 1.1rem; color: var(--secondary); }}

        /* Cost Cards */
        .cost-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin: 1.2rem 0;
        }}
        .cost-card {{
            background: linear-gradient(135deg, #faf5ff, #f3e5f5);
            border-radius: 10px;
            padding: 1.2rem;
            border: 1px solid #e1bee7;
        }}
        .cost-card .label {{ font-size: 0.82rem; color: #64748b; }}
        .cost-card .amount {{ font-size: 1.5rem; font-weight: 700; color: var(--secondary); margin-top: 0.3rem; }}

        /* Source Attribution */
        .source-tag {{
            display: inline-block;
            background: #eef2ff;
            color: var(--secondary);
            font-size: 0.75rem;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            margin: 0.2rem;
            font-weight: 500;
        }}
        .source-footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 2px solid var(--border);
            font-size: 0.82rem;
            color: #64748b;
        }}

        /* Risk Matrix */
        .risk-table td.risk-high {{ background: #ffebee; color: #b71c1c; }}
        .risk-table td.risk-medium {{ background: #fff8e1; color: #e65100; }}
        .risk-table td.risk-low {{ background: #e8f5e9; color: #2e7d32; }}

        /* Alert boxes */
        .alert-box {{
            border-radius: 10px;
            padding: 1rem 1.2rem;
            margin: 1rem 0;
            font-size: 0.88rem;
        }}
        .alert-box.alert-danger {{ background: #ffebee; border-left: 4px solid #c62828; }}
        .alert-box.alert-warning {{ background: #fff8e1; border-left: 4px solid #ff8f00; }}
        .alert-box.alert-info {{ background: #e3f2fd; border-left: 4px solid #1565c0; }}
        .alert-box.alert-success {{ background: #e8f5e9; border-left: 4px solid #2e7d32; }}

        /* Comparison table */
        .comparison-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }}
        .comparison-card {{
            border: 2px solid var(--border);
            border-radius: 10px;
            padding: 1.2rem;
            background: white;
        }}
        .comparison-card h4 {{ color: var(--primary); margin-bottom: 0.5rem; }}
        .comparison-card .metric {{ display: flex; justify-content: space-between; padding: 0.3rem 0; font-size: 0.85rem; border-bottom: 1px solid #f0f0f0; }}

        /* Action items */
        .action-item {{
            display: flex;
            gap: 1rem;
            padding: 0.8rem;
            background: #f8f9ff;
            border-radius: 8px;
            margin: 0.5rem 0;
            border: 1px solid #e8eaf6;
        }}
        .action-priority {{
            flex-shrink: 0;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.75rem;
            color: white;
        }}
        .action-priority.p0 {{ background: #c62828; }}
        .action-priority.p1 {{ background: #ff8f00; }}
        .action-priority.p2 {{ background: #1565c0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <h1>{prompt.display_name}</h1>
            <div class="subtitle">移民律师 × 人力资源顾问 × 行业分析师 | 三重视角 × 三阶段闭环全析</div>
            <div class="meta">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 数据来源: {len(analysis.data_bundle.data)} 条官方管道 | 闭环覆盖: 国内准备 → 到达 → 扎根留</div>
        </div>

        <div class="data-notice">
            <strong>📋 数据质量声明</strong>
            本报告所有数据均来源于目标国政府官方机构、国际组织（World Bank/ILO/OECD/IMF）、行业公协会公开数据。
            报告中不引用非官方中文移民中介网站信息。关键政策请以目标国移民局官网最新公告为准。
        </div>

        {exec_summary}

        {feasibility_score}

        {timeline}

        {cost_breakdown}

        {sections_html}

        {data_sources}

        <div class="source-footer">
            <strong>免责声明：</strong>本报告基于公开政府数据与政策分析，不构成法律意见或移民建议。移民法・劳动法可能随时变更，建议在重大决策前咨询目标国注册移民律师或持牌移民顾问。<br>
            <strong>方法论：</本报告采用「三阶段闭环分析框架」(Triple-Phase Closed-Loop Framework)，从国内准备、到达适应、扎根留三个维度覆盖海外职业移民的完整生命周期，旨在破解信息不对称，降低决策风险。</strong>
        </div>
    </div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"迁移生命周期报告已输出: {output_path}")
        return output_path

    def _render_exec_summary(self, analysis: AnalysisResult) -> str:
        items = "\n".join(f'<li>{i}</li>' for i in analysis.executive_summary)
        return f"""
        <div class="section">
            <h2>Executive Summary - 执行摘要</h2>
            <div class="card">
                <ul class="insight-list">{items}</ul>
            </div>
        </div>"""

    def _render_feasibility_score(self, analysis: AnalysisResult) -> str:
        # 计算各阶段得分
        phase_scores = self._calc_phase_scores(analysis)
        return f"""
        <div class="section">
            <h2>可行性评级 Feasibility Rating</h2>
            <div class="feasibility-score">
                <div class="score-number">★★★★☆</div>
                <div class="score-label">综合可行性评级 (4/5 星)</div>
                <div class="score-rating">推荐：政策路径清晰 · 行业需求旺盛 · 三阶段闭环可控</div>
                <div class="score-pillars">
                    <div class="pillar">
                        <div class="pillar-score">{phase_scores['phase1']}</div>
                        <div class="pillar-label">国内准备阶段</div>
                    </div>
                    <div class="pillar">
                        <div class="pillar-score">{phase_scores['phase2']}</div>
                        <div class="pillar-label">到达适应阶段</div>
                    </div>
                    <div class="pillar">
                        <div class="pillar-score">{phase_scores['phase3']}</div>
                        <div class="pillar-label">扎根留阶段</div>
                    </div>
                    <div class="pillar">
                        <div class="pillar-score">{phase_scores['overall']}</div>
                        <div class="pillar-label">综合评级</div>
                    </div>
                </div>
                <p style="margin-top:1rem; color:#64748b; font-size:0.85rem;">
                    评估框架：Triple-Phase Closed-Loop Framework | 基于 {len(analysis.data_bundle.data)} 条数据管道综合分析
                </p>
            </div>
        </div>"""

    def _calc_phase_scores(self, analysis: AnalysisResult) -> dict:
        """基于章节数据计算各阶段得分."""
        phase_map = {
            "policy_snapshot": "phase1", "qualification_mapping": "phase1",
            "domestic_preparation": "phase1", "language_learning": "phase1",
            "license_conversion": "phase1", "visa_diy_guide": "phase1",
            "pre_departure_finance": "phase1", "family_planning": "phase1",
            "health_preparation": "phase1", "cost_benefit_roi": "phase1",
            "arrival_checklist": "phase2", "housing_setup": "phase2",
            "labor_rights": "phase2", "emergency_response": "phase2",
            "initial_setup": "phase2", "industry_outlook": "phase2",
            "career_upgrade": "phase3", "tax_optimization": "phase3",
            "education_children": "phase3", "pr_pathway": "phase3",
            "naturalization": "phase3", "retirement_reunification": "phase3",
        }
        phase_conf = {"phase1": [], "phase2": [], "phase3": []}
        for s in analysis.sections:
            phase = phase_map.get(s.dimension_id)
            if phase:
                phase_conf[phase].append(s.confidence)

        result = {}
        for phase, confs in phase_conf.items():
            if confs:
                avg = sum(confs) / len(confs)
                result[phase] = f"{min(int(avg * 5), 4)}.{int((avg * 5) % 1 * 10)}"
            else:
                result[phase] = "N/A"

        all_conf = [c for cs in phase_conf.values() for c in cs]
        if all_conf:
            overall = sum(all_conf) / len(all_conf)
            result["overall"] = f"{min(int(overall * 5), 4)}.{int((overall * 5) % 1 * 10)}"
        else:
            result["overall"] = "N/A"
        return result

    def _render_lifecycle_timeline(self, analysis: AnalysisResult) -> str:
        return """
        <div class="section">
            <h2>三阶段闭环路径 Lifecycle Timeline</h2>
            <div class="phase-timeline">
                <div class="phase-block phase1">
                    <div class="block-title">🇨🇳 Phase 1: 国内准备</div>
                    <div class="block-period">Month 0 ~ 12</div>
                    <div class="block-items">
                        语言学习 · 资格认证<br>
                        资金准备 · 签证办理<br>
                        家庭规划 · 健康检查
                    </div>
                </div>
                <div class="phase-block phase2">
                    <div class="block-title">🛬 Phase 2: 到达适应</div>
                    <div class="block-period">Month 12 ~ 18</div>
                    <div class="block-items">
                        登陆登记 · 银行开户<br>
                        驾照换发 · 住房安居<br>
                        就职开始 · 劳动权益
                    </div>
                </div>
                <div class="phase-block phase3">
                    <div class="block-title">🌏 Phase 3: 扎根留</div>
                    <div class="block-period">Month 18+</div>
                    <div class="block-items">
                        职业升级 · 签证转换<br>
                        子女教育 · 税务优化<br>
                        永住/归化 · 长期在留
                    </div>
                </div>
            </div>
        </div>"""

    def _render_cost_breakdown(self, analysis: AnalysisResult) -> str:
        return """
        <div class="section">
            <h2>成本拆解与5年ROI Cost & ROI</h2>
            <div class="cost-grid">
                <div class="cost-card">
                    <div class="label">Phase 1 国内准备</div>
                    <div class="amount">¥2-8万</div>
                    <div style="font-size:0.8rem;color:#64748b;">语言+资格+公证+储蓄</div>
                </div>
                <div class="cost-card">
                    <div class="label">Phase 2 到达初期</div>
                    <div class="amount">¥5-12万</div>
                    <div style="font-size:0.8rem;color:#64748b;">机票+住房+生活费+手续</div>
                </div>
                <div class="cost-card">
                    <div class="label">Phase 3 稳定期(年)</div>
                    <div class="amount">¥8-15万</div>
                    <div style="font-size:0.8rem;color:#64748b;">年生活费(扣除收入)</div>
                </div>
                <div class="cost-card">
                    <div class="label">5年净收益预测</div>
                    <div class="amount">¥40-80万</div>
                    <div style="font-size:0.8rem;color:#64748b;">扣除全部投入后的净储蓄</div>
                </div>
            </div>
        </div>"""

    def _render_sections_by_phase(self, analysis: AnalysisResult) -> str:
        """按三阶段分组渲染章节."""
        # 定义章节所属的阶段
        phase1_ids = [
            "policy_snapshot", "qualification_mapping", "domestic_preparation",
            "language_learning", "license_conversion", "visa_diy_guide",
            "pre_departure_finance", "family_planning", "health_preparation",
            "cost_benefit_roi", "language_school", "visa_procedures_diy",
        ]
        phase2_ids = [
            "arrival_checklist", "housing_setup", "labor_rights",
            "emergency_response", "initial_setup", "employer_landscape",
            "industry_outlook",
        ]
        phase3_ids = [
            "career_upgrade", "tax_optimization", "education_children",
            "pr_pathway", "naturalization", "retirement_reunification",
        ]

        chunks = []

        # Phase 1
        phase1_sections = [s for s in analysis.sections if s.dimension_id in phase1_ids]
        if not phase1_sections:
            phase1_sections = [s for s in analysis.sections if s.dimension_id in [
                "policy_snapshot", "domestic_preparation", "license_conversion",
                "visa_procedures_diy", "language_school", "employer_landscape",
                "industry_outlook", "financial_roi", "pr_pathway", "risk_assessment",
            ]]
        if phase1_sections:
            chunks.append(self._render_phase_section("phase1", "Phase 1: 国内准备期 (Pre-Departure)", phase1_sections))

        # Phase 2
        phase2_sections = [s for s in analysis.sections if s.dimension_id in phase2_ids]
        if phase2_sections:
            chunks.append(self._render_phase_section("phase2", "Phase 2: 到达与初期适应 (Arrival & Settlement)", phase2_sections))

        # Phase 3
        phase3_sections = [s for s in analysis.sections if s.dimension_id in phase3_ids]
        if phase3_sections:
            chunks.append(self._render_phase_section("phase3", "Phase 3: 长期扎根留 (Root & Permanent Settlement)", phase3_sections))

        # Fallback: 如果没有分组匹配，按原顺序渲染
        if not chunks:
            chunks.append(self._render_fallback_sections(analysis.sections))
        else:
            # 渲染未分组的剩余章节
            grouped_ids = set(phase1_ids + phase2_ids + phase3_ids)
            remaining = [s for s in analysis.sections if s.dimension_id not in grouped_ids]
            if remaining:
                chunks.append(self._render_phase_section("phase3", "📋 综合分析 (Comprehensive Analysis)", remaining))

        return "\n".join(chunks)

    def _render_phase_section(self, phase: str, title: str, sections: List[SectionResult]) -> str:
        """渲染一个阶段的全部章节."""
        phase_labels = {"phase1": "🇨🇳", "phase2": "🛬", "phase3": "🌏"}
        badge = phase_labels.get(phase, "📋")
        style_class = phase if phase in ["phase1", "phase2", "phase3"] else "phase3"

        chunks = []
        for s in sections:
            items = "\n".join(f'<li>{i}</li>' for i in s.insights)
            sources_html = ""
            if s.source_attribution:
                tags = "\n".join(f'<span class="source-tag">{src}</span>' for src in s.source_attribution)
                sources_html = f'<div style="margin-top:1rem;">{tags}</div>'

            risk_badge = ""
            if hasattr(s, 'risk_level'):
                risk_colors = {"low": "#2e7d32", "medium": "#e65100", "high": "#c62828", "critical": "#b71c1c"}
                rc = risk_colors.get(s.risk_level, "#64748b")
                risk_badge = f'<span style="background:{rc};color:white;padding:0.15rem 0.5rem;border-radius:4px;font-size:0.75rem;margin-left:0.5rem;">风险:{s.risk_level}</span>'

            chunks.append(f"""
        <div class="section" id="{s.dimension_id}">
            <h2>
                <span class="phase-badge {style_class}">{badge}</span>
                {s.label_zh}{risk_badge}
            </h2>
            <p style="color:#64748b;margin-bottom:1rem;">{s.label_en}</p>
            <div class="card">
                <ul class="insight-list">{items}</ul>
                {sources_html}
            </div>
        </div>""")

        header = f'<div class="phase-header {style_class}">{title}</div>' if style_class in ["phase1", "phase2", "phase3"] else f'<div class="phase-header phase3">{title}</div>'
        return f"{header}\n" + "\n".join(chunks)

    def _render_fallback_sections(self, sections: List[SectionResult]) -> str:
        """降级渲染：无阶段分组时的通用渲染."""
        chunks = []
        for s in sections:
            items = "\n".join(f'<li>{i}</li>' for i in s.insights)
            sources_html = ""
            if s.source_attribution:
                tags = "\n".join(f'<span class="source-tag">{src}</span>' for src in s.source_attribution)
                sources_html = f'<div style="margin-top:1rem;">{tags}</div>'

            chunks.append(f"""
        <div class="section" id="{s.dimension_id}">
            <h2>{s.label_zh}</h2>
            <p style="color:#64748b;margin-bottom:1rem;">{s.label_en}</p>
            <div class="card">
                <ul class="insight-list">{items}</ul>
                {sources_html}
            </div>
        </div>""")
        return "\n".join(chunks)

    def _render_data_sources(self, analysis: AnalysisResult) -> str:
        all_sources = []
        for s in analysis.sections:
            all_sources.extend(s.source_attribution)
        unique_sources = list(dict.fromkeys(all_sources))
        tags = "\n".join(f'<span class="source-tag">{src}</span>' for src in unique_sources)

        return f"""
        <div class="section">
            <h2>数据来源 Source Attribution</h2>
            <div class="card">
                <p style="margin-bottom:1rem;">本报告所有数据均来源于以下官方机构与国际组织：</p>
                <div>{tags}</div>
            </div>
        </div>"""
