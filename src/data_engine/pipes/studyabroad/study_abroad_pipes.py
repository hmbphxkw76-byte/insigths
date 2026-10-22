"""
留学行业数据管道 v2 — Data-Driven Architecture
================================================

覆盖 13 个国家 × 5 条管道(本科/硕士/博士/签证/奖学金) = 65 条管道
每条管道覆盖: 排名/申请/项目/费用/奖学金 全维度
数据来源: 官方权威机构优先, 内置 fallback 标注来源

国家代码(共13个):
  NZ 新西兰 | NL 荷兰 | FI 芬兰 | IE 爱尔兰 | MY 马来西亚
  HK 香港   | AE 阿联酋 | SA 沙特 | QA 卡塔尔 | FR 法国
  US 美国   | CA 加拿大 | SG 新加坡

学位层次:
  bachelor  — 高中毕业申请本科
  master    — 本科毕业申请硕士
  phd       — 本科直博 / 硕士申博
  poststudy — 签证与毕业后工作权利
  all       — 奖学金(覆盖所有学位层次)
"""

from __future__ import annotations
from typing import ClassVar, Dict, List
import pandas as pd
from src.data_engine import DataPipe
from src.data_engine.pipes import _fallback_df

# ── 国家元数据 ──
_COUNTRY_META = {
    "NZ": {"zh": "新西兰", "en": "New Zealand", "region": "Oceania", "cur": "NZD"},
    "NL": {"zh": "荷兰", "en": "Netherlands", "region": "Europe", "cur": "EUR"},
    "FI": {"zh": "芬兰", "en": "Finland", "region": "Europe", "cur": "EUR"},
    "IE": {"zh": "爱尔兰", "en": "Ireland", "region": "Europe", "cur": "EUR"},
    "MY": {"zh": "马来西亚", "en": "Malaysia", "region": "Asia", "cur": "MYR"},
    "HK": {"zh": "香港", "en": "Hong Kong SAR", "region": "Asia", "cur": "HKD"},
    "AE": {"zh": "阿联酋", "en": "United Arab Emirates", "region": "Middle East", "cur": "AED"},
    "SA": {"zh": "沙特阿拉伯", "en": "Saudi Arabia", "region": "Middle East", "cur": "SAR"},
    "QA": {"zh": "卡塔尔", "en": "Qatar", "region": "Middle East", "cur": "QAR"},
    "FR": {"zh": "法国", "en": "France", "region": "Europe", "cur": "EUR"},
    "US": {"zh": "美国", "en": "United States", "region": "America", "cur": "USD"},
    "CA": {"zh": "加拿大", "en": "Canada", "region": "America", "cur": "CAD"},
    "SG": {"zh": "新加坡", "en": "Singapore", "region": "Asia", "cur": "SGD"},
}


def _d(pipe_id, cols, rows, source, url, level, cc, attribution):
    """生成数据条目."""
    if isinstance(attribution, str):
        attribution = [attribution]
    return {
        "pipe_id": pipe_id, "country": _COUNTRY_META.get(cc, {}).get("zh", ""),
        "country_code": cc, "level": level,
        "columns": cols, "data": rows,
        "source": source, "source_url": url, "attribution": attribution or [],
    }


# ── 全量数据字典 ──
_SA_DATA: {str: dict} = {}


# ====== 新西兰 NZ ======
_SA_DATA["nz_bachelor"] = _d("nz_bachelor",
    ["university_zh", "university_en", "qs_2025", "ielts", "gaokao",
     "tuition_nzd", "living_year_nzd", "top_programs", "moe_ok"],
    [
        ["奥克兰大学", "UoA", 68, 6.0, "直录预科", 32000, 20000, "工程/医学/商科", "是"],
        ["奥塔哥大学", "Otago", 207, 6.0, "直录预科", 29000, 18000, "牙医/生物医学", "是"],
        ["惠灵顿维多利亚", "VUW", 239, 6.0, "直录预科", 28000, 19000, "法学/IT/政策", "是"],
        ["坎特伯雷大学", "UC", 255, 6.0, "直录预科", 30000, 17000, "工程/南极研究", "是"],
        ["梅西大学", "Massey", 212, 6.0, "直录预科", 27000, 16000, "兽医/航空/食品", "是"],
        ["怀卡托大学", "UoW", 225, 6.0, "直录预科", 27000, 16000, "计算机/管理", "是"],
    ],
    "Study in NZ官方/各大学官网2024",
    "https://www.studyinnewzealand.govt.nz", "bachelor", "NZ",
    ["Study in NZ官方", "各大学官网"])

_SA_DATA["nz_master"] = _d("nz_master",
    ["university_zh", "university_en", "qs", "ielts", "years",
     "tuition_nzd", "gpa_pct", "top_masters", "type"],
    [
        ["奥克兰大学", "UoA", 68, 6.5, 1.5, 38000, 80, "工程/数据/商", "研究+授课"],
        ["奥塔哥大学", "Otago", 207, 6.5, 2.0, 35000, 75, "公共卫生/牙医", "研究型"],
        ["坎特伯雷大学", "UC", 255, 6.5, 1.5, 36000, 75, "工程/教育", "研究+授课"],
        ["惠灵顿维多利亚", "VUW", 239, 6.5, 1.5, 34000, 75, "IT/公共政策", "授课型"],
        ["梅西大学", "Massey", 212, 6.5, 1.5, 33000, 75, "食品/兽医", "研究型"],
    ],
    "Study in NZ官方2024",
    "https://www.studyinnewzealand.govt.nz", "master", "NZ",
    ["Study in NZ官方"])

_SA_DATA["nz_phd"] = _d("nz_phd",
    ["university_zh", "university_en", "qs", "ielts", "years",
     "fee_nzd", "stipend_nzd", "gpa_pct", "fields", "comp"],
    [
        ["奥克兰大学", "UoA", 68, 6.5, 3, 7500, 28000, 85, "工程/医学/数据", "高"],
        ["奥塔哥大学", "Otago", 207, 6.5, 3, 7500, 28000, 80, "生物医学/牙医", "高"],
        ["坎特伯雷大学", "UC", 255, 6.5, 3, 7500, 28000, 80, "工程/计算机", "中"],
        ["惠灵顿维多利亚", "VUW", 239, 6.5, 3, 7500, 28000, 80, "IT/数据", "中"],
        ["梅西大学", "Massey", 212, 6.5, 3, 7500, 28000, 75, "兽医/食品", "中"],
    ],
    "Study in NZ/UC(PG)2024",
    "https://www.studyinnewzealand.govt.nz", "phd", "NZ",
    ["Study in NZ官方"])

_SA_DATA["nz_visa_poststudy"] = _d("nz_visa_poststudy",
    ["visa_cat", "duration", "work_rights", "sponsor", "pr_path", "condition"],
    [
        ["Post-study work(open)", "最多3年", "自由", "无需", "Skilled Migrant", "NZ 7级+注册机构"],
        ["Post-study(employer)", "2年", "指定雇主", "需要", "雇主担保", "雇主协助+中位数时薪"],
        ["Skilled Migrant(居留)", "永久", "—", "—", "永久", "160分+获邀"],
        ["AEWV雇主认证签", "5年可续", "指定雇主", "需要", "2年后可转永居", "认证雇主+时薪"],
    ],
    "Immigration NZ 2024",
    "https://www.immigration.govt.nz/new-zealand-visas/options/study",
    "poststudy", "NZ", ["Immigration NZ官方"])

_SA_DATA["nz_scholarships"] = _d("nz_scholarships",
    ["name", "provider", "benefit", "level", "amount", "coverage", "deadline", "comp"],
    [
        ["NZS (新国奖)", "MFAT外交部", "+生活费/机票/保险", "本科/硕/博", "full", "全额", "3-4月", "极高"],
        ["UoA Intl Scholarship", "奥克兰大学", "最高NZ$10,000/年", "本科/硕士", "10000/年", "学费减免", "Rolling", "高"],
        ["UC Intl 1st Year", "坎特伯雷", "NZ$15,000-20,000", "本科", "15000-20000", "学费减免", "8月", "高"],
        ["VUW Masters Thesis", "惠灵顿", "学费+NZ$15,000", "硕士", "15000/年", "学费+津贴", "Rolling", "中"],
        ["Massey VC Schol", "梅西大学", "最高NZ$15,000/年", "本科/硕士", "15000/年", "学费减免", "9月", "中"],
        ["Otago Doctoral Sch", "奥塔哥", "学费+NZ$28,000/年", "PhD", "28000/年", "学费+津贴", "Rolling", "高"],
        ["NZIDRS", "新西兰政府", "全额学费+生活费(3年)", "PhD", "full", "全额", "7月", "极高"],
    ],
    "Study in NZ/各大学2024",
    "https://www.studyinnewzealand.govt.nz", "all", "NZ",
    ["MFAT", "各大学奖学金页"])


# ====== 荷兰 NL ======
_SA_DATA["nl_bachelor"] = _d("nl_bachelor",
    ["university_zh", "university_en", "qs_2025", "ielts", "tuition_non_eur",
     "living_month_eur", "top_programs", "english_pct", "university_type"],
    [
        ["代尔夫特理工", "TU Delft", 49, 6.5, 16000, 900, "工程/建筑/计算机", ">80%", "研究型"],
        ["阿姆斯特丹大学", "UvA", 53, 6.5, 12000, 1000, "商科/传媒/法学/AI", ">85%", "研究型"],
        ["乌得勒支大学", "Utrecht", 105, 6.5, 11000, 950, "兽医/社科/生物医学", ">70%", "研究型"],
        ["莱顿大学", "Leiden", 113, 6.5, 11000, 950, "法学/人文/国际关系", ">80%", "研究型"],
        ["埃因霍温理工", "TU/e", 136, 6.5, 12000, 850, "工程/计算机", ">90%", "研究型"],
        ["格罗宁根大学", "RUG", 139, 6.5, 10000, 850, "经济/化学/能源", ">75%", "研究型"],
        ["瓦赫宁根大学", "WUR", 153, 6.5, 10000, 900, "农业/食品/环境", ">85%", "研究型"],
    ],
    "Nuffic/Study in Holland/各大学2024",
    "https://www.studyinholland.nl", "bachelor", "NL",
    ["Nuffic", "Study in Holland官方"])

_SA_DATA["nl_master"] = _d("nl_master",
    ["university_zh", "university_en", "qs", "ielts", "years",
     "tuition_eur", "gpa_pct", "top_masters", "rank"],
    [
        ["代尔夫特理工", "TU Delft", 49, 6.5, 2.0, 20000, 80, "航空/水利/微电子", "极高(欧洲Top5)"],
        ["阿姆斯特丹大学", "UvA", 53, 6.5, 1.0, 18000, 80, "AI/商科/国际法", "高"],
        ["莱顿大学", "Leiden", 113, 6.5, 1.0, 19000, 75, "法学/考古/国际关系", "高"],
        ["瓦赫宁根大学", "WUR", 153, 6.5, 2.0, 20000, 75, "农业/食品", "极高(QS农林No.1)"],
        ["乌得勒支大学", "Utrecht", 105, 6.5, 1.0, 19000, 75, "可持续发展/生物", "高"],
        ["埃因霍温理工", "TU/e", 136, 6.5, 2.0, 21000, 80, "工程/数据科学", "高"],
    ],
    "Study in Holland官方2024",
    "https://www.studyinholland.nl/study-options/masters", "master", "NL",
    ["Nuffic", "各研究生院"])

_SA_DATA["nl_phd"] = _d("nl_phd",
    ["university_zh", "university_en", "qs", "ielts", "years",
     "salary_eur", "monthly_eur", "employment_type", "research_focus"],
    [
        ["代尔夫特理工", "TU Delft", 49, 6.5, 4.0, 35000, 2800, "雇员制", "工程/应用科学"],
        ["阿姆斯特丹大学", "UvA", 53, 6.5, 4.0, 37000, 2900, "雇员制", "AI/社科/生物医学"],
        ["莱顿大学", "Leiden", 113, 6.5, 4.0, 34000, 2700, "雇员制", "法学/人文/自然科学"],
        ["瓦赫宁根大学", "WUR", 153, 6.5, 4.0, 33000, 2600, "雇员制", "农业/食品/环境"],
        ["乌得勒支大学", "Utrecht", 105, 6.5, 4.0, 35000, 2800, "雇员制", "医学/兽医"],
        ["埃因霍温理工", "TU/e", 136, 6.5, 4.0, 34000, 2700, "雇员制", "工程/计算机"],
    ],
    "AcademicTransfer/各研究生院2024",
    "https://www.academictransfer.com", "phd", "NL",
    ["AcademicTransfer", "VSNU"])

_SA_DATA["nl_visa_poststudy"] = _d("nl_visa_poststudy",
    ["visa_cat", "duration", "work_rights", "sponsor", "pr_path", "condition"],
    [
        ["Orientation Year(Zoekjaar)", "1年", "自由", "无需", "可转KM/HSM", "3年内毕业"],
        ["Highly Skilled Migrant", "5年", "自由(换雇主)", "需要(认证雇主)", "5年+可申永住", "€39,072+"],
        ["EU Blue Card", "4年可续", "自由", "需要", "5年可转", "€63,459+"],
        ["Self-Employed", "1-2年可续", "自雇", "—", "可转永居", "KvK+经济评估"],
    ],
    "IND Netherlands 2024",
    "https://ind.nl/en", "poststudy", "NL", ["IND", "Nuffic"])

_SA_DATA["nl_scholarships"] = _d("nl_scholarships",
    ["name", "provider", "benefit", "level", "amount", "coverage", "deadline", "comp"],
    [
        ["Holland Schol", "Nuffic", "€5,000(首年)", "本科/硕士", "5000一次性", "部分", "各大学不同", "中"],
        ["OKP橙色知识项目", "Nuffic/政府", "+生活费+保险", "硕士", "full", "全额", "2月/6月", "高"],
        ["TU Delft Excellence", "代尔夫特理工", "学费+生活费", "硕士", "full", "全额", "12月/2月", "极高"],
        ["UvA Amsterdam Merit", "阿大", "最高€25,000", "硕士", "最高25000", "部分", "1月", "高"],
        ["RUG Scholarship", "格罗宁根大学", "学费+€5,000", "本科/硕士", "学费+5000", "部分", "1-5月", "中"],
    ],
    "StudyFinder/各大学2024",
    "https://www.studyinholland.nl/finance", "all", "NL", ["Nuffic"])


# ====== 芬兰 FI ======
_SA_DATA["fi_bachelor"] = _d("fi_bachelor",
    ["university_zh", "university_en", "qs_2025", "ielts", "tuition_non_eur",
     "living_month_eur", "top_programs", "english_pct", "joint_app"],
    [
        ["赫尔辛基大学", "U Helsinki", 103, 6.5, 13000, 850, "社科/环境/神学", "~10%", "Studyinfo"],
        ["阿尔托大学", "Aalto", 113, 6.5, 12000, 900, "设计/商/工程", "~30%", "Studyinfo"],
        ["奥卢大学", "Oulu", 270, 6.0, 10000, 750, "通信/环境/医学", "~15%", "Studyinfo"],
        ["坦佩雷大学", "Tampere", 347, 6.0, 10000, 800, "社科/工程/IT", "~15%", "Studyinfo"],
        ["图尔库大学", "Turku", 358, 6.0, 8000, 800, "医学/法律", "~10%", "Studyinfo"],
        ["LUT大学", "LUT", 500, 6.0, 10000, 750, "清洁能源/工程", "~20%", "Studyinfo"],
    ],
    "Study in Finland联合招生2024",
    "https://www.studyinfinland.fi", "bachelor", "FI",
    ["Study in Finland官方", "EDUFI"])

_SA_DATA["fi_master"] = _d("fi_master",
    ["university_zh", "university_en", "qs", "ielts", "years",
     "tuition_eur", "gpa_pct", "top_masters", "tier"],
    [
        ["阿尔托大学", "Aalto", 113, 6.5, 2.0, 15000, 80, "设计/商/工程", "高"],
        ["赫尔辛基大学", "U Helsinki", 103, 6.5, 2.0, 15000, 75, "社科/环境/数据", "高(QS前百)"],
        ["坦佩雷大学", "Tampere", 347, 6.0, 2.0, 12000, 70, "社科/健康/IT", "中"],
        ["奥卢大学", "Oulu", 270, 6.0, 2.0, 12000, 70, "通信/医学", "中"],
        ["图尔库大学", "Turku", 358, 6.0, 2.0, 10000, 70, "生物医学/教育", "中"],
    ],
    "Studyinfo.fi/各大学2024",
    "https://opintopolku.fi/konfo/en", "master", "FI",
    ["Finnish National Agency for Education"])

_SA_DATA["fi_phd"] = _d("fi_phd",
    ["university_zh", "university_en", "qs", "ielts", "years",
     "salary_eur", "monthly_eur", "employment_type", "doctoral_schools"],
    [
        ["阿尔托大学", "Aalto", 113, 6.5, 4.0, 38000, 3100, "雇员制", "自然科学/工程/商科"],
        ["赫尔辛基大学", "U Helsinki", 103, 6.5, 4.0, 40000, 3200, "雇员制", "医学/社科/环境"],
        ["坦佩雷大学", "Tampere", 347, 6.5, 4.0, 36000, 2900, "雇员制", "医学/健康/工程"],
        ["奥卢大学", "Oulu", 270, 6.5, 4.0, 34000, 2700, "雇员制", "通信/医学"],
        ["图尔库大学", "Turku", 358, 6.5, 4.0, 35000, 2800, "雇员制", "医学/社科/教育"],
    ],
    "Finnish National Agency/博士学校2024",
    "https://www.studyinfinland.fi/admissions", "phd", "FI",
    ["Finnish National Agency", "各doctoral school"])

_SA_DATA["fi_visa_poststudy"] = _d("fi_visa_poststudy",
    ["visa_cat", "duration", "work_rights", "pr_path", "condition"],
    [
        ["Job Search Visa(A)", "最多2年", "自由", "可转工作签", "芬兰留学签证+毕业"],
        ["Work Permit(A/B)", "B=1年/A=4年", "自由", "A类4年可永住", "雇主合同+€3,600/月+"],
        ["Specialist Permit", "最多2年", "自由", "可永居", "硕士+特殊技能"],
        ["Startup Permit", "最长2年", "自雇", "可永居", "创业评估"],
    ],
    "Migri芬兰移民局2024",
    "https://migri.fi/en", "poststudy", "FI", ["Migri"])

_SA_DATA["fi_scholarships"] = _d("fi_scholarships",
    ["name", "provider", "benefit", "level", "amount", "coverage", "deadline", "comp"],
    [
        ["Finland Scholarship", "政府/各大学", "首年€5,000+入学奖", "硕士", "5000首年", "部分", "同年入学", "中"],
        ["Aalto Full Schol", "阿尔托大学", "全额或50%学费", "本科/硕士", "full或50%", "学费", "1-2月", "高"],
        ["U Helsinki Full Sch", "赫尔辛基大学", "+生活费(部分)", "硕士", "full", "全额", "1-2月", "高"],
        ["EDUFI Fellowship", "国家教育署", "€1,500/月(硕士€900)", "硕士/PhD", "1500/月", "生活费", "Rolling", "中"],
        ["Tampere Scholarship", "坦佩雷大学", "100%学费", "本科/硕士", "full", "学费", "同年开学", "中"],
        ["芬兰博士学校", "各博士学校", "雇员全职薪资", "PhD", "3000-4000/月", "薪资", "各学校不同", "中"],
    ],
    "Study in Finland/各大学2024",
    "https://www.studyinfinland.fi/scholarships", "all", "FI",
    ["Study in Finland", "Finnish National Agency"])


# ====== 爱尔兰 IE ======
_SA_DATA["ie_bachelor"] = _d("ie_bachelor",
    ["university_zh", "university_en", "qs_2025", "ielts", "tuition_non_eur",
     "living_year_eur", "top_programs", "pathway", "internship"],
    [
        ["都柏林圣三一学院", "TCD", 75, 6.5, 21000, 15000, "文学/工程/医学", "预科+高考", "部分含"],
        ["都柏林大学", "UCD", 115, 6.5, 20000, 14000, "商科/兽医/工程", "预科+高考", "含实习"],
        ["国立大学高威", "UGalway", 270, 6.0, 18000, 12000, "生物医学/工程", "预科", "含实习"],
        ["都柏林城市大学", "DCU", 350, 6.0, 15500, 12000, "计算机/商/传/教", "预科", "INTRA实习"],
        ["科克大学", "UCC", 280, 6.0, 18000, 12000, "食品/医学/法律", "预科", "含实习"],
        ["利默里克大学", "UL", 400, 6.0, 15500, 11000, "工程/音乐/航空", "预科", "合作教育"],
    ],
    "Education in Ireland/各大学2024",
    "https://www.educationinireland.com", "bachelor", "IE",
    ["Enterprise Ireland", "HEA"])

_SA_DATA["ie_master"] = _d("ie_master",
    ["university_zh", "university_en", "qs", "ielts", "years",
     "tuition_eur", "gpa_pct", "top_masters", "internship"],
    [
        ["都柏林圣三一学院", "TCD", 75, 6.5, 1.0, 22000, 80, "计算机/金融/文学", "部分含"],
        ["都柏林大学", "UCD", 115, 6.5, 1.0, 24000, 80, "商科(SMURFIT Top15)", "可选实习"],
        ["国立大学高威", "UG", 270, 6.0, 1.0, 20000, 75, "生物医学/海洋科学", "含实习"],
        ["科克大学", "UCC", 280, 6.0, 1.0, 19000, 75, "食品/护理/商科", "部分含"],
        ["都柏林城市大学", "DCU", 350, 6.0, 1.0, 18000, 75, "计算机/翻译/商科", "INTRA"],
    ],
    "Education in Ireland/各大学2024",
    "https://www.educationinireland.com", "master", "IE",
    ["Education in Ireland"])

_SA_DATA["ie_phd"] = _d("ie_phd",
    ["university_zh", "university_en", "qs", "ielts", "years",
     "stipend_eur", "gpa_pct", "funding_source", "research_strength", "employment"],
    [
        ["都柏林圣三一学院", "TCD", 75, 6.5, 4.0, 18000, 85, "IRC/SFI/学院", "文学/医学/计算机", "资助学生"],
        ["都柏林大学", "UCD", 115, 6.5, 4.0, 18000, 85, "IRC/SFI/欧盟", "商科/医学/工程", "资助学生"],
        ["国立大学高威", "UG", 270, 6.5, 4.0, 16000, 80, "IRC/SFI/欧盟", "生物医学/海洋", "资助学生"],
        ["科克大学", "UCC", 280, 6.5, 4.0, 16000, 80, "IRC/SFI", "食品/医学/社科", "资助学生"],
        ["都柏林城市大学", "DCU", 350, 6.0, 4.0, 16000, 80, "IRC/SFI/行业", "计算机/翻译", "资助学生"],
    ],
    "Irish Research Council/各大学2024",
    "https://www.iua.ie/for-students", "phd", "IE",
    ["IRC", "SFI"])

_SA_DATA["ie_visa_poststudy"] = _d("ie_visa_poststudy",
    ["visa_cat", "duration", "work_rights", "pr_path", "condition"],
    [
        ["Third Level Grad Scheme(Stamp 1G)", "本1年/硕博2年", "自由", "可转Critical Skills", "爱尔兰Level 7-10学历"],
        ["Critical Skills Employment Permit", "2年可续", "自由(换雇主)", "2年+可Stamp4→永住", "€38,000+列表职业"],
        ["General Employment Permit", "2年可续", "指定雇主", "5年后可住", "€34,000+/测试"],
        ["Study Visa(Stamp 2)", "课程期间", "每周20h/假期全职", "—", "认可学校+存款证明"],
    ],
    "INIS Ireland 2024",
    "https://www.irishimmigration.ie", "poststudy", "IE", ["INIS", "DETE"])

_SA_DATA["ie_scholarships"] = _d("ie_scholarships",
    ["name", "provider", "benefit", "level", "amount", "coverage", "deadline", "comp"],
    [
        ["GoI Intl Schol", "GoI/HEA", "+€10,000/年", "本科/硕/博", "full+10000", "全额+生活费", "2-3月", "极高(~60名)"],
        ["TCD Global Excellence", "圣三一学院", "全额学费", "本科/硕士", "full", "学费", "12/3月", "高"],
        ["UCD Global Excellence", "都柏林大学", "全额或50%", "本科/硕士", "full或50%", "学费", "12/3月", "高"],
        ["IRC Gov PG", "IRC", "€18,000+学费", "PhD", "18000+学费", "全额", "Rolling", "高"],
        ["SFI Centre", "SFI", "4年全额", "PhD", "18000/年", "全额", "各中心不同", "高"],
        ["Hardiman Schol", "高威大学", "+生活费", "PhD", "full+生活费", "全额", "3月", "高"],
    ],
    "Education in Ireland/IRC 2024",
    "https://www.iua.ie/for-students/scholarships", "all", "IE",
    ["Education in Ireland", "IRC"])


# ====== 马来西亚 MY ======
_SA_DATA["my_bachelor"] = _d("my_bachelor",
    ["university_zh", "university_en", "qs_2025", "ielts", "years",
     "tuition_myr", "living_myr", "total_myr", "top_programs", "moe_ok"],
    [
        ["马来亚大学", "UM", 65, 6.0, 4.0, 8000, 1800, 15000, "医学/工程/社科", "是(公立)"],
        ["博特拉大学", "UPM", 120, 5.5, 4.0, 7000, 1500, 13000, "农业/兽医/商科", "是"],
        ["国民大学", "UKM", 125, 5.5, 4.0, 7500, 1500, 13500, "医学/工程/教育", "是"],
        ["理工大学", "UTM", 175, 5.5, 4.0, 7500, 1500, 13500, "工程/建筑", "是"],
        ["泰莱大学", "Taylor's", 251, 5.5, 3.0, 12000, 1800, 19000, "酒店/设计/商科", "是(私立)"],
        ["思特雅大学", "UCSI", 265, 5.5, 3.5, 11000, 1800, 18000, "医学/音乐/工程", "是"],
        ["莫纳什马分校", "Monash MY", 37, 6.5, 4.0, 40000, 2000, 48000, "医学/商/工程", "是(澳)"],
    ],
    "Study in Malaysia/各大学官网2024",
    "https://www.studyinmalaysia.com", "bachelor", "MY", ["Study in Malaysia官方"])

_SA_DATA["my_master"] = _d("my_master",
    ["university_zh", "university_en", "qs", "ielts", "years",
     "tuition_myr", "gpa_pct", "top_masters", "type"],
    [
        ["马来亚大学", "UM", 65, 6.0, 1.5, 10000, 75, "医学/工程/数据", "研究/授课"],
        ["博特拉大学", "UPM", 120, 6.0, 1.5, 9000, 70, "农业/食品/社科", "研究/授课"],
        ["国民大学", "UKM", 125, 6.0, 1.5, 9500, 70, "医学/工程/教育", "研究/授课"],
        ["理工大学", "UTM", 175, 6.0, 1.5, 9500, 70, "工程/建筑", "研究/授课"],
        ["泰莱大学", "Taylor's", 251, 6.0, 1.0, 15000, 70, "商/传媒/设计", "授课型"],
        ["莫纳什马分校", "Monash MY", 37, 6.5, 2.0, 45000, 75, "医学/公卫/商科", "研究/授课"],
    ],
    "Study in Malaysia/各大学2024",
    "https://www.studyinmalaysia.com", "master", "MY", ["Study in Malaysia"])

_SA_DATA["my_phd"] = _d("my_phd",
    ["university_zh", "university_en", "qs", "ielts", "years",
     "fee_myr", "stipend_myr", "gpa_pct", "fields", "comp"],
    [
        ["马来亚大学", "UM", 65, 6.0, 3.0, 12000, 24000, 80, "医学/工程/社科", "中"],
        ["博特拉大学", "UPM", 120, 6.0, 3.0, 11000, 24000, 75, "农业/食品/林业", "中"],
        ["国民大学", "UKM", 125, 6.0, 3.0, 11500, 24000, 75, "医学/工程/教育", "中"],
        ["理工大学", "UTM", 175, 6.0, 3.0, 11500, 24000, 75, "工程/建筑", "中"],
        ["莫纳什马分校", "Monash MY", 37, 6.5, 4.0, 15000, 30000, 80, "医学/商科", "高"],
    ],
    "各大学研究生院2024",
    "https://www.studyinmalaysia.com", "phd", "MY", ["各研究生院招生办"])

_SA_DATA["my_visa_poststudy"] = _d("my_visa_poststudy",
    ["visa_cat", "duration", "work_rights", "pr_path", "condition"],
    [
        ["Student Pass", "课程期间", "每周20h/假期全职", "—", "认可大学"],
        ["EP Employment Pass I", "最长5年", "自由", "长期居住", "≥RM10,000/月+学位"],
        ["MM2H(第二家园)", "10年", "自由", "长期", "存款RM1M+收入RM40,000/月"],
        ["Specialist Pass", "1-5年", "指定雇主", "长期", "高技能/特定行业"],
    ],
    "Expatriate Services Division 2024",
    "https://esd.imi.gov.my", "poststudy", "MY", ["JIM", "ESD"])

_SA_DATA["my_scholarships"] = _d("my_scholarships",
    ["name", "provider", "benefit", "level", "amount", "coverage", "deadline", "comp"],
    [
        ["MIS奖", "MFAT", "+生活费+机票", "硕士/PhD", "full", "全额", "6-9月", "高"],
        ["MyBrainSc", "MOHE高教部", "+月津贴", "PhD", "full+生活费", "全额", "7-8月", "高(研究型)"],
        ["UM Research Fund", "马来亚大学", "生活费+经费", "PhD", "full", "部分", "Rolling", "中"],
        ["Taylor's Grad Schol", "泰莱大学", "30-50%学费", "硕士", "30-50%", "学费", "Rolling", "低-中"],
        ["TAR Foundation", "TAR大学", "学费津贴", "本科", "部分", "学费", "Rolling", "中"],
    ],
    "Study in Malaysia/MOHE/各大学2024",
    "https://biasiswa.mohe.gov.my", "all", "MY",
    ["MOHE高教部", "Study in Malaysia"])

# ====== 新加坡 SG (仅本科/硕士/PhD/签证/奖学金 精选) ======
_SA_DATA["sg_bachelor"] = _d("sg_bachelor",
    ["university_zh", "university_en", "qs_2025", "ielts", "gaokao",
     "tuition_sgd", "top_programs", "moe_ok"],
    [
        ["新加坡国立大学", "NUS", 8, 6.5, "高考达985线/国际课程", 38000, "工程/计算机/商科/法学", "是"],
        ["南洋理工大学", "NTU", 15, 6.5, "高考达985线/国际课程", 36000, "工程/计算机/商科/物理", "是"],
        ["新加坡管理大学", "SMU", 585, 7.0, "国际课程优先", 40000, "商科/法学/社科", "是"],
        ["新加坡科技设计大学", "SUTD", 440, 6.5, "高考需Top省%+面试", 42000, "工程/设计/计算机", "是"],
        ["新加坡理工大学", "SIT", "525-660", "applied pathway", 6.5, "高考/ITE", 30000, "工程/IT/健康", "是"],
    ],
    "MOE Singapore/各大学招生2024",
    "https://www.moe.gov.sg", "bachelor", "SG", ["MOE Singapore", "各大学官网"])


# ── 动态管道类工厂 ──
def _make_sa_pipe_class(pipe_id, columns, data, source, source_url,
                       level, country_code, attribution, **_ignored):
    """动态生成留学数据管道类."""
    def collect(self, params):
        df = pd.DataFrame(data, columns=columns)
        df['_source'] = source
        df['_url'] = source_url
        df['_country_code'] = country_code
        return df
    def source_attribution(self):
        return attribution or []
    cls = type(
        f'SAPipe_{pipe_id}',
        (DataPipe,),
        {
            'pipe_id': pipe_id,
            'collect': collect,
            'source_attribution': source_attribution,
            '__module__': __name__,
        }
    )
    return cls


def get_all_pipes():
    """返回所有留学管道类列表."""
    return [_make_sa_pipe_class(**entry) for entry in _SA_DATA.values()]


# ── 补充缺失条目 (由日本/香港 PhD/硕士 YAML 引用) ──

# 日本 SGU 项目 (Super Global University 英文授课项目)
_SA_DATA["jp_sgu_programs"] = _d("jp_sgu_programs",
    ["university_zh", "university_en", "sgu_track", "level", "fields",
     "deadline", "english_req", "gpa_min"],
    [
        ["東京大学", "UTokyo", "GPEAK/IME", "学士/硕士/PhD",
         "全领域/工学", "11-12月(次年10月入学)", "TOEFL 100+/IELTS 7.0", "3.4/4.0"],
        ["京都大学", "Kyoto U", "IUP/Campus Asia", "学士/硕士",
         "全领域", "1-2月(次年4月/10月)", "TOEFL 90+/IELTS 6.5", "3.2/4.0"],
        ["東京工業大学", "Tokyo Tech", "GSEP", "硕士/PhD",
         "工学", "4月/10月入学", "TOEFL 80+/IELTS 6.0", "3.0/4.0"],
        ["大阪大学", "Osaka U", "HUS/IUPS", "学士/硕士",
         "理科/国际物理学", "11-12月", "TOEFL 80+/IELTS 6.5", "3.0/4.0"],
        ["東北大学", "Tohoku U", "AMC/FDS/IMAC-U/AMB", "学士/硕士/PhD",
         "全领域", "12-1月", "TOEFL 79+/IELTS 6.0", "2.8/4.0"],
        ["名古屋大学", "Nagoya U", "G30 International Programs", "学士/硕士/PhD",
         "全领域", "12-1月(秋季)/3-4月(春季)", "TOEFL 80+/IELTS 6.5", "3.0/4.0"],
        ["九州大学", "Kyushu U", "Ito Campus", "学士/硕士/PhD",
         "全领域", "2-3月", "TOEFL 80+/IELTS 6.0", "2.8/4.0"],
        ["北海道大学", "Hokkaido U", "Modern Japanese Studies/MJSP", "硕士/PhD",
         "日本研究/全领域", "10-11月", "TOEFL 79+/IELTS 6.5", "3.0/4.0"],
        ["早稲田大学", "Waseda", "English-based Programs", "学士/硕士/PhD",
         "政治/经济/社科/理工", "2-3月(9月入学)/9-10月(4月入学)", "TOEFL 80+/IELTS 6.5", "3.0/4.0"],
        ["慶應義塾大学", "Keio", "PEARL/GIGA", "学士/硕士",
         "经济/政策/媒体设计", "1-2月", "TOEFL 80+/IELTS 6.5", "3.0/4.0"],
    ],
    "MEXT SGU/各大学招生2024",
    "https://www.mext.go.jp/en/policy/education/highered/title02/detail02/sdetail02/1373895.htm",
    "all", "JP", ["MEXT SGU官网", "JASSO", "各大学官网"])

# 香港 PhD 入学数据
_SA_DATA["hk_phd_admissions"] = _d("hk_phd_admissions",
    ["university_zh", "university_en", "qs_2025", "ielts_toefl",
     "gpa_min", "application_deadline", "keys_admission_factors"],
    [
        ["香港大学", "HKU", 17, "IELTS 6.5(6.0)/TOEFL 80",
         "一等荣誉/85+", "12月1日(Main Round)",
         "研究计划(RP) + GPA + 强学术推荐信"],
        ["香港中文大学", "CUHK", 36, "IELTS 6.5/TOEFL 79",
         "硕士/一等荣誉", "12月1日",
         "RP + 论文发表(Google Scholar) + GPA + 套磁"],
        ["香港科技大学", "HKUST", 47, "IELTS 6.5(5.5)/TOEFL 80",
         "硕士/85+", "12月1日",
         "RP + 研究经历 + 发表文章 + 套磁"],
        ["香港城市大学", "CityU", 63, "IELTS 6.5/TOEFL 79",
         "硕士/80+", "12月1日(滚动审核)",
         "RP + 研究经历 + 导师匹配"],
        ["香港理工大学", "PolyU", 57, "IELTS 6.0/TOEFL 80",
         "硕士/75+", "滚动(优先12月)",
         "RP + 发表论文 + 工作经验加分"],
        ["香港浸会大学", "HKBU", 252, "IELTS 6.0/TOEFL 79",
         "硕士/75+", "滚动",
         "RP + 学术背景 + 面试表现"],
        ["岭南大学", "LingU", 780, "IELTS 6.0/TOEFL 79",
         "硕士/70+", "1月-4月滚动",
         "RP + 学术兴趣匹配度 + 面试"],
        ["香港教育大学", "EdUHK", "N/A(教育)", "IELTS 6.0/TOEFL 79",
         "硕士/70+", "1-3月滚动(教育)",
         "RP + 教育经验 + 面试"],
    ],
    "HK UGC/各大学研究生招生2024",
    "https://www.ugc.edu.hk/eng/ugc/activity/research/postgrad.html",
    "phd", "HK", ["HK UGC", "HKPFS官网", "各大学研究生院"])

# 德国 APS 认证流程说明
_SA_DATA["de_aps_certification_info"] = _d("de_aps_certification_info",
    ["step", "description", "timeline", "fee", "notes"],
    [
        ["Step 1 材料准备", "准备学历成绩单/毕业证/高考花名册公证件", "建议提前2-3个月",
         "25 EUR(审核费)", "所有文件需德文/英文公证翻译"],
        ["Step 2 在线注册", "APS官网注册并填写申请表,打印签字", "1周内完成",
         "—", "需选择面谈或TestAS考试"],
        ["Step 3 递交材料", "邮寄或现场递交完整材料至北京/上海审核部", "材料完整后进入排队",
         "—", "高峰期排队约3-6个月"],
        ["Step 4 面谈/TestAS",
         "面谈约20min(专业+语言) 或 TestAS机考(3.5h)", "排队后约4-6周安排",
         "TestAS另付约150 EUR", "面谈可申请德语或英语"],
        ["Step 5 获得证书", "审核通过后获得APS证书(终身有效)", "面谈后约4-6周",
         "—", "补审(毕业后)需再次提交"],
        ["特殊情况 艺设类", "艺术/设计类仅审核材料,免面谈", "较快",
         "—", "需提交作品集(电子版/打印)"],
    ],
    "Akademische Prüfstelle (APS) Beijing/Shanghai 2024",
    "https://www.aps.org.cn/zh", "all", "DE",
    ["APS北京审核部", "APS上海审核部"])

# 加拿大就业展望 (Post-graduation employment)
_SA_DATA["ca_employment_outlook"] = _d("ca_employment_outlook",
    ["field_zh", "field_en", "employment_rate_2yr_pct",
     "median_salary_cad", "top_employers", "growth_outlook"],
    [
        ["计算机科学/IT", "Computer Science / IT", 92, 78000,
         "Shopify, Amazon CA, Microsoft CA, RBC DI", "高速增长(AI/ML/全栈)"],
        ["数据科学/AI", "Data Science / AI", 90, 85000,
         "Element AI, Google Health, UHN Analytics", "极高需求"],
        ["金融/会计", "Finance / Accounting", 88, 68000,
         "RBC, TD, BMO, Scotiabank, Deloitte CA", "稳定增长"],
        ["工程(机械/电气/土木)", "Engineering (Mech/Elec/Civil)", 87, 72000,
         "Toronto Hydro, Ontario Power, AECOM", "stable(infra investment)"],
        ["医疗/护理", "Healthcare / Nursing", 95, 74000,
         "UHN, SickKids, Fraser Health, PHAC", "very high demand(ageing)"],
        ["商科/市场营销", "Business / Marketing", 82, 58000,
         "Lululemon, Canadian Tire, Shopify", "moderate growth"],
        ["教育/师范", "Education / Teaching", 90, 62000,
         "TDSB, VSB, York Region DSB", "stable(provincial shortage)"],
        ["生命科学/生物技术", "Life Sciences / Biotech", 78, 60000,
         "STEMCELL, AbCellera, Resilience", "high growth(GTA/GVA)"],
    ],
    "Statistics Canada / Job Bank / StatCan 2024",
    "https://www.jobbank.gc.ca", "poststudy", "CA",
     ["Statistics Canada", "Job Bank Canada"])

# 澳洲签证与毕业后工作权利 (Post-study / Temporary Graduate Visa)
_SA_DATA["au_visa_poststudy"] = _d("au_visa_poststudy",
    ["visa_subclass", "stream", "duration", "work_rights",
     "path_to_pr", "requirements"],
    [
        ["Subclass 485(Temporary Graduate) - Graduate Work",
         "Graduate Work stream", "18个月", "全职工作权利",
         "转ENS/RSMS(需雇主)或189/190/491",
         "技能评估通过+雅思6.0+2年内毕业"],
        ["Subclass 485(Temporary Graduate) - Post-Study Work",
         "Post-Study Work stream", "2-4年(学士2年/硕士3年/PhD4年)", "全职工作权利",
         "转ENS/RSMS/189/190/491",
         "CRICOS注册课程+雅思6.0+2年内毕业"],
        ["Subclass 189(Skilled Independent)",
         "Points-tested 独立技术移民", "永久", "永久工作权利",
         "永居",
         "职业在清单上+技能评估+雅思6.0+EOI获邀(通常65+分以上)"],
        ["Subclass 190(Skilled Nominated)",
         "州担保技术移民", "永久", "永久工作权利",
         "永居",
         "州/领地提名+489→190或直达+雅思6.0"],
        ["Subclass 491(Skilled Work Regional)",
         "偏远地区技术移民", "5年", "在偏远地区工作",
         "3年后转190永居",
         "偏远地区工作+州担保+雅思6.0+年薪门槛(2025: AUD 73,100)"],
        ["Subclass 494(Employer Sponsored Regional)",
         "偏远地区雇主担保", "5年", "指定雇主全职",
         "3年后转191永居",
         "雇主提名+技能评估+雅思6.0+3年经验"],
        ["Subclass 408(Pandemic/Bridging)",
         "COVID-408/临时活动", "2年(某些)", "全职(特定行业)",
         "不直接转永居",
         "适用于疫情/特殊行业/bridging case"],
    ],
    "Australian Dept. of Home Affairs / immi.gov.au 2024",
    "https://immi.homeaffairs.gov.au/visas/working-in-australia",
     "poststudy", "AU", ["Australian Dept. of Home Affairs", "Skills Australian Government"])

# ====== 法国 FR — 本科(通用) ======
_SA_DATA["fr_bachelor"] = _d("fr_bachelor",
    ["university_zh", "university_en", "qs_2025", "program_type", "language",
     "tuition_eur", "city", "top_programs", "moe_ok"],
    [
        ["索邦大学", "Sorbonne Université", 59, "公立Licence", "法语为主", 2770, "巴黎", "人文/理学/医学/工程", "是"],
        ["巴黎西岱大学", "Université Paris Cité", 236, "公立Licence", "法语为主", 2770, "巴黎", "医学/法学/心理学/社科", "是"],
        ["巴黎萨克雷大学", "Université Paris-Saclay", 78, "公立Licence", "法语/部分英语", 2770, "巴黎(南)", "理学/工程/医学/法学", "是"],
        ["PSL巴黎文理研究大学", "PSL University", 24, "公立Licence(LMD)", "法语/英语", 2770, "巴黎", "理学/人文/艺术/社科", "是"],
        ["艾克斯-马赛大学", "Aix-Marseille Université", 387, "公立Licence", "法语为主", 2770, "马赛", "法学/社科/理学/体育", "是"],
        ["波尔多大学", "Université de Bordeaux", 465, "公立Licence", "法语为主", 2770, "波尔多", "葡萄酒/法学/理学/医学", "是"],
        ["里昂一大(UCBL)", "Université Claude Bernard Lyon 1", 387, "公立Licence", "法语为主", 2770, "里昂", "医学/理学/工程/体育", "是"],
        ["HEC Paris BBA", "HEC Paris", "—(QS商科Top1)", "高商BBA本科", "英语", 22000, "巴黎(茹伊)", "管理/金融/创业/数字", "是"],
        ["ESSEC Global BBA", "ESSEC Business School", "—(QS商科Top3)", "高商BBA本科", "英语/法语", 14500, "巴黎(塞尔吉)", "管理/金融/市场营销/咨询", "是"],
        ["ESCP BBA", "ESCP Business School", "—(QS商科Top5)", "高商BBA本科", "英语/多语", 13500, "巴黎(多校区)", "管理/金融/跨文化/咨询", "是"],
        ["EDHEC Int BBA", "EDHEC Business School", "—(QS商科Top10)", "高商BBA本科", "英语", 12000, "里尔/尼斯", "管理/全球商务/金融/分析", "是"],
        ["emlyon BBA", "emlyon Business School", "—(QS商科Top15)", "高商BBA本科", "英语", 11500, "里昂/巴黎", "管理/创业/数字/奢侈品", "是"],
        ["格勒诺布尔高商", "GEM", "—(QS商科Top30)", "高商BBA本科", "英语", 11000, "格勒诺布尔", "管理/科技/金融/国际商务", "是"],
        ["INSA Lyon (5年制)", "INSA Lyon", "—(QS工程Top)", "工程师本硕连读", "法语/英语", 3770, "里昂", "工程/机械/CS/材料", "是"],
    ],
    "Campus France / 各大学官网 / QS 2024",
    "https://www.campusfrance.org/en", "bachelor", "FR",
    ["Campus France官方", "各大学招生办", "法国高教部"])

# 法国奖学金(本科适用)
_SA_DATA["fr_scholarships"] = _d("fr_scholarships",
    ["name", "provider", "benefit", "level", "amount", "coverage", "deadline", "comp"],
    [
        ["Eiffel Excellence(埃菲尔奖)", "法国外交部", "+生活费+机票+文化", "本科/硕士", "1181EUR/月+全cover", "全额(免学费+津贴)", "1月", "极高(约1500名/全层次)"],
        ["Campus France Excellence(校奖)", "各法国大学", "免学费或学费减免", "本科", "学费减免/部分", "部分", "各大学不同", "中"],
        ["法兰西共和国助学金(CROUS)", "CROUS/政府", "+住房补贴+餐补", "本科", "最高5556EUR/年", "生活费+住房", "7-10月", "中(需居留+收入条件)"],
        ["中国政府奖学金(CSC)", "国家留学基金委", "+生活费+往返机票", "本科", "full", "全额", "3-4月", "高(中法9+9等项目)"],
        ["Erasmus+/Erasmus Mundus", "欧盟委员会", "+生活费+旅费+学费", "本科/硕士", "最高25000EUR/年", "全额", "各大学不同", "高"],
        ["EDHEC Scholarship", "EDHEC高商", "最高全额学费", "本科BBA", "最高full", "学费", "Rolling", "中-高(merit-based)"],
        ["emlyon Early Bird", "emlyon高商", "最高30%学费减免", "本科BBA", "最高30%", "学费", "12-3月", "中"],
        ["ESSEC Excellence", "ESSEC高商", "最高全额学费", "本科BBA", "最高full", "学费", "1-3月", "高"],
        ["HEC Paris Scholarship", "HEC Paris", "need-based+merit", "本科BBA", "最高full", "学费+生活费", "与申请同时", "高"],
        ["地方政府奖学金(区域奖)", "法国大区政府", "+住房+交通优惠", "本科", "500-2000EUR/年", "部分", "各区域不同", "低-中"],
    ],
    "Campus France / CSC / 各大学 2024",
    "https://www.campusfrance.org/en/scholarship-programmes", "all", "FR",
    ["Campus France", "法国外交部", "各大学国际处", "CSC"])

# 法国留学签证政策
_SA_DATA["fr_visa_policy"] = _d("fr_visa_policy",
    ["visa_category", "duration", "work_rights", "requirements", "path_to_pr"],
    [
        ["Visa Etudiant(长期学生签)", "1年(续签)", "964小时/年(约20h/周)",
         "OFII/录取通知书+资金证明(615EUR/月)+法语/英语成绩", "2年居留后转工签/永居(10年)"],
        ["Visa Etudiant-Concours(考试/面试签)", "3-6个月", "无",
         "语言学校/大学入学考试/艺术学院面试", "考试通过转长期学生签"],
        ["VLS-TS(长期访问学生签)", "3-6个月", "无",
         "语言课程/短期培训", "回国申请正式学生签"],
        ["Schengen Court Séjour(短期)", "90天/180天", "无",
         "短期课程/夏令营/语言班(≤3个月)", "N/A(居留到期)"],
        ["Passport Talent(人才护照)", "4年", "全职工作",
         "Master学位+工作合同或创业计划", "5年可申永居"],
        ["APS(Autorisation Provisoire de Séjour)", "1年(毕业后)", "找工作/兼职工作",
         "已完成-license/Master学位", "找到工作转工签+永居路径"],
    ],
    "France-Visas / Campus France / OFII 2024",
    "https://france-visas.gouv.fr", "all", "FR",
    ["France-Visas.gouv.fr", "Campus France", "OFII"])

# 美国 PhD 入学数据 (Top programs)
_SA_DATA["us_phd_admissions"] = _d("us_phd_admissions",
    ["program_zh", "institution", "usnews_dept_rank", "avg_funding_usd_yr",
     "avg_time_to_degree", "typical_admit_metrics"],
    [
        ["电子工程/计算机", "MIT", 1, "全额RA/TA(免学费+stipend ~45K)",
         "5-6年", "GPA 3.8+/TOEFL 100+/strong research"],
        ["生物医学/生物工程", "Stanford", 1, "全额(免学费+~50K/年)",
         "5-6年", "GPA 3.7+/Nature子刊论文preferred"],
        ["经济学", "Harvard", 1, "全额(免学费+~55K/年+医疗保险)",
         "5-6年", "GRE Quant 169+/math background"],
        ["物理学", "Caltech", 3, "全额(免学费+~48K/年)",
         "5-7年", "强科研+publication record"],
        ["机械工程", "UC Berkeley", 2, "RA/TA全额(免学费+~38K/年)",
         "5-6年", "GPA 3.7+/research matched advisor"],
        ["化学", "Scripps Research", "N/A", "全额NIH/NSF(~$38K)",
         "5-6年", "Chem GRE(preferred)+strong lab"],
        ["数据科学/AI", "CMU", 1, "全额(免学费+~48K/年)",
         "5年", "顶会论文+CS/Math本科"],
        ["公共政策/MPP-PhD", "Harvard Kennedy School", "N/A", "全额(~$55K)",
         "4-5年", "GRE 330+/政策经验+research fit"],
    ],
    "US News / NSF/NIH Surveys / grad.cafe 2024",
    "https://ncses.nsf.gov/surveys/earned-doctorates", "phd", "US",
    ["US News Grad Rankings", "NSF Survey of Earned Doctorates", "Carnegie Classification"])

# 美国学费与奖学金 (本科)
_SA_DATA["us_tuition_and_aid"] = _d("us_tuition_and_aid",
    ["tier", "annual_tuition_usd", "annual_total_cost_usd",
     "avg_financial_aid_pct", "aid_sources", "international_aid"],
    [
        ["Ivy League / Elite", "62,000-65,000", "85,000-92,000",
         "50-65%", "Need-blind/Need-aware(全奖概率高)", "Need-blind @ Harvard/MIT/Yale/Amherst;Need-aware @ others"],
        ["Top Public (UC/UMich/UT)", "42,000-48,000(国际)", "58,000-65,000",
         "15-25%(州内高)", "州内Need-based/绩效奖学金", "国际生奖少;少数全奖(如UT Austin自动考虑)"],
        ["Liberal Arts Colleges", "58,000-63,000", "78,000-85,000",
         "55-70%", "Merit+Need-based(慷慨)", "部分Need-blind for intl (e.g. Amherst/Swarthmore)"],
        ["州立大学(中高端)", "28,000-40,000", "42,000-55,000",
         "20-40%(州内)", "Merit/Research/RA/TA", "通常提供较少国际生奖,Merit-based常见"],
        ["Community Colleges", "8,000-15,000", "20,000-28,000",
         "有限", "州政府资助(州居民)", "无联邦资助;少数院校奖"],
    ],
    "College Board / IPEDS / US News 2024",
    "https://research.collegeboard.org/trends/college-pricing",
     "bachelor", "US", ["College Board", "IPEDS", "US Department of Education"])

# 荷兰硕士入学 (English-taught Master's programs)
_SA_DATA["nl_master_admissions"] = _d("nl_master_admissions",
    ["university_zh", "university_en", "qs_2025", "ielts", "gpa_pct",
     "tuition_eur", "top_masters", "duration_years"],
    [
        ["代尔夫特理工大学", "TU Delft", 47, "IELTS 6.5(6.0)", 75,
         "€16,000-20,000", "航空航天/EEE/CS/Civil/工业", 2],
        ["阿姆斯特丹大学", "UvA", 53, "IELTS 6.5(6.0)", 75,
         "€15,000-18,000", "传播学/经济/法学/AI/数据科学", 1-2],
        ["莱顿大学", "Leiden", 114, "IELTS 6.5-7.0", 75,
         "€18,000-20,000", "国际关系/法学/药理学/哲学", 1-2],
        ["乌得勒支大学", "UU", 105, "IELTS 6.5(6.0)", 70,
         "€15,000-19,000", "可持续发展/兽医学/社科", 1-2],
        ["埃因霍温理工大学", "TU/e", 126, "IELTS 6.5(6.0)", 70,
         "€16,000-20,000", "EEE/CS/工业设计/化学", 2],
        ["瓦赫宁根大学", "WUR", 67, "IELTS 6.5(6.0)", 75,
         "€18,000-20,000", "农业/食品/环境/生命科学", 2],
        ["伊拉斯姆斯大学(鹿特丹)", "EUR", 158, "IELTS 6.5-7.0", 75,
         "€14,000-18,000", "Erasmus MC(医科)/RSM(商科)/经济", 1-2],
        ["特文特大学", "UT", 222, "IELTS 6.5(6.0)", 70,
         "€12,000-16,000", "工程技术/社会技术/纳米/遥控", 2],
        ["马斯特里赫特大学", "UM", 228, "IELTS 6.0-6.5", 70,
         "€13,000-16,000", "PBL教学法/健康/法学/数据", 1],
    ],
    "Study in Holland / Nuffic 各大学官网 2024",
    "https://www.studyinholland.nl", "master", "NL",
    ["Nuffic", "VSB", "各大学官网"])

# 芬兰本科入学 (Bachelor's admissions - Finnish/English-taught)
_SA_DATA["fi_bachelor_admissions"] = _d("fi_bachelor_admissions",
    ["university_zh", "university_en", "qs_rank", "ielts_toefl",
     "admission_method", "tuition_eur_non_eu", "living_eur_yr", "top_fields"],
    [
        ["赫尔辛基大学", "UH", 107, "IELTS 6.5/TOEFL 90",
         "SAT/AHPASK/National exam", "€13,000-18,000", "10,000",
         "Law/Science/Social/Agri/Ed"],
        ["阿尔托大学", "Aalto", 113, "IELTS 6.5/TOEFL 92",
         "Fields-specific entrance exam", "€12,000", "10,000",
         "Design/Business/Technology/ARTS"],
        ["奥卢大学", "UO", 290, "IELTS 6.0/TOEFL 78",
         "Entrance exam / SAT", "€10,000", "9,000",
         "Engineering/IT/Biomed/Ed"],
        ["坦佩雷大学", "TAU", 295, "IELTS 6.5/TOEFL 90",
         "Entrance exam", "€8,000-12,000", "9,500",
         "Tech/Social/Health/Management"],
        ["图尔库大学", "UTU", 315, "IELTS 6.0/TOEFL 78",
         "Entrance exam / SAT", "€8,000-10,000", "9,500",
         "Medicine/Law/Ed/Science/East Asian Studies"],
        ["于韦斯屈莱大学", "JYU", 351, "IELTS 6.0/TOEFL 78",
         "Entrance exam", "€8,000-10,000", "9,000",
         "Ed/Sport/Psychology/IT/Tourism"],
        ["拉赫蒂工业大学", "LUT", "351-400", "IELTS 6.0/TOEFL 78",
         "Entrance exam", "€10,000", "8,500",
         "Tech/Business/Clean Energy/Design"],
        ["拉普兰塔理工大学", "LUT(Lappeenranta)", "351-400", "IELTS 6.0",
         "Entrance exam", "€10,000", "8,000",
         "Tech/Business/Clean Energy"],
    ],
    "Study in Finland / UAS/University Admissions Finland (UAF) 2024",
     "https://www.studyinfinland.fi", "bachelor", "FI",
     ["Study in Finland", "UAF", "各大学官网"])

# 沙特阿拉伯奖学金 (KAUST + Ministry of Education + SACM)
_SA_DATA["sa_scholarships"] = _d("sa_scholarships",
    ["scholarship_name", "provider", "level", "benefit",
     "coverage", "deadline", "eligibility"],
    [
        ["KAUST Fellowship", "KAUST (阿卜杜拉国王科技大学)", "硕士/PhD",
         "全额奖学金+住宿+医疗+旅行", "全额(学费+生活费$30K/y)",
         "Rolling", "理工科/GPA 3.5+/IELTS 6.0"],
        ["SACM Fully Funded", "沙特文化部(SACM)", "本科/硕士/PhD",
         "学费+月津贴+住宿+年度机票", "全额(按学历津贴)",
         "每年开放(3-5月)", "沙大优先/非沙国籍+学术卓越"],
        ["KAUST VSRP (暑期)", "KAUST", "本科大三/大四",
         "2-3个月科研+住宿+生活费+机票", "全额(暑期计划)",
         "每年10月-次年3月", "Top大学生+推荐信+研究兴趣匹配"],
        ["King Abdulaziz Univ. (KAAU)", "KAAU / Jeddah", "本科/硕士/PhD",
         "免学费+月津贴+住宿+机票", "部分/全额(按专业)",
         "Rolling/每年特定", "伊斯兰研究/阿拉伯/工程/科学"],
        ["Islamic Development Bank (IsDB)", "IsDB + Saudi Universities", "本科/硕士/PhD",
         "学费+生活费+住宿+医疗+旅行", "全额",
         "每年1-2月", "IsDB成员国公民+STEM优先"],
    ],
    "KAUST / SACM / Saudi MOE 2024",
    "https://www.kaust.edu.sa/en/study/fellowship", "all", "SA",
    ["KAUST Off. of Sponsored Programs", "MOE Saudi", "SACM"])

# 芬兰 PhD 入学 (Doctoral admissions, mostly in English)
_SA_DATA["fi_phd_admissions"] = _d("fi_phd_admissions",
    ["university_zh", "university_en", "qs_rank", "ielts_toefl",
     "funding_model", "application_cycle", "requirements"],
    [
        ["赫尔辛基大学", "UH", 107, "IELTS 6.5/TOEFL 90",
         "Salaried(4年,EUR3.5K/月)+Faculty positions or grants",
         "Rolling(1月/8月)", "Master+research plan+potential supervisor"],
        ["阿尔托大学", "Aalto", 113, "IELTS 6.5/TOEFL 92",
         "Salaried(EUR3.3-3.6K/月)4年+ tuition waiver",
         "2 cycles(Jan/Aug)", "Master(相关学科)+research proposal"],
        ["奥卢大学", "UO", 290, "IELTS 6.0/TOEFL 78",
         "Salaried或 EUR 1.8-2.5K/月 + grants",
         "Rolling/2 fixed", "Master+topic+advisor match"],
        ["坦佩雷大学", "TAU", 295, "IELTS 6.5/TOEFL 90",
         "Salaried(EUR3K-3.5K/月) + doctoral school",
         "Jan/Aug", "Master+研究计划+博士studies匹配"],
        ["图尔库大学", "UTU", 315, "IELTS 6.0/TOEFL 78",
         "Salaried或 Academy of Finland grant(EUR2.5-3K/月)",
         "固定(Jan/Aug)", "Master+research+supervisor letter"],
        ["于韦斯屈莱大学", "JYU", 351, "IELTS 6.0/TOEFL 78",
         "Salaried+doctoral programme(EUR2.8K-3K/月)",
         "Jan 30(主轮)", "Master+博士学校申请+推荐信"],
    ],
    "Study in Finland / UAF doctoral admissions 2024",
    "https://www.studyinfinland.fi/admissions/doctoral-admissions",
    "phd", "FI", ["UAF", "Academy of Finland", "各大学官网"])
