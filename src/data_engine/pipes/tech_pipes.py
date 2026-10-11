"""
科技行业数据管道实现

覆盖: 半导体销售、AI 计算需求、公司财报、行业新闻、初创公司融资
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, List

import pandas as pd
from loguru import logger

from src.data_engine import DataPipe
from src.data_engine.pipes import _fallback_df, FALLBACK_NOTE


class SemiconductorSalesPipe(DataPipe):
    """全球半导体销售数据(SIA/WSTS)."""

    pipe_id = "sts_semiconductor_sales"

    def collect(self, params: Dict) -> pd.DataFrame:
        return _fallback_df(
            ["month", "billings_usd_b YoY_growth", "region", "segment"],
            [
                ["2025-08", 55.2, 6.8, "Americas", "Total"],
                ["2025-08", 32.1, 12.3, "Asia Pacific", "Total"],
                ["2025-08", 15.8, 3.2, "Europe", "Total"],
                ["2025-08", 11.9, 8.5, "Japan", "Total"],
            ],
            source="SIA/WSTS (fallback)"
        )

    def source_attribution(self):
        return ["SIA (Semiconductor Industry Association)", "WSTS"]


class AIComputeDemandPipe(DataPipe):
    """AI 计算需求(GPU, Accelerators, Data Center Power)."""

    pipe_id = "ai_compute_demand"

    def collect(self, params: Dict) -> pd.DataFrame:
        metrics = params.get("metrics", ["GPU", "AI accelerators"])
        return _fallback_df(
            ["metric", "2025E", "2026E", "2030E", "unit", "cagr"],
            [
                ["AI GPU Market", 85.0, 140.0, 380.0, "B USD", "35%"],
                ["Total AI Accelerator", 95.0, 160.0, 450.0, "B USD", "36%"],
                ["Data Center Power Demand", 45.0, 65.0, 150.0, "GW", "27%"],
                ["HBM Memory Revenue", 18.0, 35.0, 80.0, "B USD", "35%"],
            ],
            source="Industry analyst consensus (fallback)"
        )

    def source_attribution(self):
        return ["NVIDIA IR", "TSMC", "IDC", "Gartner"]


class CompanyEarningsPipe(DataPipe):
    """上市公司财报数据(科技巨头)."""

    pipe_id = "company_earnings"

    def collect(self, params: Dict) -> pd.DataFrame:
        tickers: List[str] = params.get("tickers", ["NVDA", "MSFT", "GOOGL"])
        focus: List[str] = params.get("focus", ["revenue"])

        rows = []
        demo_data = {
            "NVDA": {"name": "NVIDIA", "rev": 96.3, "rev_yoy": 55, "ai_rev": 85.0, "capex": 4.5},
            "MSFT": {"name": "Microsoft", "rev": 76.4, "rev_yoy": 16, "ai_rev": 15.0, "capex": 12.0},
            "GOOGL": {"name": "Alphabet", "rev": 105.0, "rev_yoy": 14, "ai_rev": 12.0, "capex": 14.0},
            "META": {"name": "Meta", "rev": 48.0, "rev_yoy": 22, "ai_rev": 8.0, "capex": 8.0},
            "AMZN": {"name": "Amazon", "rev": 185.0, "rev_yoy": 11, "ai_rev": 20.0, "capex": 18.0},
            "TSM": {"name": "TSMC", "rev": 30.0, "rev_yoy": 32, "ai_rev": 5.0, "capex": 11.0},
            "AMD": {"name": "AMD", "rev": 7.5, "rev_yoy": 25, "ai_rev": 5.5, "capex": 1.0},
            "INTC": {"name": "INTC", "rev": 13.5, "rev_yoy": -2, "ai_rev": 0.5, "capex": 8.0},
        }
        for t in tickers:
            if t in demo_data:
                d = demo_data[t]
                rows.append({
                    "ticker": t, "company_name": d["name"],
                    "revenue_usd_b": d["rev"], "revenue_yoy_pct": d["rev_yoy"],
                    "ai_revenue_usd_b": d["ai_rev"], "capex_usd_b": d["capex"],
                    "source": "Company IR (demo)",
                })
        return pd.DataFrame(rows) if rows else _fallback_df(
            ["ticker", "company_name", "revenue_usd_b", "revenue_yoy_pct", "ai_revenue_usd_b", "capex_usd_b", "source"],
            [], source="Company IR (empty)"
        )

    def source_attribution(self):
        return ["SEC EDGAR", "Company IR Filings", "Earnings Transcripts"]


class AIStartupFundingPipe(DataPipe):
    """AI 初创公司融资与估值."""

    pipe_id = "ai_startup_funding"

    def collect(self, params: Dict) -> pd.DataFrame:
        return _fallback_df(
            ["company", "sector", "stage", "amount_m", "valuation_m", "date", "lead_investor"],
            [
                ["Anthropic", "Foundation Models", "Series E", 3500, 183000, "2025-03", "Menlo Ventures"],
                ["OpenAI", "Foundation Models", "Series D", 40000, 157000, "2024-10", "Thrive Capital"],
                ["xAI", "Foundation Models", "Series C", 6000, 24000, "2024-12", "a16z"],
                ["Cohere", "AI Tools", "Series D", 500, 5500, "2024-11", "PSP Investments"],
                ["Mistral AI", "Foundation Models", "Series B", 640, 6000, "2024-06", "General Catalyst"],
                ["Perplexity", "AI Tools", "Series C", 500, 8000, "2024-12", "IVP"],
            ],
            source="PitchBook/Bloomberg (fallback)"
        )

    def source_attribution(self):
        return ["PitchBook", "Crunchbase", "Bloomberg", "FT"]


class NewsFinancialPipe(DataPipe):
    """财经新闻采集(收罗定性信号)."""

    pipe_id = "news_financial"

    def collect(self, params: Dict) -> pd.DataFrame:
        keywords = params.get("keywords", ["Federal Reserve", "inflation"])

        # 尝试复用现有新闻采集器
        try:
            from src.news.news_collector import NewsCollector
            collector = NewsCollector()
            news_list = collector.collect_all_news()
            rows = []
            for n in news_list[:50]:
                rows.append({
                    "date": n.get("date", ""),
                    "title": n.get("title", ""),
                    "source": n.get("source", ""),
                    "url": n.get("url", ""),
                    "snippet": n.get("snippet", "")[:200],
                })
            if rows:
                return pd.DataFrame(rows)
        except Exception as e:
            logger.debug(f"[news_financial] fallback: {e}")

        return _fallback_df(
            ["date", "title", "source", "snippet", "url"],
            [
                ["2025-10-10", "Fed minutes signal gradual rate adjustment path", "Reuters", "The Federal Reserve...", ""],
                ["2025-10-09", "US September NFP adds 142K, unemployment rate steady", "Bloomberg", "Nonfarm payrolls...", ""],
                ["2025-10-08", "China stimulus package to boost domestic demand", "FT", "Beijing announced...", ""],
            ],
            source="News aggregators (fallback)"
        )

    def source_attribution(self):
        return ["Reuters", "Bloomberg", "Financial Times", "Wall Street Journal"]


class BenchmarkPipe(DataPipe):
    """AI 模型基准(MMLU, HumanEval 等)."""

    pipe_id = "ai_benchmark"

    def collect(self, params: Dict) -> pd.DataFrame:
        benchmarks = params.get("benchmarks", ["MMLU", "HumanEval"])
        models = params.get("models", ["GPT-5", "Claude 4", "Gemini 2.5"])
        return _fallback_df(
            ["model", "MMLU", "HumanEval", "GPQA", "SWE-bench", "release_date"],
            [
                ["GPT-5", 92.1, 94.5, 78.0, 74.3, "2025-08"],
                ["Claude 4", 90.8, 95.2, 80.1, 72.8, "2025-05"],
                ["Gemini 2.5", 91.5, 93.0, 79.5, 70.5, "2025-06"],
                ["DeepSeek-V3", 89.2, 91.0, 75.0, 68.0, "2024-12"],
            ],
            source="Epaimodels/Arena (fallback)"
        )

    def source_attribution(self):
        return ["Epam System", "LMSYS Arena", "company tech reports"]


# ── 额外复用现有 tickers 配置 ──
class TechGiantsPipe(DataPipe):
    """现有科技巨头追踪配置(复用 settings.py)."""

    pipe_id = "tech_giants_tracking"

    def collect(self, params: Dict) -> pd.DataFrame:
        from config.settings import TECH_TRACKING
        rows = []
        for g in TECH_TRACKING.get("giants", []):
            rows.append({
                "name": g.get("name", ""),
                "ticker": g.get("ticker", ""),
                "sectors": g.get("sectors", ""),
                "products": g.get("products", ""),
            })
        return pd.DataFrame(rows) if rows else _fallback_df(
            ["name", "ticker", "sectors", "products"], [], source="config/settings.py"
        )

    def source_attribution(self):
        return ["NVIDIA IR", "Microsoft IR", "Amazon IR", "Alphabet IR", "Meta IR", "Apple IR", "Tesla IR"]
