"""
全球经济动态追踪系统 — Prompt-Driven 架构
================================================
src/
  prompt_registry/   Prompt YAML 加载与校验
  prompt_runtime     Prompt → 调度执行
  data_engine/       管道引擎 (91 条 Pipe)
    pipes/           具体采集管道实现
  renderers/         报告 HTML 渲染器 (7 个)
================================================
"""

__version__ = "3.0.0"
__author__ = "Economic Intelligence System"
