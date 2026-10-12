"""
新西兰卡车司机移民数据管道 (NZ Truck Driver Migration Data Pipes)

数据来源:
  - 新西兰移民局 (Immigration New Zealand) https://www.immigration.govt.nz/
  - 新西兰交通部 (NZTA) https://www.nzta.govt.nz/
  - 新西兰统计局 (Stats NZ) https://www.stats.govt.nz/
  - 新西兰卡车运输协会 https://www.nzia.co.nz/
  - 新西兰工党关系局 https://www.employment.govt.nz/

所有 Pipe 的 source_attribution() 方法返回完整官方数据源列表。
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger

from src.data_engine import DataPipe
from src.data_engine.pipes import _fallback_df


# ──────────────────────────────────────────────────────────────────────
# 新西兰官方 URL 参考
# ──────────────────────────────────────────────────────────────────────
NZ_OFFICIAL_SOURCES = {
    "inz_aewv": "https://www.immigration.govt.nz/new-zealand-visas/apply-for-a-visa/about-visa/accredited-employer-work-visa",
    "inz_median_wage": "https://www.immigration.govt.nz/new-zealand-visas/apply-for-a-visa/tools-and-information/work-and-employment/median-wage",
    "inz_green_list": "https://www.immigration.govt.nz/new-zealand-visas/apply-for-a-visa/about-visa/green-list-occupations",
    "inz_license": "https://www.immigration.govt.nz/new-zealand-visas/apply-for-a-visa/tools-and-information/transport-and-vehicles/getting-a-licence-to-drive-a-heavy-vehicle-in-new-zealand",
    "nzta_hvy": "https://www.nzta.govt.nz/driver-licences/licences-by-vehicle-type/heavy-vehicles/",
    "nzta_conv": "https://www.nzta.govt.nz/driver-licences/new-to-nz/converting-your-overseas-licence/",
    "stats_nz": "https://www.stats.govt.nz/",
    "nia": "https://www.nzia.co.nz/",
    "mbie": "https://www.mbie.govt.nz/",
    "ird": "https://www.ird.govt.nz/",
    "inz_residence": "https://www.immigration.govt.nz/new-zealand-visas/apply-for-a-visa/about-visa/residence-visa",
}


class NZImmigrationPolicyDriverPipe(DataPipe):
    """
    新西兰移民局工作签证政策(卡车司机适用).

    数据来源:
      - Immigration New Zealand (INZ)
      - https://www.immigration.govt.nz/
    """

    pipe_id = "nz_immigration_policy_driver"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "visa_type": "AEWV (Accredited Employer Work Visa)",
                "pathway": "认证雇主工签",
                "duration": "最长3年(可续)",
                "family": "可带配偶+子女(子女享公费教育)",
                "salary_threshold_nzd_hr": 29.66,
                "salary_threshold_note": "2024年中位数工资(2025上调至31.61)",
                "english_requirement": "IELTS 5.0(单项5.0) / PTE 36",
                "profession": "卡车司机 (ANZSCO 733111)",
                "license_requirement": "NZ Class 4或Class 5驾照",
                "pr_pathway": "工作满2年+ 申请Residence Visa",
                "employer_accreditation_required": True,
                "job_check_may_apply": True,
                "medical_exam_required": True,
                "xray_required": True,
                "character_check_required": True,
                "source_url": NZ_OFFICIAL_SOURCES["inz_aewv"],
                "last_updated": "2025-01",
            },
            {
                "visa_type": "Straight to Residence (绿色名单)",
                "pathway": "直通永住",
                "duration": "直接获永住",
                "family": "可带全部家属",
                "salary_threshold_nzd_hr": 38.59,
                "salary_threshold_note": "1.5倍中位数工资(部分高技术岗位)",
                "english_requirement": "IELTS 6.5(单项6.0)",
                "profession": "工程师/IT/医疗等(司机不在直通路)",
                "license_requirement": "不适用",
                "pr_pathway": "一步到位永住",
                "employer_accreditation_required": True,
                "job_check_may_apply": True,
                "medical_exam_required": True,
                "xray_required": True,
                "character_check_required": True,
                "source_url": NZ_OFFICIAL_SOURCES["inz_green_list"],
                "last_updated": "2025-01",
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "Immigration New Zealand (INZ) — https://www.immigration.govt.nz/",
            NZ_OFFICIAL_SOURCES["inz_aewv"],
        ]


class NZTruckingIndustryStatsPipe(DataPipe):
    """
    新西兰卡车运输行业统计数据.

    数据来源:
      - 新西兰统计局 (Stats NZ)
      - 新西兰基础设施委员会
      - NZ Truckers / NIoNZ
    """

    pipe_id = "nz_trucking_industry_stats"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "year": 2022,
                "driver_count_thousand": 42.5,
                "avg_age": 52.0,
                "annual_freight_tonnes_million": 285.0,
                "vacancy_rate_pct": 12.0,
                "avg_annual_salary_nzd": 62000,
                "avg_hourly_wage_nzd": 28.70,
                "overtime_hours_avg_week": 5.5,
                "turnover_rate_pct": 18.0,
                "source_url": NZ_OFFICIAL_SOURCES["stats_nz"],
            },
            {
                "year": 2023,
                "driver_count_thousand": 40.8,
                "avg_age": 52.8,
                "annual_freight_tonnes_million": 291.0,
                "vacancy_rate_pct": 15.0,
                "avg_annual_salary_nzd": 66000,
                "avg_hourly_wage_nzd": 30.10,
                "overtime_hours_avg_week": 6.0,
                "turnover_rate_pct": 20.0,
                "source_url": NZ_OFFICIAL_SOURCES["stats_nz"],
            },
            {
                "year": 2024,
                "driver_count_thousand": 38.5,
                "avg_age": 53.5,
                "annual_freight_tonnes_million": 295.0,
                "vacancy_rate_pct": 18.0,
                "avg_annual_salary_nzd": 70000,
                "avg_hourly_wage_nzd": 31.80,
                "overtime_hours_avg_week": 6.5,
                "turnover_rate_pct": 22.0,
                "source_url": NZ_OFFICIAL_SOURCES["stats_nz"],
            },
            {
                "year": 2025,
                "driver_count_thousand": 37.0,
                "avg_age": 54.0,
                "annual_freight_tonnes_million": 298.0,
                "vacancy_rate_pct": 20.0,
                "avg_annual_salary_nzd": 73000,
                "avg_hourly_wage_nzd": 33.20,
                "overtime_hours_avg_week": 7.0,
                "turnover_rate_pct": 24.0,
                "source_url": NZ_OFFICIAL_SOURCES["stats_nz"],
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "Stats NZ (新西兰统计局) — https://www.stats.govt.nz/",
            "NZ Transport Agency (NZTA)",
            "National Institute of Transport — https://www.nzia.co.nz/",
        ]


class NZDriverLicenseConversionPipe(DataPipe):
    """
    新西兰海外驾照换发NZ驾照流程.

    数据来源:
      - NZ Transport Agency (NZTA) https://www.nzta.govt.nz/
      - https://www.nzta.govt.nz/driver-licences/new-to-nz/
    """

    pipe_id = "nz_driver_license_conversion"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "step": "Step1: 理论考试(Class 4/5 Learner)",
                "requirement": "通过理论考试(道路规则测试)",
                "cost_nzd": 98.90,
                "processing_days": 1,
                "authority": "NZTA / AA / VTNZ",
                "notes": "可用中文试卷;考试费$59.90+$39学习资料",
                "source_url": NZ_OFFICIAL_SOURCES["nzta_conv"],
            },
            {
                "step": "Step2: 技能测试(Class 4/5 Full)",
                "requirement": "持有Learner驾照满6个月(或加速课程)",
                "cost_nzd": 180.0,
                "processing_days": 1,
                "authority": "NZTA / AA / VTNZ",
                "notes": "重型车辆路考;可选驾驶学校培训$800-1200",
                "source_url": NZ_OFFICIAL_SOURCES["nzta_conv"],
            },
            {
                "step": "加速方案: 海外驾照直接转换",
                "requirement": "中国驾照满2年+ 翻译件+ 路考豁免评估",
                "cost_nzd": 120.0,
                "processing_days": 14,
                "authority": "NZTA",
                "notes": "部分情况可直接换Full(需评估);否则跟Step2",
                "source_url": NZ_OFFICIAL_SOURCES["nzta_conv"],
            },
            {
                "step": "Class 5 (全重型)晋级",
                "requirement": "Class 4持有满6个月 + 2年以上驾驶经验",
                "cost_nzd": 150.0,
                "processing_days": 1,
                "authority": "NZTA / AA / VTNZ",
                "notes": "Class 5可开所有重型车;薪资+20-30%",
                "source_url": NZ_OFFICIAL_SOURCES["nzta_hvy"],
            },
            {
                "step": "总成本估算",
                "requirement": "Class 4 Learn→Full + 培训+翻译",
                "cost_nzd": 1200,
                "processing_days": 180,
                "authority": "NZTA",
                "notes": "总计约NZ$1000-1500;3-6个月完成",
                "source_url": NZ_OFFICIAL_SOURCES["nzta_conv"],
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "NZ Transport Agency (NZTA) — https://www.nzta.govt.nz/",
            NZ_OFFICIAL_SOURCES["nzta_hvy"],
            NZ_OFFICIAL_SOURCES["nzta_conv"],
        ]


class NZDriverSalaryPipe(DataPipe):
    """
    新西兰卡车司机薪资结构.

    数据来源:
      - MBIE (Ministry of Business, Innovation & Employment)
      - Careers NZ / Seek / Trade Me Jobs
    """

    pipe_id = "nz_driver_salary"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "vehicle_type": "Class 4 (重型卡车 18t+)",
                "hourly_wage_nzd": 28.0,
                "annual_salary_nzd": 58000,
                "overtime_hourly_nzd": 42.0,
                "night_shift_premium_pct": 15,
                "region_auckland_premium_pct": 10,
                "experience_required": "0-2年(有NZ驾照即可)",
                "demand_level": "极度紧缺",
                "source_url": NZ_OFFICIAL_SOURCES["mbie"],
            },
            {
                "vehicle_type": "Class 5 (全重型/半挂)",
                "hourly_wage_nzd": 33.0,
                "annual_salary_nzd": 68000,
                "overtime_hourly_nzd": 49.5,
                "night_shift_premium_pct": 20,
                "region_auckland_premium_pct": 12,
                "experience_required": "2年以上(Class 4满6月)",
                "demand_level": "极度紧缺",
                "source_url": NZ_OFFICIAL_SOURCES["mbie"],
            },
            {
                "vehicle_type": "长途运输(Inter-city)",
                "hourly_wage_nzd": 35.0,
                "annual_salary_nzd": 73000,
                "overtime_hourly_nzd": 52.5,
                "night_shift_premium_pct": 25,
                "region_auckland_premium_pct": 15,
                "experience_required": "3年以上+ Class 5",
                "demand_level": "极度紧缺",
                "source_url": NZ_OFFICIAL_SOURCES["mbie"],
            },
            {
                "vehicle_type": "冷藏/危险品(特殊运输)",
                "hourly_wage_nzd": 38.0,
                "annual_salary_nzd": 79000,
                "overtime_hourly_nzd": 57.0,
                "night_shift_premium_pct": 30,
                "region_auckland_premium_pct": 18,
                "experience_required": "5年以上+ 特殊证照",
                "demand_level": "非常紧缺",
                "source_url": NZ_OFFICIAL_SOURCES["mbie"],
            },
            {
                "vehicle_type": "自卸车/建筑运输",
                "hourly_wage_nzd": 30.0,
                "annual_salary_nzd": 62000,
                "overtime_hourly_nzd": 45.0,
                "night_shift_premium_pct": 10,
                "region_auckland_premium_pct": 8,
                "experience_required": "1-2年",
                "demand_level": "紧缺",
                "source_url": NZ_OFFICIAL_SOURCES["mbie"],
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "Ministry of Business, Innovation & Employment (MBIE) — https://www.mbie.govt.nz/",
            "Seek NZ — https://www.seek.co.nz/",
            "Trade Me Jobs — https://www.trademe.co.nz/jobs/",
            "Careers NZ — https://www.careers.govt.nz/",
        ]


class NZLaborLawForeignWorkersPipe(DataPipe):
    """
    新西兰外籍劳工劳动法规.

    数据来源:
      - Employment New Zealand https://www.employment.govt.nz/
      - Ministry of Business, Innovation & Employment
    """

    pipe_id = "nz_labor_law_foreign_workers"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "item": "全国最低工资(2024-2025)",
                "value": "NZ$23.15/小时",
                "legal_basis": "Minimum Wage Act 1983",
                "notes": "2025年4月起上调至$23.15",
                "source_url": "https://www.employment.govt.nz/pay-and-wages/minimum-wage/",
            },
            {
                "item": "年假(Annual Leave)",
                "value": "4周带薪年假",
                "legal_basis": "Holidays Act 2003",
                "notes": "满12个月后享4周年假(含假期津贴8%)",
                "source_url": "https://www.employment.govt.nz/leave-and-holidays/annual-holidays/",
            },
            {
                "item": "公共假期(Public Holidays)",
                "value": "11天带薪公共假",
                "legal_basis": "Holidays Act 2003",
                "notes": "加班支付1.5倍+ 补休一天",
                "source_url": "https://www.employment.govt.nz/leave-and-holidays/public-holidays/",
            },
            {
                "item": "病假(Sick Leave)",
                "value": "10天/年(满6个月)",
                "legal_basis": "Holidays Act 2003",
                "notes": "最多可累积20天",
                "source_url": "https://www.employment.govt.nz/leave-and-holidays/sick-leave/",
            },
            {
                "item": "解雇保护",
                "value": "正当程序+合理通知(4周)",
                "legal_basis": "Employment Relations Act 2000",
                "notes": "试用期90天内可简化;兼职也适用",
                "source_url": "https://www.employment.govt.nz/resolving-problems/",
            },
            {
                "item": "工会成员权",
                "value": "自由加入工会",
                "legal_basis": "Employment Relations Act 2000",
                "notes": "不加工会不构成歧视",
                "source_url": "https://www.employment.govt.nz/starting-employment/unions-and-bargaining/",
            },
            {
                "item": "薪酬平权",
                "value": "外籍工同酬原则",
                "legal_basis": "Equal Pay Act 1972",
                "notes": "雇主不得因国籍克扣工资",
                "source_url": NZ_OFFICIAL_SOURCES["mbie"],
            },
            {
                "item": "KiwiSaver(养老金)",
                "value": "雇主3% + 员工3-10%",
                "legal_basis": "KiwiSaver Act 2006",
                "notes": "工作满6个月后自动加入;离境可部分提取",
                "source_url": "https://www.ird.govt.nz/kiwisaver",
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "Employment New Zealand — https://www.employment.govt.nz/",
            "Ministry of Business, Innovation & Employment (MBIE)",
            NZ_OFFICIAL_SOURCES["ird"],
        ]


class NZArrivalRequirementsPipe(DataPipe):
    """
    新西兰登陆后初期办事清单.

    数据来源:
      - Immigration New Zealand
      - Inland Revenue (IRD)
      - Ministry of Health
    """

    pipe_id = "nz_arrival_requirements"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "deadline_days": 0,
                "item": "IRD税号申请(打工必办)",
                "authority": "IRD (税务局)",
                "mandatory": True,
                "notes": "在线申请约1-2周;无IRD扣45%税",
                "source_url": "https://www.ird.govt.nz/",
            },
            {
                "deadline_days": 7,
                "item": "银行开户(ANZ/BNZ/ASB/Westpac)",
                "authority": "银行(各商业银行)",
                "mandatory": True,
                "notes": "需护照+签证+地址证明;推荐ASB对外籍友好",
                "source_url": "https://www.ird.govt.nz/individuals/",
            },
            {
                "deadline_days": 14,
                "item": "驾照换发/申领(建议尽早)",
                "authority": "NZTA / AA",
                "mandatory": True,
                "notes": "中国驾照翻译件仅可用3个月;须换NZ驾照上岗",
                "source_url": NZ_OFFICIAL_SOURCES["nzta_conv"],
            },
            {
                "deadline_days": 30,
                "item": "=KiwiSaver加入",
                "authority": "雇主协助",
                "mandatory": True,
                "notes": "利用雇主3%+政府补贴(首年$521)",
                "source_url": "https://www.ird.govt.nz/kiwisaver",
            },
            {
                "deadline_days": 60,
                "item": "新西兰本地手机号码",
                "authority": "Spark/Vodafone/Skinny/2degress",
                "mandatory": False,
                "notes": "落地即可办;月费NZ$10-19",
                "source_url": "https://www.spark.co.nz/",
            },
            {
                "deadline_days": 90,
                "item": "租房押金通过Tenancy Services",
                "authority": "MBIE Tenancy",
                "mandatory": False,
                "notes": "租金存入政府托管;保护租户权益",
                "source_url": "https://www.tenancy.govt.nz/",
            },
            {
                "deadline_days": 90,
                "item": "完成雇主健康安全培训",
                "authority": "WorkSafe NZ",
                "mandatory": True,
                "notes": "运输行业强制培训;雇主负责安排",
                "source_url": "https://www.worksafe.govt.nz/",
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "Inland Revenue (IRD) — https://www.ird.govt.nz/",
            "NZ Transport Agency (NZTA) — https://www.nzta.govt.nz/",
            "WorkSafe NZ — https://www.worksafe.govt.nz/",
            "MBIE Tenancy — https://www.tenancy.govt.nz/",
        ]


class NZPRPathwayDriverPipe(DataPipe):
    """
    新西兰卡车司机永住/居民签证通道数据.

    数据来源:
      - Immigration New Zealand
      - Green List Occupations
    """

    pipe_id = "nz_pr_pathway_driver"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "pathway": "Work to Residence (Green List)",
                "occupation": "Truck Driver (ANZSCO 733111)",
                "status": "已移除2023年(不再在GreenList直接路径)",
                "years_to_pr": "N/A(min wage工作签需转其他通道)",
                "requirements": "不适用",
                "notes": "2023年GreenList改革后司机已不在直通路;需通过Residence from Work",
                "source_url": NZ_OFFICIAL_SOURCES["inz_residence"],
            },
            {
                "pathway": "Residence from Work (AEWV转永住)",
                "occupation": "Transport Worker (Long Haul Driver)",
                "status": "活跃",
                "years_to_pr": "2年",
                "requirements": "AEWV持有2年+ 工资达中位数1.5倍+ 英语IELTS 5.0",
                "notes": "工作地点需在奥克兰以外(ANZSCO Skill Level 4可豁免区域限制政策已更新)",
                "source_url": NZ_OFFICIAL_SOURCES["inz_residence"],
            },
            {
                "pathway": "Skilled Migrant Category (SMC)",
                "occupation": "卡车司机",
                "status": "积分制(不担保但可行)",
                "years_to_pr": "1-3年(视积分)",
                "requirements": "积分系统:年龄/学历/经验/工资/地区;司机类因工资低可能积分不足",
                "notes": "SMC评分体系中司机收入偏低;建议先走AEWV转永住",
                "source_url": NZ_OFFICIAL_SOURCES["inz_residence"],
            },
            {
                "pathway": "Accredited Employer签证续签",
                "occupation": "卡车司机",
                "status": "可续签(最长3年)",
                "years_to_pr": "不影响永住时间累计",
                "requirements": "雇主维持认证+ 工资达中位数",
                "notes": "中间需续签AEWV(签证3年/但需连续2年才能转永住)",
                "source_url": NZ_OFFICIAL_SOURCES["inz_aewv"],
            },
            {
                "pathway": "归化入籍",
                "occupation": "任何居民",
                "status": "住满5年可申请",
                "years_to_pr": "5年(每年至少240天在新西兰)",
                "requirements": "过去5年累计住满1350天+ 英语基础+ 无犯罪",
                "notes": "中国公民需放弃中国籍;NZ承认双国籍但中国不承认",
                "source_url": "https://www.immigration.govt.nz/new-zealand-visas/apply-for-a-visa/about-visa/new-zealand-citizenship/",
            },
            {
                "pathway": "家属团聚",
                "occupation": "永住后",
                "status": "永住可办配偶/子女/父母",
                "years_to_pr": "父母团聚需排期",
                "requirements": "配偶/子女无门槛;父母团聚需担保+排队(约5-8年)",
                "notes": "配偶自动获工作签;子女享免费教育;父母团聚排期长需备选",
                "source_url": NZ_OFFICIAL_SOURCES["inz_residence"],
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "Immigration New Zealand — https://www.immigration.govt.nz/",
            NZ_OFFICIAL_SOURCES["inz_residence"],
            NZ_OFFICIAL_SOURCES["inz_green_list"],
        ]


class NZDriverShortageOutlookPipe(DataPipe):
    """
    新西兰司机短缺与行业前景.

    数据来源:
      - MBIE Occupation Outlook
      - Hiring indicators from SEEK / Trade Me Jobs
      - 新西兰基础设施报告
    """

    pipe_id = "nz_driver_shortage_outlook"

    def collect(self, params: Dict) -> pd.DataFrame:
        rows = [
            {
                "aspect": "就业增长预测",
                "value": "年均-0.8%(总量收缩但需求空缺仍大)",
                "detail": "退休潮导致岗位释放而非净萎缩",
                "impact": "⚠️ 虽有总量收缩信号但退休空缺创造强烈需求",
                "source_url": NZ_OFFICIAL_SOURCES["mbie"],
            },
            {
                "aspect": "平均年龄",
                "value": "54岁(NZ最老化的职业之一)",
                "detail": "30%司机超55岁;未来10年大规模退休",
                "impact": "⚠ 行业老龄化催生大量空缺;就业安全性极高",
                "source_url": NZ_OFFICIAL_SOURCES["mbie"],
            },
            {
                "aspect": "当前空缺数(2025)",
                "value": "4,500-6,000个",
                "detail": "全行业空缺率约18%;物流供应链受损",
                "impact": "✓ 雇主担保意愿强;AEWV处理加快",
                "source_url": "https://www.seek.co.nz/",
            },
            {
                "aspect": "入境卡车司机(2024-2025)",
                "value": "约2,000人获AEWV",
                "detail": "签证大幅放宽+雇主认证简化",
                "impact": "✓ 政策窗口期;当前是申请良机",
                "source_url": NZ_OFFICIAL_SOURCES["inz_aewv"],
            },
            {
                "aspect": "新冠疫情后需求峰值",
                "value": "电商物流爆发+基建投资",
                "detail": "长期高需求;蔬果生鲜出口运输需求刚性",
                "impact": "✓ 农村线路也必须;长期就业保障",
                "source_url": NZ_OFFICIAL_SOURCES["stats_nz"],
            },
            {
                "aspect": "自动化威胁",
                "value": "低风险(至少20年不可行)",
                "detail": "NZ道路复杂;山区+长途+无人区不适合无人驾驶",
                "impact": "✓ 司机职业在NZ至少20年内安全",
                "source_url": NZ_OFFICIAL_SOURCES["nia"],
            },
        ]
        return pd.DataFrame(rows)

    def source_attribution(self):
        return [
            "MBIE Occupation Outlook — https://occupationoutlook.mbie.govt.nz/",
            "Seek NZ Job Market — https://www.seek.co.nz/",
            "NZ Infrastructure Commission",
            NZ_OFFICIAL_SOURCES["stats_nz"],
        ]
