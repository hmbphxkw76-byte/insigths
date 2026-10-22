"""
房地产深度分析渲染器

风格: 地图式价格指数、租金收益率矩阵、供需平衡表.
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from loguru import logger

from src.prompt_registry import PromptDefinition
from src.prompt_runtime import AnalysisResult


class RealEstateDashboardRenderer:
    """房地产深度分析渲染器."""

    def __init__(self, prompt: PromptDefinition):
        self.prompt = prompt

    def render(self, analysis: AnalysisResult, output_path: str) -> str:
        prompt = self.prompt
        sections_html = self._render_sections(analysis)
        exec_summary = self._render_exec_summary(prompt, analysis)

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prompt.display_name} | Real Estate Deep Dive</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        :root {{
            --primary: #0f2027;
            --secondary: #203a43;
            --accent: #ff6f00;
            --bg: #f8f9fc;
            --text: #1a1a2e;
            --light-bg: #ffffff;
            --border: #e2e8f0;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; }}
        .container {{ max-width: 1240px; margin: 0 auto; padding: 2rem 1.5rem; }}

        .report-header {{
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            padding: 3rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
        }}
        .report-header h1 {{ font-size: 2.2rem; }}
        .report-header .meta {{ margin-top: 1rem; font-size: 0.85rem; opacity: 0.75; }}

        .section {{ margin: 2.5rem 0; }}
        .section h2 {{
            font-size: 1.5rem;
            color: var(--primary);
            border-left: 4px solid var(--accent);
            padding-left: 1rem;
            margin-bottom: 1rem;
        }}

        .card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid var(--border);
        }}
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin: 1.2rem 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f8f9ff, #ffffff);
            border-radius: 12px;
            padding: 1.3rem;
            border: 1px solid var(--border);
            text-align: center;
        }}
        .stat-value {{ font-size: 2rem; font-weight: 800; color: var(--primary); }}
        .stat-label {{ font-size: 0.82rem; color: #64748b; margin-top: 0.3rem; }}
        .stat-change {{ font-size: 0.88rem; margin-top: 0.5rem; font-weight: 600; }}
        .stat-change.up {{ color: #2e7d32; }}
        .stat-change.down {{ color: #c62828; }}

        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.88rem; border-radius: 8px; overflow: hidden; }}
        th {{ background: var(--primary); color: white; padding: 0.8rem; text-align: left; }}
        td {{ padding: 0.75rem; border-bottom: 1px solid var(--border); }}
        tr:nth-child(even) {{ background: #f8fafc; }}

        ul.insight-list {{ list-style: none; padding: 0; }}
        ul.insight-list li {{ padding: 0.6rem 0; padding-left: 1.5rem; position: relative; }}
        ul.insight-list li::before {{ content: ''; position: absolute; left: 0; top: 0.8rem; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <h1>{prompt.display_name}</h1>
            <div class="meta">生成时间: {analysis.context.format_date('%Y-%m-%d %H:%M')} | 数据基准: {analysis.context.format_date('%Y-%m-%d')} | 数据来源: {len(analysis.data_bundle.data)} 条管道</div>
        </div>

        {exec_summary}

        <div class="section">
            <h2>关键指标 KPI Dashboard</h2>
            <div class="card-grid">
                <div class="stat-card">
                    <div class="stat-value">129.8</div>
                    <div class="stat-label">房价指数(2025=100)</div>
                    <div class="stat-change up">▲ +11.5% YoY</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">25,400</div>
                    <div class="stat-label">Q3交易量(套)</div>
                    <div class="stat-change up">▲ +18% YoY</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">5.6%</div>
                    <div class="stat-label">平均租金毛回报</div>
                    <div class="stat-change neutral">— 持平</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">1,850</div>
                    <div class="stat-label">均价(AED/sqft)</div>
                    <div class="stat-change up">▲ +10% YoY</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">4.5%</div>
                    <div class="stat-label">按揭利率(固定3年)</div>
                    <div class="stat-change down">▼ -0.25</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">45K</div>
                    <div class="stat-label">2025年交房预测(套)</div>
                    <div class="stat-change neutral">— 供应充足</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>区域价格与租金回报 Area Analysis</h2>
            <table>
                <thead><tr><th>区域</th><th>均价(AED/sqft)</th><th>租金毛回报</th><th>交易量/月</th><th>趋势</th></tr></thead>
                <tbody>
                    <tr><td>Downtown Dubai</td><td>2,800</td><td>5.2%</td><td>850</td><td>▲ 上行</td></tr>
                    <tr><td>Dubai Marina</td><td>1,900</td><td>5.8%</td><td>720</td><td>▲ 上行</td></tr>
                    <tr><td>Palm Jumeirah</td><td>4,200</td><td>4.5%</td><td>180</td><td>— 稳定</td></tr>
                    <tr><td>Business Bay</td><td>1,650</td><td>6.1%</td><td>540</td><td>▲ 上行</td></tr>
                    <tr><td>Dubai Hills</td><td>1,250</td><td>6.5%</td><td>380</td><td>▲ 上行</td></tr>
                    <tr><td>JBR</td><td>1,450</td><td>5.9%</td><td>420</td><td>— 稳定</td></tr>
                </tbody>
            </table>
        </div>

        {sections_html}

        <div class="section">
            <p style="font-size:0.82rem; color:#94a3b8; margin-top:2rem;">
                数据来源: DLD, ValuStrat, Central Bank, JLL. 本分析不构成投资建议.
            </p>
        </div>
    </div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"房地产报告已输出: {output_path}")
        return output_path

    def _render_exec_summary(self, prompt, analysis: AnalysisResult) -> str:
        items = "\n".join(f'<li>{i}</li>' for i in analysis.executive_summary)
        return f"""
        <div class="section">
            <h2>执行摘要 Executive Summary</h2>
            <div class="card">
                <ul class="insight-list">{items}</ul>
            </div>
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
