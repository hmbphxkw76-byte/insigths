"""
Study Abroad Renderers — 海外留学报告渲染器
对齐: prompts/studyabroad/

注: 留学报告复用麦肯锡风格渲染器,无需独立渲染器
"""

# 留学报告默认使用 McKinseyTechRenderer
from src.renderers.tech.mckinsey_style import McKinseyTechRenderer as StudyAbroadRenderer

__all__ = ["StudyAbroadRenderer"]
