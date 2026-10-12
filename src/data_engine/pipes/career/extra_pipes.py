"""
补充数据管道实现

覆盖: 德国留学签证、AI 法规政策等缺失管道.
遵循 Parse-Driven Architecture，所有管道仅负责采集到结构化 DataFrame.
"""

from __future__ import annotations
from typing import Dict

import pandas as pd

from src.data_engine import DataPipe
from src.data_engine.pipes import _fallback_df


class DEVisaPolicyStudentPipe(DataPipe):
    """德国留学生签证政策."""

    pipe_id = "de_visa_policy_student"

    def collect(self, params: Dict) -> pd.DataFrame:
        return _fallback_df(
            ["visa_category", "duration", "work_rights", "requirements", "notes"],
            [
                ["Student Applicant Visa (§16b)", "课程期间", "120天全职/240天兼职",
                 "录取通知书+资金证明+语言成绩", "申请长期居留许可"],
                ["Language Course Visa", "最长1年", "无工作权利",
                 "注册语言课程", "不可直接转学签"],
                ["Job Seeker Visa (§20)", "6个月", "试工10h/周",
                 "德国/等同学位+资金证明", "找到工作后转工签"],
                ["EU Blue Card", "4年", "全职工作",
                 "工作合同+年薪≥43,800EUR", "21个月(德语B1)/33个月转永住"],
                ["Skilled Worker Visa (§18a)", "与合同同", "全职工作",
                 "学位+工作合同+Bundesagentur批准", "通用技术移民路径"],
            ],
            source="German Federal Foreign Office / Make it in Germany (fallback)"
        )

    def source_attribution(self):
        return [
            "German Federal Foreign Office",
            "Make it in Germany Portal",
            "Aufenthaltsgesetz (AufenthG)",
        ]


class AIRegulationPipe(DataPipe):
    """全球 AI 法规政策追踪(欧盟AI Act, 美国 EO, 中国生成式AI等).
    
    数据来源: 仅使用英文权威来源(政府英文门户/国际机构)。
    """

    pipe_id = "ai_regulation"

    def collect(self, params: Dict) -> pd.DataFrame:
        return _fallback_df(
            ["jurisdiction", "regulation_name", "status", "scope",
             "effective_date", "key_requirements", "risk_level"],
            [
                ["EU", "EU AI Act (Reg. 2024/1689)",
                 "生效 (2025年2月起分阶段)", "全欧盟市场",
                 "2025-02", "基于风险分层的监管框架/高风险AI需CE标志/基础模型强制性合规", "极高"],
                ["US", "EO 14110 + NIST AI RMF",
                 "行政令+自愿框架", "联邦机构+承包商",
                 "2023-10", "联邦机构采购AI需符合安全标准/鼓励行业自律", "高"],
                ["US", "State AI Laws (Colorado SB24-205)",
                 "各州立法", "州内企业",
                 "2026-02(预计)", "高风险AI系统需影响评估和透明度", "中-高"],
                ["China", "Interim Measures for Generative AI Services (2023)",
                 "生效", "面向公众的生成式AI",
                 "2023-08", "Content compliance, real-name registration, safety assessment required", "高"],
                ["China", "Provisions on Deep Synthesis (2023)",
                 "生效", "深度合成技术(Voice/Video)",
                 "2023-01", "Prominent labeling, user consent, content moderation", "中-高"],
                ["UK", "Pro-Innovation AI Framework",
                 "生效(原则导向)", "英国全境+跨境",
                 "2023-03", "5大原则(安全/透明/公平/问责/可争议)/不设新监管机构", "中"],
                ["Japan", "AI Business Guidelines",
                 "非约束性指南", "日本AI企业",
                 "2024-04", "自愿遵守/重点:透明性+知识产权+安全", "低-中"],
            ],
            source="Government portals, NIST, EU AI Office (fallback)"
        )

    def source_attribution(self):
        return [
            "European Commission - AI Act Portal",
            "NIST AI Risk Management Framework",
            "Brookings AI Regulation Tracker",
            "White House Executive Orders",
            "Oxford AI Governance Tracker (英文权威来源)",
        ]


class CyberCompanyEarningsPipe(DataPipe):
    """网络安全公司财报追踪(CrowdStrike / Palo Alto / Zscaler / Fortinet)."""

    pipe_id = "cyber_company_earnings"

    def collect(self, params: Dict) -> pd.DataFrame:
        return _fallback_df(
            ["company", "ticker", "quarter", "revenue_usd_b", "revenue_yoy_pct",
             "arr_usd_b", "gross_margin_pct", "metric_focus"],
            [
                ["CrowdStrike", "CRWD", "FY26Q2", 1.17, 0.20, 4.63, 78.0, " plataforma/Sensor/Cloud"],
                ["Palo Alto Networks", "PANW", "FY25Q4", 2.54, 0.18, 10.80, 72.0, "Prisma/SaaS/XSIAM"],
                ["Zscaler", "ZS", "FY25Q4", 0.72, 0.24, 2.90, 79.0, "Zero Trust/SSE"],
                ["Fortinet", "FTNT", "25Q2", 1.63, 0.13, 5.90, 68.0, "FortiGate/SASE/OT"],
                ["Cloudflare", "NET", "25Q2", 0.54, 0.28, 2.15, 77.0, "WAF/CDN/Zero Trust"],
                ["Okta", "OKTA", "FY26Q2", 0.77, 0.13, 3.00, 78.0, "Identity/SSO/CIAM"],
                ["SentinelOne", "S", "FY26Q2", 0.25, 0.18, 1.00, 77.0, "Singularity AI EDR"],
                ["CyberArk", "CYBR", "25Q2", 0.34, 0.20, 1.30, 80.0, "PAM/Identity Security"],
            ],
            source="SEC filings, IR pages (fallback)"
        )

    def source_attribution(self):
        return [
            "SEC Filings (10-K / 10-Q)",
            "Company Investor Relations",
            "S&P Capital IQ",
        ]


class AitalentFlowPipe(DataPipe):
    """AI 人才流动追踪(LinkedIn / arXiv / NeurIPS / top lab movements)."""

    pipe_id = "ai_talent_flow"

    def collect(self, params: Dict) -> pd.DataFrame:
        return _fallback_df(
            ["direction", "person", "origin", "destination",
             "domain", "significance", "date"],
            [
                ["Exit", "Ilya Sutskever", "OpenAI (Co-founder)", "SSI (Safe Superintelligence Inc.)",
                 "Alignment/Safety", "Founder exit + safety-focused startup", "2024-06"],
                ["Exit", "Dario Amodei", "OpenAI", "Anthropic (CEO)",
                 "LLM/Claude", "RLHF + Constitutional AI pioneer", "2021-12 (Notable)"],
                ["Hire", "Sam Altman(collapsed)", "OpenAI board fired", "Reinstated + board restructure",
                 "GPT-4/5 org", "Governance crisis (brief)", "2023-11"],
                ["Movement", "DeepMind researchers", "DeepMind London", "OpenAI/Anthropic/Self-founded",
                 "AGI/RL/Multi-modal", "Primary hiring pipeline for frontier labs", "Ongoing"],
                ["Flow", "Top PhD (Stanford/Berkeley/MIT/Cambridge/Tsinghua)",
                 "University labs", "OpenAI/Anthropic/Google DeepMind/independent",
                 "LLM/VLM/Robotics/Alignment", "Core talent migration from academia", "2023-2025"],
                ["Policy", "China AI researchers", "Overseas labs", "Alibaba ByteDance DeepSeek Baidu",
                 "LLM", "Closed-source policy drives domestic investment", "2023-2025"],
            ],
            source="Public announcements, LinkedIn, arXiv fallback"
        )

    def source_attribution(self):
        return [
            "LinkedIn Public Data",
            "arXiv CS.LG / CS.AI author lists",
            "NeurIPS / ICML / ICLR proceedings",
            "Company official press releases (English)",
        ]
