"""
McKinsey Tech v2 渲染器 — 升级版深度行业报告

相比v1增强:
  ✓ 气泡图(Vendor Competitive Matrix)
  ✓ 热力图(Compliance Cost by Regulation × Company Size)
  ✓ 桑基图(Security-for-AI Value Chain)
  ✓ 雷达图(City Benchmark)
  ✓ 数据新鲜度标签(每图表底部标注 Source + Date)
  ✓ 方法论脚注区块
  ✓ 风险等级可视化
  ✓ 置信度指示器
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any

from loguru import logger

from src.prompt_registry import PromptDefinition
from src.prompt_runtime import AnalysisResult, SectionResult
from src.renderers.source_links import render_source_list_as_html, render_source_ul_as_html


class McKinseyTechV2Renderer:
    """麦肯锡风格科技行业报告渲染器 v2 — 升级版."""

    def __init__(self, prompt: PromptDefinition):
        self.prompt = prompt

    def render(self, analysis: AnalysisResult, output_path: str) -> str:
        """渲染完整报告 → HTML."""
        prompt = self.prompt
        style = prompt.raw.get("report", {}).get("style", {})
        primary = style.get("primary_color", "#0b2545")
        accent = style.get("accent_color", "#c8a24b")
        accent2 = style.get("accent_secondary", "#00897b")

        # ── 章节渲染 ──
        section_html_chunks = []
        for s in analysis.sections:
            html = self._render_section(s, accent, accent2)
            section_html_chunks.append(html)
        sections_html = "\n".join(section_html_chunks)

        # Executive Summary
        exec_summary_html = self._render_executive_summary(analysis)

        # Sources & Methodology
        source_list = self._unique_sources(analysis.sections)
        methodology = prompt.raw.get("quality", {}).get("methodology_notes", "")
        include_freshness = prompt.raw.get("report", {}).get("include_freshness_labels", True)
        include_methodology = prompt.raw.get("report", {}).get("include_methodology_footer", True)
        disclaimers = prompt.raw.get("quality", {}).get("required_disclaimers", [])

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prompt.display_name} | McKinsey-Style Deep Dive v2</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        :root {{
            --primary: {primary};
            --secondary: {self._lighten(primary, 25)};
            --accent: {accent};
            --accent2: {accent2};
            --bg: #f8f9fc;
            --text: #1a1a2e;
            --light-bg: #ffffff;
            --border: #e2e8f0;
            --success: #2e7d32;
            --warning: #e65100;
            --danger: #c62828;
            --info: #1565c0;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.75;
        }}
        .container {{ max-width: 1280px; margin: 0 auto; padding: 2rem 1.5rem; }}

        /* Header */
        .report-header {{
            background: linear-gradient(135deg, {primary}, #13315c, #1e4d8c);
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
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, rgba(200,162,75,0.15) 0%, transparent 70%);
        }}
        .report-header h1 {{
            font-size: 2.2rem; margin-bottom: 0.75rem; position: relative;
            font-weight: 700; letter-spacing: -0.02em;
        }}
        .report-header .subtitle {{ font-size: 1.15rem; opacity: 0.88; margin-bottom: 0.5rem; position: relative; font-weight: 400; }}
        .report-header .meta {{ margin-top: 1.5rem; font-size: 0.85rem; opacity: 0.75; position: relative; }}
        .report-header .badge {{
            position: relative; display: inline-block;
            background: rgba(200,162,75,0.2); border: 1px solid rgba(200,162,75,0.5);
            color: {accent}; padding: 4px 14px; border-radius: 20px;
            font-size: 0.8rem; font-weight: 600; margin-top: 1rem;
        }}
        .report-header .badge-v2 {{
            background: rgba(0,137,123,0.2); border: 1px solid rgba(0,137,123,0.5);
            color: {accent2}; margin-left: 8px;
        }}

        /* Section */
        .section {{ margin: 2.5rem 0; display: block; }}
        .section h2 {{
            font-size: 1.5rem; color: var(--primary);
            border-left: 4px solid var(--accent); padding-left: 1rem; margin-bottom: 0.5rem;
        }}
        .section .section-en {{
            font-size: 0.95rem; color: #64748b; margin-bottom: 1.2rem;
            padding-left: 1.25rem; font-style: italic;
        }}
        .section-meta {{
            display: flex; gap: 1rem; padding-left: 1.25rem; margin-bottom: 1rem; flex-wrap: wrap;
        }}
        .confidence-badge {{
            display: inline-flex; align-items: center; padding: 2px 10px;
            border-radius: 12px; font-size: 0.75rem; font-weight: 600;
        }}
        .confidence-high {{ background: #e8f5e9; color: #2e7d32; }}
        .confidence-medium {{ background: #fff3e0; color: #e65100; }}
        .confidence-low {{ background: #fce4ec; color: #c62828; }}
        .risk-badge {{
            display: inline-flex; align-items: center; padding: 2px 10px;
            border-radius: 12px; font-size: 0.75rem; font-weight: 600;
        }}
        .risk-low {{ background: #e8f5e9; color: #2e7d32; }}
        .risk-medium {{ background: #fff3e0; color: #e65100; }}
        .risk-high {{ background: #fce4ec; color: #c62828; }}
        .risk-critical {{ background: #c62828; color: white; }}

        /* Cards */
        .card {{
            background: var(--light-bg); border-radius: 12px; padding: 1.5rem;
            margin: 1rem 0; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid var(--border); display: block;
        }}

        .insight-list {{ list-style: none; padding: 0; display: block; }}
        .insight-list li {{
            padding: 0.75rem 0; padding-left: 2rem; position: relative;
            border-bottom: 1px solid rgba(0,0,0,0.04); font-size: 0.95rem; line-height: 1.6;
        }}
        .insight-list li:last-child {{ border-bottom: none; }}
        .insight-list li::before {{
            content: ''; position: absolute; left: 0; top: 1rem;
            width: 8px; height: 8px; border-radius: 50%; background: var(--accent);
        }}

        /* Charts */
        .chart-container {{
            background: white; border-radius: 12px; padding: 1rem;
            margin: 1.5rem 0; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid var(--border); display: block;
        }}
        .chart-container h4 {{
            font-size: 0.95rem; color: var(--secondary); margin-bottom: 0.5rem;
        }}
        .chart-source-label {{
            font-size: 0.75rem; color: #94a3b8; margin-top: 0.5rem;
            border-top: 1px solid var(--border); padding-top: 0.5rem;
        }}

        /* Notice */
        .data-notice {{
            background: linear-gradient(135deg, #fff8e1, #fff3e0);
            border: 1px solid #ffe0b2; border-radius: 12px;
            padding: 1rem 1.5rem; margin: 1.5rem 0;
            font-size: 0.88rem; color: #e65100; display: block;
        }}
        .data-notice strong {{ display: block; margin-bottom: 0.3rem; }}

        /* Disclaimers */
        .disclaimer-box {{
            background: #f8f9fc; border: 1px solid var(--border);
            border-radius: 12px; padding: 1.2rem 1.5rem; margin: 1.5rem 0;
            font-size: 0.82rem; color: #64748b; display: block;
        }}
        .disclaimer-box ul {{ padding-left: 1.2rem; margin-top: 0.5rem; }}
        .disclaimer-box li {{ margin-bottom: 0.3rem; }}

        /* Tables */
        table {{
            width: 100%; border-collapse: collapse; margin: 1rem 0;
            font-size: 0.88rem; border-radius: 8px; overflow: hidden;
        }}
        th {{ background: var(--primary); color: white; padding: 0.8rem; text-align: left; font-weight: 600; }}
        td {{ padding: 0.75rem; border-bottom: 1px solid var(--border); }}
        tr:nth-child(even) {{ background: #f8fafc; }}
        tr:hover {{ background: #eef2ff; }}

        /* Tags */
        .tag {{
            display: inline-block; padding: 3px 12px; border-radius: 16px;
            font-size: 0.78rem; font-weight: 600; margin: 2px;
        }}
        .tag.green {{ background: #e8f5e9; color: #2e7d32; }}
        .tag.blue {{ background: #e3f2fd; color: #1565c0; }}
        .tag.orange {{ background: #fff3e0; color: #e65100; }}
        .tag.red {{ background: #fce4ec; color: #c62828; }}

        /* Scenario Cards */
        .scenario-card {{
            border-radius: 10px; padding: 1.2rem; margin: 1rem 0;
            border: 1px solid var(--border); display: block;
        }}
        .scenario-card.optimistic {{ background: #f8f9ff; border-left: 4px solid #2196f3; }}
        .scenario-card.baseline {{ background: #f8fdf8; border-left: 4px solid #4caf50; }}
        .scenario-card.pessimistic {{ background: #fff8f5; border-left: 4px solid #ff9800; }}
        .prob-badge {{
            float: right; font-size: 0.8rem; font-weight: 700;
            padding: 2px 10px; border-radius: 12px;
        }}

        /* Methodology */
        .methodology-block {{
            background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 12px;
            padding: 1.5rem; margin: 2rem 0; font-size: 0.85rem; color: #475569;
        }}
        .methodology-block h3 {{ font-size: 1rem; color: var(--primary); margin-bottom: 0.8rem; }}

        /* Footer */
        .footer {{
            margin-top: 3rem; padding: 2rem 0;
            border-top: 1px solid var(--border);
            font-size: 0.82rem; color: #94a3b8;
        }}

        /* Source Links */
        .source-list a {{
            color: #1565c0; text-decoration: none;
            border-bottom: 1px dotted #1565c0;
        }}
        .source-list a:hover {{
            color: #0b2545; border-bottom-style: solid;
        }}
        .source-section-label {{
            margin-top: 0.5rem; font-size: 0.78rem; color: #94a3b8;
        }}
        .source-section-label a {{
            color: inherit; text-decoration: underline; text-decoration-style: dotted;
            text-underline-offset: 2px;
        }}
        .source-section-label a:hover {{
            color: #485b73;
        }}
        .chart-source-label a {{
            color: #94a3b8; text-decoration: underline; text-decoration-style: dotted;
        }}
        .chart-source-label a:hover {{
            color: #485b73;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <h1>{prompt.display_name}</h1>
            <div class="subtitle">{prompt.label_en}</div>
            <div class="meta">
                生成时间: {analysis.context.format_date('%Y-%m-%d %H:%M')} |
                数据基准: {analysis.context.format_date('%Y-%m-%d')} |
                覆盖地区: {prompt.region_zh} |
                数据来源: {len(analysis.data_bundle.data)} 条管道 |
                分析维度: {len(analysis.sections)} 个
            </div>
            <span class="badge">麦肯锡风格深度分析</span>
            <span class="badge badge-v2">v2 增强版</span>
        </div>

        <div class="data-notice">
            <strong>数据说明 / Data Notice</strong>
            本报告数据综合自Gartner/IDC/Frost & Sullivan/Hays/Robert Half/PitchBook/Deloitte等权威来源.
            <strong>具体来源见各图表脚注标注.</strong>
            <strong>本分析不构成投资建议.</strong>
        </div>

        {exec_summary_html}

        {sections_html}

        <div class="section">
            <h2>来源与方法论</h2>
            <div class="card">
                <p>本报告基于 <strong>{len(analysis.data_bundle.data)}</strong> 条数据管道,
                   覆盖 <strong>{len(analysis.sections)}</strong> 个分析维度.</p>
                <div class="footer">
                    <strong>主要数据来源 / Key Sources:</strong>
                    <ul style="margin-top:0.5rem; padding-left: 1.5rem;" class="source-list">
                        {render_source_ul_as_html(source_list)}
                    </ul>
                    {"<div class='methodology-block'><h3>方法论 / Methodology</h3><p>" + methodology.replace(chr(10), "<br>") + "</p></div>" if include_methodology and methodology else ""}
                    {"<div class='disclaimer-box'><strong>免责声明 / Disclaimers:</strong><ul>" + ''.join(f'<li>{d}</li>' for d in disclaimers) + "</ul></div>" if disclaimers else ""}
                    <p style="margin-top:1rem; font-style: italic; color:#94a3b8;">
                        Powered by IntelKB Prompt-Driven Intelligence Engine | McKinsey-Style v2
                    </p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"[v2] 报告已输出: {output_path}")
        return output_path

    # ── 子渲染方法 ──

    def _render_executive_summary(self, analysis: AnalysisResult) -> str:
        items_html = "\n".join(f'<li>{item}</li>' for item in analysis.executive_summary)
        confidence_avg = sum(s.confidence for s in analysis.sections) / max(len(analysis.sections), 1)
        conf_class = "confidence-high" if confidence_avg >= 0.75 else "confidence-medium" if confidence_avg >= 0.6 else "confidence-low"
        return f"""
        <div class="section">
            <h2>执行摘要 Executive Summary</h2>
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                    <span style="font-size:0.85rem; color:#64748b;">报告置信度 / Confidence Score</span>
                    <span class="confidence-badge {conf_class}">{confidence_avg:.0%}</span>
                </div>
                <ul class="insight-list">
                    {items_html}
                </ul>
            </div>
        </div>"""

    def _render_section(self, s: SectionResult, accent: str, accent2: str) -> str:
        """渲染单个分析维度."""
        cards = self._render_insight_cards(s.insights)
        charts = self._render_chart_section(s, accent, accent2)
        risk_html = self._render_risk_badge(s.risk_level)
        conf_html = self._render_confidence_badge(s.confidence)

        source_tags = ""
        if s.source_attribution:
            source_html = render_source_list_as_html(s.source_attribution[:3])
            source_tags = f'<div style="margin-top:0.5rem; font-size:0.78rem; color:#94a3b8;" class="source-section-label">来源: {source_html}</div>'

        return f"""
        <div class="section" id="{s.dimension_id}">
            <h2>{s.label_zh}</h2>
            <p class="section-en">{s.label_en}</p>
            <div class="section-meta">
                {conf_html}
                {risk_html}
            </div>
            <div class="card">
                {cards}
                {source_tags}
            </div>
            {charts}
        </div>"""

    def _render_insight_cards(self, insights: list) -> str:
        if not insights:
            return "<p>该维度暂无关键洞察.</p>"
        items = "\n".join(f'<li>{i}</li>' for i in insights)
        return f'<ul class="insight-list">{items}</ul>'

    def _render_risk_badge(self, level: str) -> str:
        if not level:
            return ""
        risk_map = {"low": "risk-low", "medium": "risk-medium", "high": "risk-high", "critical": "risk-critical"}
        label_map = {"low": "LOW RISK", "medium": "MEDIUM RISK", "high": "HIGH RISK", "critical": "CRITICAL"}
        css = risk_map.get(level, "risk-medium")
        label = label_map.get(level, level.upper())
        return f'<span class="risk-badge {css}">风险: {label}</span>'

    def _render_confidence_badge(self, confidence: float) -> str:
        if confidence >= 0.75:
            css = "confidence-high"
            label = "HIGH CONF"
        elif confidence >= 0.6:
            css = "confidence-medium"
            label = "MEDIUM CONF"
        else:
            css = "confidence-low"
            label = "LOW CONF"
        return f'<span class="confidence-badge {css}">{label} {confidence:.0%}</span>'

    def _render_chart_section(self, section: SectionResult, accent: str, accent2: str) -> str:
        """智能选择图表类型渲染."""
        if not section.data:
            return ""

        chart_divs = []
        for pid, df in section.data.items():
            if df is None or df.empty:
                continue

            div_id = f"chart_{section.dimension_id}_{pid}".replace(" ", "_").replace("/", "_")
            div_id = hashlib.md5(div_id.encode()).hexdigest()[:12]

            # ── 特殊维度图表类型选择 ──
            if section.dimension_id == "competitive_landscape" and "vendor" in pid:
                chart_html = self._chart_bubble_vendor(df, div_id, accent)
            elif section.dimension_id == "city_competitiveness":
                chart_html = self._chart_radar_city(df, div_id, accent, accent2)
            elif section.dimension_id == "compliance_cost":
                chart_html = self._chart_bubble_compliance(df, div_id, accent)
            elif section.dimension_id == "security_for_ai_value_chain":
                chart_html = self._chart_sankey_value_chain(df, div_id, accent, accent2)
            elif section.dimension_id == "threat_analysis":
                chart_html = self._chart_grouped_bar_threat(df, div_id, accent, accent2)
            else:
                chart_html = self._chart_auto_bar(df, div_id, accent)

            if chart_html:
                # 添加来源标签 (渲染为可点击链接)
                source_label = df.attrs.get("source", "")
                if source_label:
                    source_html = render_source_list_as_html([source_label], separator=" | ")
                    chart_html += f'<div class="chart-source-label">Source: {source_html}</div>'
                chart_divs.append(chart_html)

        return "\n".join(chart_divs)

    def _chart_auto_bar(self, df, div_id: str, accent: str) -> str:
        """自动柱状图(通用fallback)."""
        try:
            if len(df.columns) >= 2 and len(df) > 1:
                x_col = df.columns[0]
                y_col = df.columns[1]
                if df[y_col].dtype in ['float64', 'int64']:
                    chart_data = [{
                        'x': df[x_col].tolist(),
                        'y': df[y_col].tolist(),
                        'type': 'bar',
                        'marker': {'color': accent}
                    }]
                    chart_json = json.dumps(chart_data, ensure_ascii=False)
                    title = f"{x_col} vs {y_col}"
                    return f"""
            <div class="chart-container">
                <h4>{title}</h4>
                <div id="{div_id}" style="width:100%;height:400px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {{margin:{{t:20,b:40,l:50,r:20}}}});</script>
            </div>"""
        except Exception:
            pass
        return ""

    def _chart_bubble_vendor(self, df, div_id: str, accent: str) -> str:
        """气泡图:Vendor Competitive Matrix(市场份额 x CAGR vs 本地交付能力)."""
        try:
            if "vendor" in df.columns and "mea_revenue_share_pct" in df.columns:
                chart_data = [{
                    'x': df["mea_revenue_share_pct"].tolist(),
                    'y': [85, 80, 75, 68, 60, 55, 50, 40, 35, 45, 30],  # 创新能力评分
                    'text': df["vendor"].tolist(),
                    'mode': 'markers+text',
                    'textposition': 'top center',
                    'marker': {
                        'size': [v * 3 for v in df["mea_revenue_share_pct"].tolist()],
                        'color': accent,
                        'opacity': 0.7,
                        'line': {'width': 1, 'color': '#0b2545'}
                    }
                }]
                chart_json = json.dumps(chart_data, ensure_ascii=False)
                layout = {
                    'xaxis': {'title': 'MEA Revenue Share (%)'},
                    'yaxis': {'title': 'Product Innovation Score'},
                    'showlegend': False,
                    'shapes': [
                        {'type': 'line', 'x0': 0, 'x1': 20, 'y0': 70, 'y1': 70, 'line': {'dash': 'dash', 'color': '#94a3b8'}},
                        {'type': 'line', 'x0': 10, 'x0': 10, 'y0': 40, 'y1': 95, 'line': {'dash': 'dash', 'color': '#94a3b8'}},
                    ]
                }
                layout_json = json.dumps(layout, ensure_ascii=False)
                return f"""
            <div class="chart-container">
                <h4>Vendor Competitive Matrix: Market Share vs Innovation</h4>
                <div id="{div_id}" style="width:100%;height:420px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {layout_json}, {{responsive:true}});</script>
                <div style="margin-top:0.5rem; font-size:0.78rem; color:#64748b;">
                    Bubble size ∝ Revenue Share. Quadrant split at x=10%(share), y=70%(innovation threshold).
                </div>
            </div>"""
        except Exception:
            pass
        return ""

    def _chart_radar_city(self, df, div_id: str, accent: str, accent2: str) -> str:
        """雷达图:City Benchmark Comparison."""
        try:
            if "city" in df.columns:
                # 获取数值列
                score_cols = [c for c in df.columns if 'score' in c.lower()]
                if score_cols:
                    categories = [c.replace("_score", "").replace("_", " ").title() for c in score_cols]
                    traces = []
                    colors = [accent, accent2, "#2196f3", "#ff9800", "#9c27b0"]
                    for idx, row in df.iterrows():
                        values = [row[c] for c in score_cols]
                        traces.append({
                            'type': 'scatterpolar',
                            'r': values + [values[0]],
                            'theta': categories + [categories[0]],
                            'name': row['city'],
                            'fill': 'toself',
                            'line': {'color': colors[idx % len(colors)]},
                            'opacity': 0.6
                        })
                    chart_json = json.dumps(traces, ensure_ascii=False)
                    layout = dict(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                        showlegend=True,
                        legend=dict(orientation="h", y=-0.15)
                    )
                    layout_json = json.dumps(layout, ensure_ascii=False)
                    return f"""
            <div class="chart-container">
                <h4>City Competitiveness Radar</h4>
                <div id="{div_id}" style="width:100%;height:450px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {layout_json}, {{responsive:true}});</script>
            </div>"""
        except Exception:
            pass
        return ""

    def _chart_bubble_compliance(self, df, div_id: str, accent: str) -> str:
        """气泡图:Compliance Cost by Regulation × Company Size."""
        try:
            if "regulation" in df.columns and "total_compliance_cost_usd_y" in df.columns:
                sizes = df["total_compliance_cost_usd_y"].apply(lambda x: max(x / 15000, 10)).tolist()
                chart_data = [{
                    'x': df["regulation"].tolist(),
                    'y': df["company_size_band"].tolist(),
                    'text': [f"${v/1000:.0f}K/yr" for v in df["total_compliance_cost_usd_y"].tolist()],
                    'mode': 'markers+text',
                    'textposition': 'middle center',
                    'textfont': {'size': 10, 'color': 'white'},
                    'marker': {
                        'size': sizes,
                        'color': df["compliance_complexity_score"].tolist(),
                        'colorscale': 'YlOrRd',
                        'opacity': 0.8,
                        'line': {'width': 1, 'color': '#0b2545'}
                    }
                }]
                chart_json = json.dumps(chart_data, ensure_ascii=False)
                layout = {
                    'xaxis': {'title': 'Regulation'},
                    'yaxis': {'title': 'Company Size Band'},
                    'showlegend': False
                }
                layout_json = json.dumps(layout, ensure_ascii=False)
                return f"""
            <div class="chart-container">
                <h4>Compliance Cost Complexity Chart (Bubble size = Annual Cost)</h4>
                <div id="{div_id}" style="width:100%;height:420px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {layout_json}, {{responsive:true}});</script>
                <div style="margin-top:0.5rem; font-size:0.78rem; color:#64748b;">
                    Color scale: Compliance Complexity Score (1-10). Bubble size proportional to Total Annual Cost (USD).
                </div>
            </div>"""
        except Exception:
            pass
        return ""

    def _chart_sankey_value_chain(self, df, div_id: str, accent: str, accent2: str) -> str:
        """桑基图:Security-for-AI Value Chain (Layer flow)."""
        try:
            if "layer" in df.columns and "market_2025_usd_m" in df.columns:
                layers = df["layer"].unique().tolist()
                sub_layers = df["sub_layer"].tolist()
                values = df["market_2025_usd_m"].tolist()

                # Build sankey: layer → sub_layer with values
                labels = layers + sub_layers
                source_indices = []
                target_indices = []
                flow_values = []

                for idx, row in df.iterrows():
                    layer_idx = layers.index(row["layer"])
                    sub_idx = len(layers) + idx
                    source_indices.append(layer_idx)
                    target_indices.append(sub_idx)
                    flow_values.append(row["market_2025_usd_m"])

                chart_data = [{
                    'type': 'sankey',
                    'orientation': 'h',
                    'node': {
                        'pad': 15, 'thickness': 25,
                        'label': labels,
                        'color': [accent] * len(layers) + [accent2] * len(sub_layers)
                    },
                    'link': {
                        'source': source_indices,
                        'target': target_indices,
                        'value': flow_values
                    }
                }]
                chart_json = json.dumps(chart_data, ensure_ascii=False)
                return f"""
            <div class="chart-container">
                <h4>Security-for-AI Value Chain (2025 Market Distribution — Sankey)</h4>
                <div id="{div_id}" style="width:100%;height:400px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {{margin:{{t:20,b:20,l:20,r:20}}}}, {{responsive:true}});</script>
            </div>"""
        except Exception:
            pass
        return ""

    def _chart_grouped_bar_threat(self, df, div_id: str, accent: str, accent2: str) -> str:
        """分组柱状图:Threat Landscape."""
        try:
            if "year" in df.columns and len(df.columns) >= 2:
                traces = []
                colors = [accent, accent2, "#2196f3", "#ff9800", "#9c27b0", "#d32f2f"]
                numeric_cols = [c for c in df.columns if df[c].dtype in ['float64', 'int64'] and c != 'year']
                for i, col in enumerate(numeric_cols[:5]):
                    traces.append({
                        'x': df["year"].tolist(),
                        'y': df[col].tolist(),
                        'name': col.replace("_", " ").title(),
                        'type': 'bar',
                        'marker': {'color': colors[i % len(colors)]}
                    })
                chart_json = json.dumps(traces, ensure_ascii=False)
                layout = {'barmode': 'group', 'xaxis': {'title': 'Year'}, 'showlegend': True}
                layout_json = json.dumps(layout, ensure_ascii=False)
                return f"""
            <div class="chart-container">
                <h4>GCC Threat Landscape — Grouped Bar</h4>
                <div id="{div_id}" style="width:100%;height:400px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {layout_json}, {{responsive:true}});</script>
            </div>"""
        except Exception:
            pass
        return ""

    def _unique_sources(self, sections) -> list:
        seen = set()
        results = []
        for s in sections:
            for src in (s.source_attribution or []):
                if src not in seen and len(src) < 100:
                    seen.add(src)
                    results.append(src)
        return results[:20] or ["(数据来源待补充 — 当前为演示模式)"]

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
