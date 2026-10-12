"""
Macro Domain — 宏观经济数据管道

覆盖: IMF WEO, FRED, World Bank, OECD CLI, 经济日历
对齐: prompts/macro/
"""

from src.data_engine.pipes.macro.macro_pipes import (
    IMFWEOPipe,
    FREDMacroPipe,
    WorldBankPipe,
    OECDCLIPipe,
    EconomicCalendarPipe,
)

__all__ = [
    "IMFWEOPipe",
    "FREDMacroPipe",
    "WorldBankPipe",
    "OECDCLIPipe",
    "EconomicCalendarPipe",
]
