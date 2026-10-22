"""
报告日期感知工具 — Report Date Awareness Utility

遵循宪法 v1.6 「反时间幻觉约束」:
  - 所有报告必须基于生产日期为时间基准
  - 禁止使用硬编码年份(如 "2025年"/"2026年") 除非在分析管道回退分析引用语中
  - 所有时间引用必须相对于报告日期进行动态计算

功能:
  - ReportContext: 报告上下文,包含 report_date 和派生时间属性
  - format_relative_date: 将绝对日期格式化为"今年/明年/N年后"等相对表示
  - format_fiscal_quarter: 根据日期生成日本财政季度表示
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class ReportContext:
    """报告日期上下文 — 贯穿整个报告生成管道的时间基准.
    
    属性:
      report_date: 报告生产日期(基准日期)
      report_year: 报告年份
      report_month: 报告月份
      report_quarter: 报告季度 (1-4)
      current_fy: 日本财政年度(4月1日开始)
      next_fy: 下一财政年度
      horizon_years: 前瞻年限(默认3年)
    """
    report_date: datetime
    
    def __init__(self, report_date: Optional[datetime] = None):
        self.report_date = report_date or datetime.now()
        self.report_year = self.report_date.year
        self.report_month = self.report_date.month
        self.report_quarter = (self.report_date.month - 1) // 3 + 1
        # 日本财政年度: 4月1日~次年3月31日
        self.current_fy = self.report_year if self.report_month >= 4 else self.report_year - 1
        self.next_fy = self.current_fy + 1
        self.horizon_years = 3
    
    @property
    def this_year(self) -> int:
        """今年"""
        return self.report_year
    
    @property
    def next_year(self) -> int:
        """明年"""
        return self.report_year + 1
    
    @property
    def two_years_later(self) -> int:
        """后年"""
        return self.report_year + 2
    
    @property
    def three_years_later(self) -> int:
        """大后年"""
        return self.report_year + 3
    
    def year_str(self, offset: int = 0) -> str:
        """获取相对于报告年份的年份字符串,带 'E' (Estimated/预测) 后缀"""
        target_year = self.report_year + offset
        if offset == 0:
            return f"{target_year}年"
        elif offset == 1:
            return f"{target_year}年(E)"
        else:
            return f"{target_year}年(E)"
    
    def quarter_str(self, year_offset: int = 0, quarter: int = 0) -> str:
        """生成季度表示,如 2026-Q4 / 2027-Q1(E)"""
        if quarter == 0:
            quarter = self.report_quarter
        target_year = self.report_year + year_offset
        suffix = "(E)" if year_offset > 0 else ""
        return f"{target_year}-Q{quarter}{suffix}"
    
    def period_str(self, year_offset: int = 0) -> str:
        """生成 IMF WEO 风格的时期标识,如 2026 / 2027E"""
        target_year = self.report_year + year_offset
        suffix = "E" if year_offset > 0 else ""
        return f"{target_year}{suffix}"
    
    def date_tag(self) -> str:
        """生成 YYYYMMDD 日期标签(用于文件名)"""
        return self.report_date.strftime("%Y%m%d")
    
    def format_date(self, fmt: str = "%Y-%m-%d") -> str:
        """格式化报告日期"""
        return self.report_date.strftime(fmt)


def format_relative_year(report_date: datetime, target_year: int) -> str:
    """根据报告日期将目标年份格式化为相对表示.
    
    示例:
      report_date=2026-10-12, target_year=2026 -> "今年(2026年)"
      report_date=2026-10-12, target_year=2027 -> "明年(2027年)"
      report_date=2026-10-12, target_year=2028 -> "后年(2028年)"
      report_date=2026-10-12, target_year=2029 -> "2029年(3年后)"
    """
    delta = target_year - report_date.year
    if delta == 0:
        return f"今年({target_year}年)"
    elif delta == 1:
        return f"明年({target_year}年)"
    elif delta == 2:
        return f"后年({target_year}年)"
    elif delta > 2:
        return f"{target_year}年({delta}年后)"
    elif delta == -1:
        return f"去年({target_year}年)"
    else:
        return f"{target_year}年"


def format_projection_period(report_date: datetime, year_offset: int = 0) -> str:
    """格式化预测时期标识。
    
    示例:
      report_date=2026-10-12, year_offset=0 -> "2026年(今年)"
      report_date=2026-10-12, year_offset=1 -> "2027年(明年,预测)"
      report_date=2026-10-12, year_offset=2 -> "2028年(后年,预测)"
    """
    target_year = report_date.year + year_offset
    if year_offset == 0:
        return f"{target_year}年(最新)"
    elif year_offset == 1:
        return f"{target_year}年(明年,E)"
    elif year_offset == 2:
        return f"{target_year}年(后年,E)"
    else:
        return f"{target_year}年({year_offset}年后,E)"


def get_report_context(report_date: Optional[datetime] = None) -> ReportContext:
    """获取报告上下文工厂函数.
    
    Args:
      report_date: 指定报告日期; 为 None 时使用当前系统时间.
    """
    return ReportContext(report_date)
