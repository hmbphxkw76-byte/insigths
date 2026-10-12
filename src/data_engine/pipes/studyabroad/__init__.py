"""
Study Abroad Domain — 海外留学数据管道

覆盖: 13个国家 × 5条管道(本科/硕士/博士/签证/奖学金)
对齐: prompts/studyabroad/
"""

# 导入模块中所有以Pipe结尾的类
from src.data_engine.pipes.studyabroad import study_abroad_pipes as _mod
import inspect

__all__ = [
    name for name, obj in inspect.getmembers(_mod, inspect.isclass)
    if name.endswith("Pipe") and obj.__module__ == _mod.__name__
]

# 动态导出所有管道类
globals().update({name: getattr(_mod, name) for name in __all__})
