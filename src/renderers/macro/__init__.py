"""
Macro Renderers — 宏观经济报告渲染器
对齐: prompts/macro/
"""

from src.renderers.macro.dashboard import MacroDashboardRenderer
from src.renderers.macro.japan_economy import JapanEconomyRenderer

__all__ = ["MacroDashboardRenderer", "JapanEconomyRenderer"]
