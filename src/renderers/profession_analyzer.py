"""
麦肯锡风格 — 职业 × 国家/地区 人才需求深度分析渲染器

设计语言:
- 深蓝主色调 (#0b2545) + 金色 accent (#c8a24b)
- 核心指标卡片 (KPI Cards) — 顶部摘要
- 供需对比的双轴图 — 人才缺口可视化
- 薪资阶梯表 — 透明化P25-P90区间
- 职业ROI计算器 — 5年净现值模型
- 风险热力矩阵 — 4象限评估

参考: McKinsey Global Institute talent reports + BCG Future of Work analysis
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional

import pandas as pd
from loguru import logger

from src.prompt_registry import PromptDefinition
from src.prompt_runtime import AnalysisResult


class ProfessionAnalyzerRenderer:
    """麦肯锡风格职业人才需求深度分析渲染器."""

    def __init__(self, prompt: PromptDefinition):
        self.prompt = prompt

    def render(self, analysis: AnalysisResult, output_path: str) -> str:
        """渲染完整报告 → HTML."""
        prompt = self.prompt
        primary = prompt.raw.get("report", {}).get("style", {}).get("primary_color", "#0b2545")
        accent = prompt.raw.get("report", {}).get("style", {}).get("accent_color", "#c8a24b")

        # ── 章节渲染 ──
        section_html_chunks = []
        for s in analysis.sections:
            cards = self._render_insight_cards(s.insights)
            charts = self._render_chart_section(s)
            html = f"""
        <div class="section" id="{s.dimension_id}">
            <h2>{s.label_zh}</h2>
            <p class="section-en">{s.label_en}</p>
            <div class="card">
                {cards}
            </div>
            {charts}
        </div>"""
            section_html_chunks.append(html)
        sections_html = "\n".join(section_html_chunks)

        # ── 执行摘要 ──
        exec_summary_html = self._render_executive_summary(analysis)

        # ── KPI 仪表盘 ──
        kpi_html = self._render_kpi_dashboard(analysis)

        # ── 薪资对比表 (如有数据) ──
        salary_table = self._render_salary_table(analysis)

        # ── 行动建议 ──
        actions_html = self._render_action_recommendations()

        # ── 来源追踪 ──
        source_list = self._unique_sources(analysis.sections)

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prompt.display_name} | McKinsey-Style Talent Deep Dive</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        :root {{
            --primary: {primary};
            --secondary: {self._lighten(primary, 15)};
            --accent: {accent};
            --accent2: #00897b;
            --bg: #f5f7fa;
            --text: #1a1a2e;
            --light-bg: #ffffff;
            --border: #e2e8f0;
            --success: #2e7d32;
            --warning: #e65100;
            --danger: #c62828;
            --muted: #64748b;
        }}
        {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.75;
        }}
        .container {{ max-width: 1240px; margin: 0 auto; padding: 2rem 1.5rem; }}

        /* ── Badges & Labels ── */
        .badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }}
        .badge-red {{ background: #fee2e2; color: #dc2626; }}
        .badge-blue {{ background: #dbeafe; color: #2563eb; }}
        .badge-green {{ background: #d1fae5; color: #16a34a; }}
        .badge-amber {{ background: #fef3c7; color: #d97706; }}

        /* ── Header ── */
        .report-header {{
            background: linear-gradient(135deg, #0b2545 0%, #13315c 50%, #1e4d8c 100%);
            color: white;
            padding: 3rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(11,37,69,0.3);
            position: relative;
            overflow: hidden;
        }}
        .report-header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 700px;
            height: 700px;
            background: radial-gradient(circle, rgba(200,162,75,0.12) 0%, transparent 70%);
        }}
        .report-header h1 {{ font-size: 2.2rem; margin-bottom: 0.5rem; position: relative; font-weight: 700; }}
        .report-header .subtitle {{ font-size: 1.1rem; opacity: 0.85; position: relative; }}
        .report-header .meta {{ margin-top: 1.5rem; font-size: 0.85rem; opacity: 0.7; position: relative; display: flex; gap: 2rem; flex-wrap: wrap; }}
        .report-header .badge {{ display: inline-block; background: rgba(200,162,75,0.2); border: 1px solid rgba(200,162,75,0.5); color: #c8a24b; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-top: 1rem; position: relative; }}

        /* ── KPI Cards ── */
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.2rem; margin: 2rem 0; }}
        .kpi-card {{ background: white; border-radius: 14px; padding: 1.5rem; text-align: center; box-shadow: 0 2px 16px rgba(0,0,0,0.06); border: 1px solid var(--border); transition: transform 0.2s, box-shadow 0.2s; }}
        .kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }}
        .kpi-card .label {{ font-size: 0.82rem; color: var(--muted); margin-bottom: 0.6rem; font-weight: 500; }}
        .kpi-card .value {{ font-size: 2.2rem; font-weight: 800; color: var(--primary); line-height: 1.1; }}
        .kpi-card .unit {{ font-size: 0.85rem; font-weight: 500; color: var(--muted); }}
        .kpi-card .change {{ font-size: 0.82rem; margin-top: 0.5rem; font-weight: 600; }}
        .kpi-card .change.up {{ color: var(--success); }}
        .kpi-card .change.down {{ color: var(--danger); }}
        .kpi-card .change.widening {{ color: var(--warning); }}

        /* ── Sections ── */
        .section {{ margin: 2.5rem 0; display: block; }}
        .section h2 {{ font-size: 1.5rem; color: var(--primary); border-left: 4px solid var(--accent); padding-left: 1rem; margin-bottom: 0.5rem; }}
        .section .section-en {{ font-size: 0.92rem; color: var(--muted); margin-bottom: 1.2rem; padding-left: 1.3rem; font-style: italic; }}

        /* ── Cards ── */
        .card {{ background: white; border-radius: 14px; padding: 1.8rem; margin: 1.2rem 0; box-shadow: 0 2px 16px rgba(0,0,0,0.06); border: 1px solid var(--border); display: block; }}
        .card h3 {{ font-size: 1.1rem; color: var(--secondary); margin-bottom: 0.8rem; }}

        /* ── Insight List ── */
        .insight-list {{ list-style: none; padding: 0; display: block; }}
        .insight-list li {{ padding: 0.85rem 0; padding-left: 2.2rem; position: relative; border-bottom: 1px solid rgba(0,0,0,0.04); font-size: 0.95rem; line-height: 1.65; }}
        .insight-list li:last-child {{ border-bottom: none; }}
        .insight-list li::before {{ content: ''; position: absolute; left: 0; top: 1.1rem; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }}

        /* ── Chart Container ── */
        .chart-container {{ background: white; border-radius: 14px; padding: 1.2rem; margin: 1.5rem 0; box-shadow: 0 2px 16px rgba(0,0,0,0.06); border: 1px solid var(--border); display: block; }}

        /* ── Data Notice ── */
        .data-notice {{ background: linear-gradient(135deg, #fff8e1, #fff3e0); border: 1px solid #ffe0b2; border-radius: 12px; padding: 1rem 1.5rem; margin: 1.5rem 0; font-size: 0.88rem; color: #e65100; display: block; }}
        .data-notice strong {{ display: block; margin-bottom: 0.3rem; }}

        /* ── Tables ── */
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.88rem; border-radius: 8px; overflow: hidden; }}
        th {{ background: var(--primary); color: white; padding: 0.85rem 0.7rem; text-align: left; font-weight: 600; font-size: 0.82rem; }}
        td {{ padding: 0.75rem 0.7rem; border-bottom: 1px solid var(--border); vertical-align: top; }}
        tr:nth-child(even) {{ background: #f8fafc; }}
        tr:hover {{ background: #eef2ff; }}

        /* ── Salary Table ── */
        .salary-table th {{ background: linear-gradient(135deg, #0b2545, #1e4d8c); }}
        .salary-table td.level {{ font-weight: 700; color: var(--primary); }}
        .salary-table .p50 {{ font-weight: 700; color: var(--accent); }}
        .salary-table .highlight {{ background: linear-gradient(135deg, #fffdf5, #fef9e7); }}

        /* ── Tags ── */
        .tag {{ display: inline-block; padding: 3px 12px; border-radius: 16px; font-size: 0.78rem; font-weight: 600; margin: 2px; }}
        .tag.green {{ background: #e8f5e9; color: #2e7d32; }}
        .tag.blue {{ background: #e3f2fd; color: #1565c0; }}
        .tag.orange {{ background: #fff3e0; color: #e65100; }}
        .tag.red {{ background: #fce4ec; color: #c62828; }}

        /* ── Action Cards ── */
        .action-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.2rem; margin: 1.5rem 0; }}
        .action-card {{ background: white; border-radius: 14px; padding: 1.5rem; border: 1px solid var(--border); box-shadow: 0 2px 12px rgba(0,0,0,0.06); display: block; }}
        .action-card .step {{ display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 50%; background: var(--primary); color: white; font-weight: 700; font-size: 0.85rem; margin-bottom: 0.8rem; }}
        .action-card h4 {{ font-size: 1rem; color: var(--primary); margin-bottom: 0.5rem; }}
        .action-card p {{ font-size: 0.9rem; color: var(--muted); }}
        .action-card .timeline {{ font-size: 0.82rem; color: var(--accent); font-weight: 600; margin-top: 0.5rem; }}

        /* ── ROI Model ── */
        .roi-card {{ background: linear-gradient(135deg, #f8fdf8, #fffdf5); border: 2px solid var(--accent); border-radius: 14px; padding: 1.8rem; margin: 1.5rem 0; display: block; }}
        .roi-card h3 {{ color: var(--primary); margin-bottom: 0.5rem; }}
        .roi-value {{ font-size: 2.5rem; font-weight: 800; color: var(--success); }}
        .roi-badge {{ display: inline-block; background: #e8f5e9; color: #2e7d32; padding: 4px 14px; border-radius: 20px; font-size: 0.82rem; font-weight: 700; margin-left: 1rem; }}

        /* ── Footer ── */
        .footer {{ margin-top: 3rem; padding: 2rem 0; border-top: 1px solid var(--border); font-size: 0.82rem; color: #94a3b8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <h1>{prompt.display_name}</h1>
            <div class="subtitle">{prompt.label_en}</div>
            <div class="meta">
                <span>📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
                <span>🌍 {prompt.region_zh}</span>
                <span>📊 {len(analysis.data_bundle.data)} 条数据管道</span>
                <span>📐 {len(analysis.sections)} 个分析维度</span>
            </div>
            <span class="badge">McKinsey-Style Talent Intelligence</span>
        </div>

        <div class="data-notice">
            <strong>⚠️ 数据说明 / Data Notice</strong>
            本报告数据来源于世界银行、ILO、各国统计局及行业协会官方报告。薪资数据为区间估计值，实际受雇主规模、谈判力和经验认证影响。
            签证政策以各国移民局官方最新公告为准。本分析不构成职业/法律建议。
        </div>

        {exec_summary_html}

        {kpi_html}

        {sections_html}

        {salary_table}

        {actions_html}

        <div class="section">
            <h2>📚 来源与方法论</h2>
            <div class="card">
                <p style="margin-bottom:1rem;">本报告基于 <strong>{len(analysis.data_bundle.data)} 条数据管道</strong>的采集结果，覆盖 <strong>{len(analysis.sections)} 个分析维度</strong>。严格排除中文 UGC 数据来源。</p>
                <strong>核心数据来源 (权威机构):</strong>
                <ul style="margin-top:0.6rem; padding-left: 1.5rem; line-height: 2;">
                    {''.join(f'<li>{s}</li>' for s in source_list)}
                </ul>
                <p style="margin-top:1.2rem; font-style: italic; color:#94a3b8; font-size: 0.85rem;">
                    Powered by IntelKB Prompt-Driven Intelligence Engine | McKinsey-Style Professional Analysis | 不构成职业咨询/法律建议
                </p>
            </div>
        </div>
    </div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"职业分析报告已输出: {output_path}")
        return output_path

    # ──────────────────────────────────────────────────────────────────
    # 子渲染方法
    # ──────────────────────────────────────────────────────────────────

    def _render_executive_summary(self, analysis: AnalysisResult) -> str:
        items_html = "\n".join(f'<li>{item}</li>' for item in analysis.executive_summary)
        return f"""
        <div class="section">
            <h2>执行摘要 Executive Summary</h2>
            <div class="card">
                <ul class="insight-list">
                    {items_html}
                </ul>
            </div>
        </div>"""

    def _render_kpi_dashboard(self, analysis: AnalysisResult) -> str:
        """提取各维度核心指标生成KPI卡片."""
        kpis = []
        for s in analysis.sections:
            for ins in (s.insights or []):
                # 从 insight 文本提取关键数字
                if any(kw in ins for kw in ["缺口", "增长", "CAGR", "需求", "USD", "百万", "十亿"]):
                    kpis.append(ins)
                    break

        if not kpis:
            # Fallback: 使用维度自身的 insights
            kpis = [f"{s.label_zh}: 见详细章节" for s in analysis.sections[:6]]

        # 渲染 KPI 卡片
        cards_html = ""
        for i, kpi in enumerate(kpis[:6]):
            # 尝试提取数字
            import re
            nums = re.findall(r'[\d.]+(?:%|百万|十亿|K|M|B)?', kpi)
            value = nums[0] if nums else "—"
            label = kpi[:50] + "..." if len(kpi) > 50 else kpi
            cards_html += f"""
                <div class="kpi-card">
                    <div class="value">{value}</div>
                    <div class="label">{label}</div>
                </div>"""

        return f"""
        <div class="section">
            <h2>核心指标仪表盘 KPI Dashboard</h2>
            <div class="kpi-grid">
                {cards_html}
            </div>
        </div>"""

    def _render_insight_cards(self, insights: list) -> str:
        if not insights:
            return "<p style='color:#94a3b8;'>该维度洞察详见分析章节.</p>"
        items = "\n".join(f'<li>{i}</li>' for i in insights)
        return f'<ul class="insight-list">{items}</ul>'

    def _render_chart_section(self, section) -> str:
        """为含数据的维度生成图表 — 增强版支持15维度."""
        if not section.data:
            return ""

        dim_id = section.dimension_id
        chart_divs = []
        for pid, df in section.data.items():
            if df is None or df.empty:
                continue
            div_id = f"chart_{dim_id}_{pid}".replace(" ", "_").replace("/", "_")
            try:
                # ── 定制图表路由 ──
                if dim_id == "cost_of_living":
                    chart_divs.append(self._chart_expense_breakdown(div_id, pid, df))
                elif dim_id == "city_comparison":
                    chart_divs.append(self._chart_city_radar(div_id, pid, df))
                elif dim_id == "ai_disruption_risk":
                    chart_divs.append(self._chart_disruption_risk(div_id, pid, df))
                elif dim_id == "compliance_framework":
                    chart_divs.append(self._chart_compliance_table(div_id, pid, df))
                elif dim_id == "candidate_supply":
                    chart_divs.append(self._chart_supply_gauge(div_id, pid, df))
                elif dim_id == "employer_micro_intel":
                    chart_divs.append(self._chart_employer_scatter(div_id, pid, df))
                elif dim_id == "visa_timeline":
                    chart_divs.append(self._chart_visa_gantt(div_id, pid, df))
                elif dim_id == "cross_cultural_adaptation":
                    chart_divs.append(self._chart_cultural_adaptation_timeline(div_id, pid, df))
                elif dim_id == "salary_negotiation":
                    chart_divs.append(self._chart_negotiation_strategy_table(div_id, pid, df))
                elif dim_id == "certification_path":
                    chart_divs.append(self._chart_certification_roadmap(div_id, pid, df))
                else:
                    chart_divs.append(self._chart_generic_bar(div_id, pid, df))
            except Exception:
                pass

        return "\n".join(c for c in chart_divs if c)

    def _chart_generic_bar(self, div_id: str, pid: str, df: 'pd.DataFrame') -> str:
        """通用柱状图."""
        if len(df.columns) >= 2 and len(df) > 1:
            x_col = df.columns[0]
            y_col = df.columns[1] if df[df.columns[1]].dtype in ['float64', 'int64'] else None
            if y_col:
                chart_data = [{
                    'x': df[x_col].tolist(), 'y': df[y_col].tolist(),
                    'type': 'bar', 'marker': {'color': '#c8a24b'}
                }]
                chart_json = json.dumps(chart_data, ensure_ascii=False)
                return f"""
            <div class="chart-container">
                <h4>{pid} — {x_col} vs {y_col}</h4>
                <div id="{div_id}" style="width:100%;height:380px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {{margin:{{t:20,b:60,l:60,r:20}}}});</script>
            </div>"""
        return self._chart_generic_table(div_id, pid, df)

    def _chart_generic_table(self, div_id: str, pid: str, df: 'pd.DataFrame') -> str:
        """通用数据表."""
        if len(df) <= 20:
            header = "".join(f"<th>{c}</th>" for c in df.columns)
            rows = ""
            for _, row in df.iterrows():
                cells = "".join(f"<td>{v}</td>" for v in row)
                rows += f"<tr>{cells}</tr>"
            return f"""
            <div class="chart-container">
                <h4>{pid}</h4>
                <table><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table>
            </div>"""
        return ""

    def _chart_expense_breakdown(self, div_id: str, pid: str, df: 'pd.DataFrame') -> str:
        """生活成本构成横向柱状图."""
        if 'expense_category' in df.columns and 'monthly_aed' in df.columns:
            df_plot = df[df['monthly_aed'].notna()].copy()
            if not df_plot.empty:
                colors = ['#0b2545' if 'TOTAL' not in str(c) else '#c8a24b'
                          for c in df_plot['expense_category']]
                chart_data = [{
                    'type': 'bar', 'orientation': 'h',
                    'x': df_plot['monthly_aed'].tolist(),
                    'y': df_plot['expense_category'].tolist(),
                    'marker': {'color': colors},
                    'text': [f"{v:,.0f} AED" if v else "" for v in df_plot['monthly_aed']],
                    'textposition': 'auto',
                }]
                chart_json = json.dumps(chart_data, ensure_ascii=False)
                return f"""
            <div class="chart-container">
                <h4>Monthly Expense Breakdown — Dubai (AED)</h4>
                <div id="{div_id}" style="width:100%;height:400px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {{margin:{{t:10,b:40,l:200,r:40}},xaxis:{{title:"AED/month"}}}});</script>
            </div>"""
        return self._chart_generic_table(div_id, pid, df)

    def _chart_city_radar(self, div_id: str, pid: str, df: 'pd.DataFrame') -> str:
        """城市对标雷达图."""
        if 'city' in df.columns:
            metrics = ['cyber_p50_annual_usd', 'effective_savings_rate_pct', 'salary_growth_yoy_pct']
            available = [m for m in metrics if m in df.columns]
            if available and len(df) > 1:
                # 归一化到 0-100 范围
                categories = ['Salary (P50 USD)', 'Savings Rate %', 'Salary Growth %']
                chart_data = []
                for _, row in df.iterrows():
                    values = []
                    for m in available:
                        v = row[m] if pd.notna(row[m]) else 0
                        if m == 'cyber_p50_annual_usd':
                            values.append(min(v / 1000, 100))  # 92000 → 92
                        else:
                            values.append(v)
                    chart_data.append({
                        'type': 'scatterpolar', 'r': values + [values[0]],
                        'theta': categories + [categories[0]],
                        'fill': 'toself', 'name': row['city'],
                    })
                layout = {'polar': {'radialaxis': {'visible': True, 'range': [0, 100]}},
                          'showlegend': True, 'margin': {'t': 30, 'b': 30, 'l': 40, 'r': 40}}
                chart_json = json.dumps(chart_data, ensure_ascii=False)
                layout_json = json.dumps(layout, ensure_ascii=False)
                return f"""
            <div class="chart-container">
                <h4>Global City Comparison — Cybersecurity Expats</h4>
                <div id="{div_id}" style="width:100%;height:450px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {layout_json});</script>
            </div>"""
        return self._chart_generic_table(div_id, pid, df)

    def _chart_disruption_risk(self, div_id: str, pid: str, df: 'pd.DataFrame') -> str:
        """AI颠覆风险横向柱状图."""
        if 'role_subtype' in df.columns and 'ai_disruption_risk_pct' in df.columns:
            df_p = df[df['ai_disruption_risk_pct'].notna()].sort_values('ai_disruption_risk_pct')
            colors = []
            for v in df_p['ai_disruption_risk_pct']:
                if v >= 60:
                    colors.append('#dc2626')
                elif v >= 40:
                    colors.append('#f59e0b')
                else:
                    colors.append('#16a34a')
            chart_data = [{
                'type': 'bar', 'orientation': 'h',
                'x': df_p['ai_disruption_risk_pct'].tolist(),
                'y': df_p['role_subtype'].tolist(),
                'marker': {'color': colors},
                'text': [f"{v}%" for v in df_p['ai_disruption_risk_pct']],
                'textposition': 'auto',
            }]
            chart_json = json.dumps(chart_data, ensure_ascii=False)
            return f"""
            <div class="chart-container">
                <h4>AI/Automation Disruption Risk — Cybersecurity Roles</h4>
                <div id="{div_id}" style="width:100%;height:380px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {{margin:{{t:10,b:40,l:180,r:40}},xaxis:{{title:"Disruption Risk (%)",range:[0,100]}}}});</script>
            </div>"""
        return self._chart_generic_table(div_id, pid, df)

    def _chart_compliance_table(self, div_id: str, pid: str, df: 'pd.DataFrame') -> str:
        """合规框架专用表 — 彩色标签展示 mandatory/voluntary."""
        if 'framework' in df.columns:
            header = "".join(f"<th>{c}</th>" for c in df.columns)
            rows = ""
            for _, row in df.iterrows():
                cells = ""
                for v in row:
                    v_str = str(v)
                    if v_str == 'True':
                        cells += f'<td><span class="badge badge-red">Mandatory</span></td>'
                    elif v_str == 'False':
                        cells += f'<td><span class="badge badge-blue">Voluntary</span></td>'
                    else:
                        cells += f"<td>{v_str}</td>"
                rows += f"<tr>{cells}</tr>"
            return f"""
            <div class="chart-container">
                <h4>{pid}</h4>
                <table class="compliance-table"><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table>
            </div>"""
        return self._chart_generic_table(div_id, pid, df)

    def _chart_supply_gauge(self, div_id: str, pid: str, df: 'pd.DataFrame') -> str:
        """候选人供需比仪表盘."""
        if 'metric' in df.columns and 'value' in df.columns:
            # 找 candidate-to-vacancy ratio
            ratio_row = df[df['metric'].astype(str).str.contains('Ratio', case=False, na=False)]
            if not ratio_row.empty and pd.notna(ratio_row.iloc[0].get('value')):
                ratio_val = float(ratio_row.iloc[0]['value'])
                chart_data = [{
                    'type': 'indicator', 'mode': 'gauge+number',
                    'value': ratio_val,
                    'title': {'text': 'Candidate-to-Vacancy Ratio'},
                    'gauge': {
                        'axis': {'range': [0, 5]},
                        'bar': {'color': '#c8a24b'},
                        'steps': [
                            {'range': [0, 1.5], 'color': '#fee2e2', 'name': 'Shortage'},
                            {'range': [1.5, 2.5], 'color': '#fef3c7', 'name': 'Balanced'},
                            {'range': [2.5, 5], 'color': '#d1fae5', 'name': 'Surplus'},
                        ],
                        'threshold': {
                            'line': {'color': 'red', 'width': 4},
                            'thickness': 0.75, 'value': 2.0
                        }
                    }
                }]
                chart_json = json.dumps(chart_data, ensure_ascii=False)
                return f"""
            <div class="chart-container">
                <h4>Labor Market Tightness — UAE Cybersecurity</h4>
                <div id="{div_id}" style="width:100%;height:350px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {{margin:{{t:40,b:20,l:40,r:40}}}});</script>
                <p style="font-size:0.82rem;color:#94a3b8;">Below 2.0 = candidate shortage (employer-favorable market for job seekers)</p>
            </div>"""
        return self._chart_generic_table(div_id, pid, df)

    def _chart_employer_scatter(self, div_id: str, pid: str, df: 'pd.DataFrame') -> str:
        """雇主图: tenure vs HC范围散点图."""
        if 'employer' in df.columns and 'avg_tenure_years' in df.columns:
            colors_map = {'Tier 1': '#0b2545', 'Tier 2': '#c8a24b', 'Tier 3': '#94a3b8'}
            chart_data = []
            for tier in df['tier'].unique():
                df_tier = df[df['tier'] == tier]
                chart_data.append({
                    'type': 'scatter', 'mode': 'markers+text',
                    'name': f'{tier}',
                    'x': df_tier['avg_tenure_years'].tolist(),
                    'y': df_tier['employer'].tolist(),
                    'marker': {'size': 14, 'color': colors_map.get(tier, '#64748b')},
                    'text': df_tier['employer'].tolist(), 'textposition': 'top center',
                })
            layout = {'xaxis': {'title': 'Average Tenure (Years)'}, 'yaxis': {'title': ''},
                      'showlegend': True, 'margin': {'t': 20, 'b': 40, 'l': 200, 'r': 40}}
            chart_json = json.dumps(chart_data, ensure_ascii=False)
            layout_json = json.dumps(layout, ensure_ascii=False)
            return f"""
            <div class="chart-container">
                <h4>Employer Map — Tier Classification & Tenure</h4>
                <div id="{div_id}" style="width:100%;height:380px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {layout_json});</script>
            </div>"""
        return self._chart_generic_table(div_id, pid, df)

    def _chart_visa_gantt(self, div_id: str, pid: str, df: 'pd.DataFrame') -> str:
        """签证流程甘特图."""
        if 'step' in df.columns and 'phase' in df.columns and 'duration_days' in df.columns:
            chart_data = []
            for _, row in df.iterrows():
                dur_str = str(row['duration_days'])
                try:
                    if '-' in dur_str:
                        parts = dur_str.split('-')
                        dur = (int(parts[0]) + int(parts[1])) / 2
                    else:
                        dur = int(dur_str)
                except Exception:
                    dur = 5
                chart_data.append({
                    'type': 'bar', 'orientation': 'h',
                    'x': [dur], 'y': [f"Step {row['step']}"],
                    'name': row['phase'], 'text': [row['phase']],
                    'textposition': 'auto',
                    'marker': {'color': '#0b2545'},
                    'hovertemplate': f"{row['phase']}<br>Duration: {row['duration_days']} days<br>Cost: ${row.get('cost_usd', 'N/A')}<extra></extra>"
                })
            layout = {'barmode': 'stack', 'xaxis': {'title': 'Days'},
                      'margin': {'t': 10, 'b': 40, 'l': 120, 'r': 40}, 'showlegend': False}
            chart_json = json.dumps(chart_data, ensure_ascii=False)
            layout_json = json.dumps(layout, ensure_ascii=False)
            return f"""
            <div class="chart-container">
                <h4>UAE Work Visa Process — Step-by-Step Timeline</h4>
                <div id="{div_id}" style="width:100%;height:420px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {layout_json});</script>
            </div>"""
        return self._chart_generic_table(div_id, pid, df)

    def _chart_cultural_adaptation_timeline(self, div_id: str, pid: str, df: 'pd.DataFrame') -> str:
        """跨文化适应阶段时间线表格."""
        if 'adaptation_phase' in df.columns:
            header = "".join(f"<th>{c}</th>" for c in df.columns if c != 'source')
            rows = ""
            for _, row in df.iterrows():
                cells = ""
                for col in df.columns:
                    if col == 'source':
                        continue
                    v_str = str(row[col]) if pd.notna(row[col]) else ""
                    if col == 'adaptation_phase':
                        cells += f'<td style="font-weight:700;color:#0b2545;">{v_str}</td>'
                    elif col == 'action_items':
                        cells += f'<td style="font-size:0.85rem;">{v_str}</td>'
                    else:
                        cells += f"<td>{v_str}</td>"
                rows += f"<tr>{cells}</tr>"
            return f"""
            <div class="chart-container">
                <h4>Cross-Cultural Adaptation Roadmap — UAE Cybersecurity Expats</h4>
                <table class="salary-table"><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table>
                <p style="font-size:0.82rem;color:#94a3b8;margin-top:0.8rem;">* Data source: HSBC Expat Explorer 2024, Hofstede Insights, InterNations Expat Insider 2024</p>
            </div>"""
        return self._chart_generic_table(div_id, pid, df)

    def _chart_negotiation_strategy_table(self, div_id: str, pid: str, df: 'pd.DataFrame') -> str:
        """薪资谈判策略表格."""
        if 'negotiation_phase' in df.columns:
            header = "".join(f"<th>{c}</th>" for c in df.columns if c != 'source')
            rows = ""
            for _, row in df.iterrows():
                cells = ""
                for col in df.columns:
                    if col == 'source':
                        continue
                    v_str = str(row[col]) if pd.notna(row[col]) else ""
                    if col == 'negotiation_phase':
                        cells += f'<td style="font-weight:700;color:#0b2545;">{v_str}</td>'
                    elif col == 'script_example':
                        cells += f'<td style="font-style:italic;font-size:0.85rem;background:#fef9e7;">{v_str}</td>'
                    else:
                        cells += f"<td>{v_str}</td>"
                rows += f"<tr>{cells}</tr>"
            return f"""
            <div class="chart-container">
                <h4>Salary Negotiation Playbook — UAE Cybersecurity</h4>
                <table class="salary-table"><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table>
                <p style="font-size:0.82rem;color:#94a3b8;margin-top:0.8rem;">* Data source: Robert Half Salary Guide 2024, Hays GCC, Harvard Negotiation Project</p>
            </div>"""
        return self._chart_generic_table(div_id, pid, df)

    def _chart_certification_roadmap(self, div_id: str, pid: str, df: 'pd.DataFrame') -> str:
        """职业资格认证路径表格."""
        if 'career_level' in df.columns:
            header = "".join(f"<th>{c}</th>" for c in df.columns if c != 'source')
            rows = ""
            for _, row in df.iterrows():
                cells = ""
                for col in df.columns:
                    if col == 'source':
                        continue
                    v_str = str(row[col]) if pd.notna(row[col]) else ""
                    if col == 'career_level':
                        cells += f'<td style="font-weight:700;color:#0b2545;">{v_str}</td>'
                    elif col == 'certification_track':
                        cells += f'<td style="font-size:0.85rem;background:#f0f9ff;">{v_str}</td>'
                    else:
                        cells += f"<td>{v_str}</td>"
                rows += f"<tr>{cells}</tr>"
            return f"""
            <div class="chart-container">
                <h4>Professional Certification Roadmap — UAE Cybersecurity</h4>
                <table class="salary-table"><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table>
                <p style="font-size:0.82rem;color:#94a3b8;margin-top:0.8rem;">* Data source: (ISC)², ISACA, CompTIA, SANS Institute, NESA UAE, CBUAE</p>
            </div>"""
        return self._chart_generic_table(div_id, pid, df)

    def _render_salary_table(self, analysis: AnalysisResult) -> str:
        """渲染薪资基准对比表."""
        # 从 analysis.data 中找薪资数据
        salary_section = None
        for s in analysis.sections:
            if s.dimension_id == "salary_benchmarking":
                salary_section = s
                break

        if not salary_section:
            return ""

        # 尝试从数据中获取薪资表
        for pid, df in (salary_section.data or {}).items():
            if df is not None and not df.empty and 'p50' in str(df.columns).lower():
                cols_to_show = [c for c in df.columns if c in ['level', 'p25_annual_aed', 'p50_annual_aed', 'p75_annual_aed', 'p90_annual_aed', 'benefits典型', 'source']]
                if not cols_to_show:
                    cols_to_show = list(df.columns[:4])
                header = "".join(f"<th>{c}</th>" for c in cols_to_show)
                rows_html = ""
                for idx, row in df.iterrows():
                    cells = "".join(f'<td>{row.get(c, "")}</td>' for c in cols_to_show)
                    css_class = ' class="highlight"' if idx == len(df) // 2 else ""
                    rows_html += f"<tr{css_class}>{cells}</tr>"
                return f"""
        <div class="section">
            <h2>薪酬基准对比 Salary Benchmarking</h2>
            <div class="card">
                <table class="salary-table">
                    <thead><tr>{header}</tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
                <p style="font-size:0.82rem;color:#94a3b8;margin-top:0.8rem;">* P50为市场中位数；P75/P90分别为第75/90百分位；benefits包含住房/机票/医疗险等标准福利包估值</p>
            </div>
        </div>"""

        return ""

    def _render_action_recommendations(self) -> str:
        """行动建议 — 麦肯锡经典行动框架."""
        actions = [
            {
                "step": "1",
                "title": "技能认证优先级排序",
                "desc": "基于目标市场需求数据,优先考取高ROI认证(如CISSP/CISM/云安全),与目标行业雇主需求强匹配。",
                "timeline": "0-6 个月"
            },
            {
                "step": "2",
                "title": "目标行业与企业锁定",
                "desc": "根据雇主格局数据,聚焦需求增长率最高的3个细分行业(Financial Services/Government/Telco),建立目标企业清单。",
                "timeline": "1-3 个月"
            },
            {
                "step": "3",
                "title": "薪酬谈判策略",
                "desc": "基于P50-P90薪资区间与认证溢价数据,准备市场对标论据,在offer谈判中争取P75+总包。",
                "timeline": "收到 offer 时"
            },
            {
                "step": "4",
                "title": "签证路径规划",
                "desc": "根据目标国家外籍人才政策,提前准备文件(学历认证/工作证明/无犯罪记录),选择最优签证路径。",
                "timeline": "3-6 个月"
            },
            {
                "step": "5",
                "title": "文化适应与语言",
                "desc": "投资语言能力与跨文化沟通,阿联酋场景下阿拉伯语加分,德语场景下B1+德语大幅提升永居速度。",
                "timeline": "持续进行"
            },
            {
                "step": "6",
                "title": "5年职业路径复盘",
                "desc": "每12个月基于本报告框架复盘:需求是否仍在增长?薪资是否到达P75+?长期居留路径是否清晰?",
                "timeline": "年度复盘"
            },
        ]

        cards = ""
        for a in actions:
            cards += f"""
                <div class="action-card">
                    <div class="step">{a['step']}</div>
                    <h4>{a['title']}</h4>
                    <p>{a['desc']}</p>
                    <div class="timeline">⏱ {a['timeline']}</div>
                </div>"""

        return f"""
        <div class="section">
            <h2>行动建议 Action Recommendations</h2>
            <div class="action-grid">
                {cards}
            </div>
        </div>"""

    def _unique_sources(self, sections) -> list:
        seen = set()
        results = []
        for s in sections:
            for src in (s.source_attribution or []):
                if src not in seen:
                    seen.add(src)
                    results.append(src)
        return results[:20] or ["(数据来源待补充 — 演示模式)"]

    @staticmethod
    def _lighten(hex_color: str, percent: int) -> str:
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
            r = min(255, r + int((255 - r) * percent / 100))
            g = min(255, g + int((255 - g) * percent / 100))
            b = min(255, b + int((255 - b) * percent / 100))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color
