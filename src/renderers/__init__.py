"""
Renderer — 报告渲染器

根据 Prompt 的垂直赛道与模板,选择对应的渲染器生成最终报告.

目录结构对齐 prompts/:
  renderers/career/     签证/职业/移民生命周期报告
  renderers/macro/      宏观经济仪表盘
  renderers/realestate/ 房地产深度分析
  renderers/studyabroad/ 留学申请分析
  renderers/tech/       AI/网络安全/半导体 (麦肯锡风格)
"""

from __future__ import annotations

from typing import Dict, Optional
from loguru import logger

from src.prompt_registry import PromptDefinition

# ── 导入各主题域渲染器 ──
from src.renderers.career import (
    VisaTrackerRenderer,
    JapanDriverRenderer,
    MigrationLifecycleRenderer,
    ProfessionAnalyzerRenderer,
)
from src.renderers.macro import MacroDashboardRenderer
from src.renderers.realestate import RealEstateDashboardRenderer
from src.renderers.tech import McKinseyTechRenderer, McKinseyTechV2Renderer

# ── 渲染器注册表 (模板名 → 渲染器类) ──

_RENDERER_MAP: Dict[str, type] = {
    # Career 域
    "visa_tracker": VisaTrackerRenderer,
    "japan_driver": JapanDriverRenderer,
    "migration_lifecycle": MigrationLifecycleRenderer,
    "profession_analyzer": ProfessionAnalyzerRenderer,
    # Macro 域
    "macro_dashboard": MacroDashboardRenderer,
    # Real Estate 域
    "real_estate_dashboard": RealEstateDashboardRenderer,
    # Tech 域
    "mckinsey_tech": McKinseyTechRenderer,
    "mckinsey_tech_v2": McKinseyTechV2Renderer,
    # 留学域 (复用麦肯锡风格渲染器,与 src/renderers/studyabroad 约定一致)
    "study_abroad_analysis": McKinseyTechRenderer,
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
            vertical_fallback = {
                "macro": MacroDashboardRenderer,
                "realestate": RealEstateDashboardRenderer,
                "career": VisaTrackerRenderer,
                "studyabroad": McKinseyTechRenderer,
            }
            cls = vertical_fallback.get(prompt.vertical, McKinseyTechRenderer)

        logger.info(f"选择渲染器: {cls.__name__} (template={template})")
        return cls(prompt)

    @staticmethod
    def register(template_name: str, cls: type):
        """注册自定义渲染器."""
        _RENDERER_MAP[template_name] = cls


def get_renderer(prompt: PromptDefinition):
    """便捷函数."""
    return RendererFactory.get_renderer(prompt)
