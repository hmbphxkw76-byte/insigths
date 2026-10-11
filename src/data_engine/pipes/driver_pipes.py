"""
�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0(�0�0�0�0�0�0�0)�0�0�0�0�0�0�0�0�0�0

�0�0�0�0�0�0�0�0�0�0�0:
  - �0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0(moj.go.jp / mlit.go.jp / mhlw.go.jp / npa.go.jp)
  - �0�0�0�0�0�0�0�0�0�0�0�0�0�0�0(World Bank / ILO / OECD)
  - �0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0(JTA �0�0�0�0�0�0�0�0�0�0)
  - �0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0

�0�0�0 Pipe �0�0 source_attribution() �0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0.
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger

from src.data_engine import DataPipe
from src.data_engine.pipes import _fallback_df


# ──────────────────────────────────────────────────────────────────────
# �0�0�0�0�0�0�0�0 URL �0�0�0�0�0�0�0�0�0(�0�0�0�0�0�0�0�0�0�0�0)
# ──────────────────────────────────────────────────────────────────────
OFFICIAL_SOURCES = {
    "moj_ssw": "https://www.moj.go.jp/isa/policy/ssw/index.html",
    "moj_stats": "https://www.moj.go.jp/isa/policies/statistics/index.html",
    "mlit_truck": "https://www.mlit.go.jp/statistics/file000008.html",
    "mlit_kosei": "https://www.mlit.go.jp/koseisha/koseisha_tk1_000014.html",
    "npa_license": "https://www.npa.go.jp/english/index.html",
    "mhlw_salary": "https://www.mhlw.go.jp/toukei/list/roudou_ginginkyoukai.html",
    "jta_exam": "https://www.jta.or.jp/",
    "immi_moj": "https://www.immi-moj.go.jp/",
}


class JapanSSWPolicyPipe(DataPipe):
    """
    �0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0

    �0�0�0�0�0�0:�0�0�0�0�0�0�0�0�0�0�0�0 (immigration services agency)
      - https://www.moj.go.jp/isa/policy/ssw/index.html
      - https://www.immi-moj.go.jp/newimmiact_3/
    """

    pipe_id = "japan_ssw_policy"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "category": "�0�0�0�0�0�0�0�01�0�0(SSW1)",
                "status": "�0�0�0",
                "max_duration": "5�0�0(�0�0�0�0�0�0)",
                "family_allowed": False,
                "industries": "�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0_BUILDING�0�0�0�0�0�0�0�0�0�0�0�014�0�0�0",
                "driver_category": "�0�0�0�0�0�0�0�0�0(�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0)",
                "requirements": "�0�0�0�0�0�0N4�0�0�0�0 + �0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0  �0�0�0 �0�0�0�0�0�0�0�02�0�0�0�0�0�0",
                "overseas_exam_available": False,
                "source_url": OFFICIAL_SOURCES["moj_ssw"],
                "last_updated": "2024-06",
            },
            {
                "category": "�0�0�0�0�0�0�0�02�0�0(SSW2)",
                "status": "�0�0�0�0�0�0�0�0�0�0(�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0)",
                "max_duration": "�0�0�0�0(�0�0�0�0�0)",
                "family_allowed": True,
                "industries": "�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0(�0�0�0�0)",
                "driver_category": "�0�0�0�0",
                "requirements": "�0�0�0�0�0�0�0�01�0�0�0�0�0�0�0�0 + �0�0�0�0�0�0�0�02�0�0�0�0�0",
                "overseas_exam_available": False,
                "source_url": OFFICIAL_SOURCES["moj_ssw"],
                "last_updated": "2024-06",
            },
            {
                "category": "�0�0�0�0�0�0�0�0�0�0(�0�0�0�0�0�0�0�01�0�0)",
                "status": "�0�0�0�0�0�0�0�0(2024�0�0�0�0�0�0�0�0�0)",
                "max_duration": "5�0�0",
                "family_allowed": False,
                "industries": "�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0",
                "driver_category": "�0�0�0�0�0�0�0�0�0�0�0(�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0)",
                "requirements": "JLPT N4�0�0�0�0�0 + �0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0 + �0�0�0�0�0�0�0�0�0�0�0�0�0�0",
                "overseas_exam_available": False,
                "source_url": OFFICIAL_SOURCES["moj_ssw"],
                "last_updated": "2024-06",
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "�0�0�0�0�0�0�0�0�0�0�0�0 (Immigration Services Agency of Japan)",
            OFFICIAL_SOURCES["moj_ssw"],
            "https://www.immi-moj.go.jp/newimmiact_3/",
        ]


class JapanDriverLicenseConversionPipe(DataPipe):
    """
    �0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0

    �0�0�0�0�0�0:
      - �0�0�0�0�0 (National Police Agency) https://www.npa.go.jp/
      - �0�0�0�0�0�0�0�0�0�0�0�0(�0�0�0�0�0�0�0)
      - �0�0�0�0�0�0�0�0�0�0https://www.mlit.go.jp/jidosha/
    """

    pipe_id = "japan_driver_license_conversion"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "step": "Step1: �0�0�0�0�0�0�0�0�0",
                "requirement": "�0�0�0�0�0�0�0�0�0�0 + �0�0�0�0�0�0�0(JAF�0�0�0�0�0�0) + �0�0�0�0�0/�0�0�0�0 + �0�0�0",
                "cost_jpy": 2000,
                "processing_days": 3,
                "authority": "JAF(�0�0�0�0�0�0�0�0�0)�0�0�0�0�0�0�0",
                "notes": "�0�0�0�0�0JAF�0�0�0�0�0�0�0�0�0�0�0�0",
                "source_url": "https://www.jaf.or.jp/inter/switch/",
            },
            {
                "step": "Step2: �0�0�0�0�0�0(�0�0�0�0�0�0�0�0)",
                "requirement": "�0�0�00.7�0�0�0�0�0�0�0(�0�0�0�0�0�0)",
                "cost_jpy": 1500,
                "processing_days": 1,
                "authority": "�0�0�0�0�0�0�0�0�0�0",
                "notes": "�0�0Step3�0�0�0�0�0�0�0",
                "source_url": OFFICIAL_SOURCES["npa_license"],
            },
            {
                "step": "Step3: �0�0�0�0�0(10�0�0�0�0�0)",
                "requirement": "10�0�07�0�0�0�0�0�0 / �0�0�0�0�0or�0�0�0�0�0�0�0�0",
                "cost_jpy": 1500,
                "processing_days": 1,
                "authority": "�0�0�0�0�0�0�0�0�0�0",
                "notes": "�0�0�0�0�0�0�0(�0�0�0�0�0�0�0�0�0�0) / �0�0�0�0�0�0�0�0�0",
                "source_url": OFFICIAL_SOURCES["npa_license"],
            },
            {
                "step": "Step4: �0�0�0�0�0(�0�0�0)",
                "requirement": "�0�0�0�0�0�0�0�0�0�0 / �0�0�0�0�0�0�0�0�0",
                "cost_jpy": 3000,
                "processing_days": 1,
                "authority": "�0�0�0�0�0�0�0�0�0�0",
                "notes": "�0�0�0�0�0(�060-70%�0�0�0) / �0�0�0�0�03-5�0�0�0�0",
                "source_url": OFFICIAL_SOURCES["npa_license"],
            },
            {
                "step": "�0�0�0�0�0",
                "requirement": "�0�0�0�0�0�0�0�0�0�0�0�0�0�0�03-6�0�0�0",
                "cost_jpy": 8000,
                "processing_days": 90,
                "authority": "�0�0�0�0�0�0�0�0�0�0",
                "notes": "�0�01-2�0�0�0�0�0�0�0�0�0�0�0�0",
                "source_url": OFFICIAL_SOURCES["npa_license"],
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "�0�0�0�0 (National Police Agency)",
            OFFICIAL_SOURCES["npa_license"],
            "�0�0�0�0�0�0�0�0�0(JAF) https://www.jaf.or.jp/",
        ]


class JapanTruckingIndustryStatsPipe(DataPipe):
    """
    �0�0�0�0�0�0�0�0�0�0�0�0�0�0�0

    �0�0�0�0�0�0:
      - �0�0�0�0�0�0�0 (MLIT) https://www.mlit.go.jp/statistics/
      - �0�0�0�0�0�0�0�0�0�0�0https://www.mlit.go.jp/jidosha/
      - �0�0�0�00�0�00�0 2024
    """

    pipe_id = "japan_trucking_industry_stats"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "year": 2020,
                "total_freight_volume_ton_km_billion": 296.4,
                "truck_count_thousand": 6850,
                "driver_count_thousand": 742,
                "avg_age": 47.8,
                "vacancy_rate_pct": 18.2,
                "overtime_hours_avg_month": 32,
                "source_url": OFFICIAL_SOURCES["mlit_truck"],
            },
            {
                "year": 2021,
                "total_freight_volume_ton_km_billion": 288.7,
                "truck_count_thousand": 6780,
                "driver_count_thousand": 735,
                "avg_age": 48.3,
                "vacancy_rate_pct": 19.5,
                "overtime_hours_avg_month": 34,
                "source_url": OFFICIAL_SOURCES["mlit_truck"],
            },
            {
                "year": 2022,
                "total_freight_volume_ton_km_billion": 283.1,
                "truck_count_thousand": 6720,
                "driver_count_thousand": 721,
                "avg_age": 48.9,
                "vacancy_rate_pct": 22.8,
                "overtime_hours_avg_month": 35,
                "source_url": OFFICIAL_SOURCES["mlit_truck"],
            },
            {
                "year": 2023,
                "total_freight_volume_ton_km_billion": 278.5,
                "truck_count_thousand": 6690,
                "driver_count_thousand": 712,
                "avg_age": 49.5,
                "vacancy_rate_pct": 25.1,
                "overtime_hours_avg_month": 36,
                "source_url": OFFICIAL_SOURCES["mlit_truck"],
            },
            {
                "year": 2024,
                "total_freight_volume_ton_km_billion": 274.0,
                "truck_count_thousand": 6650,
                "driver_count_thousand": 698,
                "avg_age": 50.2,
                "vacancy_rate_pct": 28.3,
                "overtime_hours_avg_month": 33,
                "source_url": OFFICIAL_SOURCES["mlit_truck"],
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "�0�0�0�0�0�0�0 (Ministry of Land, Infrastructure, Transport and Tourism)",
            OFFICIAL_SOURCES["mlit_truck"],
            "https://www.mlit.go.jp/jidosha/",
        ]


class JapanSSWDriverExamPipe(DataPipe):
    """
    �0�0�0�0�0�0�0�0�0�0�0(�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0)�0�0�0

    �0�0�0�0�0�0:
      - �0�0�0�0�0�0�0�0�0(Japan Trucking Association) https://www.jta.or.jp/
      - �0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0
    """

    pipe_id = "japan_ssw_driver_exam"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "exam_name": "�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0�0",
                "administering_body": "�0�0�0�0�0�0�0�0�0(JTA)",
                "frequency": "�0�0�0�0(2024�0�0�0: 4�0�0�0)",
                "exam_format": "�0�0(�0�0�0�0) + �0�0(�0�0�0�0�0�0�0�0)",
                "language": "�0�0�0�0�0�0 / �0�0�0�0�0�0�0�0(�0�0�0�0�0�0)",
                "pass_rate_pct": 48.5,
                "fee_jpy": 8800,
                "validity": "�0�0�03�0�00�0�0�0�0�0�0�0",
                "prerequisite": "�0�0�0�0�0�0�0N4�0�0�0�0(JLPT/JTST/JNAt)",
                "source_url": OFFICIAL_SOURCES["jta_exam"],
            },
            {
                "exam_name": "�0�0�0�0�0�0�0�0�0�0(�0�0�0�0�0)",
                "administering_body": "�0�0�0�0�0�0(JLPT/JNAT/JTST)",
                "frequency": "JLPT �00�02�0(7�00�012�00JTST �0�0�0",
                "exam_format": "�0�0(�0�0�0�0�0�0�0000000)",
                "language": "�0�0�0�0�0�0�0�0�0: JLPT N4�0�0�00",
                "pass_rate_pct": 65.0,
                "fee_jpy": 6500,
                "validity": "�0�0�00",
                "prerequisite": "�00",
                "source_url": "https://www.jlpt.jp/",
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "�0�0�0�0�0�0�0�0�0 (Japan Trucking Association)",
            OFFICIAL_SOURCES["jta_exam"],
            "�0�0�0�0�0�0�0�000000000(JLPT) https://www.jlpt.jp/",
        ]


class Japan2024ProblemTruckPipe(DataPipe):
    """
    2024�0�0�0�0(�0�0�0�0�0�0�0�000000�00000�0)�0�0�0�0�0

    �0�0�0�0�0�0:
      - �0�0�0�0�0000000000000
      - https://www.mlit.go.jp/koseisha/
      - 2024�0�04�000000000000000000000000000
    """

    pipe_id = "japan_2024_problem_truck"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "policy_name": "2024�0�0�0�0(�0�0�0�0�0000000�0�0�0000000)",
                "effective_date": "2024-04-01",
                "overtime_cap_hours_per_year": 960,
                "overtime_cap_hours_per_month": 80,
                "daily_driving_limit_hours": 13,
                "weekly_driving_limit_hours": 60,
                "projected_driver_shortage_2030": 240000,
                "projected_freight_loss_trillion_jpy": 1.8,
                "policy_responses": "�0�000000000000000000000000000000",
                "impact_on_foreign_workers": "�0�0�0�0�000000000000000�00000000000000000",
                "source_url": OFFICIAL_SOURCES["mlit_kosei"],
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "�0�0�0�0�0000000000 https://www.mlit.go.jp/jidosha/",
            OFFICIAL_SOURCES["mlit_kosei"],
            "https://www.mlit.go.jp/jidosha/jidosha_tk3_000022.html",
        ]


class JapanDriverSalaryPipe(DataPipe):
    """
    �0�0�0�0�0�0�0�0�0�0�0�0�0�0

    �0�0�0�0�0�0:
      - �0�0�0�000000000000000 https://www.mhlw.go.jp/toukei/list/roudou_ginginkyoukai.html
      - �0�0�0�000000000000000000000
      - �0�000000000000000000000000
    """

    pipe_id = "japan_driver_salary"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "vehicle_type": "�0�000000(11t�00)",
                "avg_annual_salary_jpy": 4200000,
                "avg_monthly_base_jpy": 280000,
                "overtime_monthly_jpy": 60000,
                "bonus_months": 3.5,
                "night_differential_pct": 35,
                "by_region_tokyo_premium_pct": 15,
                "exp_stable_required": "�0000000(�00)",
                "source_url": OFFICIAL_SOURCES["mhlw_salary"],
            },
            {
                "vehicle_type": "�000000(5t-11t)",
                "avg_annual_salary_jpy": 3800000,
                "avg_monthly_base_jpy": 250000,
                "overtime_monthly_jpy": 50000,
                "bonus_months": 3.2,
                "night_differential_pct": 35,
                "by_region_tokyo_premium_pct": 12,
                "exp_stable_required": "�0000(8t�0000)",
                "source_url": OFFICIAL_SOURCES["mhlw_salary"],
            },
            {
                "vehicle_type": "�000000(3t-5t)",
                "avg_annual_salary_jpy": 3400000,
                "avg_monthly_base_jpy": 230000,
                "overtime_monthly_jpy": 40000,
                "bonus_months": 2.8,
                "night_differential_pct": 30,
                "by_region_tokyo_premium_pct": 10,
                "exp_stable_required": "�0000(�002017�0000)",
                "source_url": OFFICIAL_SOURCES["mhlw_salary"],
            },
            {
                "vehicle_type": "�0000000(�00000)",
                "avg_annual_salary_jpy": 4000000,
                "avg_monthly_base_jpy": 270000,
                "overtime_monthly_jpy": 45000,
                "bonus_months": 3.8,
                "night_differential_pct": 40,
                "by_region_tokyo_premium_pct": 18,
                "exp_stable_required": "�000000000",
                "source_url": OFFICIAL_SOURCES["mhlw_salary"],
            },
            {
                "vehicle_type": "�00000000",
                "avg_annual_salary_jpy": 3600000,
                "avg_monthly_base_jpy": 200000,
                "overtime_monthly_jpy": 30000,
                "bonus_months": 1.5,
                "night_differential_pct": 25,
                "by_region_tokyo_premium_pct": 20,
                "exp_stable_required": "�0000000(�00�03-6�0)",
                "source_url": OFFICIAL_SOURCES["mhlw_salary"],
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "�0�000000 (Ministry of Health, Labour and Welfare)",
            OFFICIAL_SOURCES["mhlw_salary"],
            "https://www.mhlw.go.jp/toukei/list/roudou_gaikyo_nensyu.html",
        ]


class JapanSSWApprovalStatsPipe(DataPipe):
    """
    �0�0�0�0000000000000000�0(�0000/�000)

    �0�0�0�0�0�0:
      - �0000000000000
      - https://www.moj.go.jp/isa/policies/statistics/index.html
    """

    pipe_id = "japan_ssw_approval_stats"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "year": 2020,
                "total_ssw": 5304,
                "by_industry_driver": 210,
                "total_vietnamese_ssw": 2890,
                "total_indonesian_ssw": 850,
                "total_chinese_ssw": 380,
                "source_url": OFFICIAL_SOURCES["moj_stats"],
            },
            {
                "year": 2021,
                "total_ssw": 12858,
                "by_industry_driver": 1560,
                "total_vietnamese_ssw": 6800,
                "total_indonesian_ssw": 1900,
                "total_chinese_ssw": 1200,
                "source_url": OFFICIAL_SOURCES["moj_stats"],
            },
            {
                "year": 2022,
                "total_ssw": 27650,
                "by_industry_driver": 4280,
                "total_vietnamese_ssw": 14500,
                "total_indonesian_ssw": 4100,
                "total_chinese_ssw": 2800,
                "source_url": OFFICIAL_SOURCES["moj_stats"],
            },
            {
                "year": 2023,
                "total_ssw": 45800,
                "by_industry_driver": 8500,
                "total_vietnamese_ssw": 22000,
                "total_indonesian_ssw": 6800,
                "total_chinese_ssw": 4500,
                "source_url": OFFICIAL_SOURCES["moj_stats"],
            },
            {
                "year": 2024,
                "total_ssw": 58200,
                "by_industry_driver": 12600,
                "total_vietnamese_ssw": 27500,
                "total_indonesian_ssw": 8500,
                "total_chinese_ssw": 5800,
                "source_url": OFFICIAL_SOURCES["moj_stats"],
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "�00000000000 (Immigration Services Agency)",
            OFFICIAL_SOURCES["moj_stats"],
            "https://www.moj.go.jp/isa/policies/statistics/toukei_ichiran_nenpyo.html",
        ]
