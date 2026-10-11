"""
Concrete Data Pipe Implementations

每种数据源对应一个 Pipe 子类.
遵循策略: Pipe 只负责"采集到结构化 DataFrame",不做分析/解读.
分析留给 Analyzer 处理.
"""

from typing import Dict
import pandas as pd


FALLBACK_NOTE = (
    "(演示数据 — 实际部署时替换为真实数据源 API / 爬虫 / 手动导入)>"
)


def _fallback_df(columns: list, data: list, source: str = "fallback") -> pd.DataFrame:
    """生成带来源标注的 DataFrame."""
    df = pd.DataFrame(data, columns=columns)
    df["_source"] = source
    df["_is_fallback"] = True
    return df


def _today_str() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")
