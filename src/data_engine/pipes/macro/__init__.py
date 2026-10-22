"""
Macro Domain — 宏观经济数据管道

覆盖: IMF WEO, FRED, World Bank, OECD CLI, 经济日历
      + 日本经济专属管道 (BoJ政策、宏观统计、外汇、贸易、人口)
对齐: prompts/macro/
"""

from src.data_engine.pipes.macro.macro_pipes import (
    IMFWEOPipe,
    FREDMacroPipe,
    WorldBankPipe,
    OECDCLIPipe,
    EconomicCalendarPipe,
)
from src.data_engine.pipes.macro.japan_macro_pipes import (
    BoJPolicyPipe,
    JapanMacroStatsPipe,
    JapanFXMarketPipe,
    JapanTradeBalancePipe,
    JapanDemographicsPipe,
)

__all__ = [
    # 全球宏观管道
    "IMFWEOPipe",
    "FREDMacroPipe",
    "WorldBankPipe",
    "OECDCLIPipe",
    "EconomicCalendarPipe",
    # 日本经济专属管道
    "BoJPolicyPipe",
    "JapanMacroStatsPipe",
    "JapanFXMarketPipe",
    "JapanTradeBalancePipe",
    "JapanDemographicsPipe",
]
