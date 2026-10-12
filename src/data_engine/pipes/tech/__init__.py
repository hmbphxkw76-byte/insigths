"""
Tech Domain — 科技行业数据管道

覆盖:
  - AI: 算力需求、模型基准、融资、法规、人才流动
  - Cybersecurity: 威胁情报、市场规模、AI安全、中东/迪拜
  - Semiconductor: 销售数据、技术路线图、地缘政治
对齐: prompts/tech/
"""

# AI & 通用科技管道
from src.data_engine.pipes.tech.tech_pipes import (
    SemiconductorSalesPipe,
    AIComputeDemandPipe,
    CompanyEarningsPipe,
    AIStartupFundingPipe,
    NewsFinancialPipe,
    BenchmarkPipe,
    TechGiantsPipe,
)

# 网络安全管道
from src.data_engine.pipes.tech.cyber_pipes import (
    ThreatIntelligencePipe,
    CybersecurityMarketPipe,
    CyberMAPipe,
    CyberRegulationPipe,
    TechnologyRoadmapPipe,
    GeopoliticalChipPipe,
    IndustryNewsPipe,
    AISecurityMarketPipe,
    NISTAIRiskFramework,
    AIRedTeamPapersPipe,
    CompanyAISecurityProductsPipe,
    AISecurityStartupsPipe,
    DubaiCybersecurityMarketPipe,
    UAEPIPolicyTrackerPipe,
    GCCThreatLandscapePipe,
    DubaiCyberTalentPipe,
    MEACybersecurityVendorsPipe,
    DubaiSmartCitySecurityPipe,
    # ── P0/P1 新增管道 (v2 升级) ──
    DubaiCompetitorBenchmarkPipe,
    MEACybersecurityFundingPipe,
    DubaiComplianceCostPipe,
    SecurityForAIValueChainPipe,
    DubaiCustomerCaseStudiesPipe,
)

__all__ = [
    # AI & 通用科技
    "SemiconductorSalesPipe",
    "AIComputeDemandPipe",
    "CompanyEarningsPipe",
    "AIStartupFundingPipe",
    "NewsFinancialPipe",
    "BenchmarkPipe",
    "TechGiantsPipe",
    # 网络安全
    "ThreatIntelligencePipe",
    "CybersecurityMarketPipe",
    "CyberMAPipe",
    "CyberRegulationPipe",
    "TechnologyRoadmapPipe",
    "GeopoliticalChipPipe",
    "IndustryNewsPipe",
    "AISecurityMarketPipe",
    "NISTAIRiskFramework",
    "AIRedTeamPapersPipe",
    "CompanyAISecurityProductsPipe",
    "AISecurityStartupsPipe",
    "DubaiCybersecurityMarketPipe",
    "UAEPIPolicyTrackerPipe",
    "GCCThreatLandscapePipe",
    "DubaiCyberTalentPipe",
    "MEACybersecurityVendorsPipe",
    "DubaiSmartCitySecurityPipe",
    # ── P0/P1 新增管道 (v2 升级) ──
    "DubaiCompetitorBenchmarkPipe",
    "MEACybersecurityFundingPipe",
    "DubaiComplianceCostPipe",
    "SecurityForAIValueChainPipe",
    "DubaiCustomerCaseStudiesPipe",
]
