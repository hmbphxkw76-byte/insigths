"""
宏观数据管道实现

覆盖: IMF WEO, FRED, World Bank, OECD CLI, 经济日历
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict

import pandas as pd
from loguru import logger

from src.data_engine import DataPipe
from src.data_engine.pipes import _fallback_df, FALLBACK_NOTE


class IMFWEOPipe(DataPipe):
    """IMF 世界经济展望(World Economic Outlook)."""

    pipe_id = "imf_weo"

    def collect(self, params: Dict) -> pd.DataFrame:
        from src.data_engine.pipes import _today_str

        economies = params.get("economies", ["US", "CN", "JP", "EU", "UK"])

        # TODO: 接入 IMF WEO REST API (https://www.imf.org/external/datamapper/api/v1/)
        # 当前返回带来源标注的 reference data
        return _fallback_df(
            ["economy", "indicator", "value", "period"],
            [
                ["US", "GDP", 2.5, _today_str()],
                ["CN", "GDP", 4.8, _today_str()],
                ["EU", "GDP", 1.2, _today_str()],
                ["JP", "GDP", 1.0, _today_str()],
            ],
            source="IMF WEO (fallback)"
        )

    def source_attribution(self):
        return ["IMF World Economic Outlook Database"]


class FREDMacroPipe(DataPipe):
    """美联储经济数据(FRED)."""

    pipe_id = "fred_macro"

    def collect(self, params: Dict) -> pd.DataFrame:
        series = params.get("series", ["GDP", "UNRATE", "FEDFUNDS"])
        rows = []
        for s in series:
            rows.append({
                "series_id": s,
                "series_name": s,
                "latest_value": 0.0,
                "period": datetime.now().strftime("%Y-%m"),
            })
        return _fallback_df(
            ["series_id", "series_name", "latest_value", "period"],
            rows,
            source="FRED/St. Louis FED (fallback)"
        )

    def source_attribution(self):
        return ["Federal Reserve Economic Data (FRED)"]


class WorldBankPipe(DataPipe):
    """世界银行发展指标(World Development Indicators)."""

    pipe_id = "worldbank_development"

    def collect(self, params: Dict) -> pd.DataFrame:
        indicators = params.get("indicators", ["NY.GDP.MKPP.KD.ZG"])
        rows = []
        for ind in indicators:
            rows.append({
                "indicator_code": ind,
                "indicator_name": ind[:30],
                "value": 0.0,
                "period": str(datetime.now().year),
            })
        return _fallback_df(
            ["indicator_code", "indicator_name", "value", "period"],
            rows,
            source="World Bank WDI (fallback)"
        )

    def source_attribution(self):
        return ["World Bank Development Indicators"]


class OECDCLIPipe(DataPipe):
    """OECD 综合领先指标(Composite Leading Indicator)."""

    pipe_id = "oecd_cli"

    def collect(self, params: Dict) -> pd.DataFrame:
        return _fallback_df(
            ["economy", "cli_value", "period", "signal"],
            [
                ["US", 99.8, "2025-09", "stable"],
                ["EU", 99.5, "2025-09", "improving"],
                ["CN", 100.2, "2025-09", "expansion"],
                ["JP", 99.3, "2025-09", "stable"],
            ],
            source="OECD CLI (fallback)"
        )

    def source_attribution(self):
        return ["OECD Composite Leading Indicators"]


class EconomicCalendarPipe(DataPipe):
    """经济日历(重要指标发布)."""

    pipe_id = "economic_calendar"

    def collect(self, params: Dict) -> pd.DataFrame:
        importance = params.get("importance", "high")
        lookahead = params.get("lookahead_days", 30)

        # TODO: 接入 Trading Economics / Forex Factory 日历 API
        # 当前返回带来源标注的 reference data
        return _fallback_df(
            ["date", "country", "event", "importance", "forecast", "previous"],
            [
                ["2025-10-15", "US", "Retail Sales (Sep)", "high", "0.3%", "0.4%"],
                ["2025-10-17", "CN", "GDP Q3", "high", "4.5%", "5.2%"],
            ],
            source="Economic Calendar (fallback)"
        )

    def source_attribution(self):
        return ["National Statistics Offices", "Trading Economics"]
