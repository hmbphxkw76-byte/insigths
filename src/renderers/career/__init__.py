"""
Career Renderers — 海外就业与职业移民报告渲染器

覆盖: 签证追踪、日本司机、通用迁移生命周期、职业分析
对齐: prompts/career/
"""

from src.renderers.career.visa_tracker import VisaTrackerRenderer
from src.renderers.career.japan_driver import JapanDriverRenderer
from src.renderers.career.migration_lifecycle import MigrationLifecycleRenderer
from src.renderers.career.profession_analyzer import ProfessionAnalyzerRenderer

__all__ = [
    "VisaTrackerRenderer",
    "JapanDriverRenderer",
    "MigrationLifecycleRenderer",
    "ProfessionAnalyzerRenderer",
]
