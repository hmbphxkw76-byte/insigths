"""
Tech Renderers — 科技行业报告渲染器

覆盖: AI、网络安全、半导体
对齐: prompts/tech/
"""

from src.renderers.tech.mckinsey_style import McKinseyTechRenderer
from src.renderers.tech.mckinsey_v2 import McKinseyTechV2Renderer

__all__ = ["McKinseyTechRenderer", "McKinseyTechV2Renderer"]
