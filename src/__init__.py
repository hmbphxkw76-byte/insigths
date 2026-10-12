"""
全球经济动态追踪系统 — Prompt-Driven 架构
================================================
src/
  prompt_registry/   Prompt YAML 加载与校验
  prompt_runtime     Prompt → 调度执行
  data_engine/       管道引擎
    pipes/           具体采集管道 (按主题域分组)
      career/        海外就业・签证移民
      macro/         宏观经济
      realestate/    海外房地产
      studyabroad/   海外留学
      tech/          科技(AI/网络安全/半导体)
  renderers/         报告 HTML 渲染器 (按主题域分组)
    career/          签证/职业/移民生命周期报告
    macro/           宏观经济仪表盘
    realestate/      房地产深度分析
    studyabroad/     留学申请分析
    tech/            AI/网络安全/半导体
================================================
"""

__version__ = "3.0.0"
__author__ = "Economic Intelligence System"
