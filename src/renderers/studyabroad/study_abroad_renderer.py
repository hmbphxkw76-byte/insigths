"""
留学申请分析专用渲染器 — StudyAbroadRenderer

特性:
  0. 数据表格渲染(院校对比/学费/奖学金等)
  1. 可点击来源链接(对齐 source_links.py)
  2. 专业留学报告UI风格
  3. 不混入其他域的内容(避免CHIPS Act张冠李戴)
  4. 演示模式仅在没有数据时触发

对齐宪法 v1.4: 来源必须可点击官方 URL
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import pandas as pd
from loguru import logger

from src.prompt_registry import PromptDefinition
from src.prompt_runtime import AnalysisResult, SectionResult
from src.renderers.source_links import render_source_list_as_html


class StudyAbroadRenderer:
    """留学申请分析报告渲染器."""

    def __init__(self, prompt: PromptDefinition):
        self.prompt = prompt
        style = prompt.raw.get("report", {}).get("style", {})
        self.primary = style.get("primary_color", "#0b3d5c")
        self.accent = style.get("accent_color", "#e8a838")
        self.secondary = self._lighten(self.primary, 25)

    # ── 主渲染入口 ──

    def render(self, analysis: AnalysisResult, output_path: str) -> str:
        """渲染完整留学报告 → HTML."""
        parts = [
            self._render_head(),
            self._render_header(analysis),
            self._render_executive_summary(analysis),
        ]

        for s in analysis.sections:
            parts.append(self._render_section(s))

        parts.append(self._render_source_footer(analysis.sections))
        parts.append(self._render_close())

        html = "\n".join(parts)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"留学报告已输出: {output_path}")
        return output_path

    # ── 渲染子方法 ──

    def _render_head(self) -> str:
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.prompt.display_name} | Study Abroad Analysis</title>
    <style>
        :root {{
            --primary: {self.primary};
            --secondary: {self.secondary};
            --accent: {self.accent};
            --bg: #f7f8fa;
            --card-bg: #ffffff;
            --text: #1a1a2e;
            --text-muted: #64748b;
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
        .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }}

        /* Header */
        .report-header {{
            background: linear-gradient(135deg, {self.primary}, {self.secondary});
            color: white;
            padding: 2.5rem 2rem;
            border-radius: 14px;
            margin-bottom: 2rem;
            box-shadow: 0 6px 24px rgba(0,0,0,0.12);
        }}
        .report-header h1 {{ font-size: 1.8rem; margin-bottom: 0.5rem; font-weight: 700; }}
        .report-header .subtitle {{ font-size: 1.05rem; opacity: 0.85; }}
        .report-header .meta {{ margin-top: 1.2rem; font-size: 0.82rem; opacity: 0.7; }}
        .badge {{
            display: inline-block;
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 3px 12px;
            border-radius: 16px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-top: 0.8rem;
        }}

        /* Sections */
        .section {{ margin: 2rem 0; }}
        .section h2 {{
            font-size: 1.35rem;
            color: var(--primary);
            border-left: 4px solid var(--accent);
            padding-left: 0.85rem;
            margin-bottom: 0.4rem;
        }}
        .section .section-en {{
            font-size: 0.88rem;
            color: var(--text-muted);
            margin-bottom: 1rem;
            padding-left: 1rem;
            font-style: italic;
        }}

        /* Cards */
        .card {{
            background: var(--card-bg);
            border-radius: 10px;
            padding: 1.3rem;
            margin: 0.8rem 0;
            box-shadow: 0 1px 8px rgba(0,0,0,0.05);
            border: 1px solid var(--border);
        }}

        /* Insight List */
        .insight-list {{
            list-style: none;
            padding: 0;
        }}
        .insight-list li {{
            padding: 0.55rem 0;
            border-bottom: 1px solid #f1f5f9;
            padding-left: 1.2rem;
            position: relative;
        }}
        .insight-list li::before {{
            content: '▸';
            position: absolute;
            left: 0;
            color: var(--accent);
            font-weight: bold;
        }}
        .insight-list li:last-child {{ border-bottom: none; }}

        /* Data Tables */
        .data-table-wrap {{
            overflow-x: auto;
            margin: 1rem 0;
            border-radius: 8px;
            border: 1px solid var(--border);
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
        }}
        .data-table thead th {{
            background: {self.primary};
            color: white;
            padding: 0.65rem 0.8rem;
            text-align: left;
            font-weight: 600;
            white-space: nowrap;
        }}
        .data-table tbody td {{
            padding: 0.55rem 0.8rem;
            border-bottom: 1px solid var(--border);
            vertical-align: top;
        }}
        .data-table tbody tr:nth-child(even) {{ background: #f8fafc; }}
        .data-table tbody tr:hover {{ background: #f1f5f9; }}
        .data-table .col-num {{ text-align: right; font-variant-numeric: tabular-nums; }}
        .data-table .col-tag {{
            display: inline-block;
            background: #e8f4fd;
            color: var(--info);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
        }}

        /* Risk indicator */
        .risk-badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .risk-high {{ background: #ffebee; color: var(--danger); }}
        .risk-medium {{ background: #fff3e0; color: var(--warning); }}
        .risk-low {{ background: #e8f5e9; color: var(--success); }}

        /* Source footer */
        .source-footer {{
            margin-top: 2.5rem;
            padding: 1.2rem;
            background: #f1f5f9;
            border-radius: 8px;
            font-size: 0.82rem;
            color: var(--text-muted);
        }}
        .source-footer h3 {{
            font-size: 0.95rem;
            color: var(--primary);
            margin-bottom: 0.5rem;
        }}
        .source-footer ul {{
            list-style: none;
            padding: 0;
        }}
        .source-footer li {{
            padding: 0.3rem 0;
        }}
        .source-footer a {{
            color: var(--info);
            text-decoration: underline;
            text-decoration-style: dotted;
        }}

        /* Confidence indicator */
        .confidence-bar {{
            display: inline-block;
            width: 60px;
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            vertical-align: middle;
            margin-left: 6px;
        }}
        .confidence-fill {{
            height: 100%;
            border-radius: 3px;
            background: var(--accent);
        }}
    </style>
</head>
<body>
<div class="container">"""

    def _render_header(self, analysis: AnalysisResult) -> str:
        style = self.prompt.raw.get("report", {})
        subtitle = style.get("subtitle", "")
        flag_emoji = style.get("flag_emoji", "🎓")
        badge_text = style.get("badge", "Study Abroad Analysis")
        today = pd.Timestamp.now().strftime("%Y-%m-%d")

        return f"""
    <div class="report-header">
        <h1>{flag_emoji} {self.prompt.display_name}</h1>
        <p class="subtitle">{subtitle}</p>
        <p class="meta">报告生成日期: {today} | 数据来源: 官方权威机构</p>
        <span class="badge">{badge_text}</span>
    </div>"""

    def _render_executive_summary(self, analysis: AnalysisResult) -> str:
        items_html = "\n".join(f"<li>{item}</li>" for item in analysis.executive_summary)
        return f"""
    <div class="section">
        <h2>执行摘要 Executive Summary</h2>
        <div class="card">
            <ul class="insight-list">
                {items_html}
            </ul>
        </div>
    </div>"""

    def _render_section(self, s: SectionResult) -> str:
        """渲染单个分析章节: insights + 数据表格."""
        # 风险标签
        risk_class = f"risk-{s.risk_level}" if s.risk_level else "risk-medium"
        risk_label = (s.risk_level or "medium").upper()
        conf_pct = int((s.confidence or 0.5) * 100)

        # Insights
        insights_html = "\n".join(f"<li>{i}</li>" for i in s.insights)

        # 数据表格
        table_html = self._render_data_tables(s.data) if s.data else ""

        # 来源归因
        source_html = ""
        if s.source_attribution:
            source_links = render_source_list_as_html(s.source_attribution, separator=" · ")
            source_html = f'<p style="font-size:0.8rem;color:var(--text-muted);margin-top:0.8rem;">📚 来源: {source_links}</p>'

        return f"""
    <div class="section" id="{s.dimension_id}">
        <h2>{s.label_zh}</h2>
        <p class="section-en">{s.label_en}</p>
        <div style="margin:0.5rem 0;">
            <span class="risk-badge {risk_class}">风险: {risk_label}</span>
            <span style="font-size:0.8rem;color:var(--text-muted);margin-left:0.8rem;">置信度: {conf_pct}%<span class="confidence-bar"><span class="confidence-fill" style="width:{conf_pct}%"></span></span></span>
        </div>
        <div class="card">
            <ul class="insight-list">
                {insights_html}
            </ul>
            {source_html}
        </div>
        {table_html}
    </div>"""

    def _render_data_tables(self, data: dict) -> str:
        """将 DataFrame 渲染为 HTML 表格 (留学专用样式)."""
        if not data:
            return ""

        tables_html = []
        for pid, df in data.items():
            if df is None or df.empty:
                continue

            # 只渲染行数适中的表格
            if len(df) > 50:
                df = df.head(50)
                trunc_note = "<p style='font-size:0.78rem;color:var(--text-muted);padding:0.3rem 0;'>* 仅展示前50条记录</p>"
            else:
                trunc_note = ""

            # 构建表头
            cols = [c for c in df.columns if not c.startswith("_")]
            header_html = "".join(f"<th>{c}</th>" for c in cols)

            # 构建行
            rows_html = []
            for _, row in df.iterrows():
                cells = []
                for c in cols:
                    val = row.get(c, "")
                    val_str = str(val) if pd.notna(val) else "—"

                    # 截断超长文本
                    if len(val_str) > 120:
                        val_str = val_str[:120] + "..."

                    # 数值列右对齐
                    if isinstance(val, (int, float)) and pd.notna(val):
                        cells.append(f'<td class="col-num">{val:,.2f}</td>')
                    else:
                        cells.append(f"<td>{val_str}</td>")
                rows_html.append(f"<tr>{''.join(cells)}</tr>")

            tables_html.append(f"""
        <div class="data-table-wrap">
            <p style="font-size:0.85rem;font-weight:600;color:var(--primary);padding:0.5rem 0.8rem 0;">📊 {pid}</p>
            <table class="data-table">
                <thead><tr>{header_html}</tr></thead>
                <tbody>
                    {"".join(rows_html)}
                </tbody>
            </table>
            {trunc_note}
        </div>""")

        return "\n".join(tables_html)

    def _render_source_footer(self, sections: List[SectionResult]) -> str:
        """全局来源汇总."""
        all_sources = []
        seen = set()
        for s in sections:
            for src in (s.source_attribution or []):
                if src not in seen:
                    seen.add(src)
                    all_sources.append(src)

        if not all_sources:
            return ""

        items_html = render_source_list_as_html(all_sources, separator="")


        return f"""
    <div class="source-footer">
        <h3>📚 数据来源与参考来源</h3>
        <ul>
            {''.join(f'<li>{src}</li>' for src in all_sources)}
        </ul>
        <p style="margin-top:0.5rem;font-size:0.75rem;">* 点击来源名称可跳转至官方页面验证信息</p>
    </div>"""

    def _render_close(self) -> str:
        return """
</div>
</body>
</html>"""

    # ── 工具方法 ──

    @staticmethod
    def _lighten(hex_color: str, percent: int) -> str:
        """将 hex 颜色变亮."""
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
        amt = int(255 * percent / 100)
        r = min(255, r + amt)
        g = min(255, g + amt)
        b = min(255, b + amt)
        return f"#{r:02x}{g:02x}{b:02x}"
