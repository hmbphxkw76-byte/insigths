"""
McKinsey 风格科技行业渲染器

覆盖: 半导体、AI、网络安全、AI × Security
以 Plotly 交互式图表 + 专业洞察卡片 + 执行摘要块为特点.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional

from loguru import logger

from src.prompt_registry import PromptDefinition
from src.prompt_runtime import AnalysisResult
from src.renderers.source_links import render_source_ul_as_html


class McKinseyTechRenderer:
    """麦肯锡风格科技行业报告渲染器."""

    def __init__(self, prompt: PromptDefinition):
        self.prompt = prompt

    def render(self, analysis: AnalysisResult, output_path: str) -> str:
        """渲染完整报告 → HTML."""
        prompt = self.prompt
        primary = prompt.raw.get("report", {}).get("style", {}).get("primary_color", "#0b2545")
        accent = prompt.raw.get("report", {}).get("style", {}).get("accent_color", "#c8a24b")

        # 章节映射
        section_html_chunks = []
        for s in analysis.sections:
            cards = self._render_insight_cards(s.insights)
            charts = self._render_chart_section(s)
            risk_class = self._risk_class(s.risk_level)
            risk_text = s.risk_level.upper() if s.risk_level else "MEDIUM"
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

        # Executive Summary
        exec_summary_html = self._render_executive_summary(analysis)

        # Source Footer
        source_list = self._unique_sources(analysis.sections)

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prompt.display_name} | McKinsey-Style Deep Dive</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        :root {{
            --primary: {primary};
            --secondary: {self._lighten(primary, 20)};
            --accent: {accent};
            --accent2: #00897b;
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
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem; }}

        .report-header {{
            background: linear-gradient(135deg, #0b2545, #13315c, #1e4d8c);
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
            font-size: 2.2rem;
            margin-bottom: 0.75rem;
            position: relative;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}
        .report-header .subtitle {{
            font-size: 1.15rem;
            opacity: 0.88;
            margin-bottom: 0.5rem;
            position: relative;
            font-weight: 400;
        }}
        .report-header .meta {{
            margin-top: 1.5rem;
            font-size: 0.85rem;
            opacity: 0.75;
            position: relative;
        }}
        .report-header .badge {{
            position: relative;
            display: inline-block;
            background: rgba(200,162,75,0.2);
            border: 1px solid rgba(200,162,75,0.5);
            color: #c8a24b;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 1rem;
        }}

        .section {{ margin: 2.5rem 0; display: block; }}
        .section h2 {{
            font-size: 1.5rem;
            color: var(--primary);
            border-left: 4px solid var(--accent);
            padding-left: 1rem;
            margin-bottom: 0.5rem;
        }}
        .section .section-en {{
            font-size: 0.95rem;
            color: #64748b;
            margin-bottom: 1.2rem;
            padding-left: 1.25rem;
            font-style: italic;
        }}

        .card {{
            background: var(--light-bg);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid var(--border);
            display: block;
        }}
        .card h3 {{
            font-size: 1.1rem;
            color: var(--secondary);
            margin-bottom: 0.75rem;
        }}

        .insight-list {{
            list-style: none;
            padding: 0;
            display: block;
        }}
        .insight-list li {{
            padding: 0.75rem 0;
            padding-left: 2rem;
            position: relative;
            border-bottom: 1px solid rgba(0,0,0,0.04);
            font-size: 0.95rem;
            line-height: 1.6;
        }}
        .insight-list li:last-child {{ border-bottom: none; }}
        .insight-list li::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 1rem;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent);
        }}

        .chart-container {{
            background: white;
            border-radius: 12px;
            padding: 1rem;
            margin: 1.5rem 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid var(--border);
            display: block;
        }}

        .data-notice {{
            background: linear-gradient(135deg, #fff8e1, #fff3e0);
            border: 1px solid #ffe0b2;
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            font-size: 0.88rem;
            color: #e65100;
            display: block;
        }}
        .data-notice strong {{ display: block; margin-bottom: 0.3rem; }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.88rem;
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{ background: var(--primary); color: white; padding: 0.8rem; text-align: left; font-weight: 600; }}
        td {{ padding: 0.75rem; border-bottom: 1px solid var(--border); }}
        tr:nth-child(even) {{ background: #f8fafc; }}
        tr:hover {{ background: #eef2ff; }}

        .tag {{
            display: inline-block;
            padding: 3px 12px;
            border-radius: 16px;
            font-size: 0.78rem;
            font-weight: 600;
            margin: 2px;
        }}
        .tag.green {{ background: #e8f5e9; color: #2e7d32; }}
        .tag.blue {{ background: #e3f2fd; color: #1565c0; }}
        .tag.orange {{ background: #fff3e0; color: #e65100; }}
        .tag.red {{ background: #fce4ec; color: #c62828; }}

        .scenario-card {{
            border-radius: 10px;
            padding: 1.2rem;
            margin: 1rem 0;
            border: 1px solid var(--border);
            display: block;
        }}
        .scenario-card.optimistic {{ background: #f8f9ff; border-left: 4px solid #2196f3; }}
        .scenario-card.baseline {{ background: #f8fdf8; border-left: 4px solid #4caf50; }}
        .scenario-card.pessimistic {{ background: #fff8f5; border-left: 4px solid #ff9800; }}

        .footer {{
            margin-top: 3rem;
            padding: 2rem 0;
            border-top: 1px solid var(--border);
            font-size: 0.82rem;
            color: #94a3b8;
        }}
        .source-list a {{
            color: #1565c0;
            text-decoration: none;
            border-bottom: 1px dotted #1565c0;
        }}
        .source-list a:hover {{
            color: #0b2545;
            border-bottom-style: solid;
        }}
        .footer .sources {{
            margin-top: 1rem;
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
                数据来源: {len(analysis.data_bundle.data)} 条管道
            </div>
            <span class="badge">麦肯锡风格深度分析</span>
        </div>

        <div class="data-notice">
            <strong>数据说明 / Data Notice</strong>
            本报告包含部分演示数据(fallback),实际部署时需接入真实 API / 爬虫 / 行业调研数据.
            <strong>本分析不构成投资建议.</strong>
        </div>

        {exec_summary_html}

        {sections_html}

        <div class="section">
            <h2>来源与方法论</h2>
            <div class="card">
                <p>本报告基于 {len(analysis.data_bundle.data)} 条数据管道的采集结果,覆盖 {len(analysis.sections)} 个分析维度.</p>
                <div class="footer">
                    <strong>主要数据来源:</strong>
                    <ul style="margin-top:0.5rem; padding-left: 1.5rem;" class="source-list">
                        {render_source_ul_as_html(source_list)}
                    </ul>
                    <p style="margin-top:1rem; font-style: italic; color:#94a3b8;">
                        Powered by IntelKB Prompt-Driven Intelligence Engine | McKinsey-Style Analysis (sources clickable)
                    </p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"报告已输出: {output_path}")
        return output_path

    # ── 子渲染方法 ──

    def _render_executive_summary(self, analysis: AnalysisResult) -> str:
        items_html = "\n".join(
            f'<li>{item}</li>' for item in analysis.executive_summary
        )
        return f"""
        <div class="section">
            <h2>执行摘要 Executive Summary</h2>
            <div class="card">
                <ul class="insight-list">
                    {items_html}
                </ul>
            </div>
        </div>"""

    def _render_insight_cards(self, insights: list) -> str:
        if not insights:
            return "<p>该维度暂无关键洞察.</p>"
        items = "\n".join(f'<li>{i}</li>' for i in insights)
        return f'<ul class="insight-list">{items}</ul>'

    def _render_chart_section(self, section) -> str:
        """为含有数据的维度生成 Plotly 图表容器."""
        if not section.data:
            return ""

        chart_divs = []
        for pid, df in section.data.items():
            if df is None or df.empty:
                continue
            div_id = f"chart_{section.dimension_id}_{pid}".replace(" ", "_")
            # 简单折线/柱状图
            try:
                if len(df.columns) >= 2 and len(df) > 1:
                    x_col = df.columns[0]
                    y_col = df.columns[1]
                    if df[y_col].dtype in ['float64', 'int64']:
                        chart_data = [{
                            'x': df[x_col].tolist(),
                            'y': df[y_col].tolist(),
                            'type': 'bar',
                            'marker': {'color': '#c8a24b'}
                        }]
                        chart_json = json.dumps(chart_data, ensure_ascii=False)
                        chart_divs.append(f"""
            <div class="chart-container">
                <h4>{pid} — {x_col} vs {y_col}</h4>
                <div id="{div_id}" style="width:100%;height:400px;"></div>
                <script>Plotly.newPlot("{div_id}", {chart_json}, {{margin:{{t:20,b:40,l:50,r:20}}}});</script>
            </div>""")
            except Exception:
                pass

        return "\n".join(chart_divs)

    def _unique_sources(self, sections) -> list:
        seen = set()
        results = []
        for s in sections:
            for src in (s.source_attribution or []):
                if src not in seen:
                    seen.add(src)
                    results.append(src)
        return results[:15] or ["(数据来源待补充 — 当前为演示模式)"]

    @staticmethod
    def _risk_class(level: str) -> str:
        m = {"low": "success", "medium": "warning", "high": "danger", "critical": "danger"}
        return m.get(level, "gray")

    @staticmethod
    def _lighten(hex_color: str, percent: int) -> str:
        """简单的颜色亮化."""
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
            r = min(255, r + int((255 - r) * percent / 100))
            g = min(255, g + int((255 - g) * percent / 100))
            b = min(255, b + int((255 - b) * percent / 100))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color
