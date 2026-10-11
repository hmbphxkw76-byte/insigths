"""
Renderer — 报告渲染器

根据 Prompt 的垂直赛道与模板,选择对应的渲染器生成最终报告.

已实现的渲染器:
- McKinseyTechRenderer: 科技/半导体/AI/网络安全 (通用麦肯锡风格)
- MacroDashboardRenderer: 宏观经济仪表盘
- RealEstateDashboardRenderer: 房地产深度分析
- VisaTrackerRenderer: 移民签证追踪
"""

from __future__ import annotations

from typing import Dict, Optional
from loguru import logger

from src.prompt_registry import PromptDefinition
from src.renderers.mckinsey_tech import McKinseyTechRenderer
from src.renderers.macro_dashboard import MacroDashboardRenderer
from src.renderers.real_estate import RealEstateDashboardRenderer
from src.renderers.visa_tracker import VisaTrackerRenderer
from src.renderers.japan_driver import JapanDriverRenderer
from src.renderers.migration_lifecycle import MigrationLifecycleRenderer
from src.renderers.profession_analyzer import ProfessionAnalyzerRenderer

# ── 渲染器注册表 ──

_RENDERER_MAP: Dict[str, type] = {
    "mckinsey_tech": McKinseyTechRenderer,
    "macro_dashboard": MacroDashboardRenderer,
    "real_estate_dashboard": RealEstateDashboardRenderer,
    "visa_tracker": VisaTrackerRenderer,
    "japan_driver": JapanDriverRenderer,
    "migration_lifecycle": MigrationLifecycleRenderer,
    "profession_analyzer": ProfessionAnalyzerRenderer,
}


class RendererFactory:
    """渲染器工厂."""

    @classmethod
    def list_templates(cls) -> list:
        """返回所有已注册模板名称."""
        return list(_RENDERER_MAP.keys())

    @staticmethod
    def get_renderer(prompt: PromptDefinition):
        """根据 Prompt 选择渲染器实例."""
        template = prompt.report_template

        cls = _RENDERER_MAP.get(template)
        if not cls:
            # fallback: 基于 vertical 猜测
            if prompt.vertical == "macro":
                cls = MacroDashboardRenderer
            elif prompt.vertical == "realestate":
                cls = RealEstateDashboardRenderer
            elif prompt.vertical == "careers":
                cls = VisaTrackerRenderer
            else:
                cls = McKinseyTechRenderer

        logger.info(f"选择渲染器: {cls.__name__} (template={template})")
        return cls(prompt)

    @staticmethod
    def register(template_name: str, cls: type):
        """注册自定义渲染器."""
        _RENDERER_MAP[template_name] = cls


def get_renderer(prompt: PromptDefinition):
    """便捷函数."""
    return RendererFactory.get_renderer(prompt)
