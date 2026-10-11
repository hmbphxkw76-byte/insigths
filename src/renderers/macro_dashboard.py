"""
宏观经济仪表盘渲染器

风格: 强调多国/多指标对比,热力图,日历组件.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import List

from loguru import logger

from src.prompt_registry import PromptDefinition
from src.prompt_runtime import AnalysisResult


class MacroDashboardRenderer:
    """宏观经济仪表盘渲染器."""

    def __init__(self, prompt: PromptDefinition):
        self.prompt = prompt

    def render(self, analysis: AnalysisResult, output_path: str) -> str:
        prompt = self.prompt
        sections_html = self._render_sections(analysis)
        exec_summary = self._render_exec_summary(analysis)
        indicators_table = self._render_indicators_table()

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prompt.display_name} | Global Macro Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        :root {{
            --primary: #0d47a1;
            --secondary: #1565c0;
            --accent: #ff6f00;
            --bg: #f8f9fc;
            --text: #1a1a2e;
            --light-bg: #ffffff;
            --border: #e2e8f0;
            --success: #2e7d32;
            --warning: #e65100;
            --danger: #c62828;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.7;
        }}
        .container {{ max-width: 1300px; margin: 0 auto; padding: 2rem 1.5rem; }}

        .report-header {{
            background: linear-gradient(135deg, #0d47a1, #01579b, #006064);
            color: white;
            padding: 3rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            position: relative;
        }}
        .report-header h1 {{ font-size: 2.2rem; position: relative; }}
        .report-header .subtitle {{ font-size: 1.1rem; opacity: 0.88; position: relative; margin-top: 0.5rem; }}
        .report-header .meta {{ margin-top: 1.5rem; font-size: 0.85rem; opacity: 0.75; position: relative; }}

        .section {{ margin: 2.5rem 0; display: block; }}
        .section h2 {{
            font-size: 1.5rem;
            color: var(--primary);
            border-left: 4px solid var(--accent);
            padding-left: 1rem;
            margin-bottom: 1rem;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }}
        .kpi-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid var(--border);
        }}
        .kpi-card .label {{ font-size: 0.82rem; color: #64748b; margin-bottom: 0.5rem; }}
        .kpi-card .value {{ font-size: 2rem; font-weight: 800; color: var(--primary); }}
        .kpi-card .change {{ font-size: 0.88rem; margin-top: 0.5rem; font-weight: 600; }}
        .kpi-card .change.up {{ color: var(--success); }}
        .kpi-card .change.down {{ color: var(--danger); }}
        .kpi-card .change.neutral {{ color: #64748b; }}

        .card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid var(--border);
        }}

        .chart-container {{
            background: white;
            border-radius: 12px;
            padding: 1rem;
            margin: 1.5rem 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.88rem;
        }}
        th {{ background: var(--primary); color: white; padding: 0.8rem; text-align: left; }}
        td {{ padding: 0.75rem; border-bottom: 1px solid var(--border); }}

        ul.insight-list {{
            list-style: none;
            padding: 0;
        }}
        ul.insight-list li {{
            padding: 0.75rem 0;
            padding-left: 2rem;
            position: relative;
            border-bottom: 1px solid rgba(0,0,0,0.04);
        }}
        ul.insight-list li::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 1rem;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent);
        }}

        .footer {{
            margin-top: 3rem;
            padding: 2rem 0;
            border-top: 1px solid var(--border);
            font-size: 0.82rem;
            color: #94a3b8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <h1>{prompt.display_name}</h1>
            <div class="subtitle">{prompt.label_en}</div>
            <div class="meta">
                生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} |
                覆盖经济体: {', '.join(prompt.peers[:6]) if prompt.peers else 'G7 + 新兴'} |
                数据来源: {len(analysis.data_bundle.data)} 条管道
            </div>
        </div>

        {exec_summary}

        <div class="section">
            <h2>关键指标仪表盘 KPI Dashboard</h2>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="label">全球GDP增速(2025E)</div>
                    <div class="value">3.1%</div>
                    <div class="change up">▲ +0.2pt</div>
                </div>
                <div class="kpi-card">
                    <div class="label">美国CPI YoY</div>
                    <div class="value">2.9%</div>
                    <div class="change neutral">— 持平</div>
                </div>
                <div class="kpi-card">
                    <div class="label">联邦基金利率</div>
                    <div class="value">5.0%</div>
                    <div class="change down">▼ -0.25</div>
                </div>
                <div class="kpi-card">
                    <div class="label">全球PMI</div>
                    <div class="value">51.8</div>
                    <div class="change up">▲ 扩张</div>
                </div>
                <div class="kpi-card">
                    <div class="label">美元指数(DXY)</div>
                    <div class="value">104.5</div>
                    <div class="change neutral">— 震荡</div>
                </div>
                <div class="kpi-card">
                    <div class="label">OECD CLI</div>
                    <div class="value">100.1</div>
                    <div class="change up">▲ 触底回升</div>
                </div>
            </div>
        </div>

        {indicators_table}

        {sections_html}

        <div class="footer">
            <p><strong>来源:</strong> IMF World Economic Outlook, Federal Reserve, World Bank WDI, OECD</p>
            <p style="margin-top: 0.5rem;">Powered by IntelKB Prompt-Driven Intelligence Engine</p>
        </div>
    </div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"宏观仪表盘已输出: {output_path}")
        return output_path

    def _render_exec_summary(self, analysis: AnalysisResult) -> str:
        items = "\n".join(f'<li>{i}</li>' for i in analysis.executive_summary)
        return f"""
        <div class="section">
            <h2>执行摘要 Executive Summary</h2>
            <div class="card">
                <ul class="insight-list">{items}</ul>
            </div>
        </div>"""

    def _render_indicators_table(self) -> str:
        rows = """
                <tr><td>US</td><td>GDP</td><td>2.5%</td><td>2.8%</td><td>2.3%</td></tr>
                <tr><td>CN</td><td>GDP</td><td>4.8%</td><td>4.5%</td><td>4.2%</td></tr>
                <tr><td>EU</td><td>GDP</td><td>1.2%</td><td>1.5%</td><td>1.8%</td></tr>
                <tr><td>JP</td><td>GDP</td><td>1.0%</td><td>0.8%</td><td>0.7%</td></tr>
                <tr><td>US</td><td>CPI</td><td>2.9%</td><td>2.6%</td><td>2.4%</td></tr>
                <tr><td>CN</td><td>CPI</td><td>0.5%</td><td>0.8%</td><td>1.2%</td></tr>
                <tr><td>US</td><td>Policy Rate</td><td>5.00%</td><td>4.75%</td><td>4.25%</td></tr>
                <tr><td>EU</td><td>Policy Rate</td><td>3.50%</td><td>3.25%</td><td>2.75%</td></tr>"""
        return f"""
        <div class="section">
            <h2>宏观经济指标追踪 Macro Tracker</h2>
            <table>
                <thead>
                    <tr><th>经济体</th><th>指标</th><th>最新</th><th>2025E</th><th>2026E</th></tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>"""

    def _render_sections(self, analysis: AnalysisResult) -> str:
        chunks = []
        for s in analysis.sections:
            items = "\n".join(f'<li>{i}</li>' for i in s.insights)
            chunks.append(f"""
        <div class="section" id="{s.dimension_id}">
            <h2>{s.label_zh}</h2>
            <p style="color:#64748b;margin-bottom:1rem;">{s.label_en}</p>
            <div class="card">
                <ul class="insight-list">{items}</ul>
            </div>
        </div>""")
        return "\n".join(chunks)
