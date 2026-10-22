"""
移民签证追踪渲染器

风格: 政策快照,时间线,积分计算器,审批统计.
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from loguru import logger

from src.prompt_registry import PromptDefinition
from src.prompt_runtime import AnalysisResult


class VisaTrackerRenderer:
    """签证追踪渲染器."""

    def __init__(self, prompt: PromptDefinition):
        self.prompt = prompt

    def render(self, analysis: AnalysisResult, output_path: str) -> str:
        prompt = self.prompt
        sections_html = self._render_sections(analysis)
        exec_summary = self._render_exec_summary(analysis)

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prompt.display_name} | Visa Tracker</title>
    <style>
        :root {{
            --primary: #1a237e;
            --secondary: #283593;
            --accent: #d32f2f;
            --bg: #f8f9fc;
            --text: #1a1a2e;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }}

        .report-header {{
            background: linear-gradient(135deg, #1a237e, #283593, #4a148c);
            color: white;
            padding: 3rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
        }}
        .report-header h1 {{ font-size: 2.2rem; }}
        .report-header .meta {{ margin-top: 1rem; font-size: 0.85rem; opacity: 0.75; }}

        .section {{ margin: 2rem 0; }}
        .section h2 {{
            font-size: 1.5rem;
            color: var(--primary);
            border-left: 4px solid var(--accent);
            padding-left: 1rem;
            margin-bottom: 1rem;
        }}

        .card {{ background: white; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; }}
        .card h3 {{ font-size: 1rem; color: var(--secondary); margin-bottom: 0.75rem; }}

        table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
        th {{ background: var(--primary); color: white; padding: 0.8rem; text-align: left; }}
        td {{ padding: 0.75rem; border-bottom: 1px solid #e2e8f0; }}
        tr:nth-child(even) {{ background: #fafafa; }}

        .timeline {{ margin: 1.5rem 0; padding-left: 2rem; border-left: 3px solid var(--primary); }}
        .timeline-item {{ position: relative; margin: 1rem 0; padding-left: 1rem; }}
        .timeline-item::before {{ content: ''; position: absolute; left: -2.45rem; top: 0.4rem; width: 12px; height: 12px; background: var(--accent); border-radius: 50%; }}

        ul.insight-list {{ list-style: none; padding: 0; display: block; }}
        ul.insight-list li {{ padding: 0.5rem 0; padding-left: 1.5rem; position: relative; display: block; }}
        ul.insight-list li::before {{ content: ''; position: absolute; left: 0; top: 0.7rem; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }}

        .scoring-card {{
            background: linear-gradient(135deg, #faf5ff, #f3e5f5);
            border-radius: 10px;
            padding: 1.2rem;
            border: 1px solid #e1bee7;
        }}
        .scoring-row {{ display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(0,0,0,0.05); }}
        .scoring-total {{ font-size: 1.4rem; font-weight: 700; color: var(--primary); margin-top: 1rem; text-align: center; }}
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
            <h2>积分模型 Scoring Model</h2>
            <div class="card scoring-card">
                <h3>日本高度人才(HSP)积分要素</h3>
                <div class="scoring-row"><span>博士学位</span><span>+10分</span></div>
                <div class="scoring-row"><span>Masters/指定专门学位</span><span>+5~10分</span></div>
                <div class="scoring-row"><span>年收1000万日元+</span><span>+10~40分</span></div>
                <div class="scoring-row"><span>年龄29以下</span><span>+15分</span></div>
                <div class="scoring-row"><span>指定大学毕业(QS/THE/ARWU Top300 +日本)</span><span>+10分</span></div>
                <div class="scoring-row"><span>日语N1</span><span>+15分 (80分路径)</span></div>
                <div class="scoring-total">70分=3年永住 | 80分=1年永住</div>
            </div>
        </div>

        <div class="section">
            <h2>永住时间线 PR Roadmap</h2>
            <div class="timeline">
                <div class="timeline-item">
                    <strong>Month 0:</strong> 提交COE申请(在留资格认定证明书)
                </div>
                <div class="timeline-item">
                    <strong>Month 2:</strong> COE获批,换签入境日本
                </div>
                <div class="timeline-item">
                    <strong>Month 12~36:</strong> 维持高度人才身份(70/80分)
                </div>
                <div class="timeline-item">
                    <strong>Year 1~3:</strong> 提交永住申请(80分/70分路径)
                </div>
                <div class="timeline-item">
                    <strong>Year 1.5~4:</strong> 永住获批,永久在留权
                </div>
            </div>
        </div>

        {sections_html}

        <div class="section">
            <p style="font-size:0.82rem; color:#94a3b8; margin-top:2rem;">
                出入国在留管理庁公开数据. 政策以官网最新为准,本分析不构成法律建议.
            </p>
        </div>
    </div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"签证追踪报告已输出: {output_path}")
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
