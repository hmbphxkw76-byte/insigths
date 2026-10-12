"""
auto_register.py — 自动发现并注册所有内置数据管道

任何其他模块都可以通过以下方式导入:

    from src.data_engine.pipes import auto_register  # noqa: F401

初始化时自动将本目录下所有 DataPipe 子类注册到全局 PipeRunner.

目录结构对齐 prompts/:
  pipes/career/     → 海外就业・签证移民
  pipes/macro/      → 宏观经济
  pipes/realestate/ → 房地产
  pipes/studyabroad/→ 留学
  pipes/tech/       → 科技(AI/网络安全/半导体)
"""

from loguru import logger

from src.data_engine import get_runner

# ── 导入各主题域管道模块（触发注册） ──
from src.data_engine.pipes import career as _career  # noqa: F401
from src.data_engine.pipes import macro as _macro  # noqa: F401
from src.data_engine.pipes import realestate as _realestate  # noqa: F401
from src.data_engine.pipes import studyabroad as _studyabroad  # noqa: F401
from src.data_engine.pipes import tech as _tech  # noqa: F401

# ── 显式导入所有管道类（按主题域分组） ──

# career - 日本签证 (japan_visa_pipes)
from src.data_engine.pipes.career.japan_visa_pipes import (
    JapanSSWPolicyPipe,
    JapanDriverLicenseConversionPipe,
    JapanTruckingIndustryStatsPipe,
    JapanSSWDriverExamPipe,
    Japan2024ProblemTruckPipe,
    JapanDriverSalaryPipe,
    JapanSSWApprovalStatsPipe,
)

# career - 新西兰签证 (nz_visa_pipes)
from src.data_engine.pipes.career.nz_visa_pipes import (
    NZImmigrationPolicyDriverPipe,
    NZTruckingIndustryStatsPipe,
    NZDriverLicenseConversionPipe,
    NZDriverSalaryPipe,
    NZLaborLawForeignWorkersPipe,
    NZArrivalRequirementsPipe,
    NZPRPathwayDriverPipe,
    NZDriverShortageOutlookPipe,
)

# career - 日本高度人才 (migration_pipes)
from src.data_engine.pipes.career.migration_pipes import (
    JapanImmigrationPolicyPipe,
    HSPUniversityListPipe,
    HSPApprovalStatsPipe,
    JapanArrivalRequirementsPipe,
    JapanLaborLawForeignWorkersPipe,
    JapanPRNaturalizationStatsPipe,
)

# career - 通用职业分析 (profession_pipes)
from src.data_engine.pipes.career.profession_pipes import (
    CountryLaborMarketPipe,
    ProfessionTalentDemandPipe,
    ProfessionSalaryBenchmarkPipe,
    CountryDigitalTransformationPipe,
    ProfessionSkillRequirementsPipe,
    CountryExpatVisaPolicyPipe,
    CountryCostOfLivingPipe,
    GlobalCityComparisonPipe,
    AIDisruptionRiskPipe,
    ComplianceFrameworkPipe,
    CandidateSupplyMetricsPipe,
    EmployerMicroIntelligencePipe,
    VisaProcessTimelinePipe,
    CrossCulturalAdaptationPipe,
    SalaryNegotiationTacticsPipe,
    ProfessionalCertificationPathPipe,
)

# career - 补充管道 (DE签证/AI法规/网络安全财报/AI人才)
from src.data_engine.pipes.career.extra_pipes import (
    DEVisaPolicyStudentPipe,
    AIRegulationPipe,
    CyberCompanyEarningsPipe,
    AitalentFlowPipe,
)

# macro - 宏观经济 (macro_pipes)
from src.data_engine.pipes.macro.macro_pipes import (
    IMFWEOPipe,
    FREDMacroPipe,
    WorldBankPipe,
    OECDCLIPipe,
    EconomicCalendarPipe,
)

# tech - AI & 通用科技 (tech_pipes)
from src.data_engine.pipes.tech.tech_pipes import (
    SemiconductorSalesPipe,
    AIComputeDemandPipe,
    CompanyEarningsPipe,
    AIStartupFundingPipe,
    NewsFinancialPipe,
    BenchmarkPipe,
    TechGiantsPipe,
)

# tech - 网络安全 (cyber_pipes)
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
)

# realestate - 海外房地产 (realestate_pipes)
from src.data_engine.pipes.realestate.realestate_pipes import (
    DLDTransactionsPipe,
    ValustratIndexPipe,
    MortgageRatesPipe,
    SupplyPipelinePipe,
    PopulationDemographicsPipe,
    RealEstateNewsPipe,
)

# studyabroad - 海外留学 (study_abroad_pipes)
from src.data_engine.pipes.studyabroad.study_abroad_pipes import (
    get_all_pipes as _study_abroad_get_all,
)

# ── 收集所有显式定义的静态管道类 ──
_ALL_STATIC_PIPE_CLASSES = [
    # ── Career 域 (海外就业) ──
    # 日本签证 (7)
    JapanSSWPolicyPipe,
    JapanDriverLicenseConversionPipe,
    JapanTruckingIndustryStatsPipe,
    JapanSSWDriverExamPipe,
    Japan2024ProblemTruckPipe,
    JapanDriverSalaryPipe,
    JapanSSWApprovalStatsPipe,
    # 新西兰签证 (8)
    NZImmigrationPolicyDriverPipe,
    NZTruckingIndustryStatsPipe,
    NZDriverLicenseConversionPipe,
    NZDriverSalaryPipe,
    NZLaborLawForeignWorkersPipe,
    NZArrivalRequirementsPipe,
    NZPRPathwayDriverPipe,
    NZDriverShortageOutlookPipe,
    # 日本高度人才 (6)
    JapanImmigrationPolicyPipe,
    HSPUniversityListPipe,
    HSPApprovalStatsPipe,
    JapanArrivalRequirementsPipe,
    JapanLaborLawForeignWorkersPipe,
    JapanPRNaturalizationStatsPipe,
    # 职业分析 (16)
    CountryLaborMarketPipe,
    ProfessionTalentDemandPipe,
    ProfessionSalaryBenchmarkPipe,
    CountryDigitalTransformationPipe,
    ProfessionSkillRequirementsPipe,
    CountryExpatVisaPolicyPipe,
    CountryCostOfLivingPipe,
    GlobalCityComparisonPipe,
    AIDisruptionRiskPipe,
    ComplianceFrameworkPipe,
    CandidateSupplyMetricsPipe,
    EmployerMicroIntelligencePipe,
    VisaProcessTimelinePipe,
    CrossCulturalAdaptationPipe,
    SalaryNegotiationTacticsPipe,
    ProfessionalCertificationPathPipe,
    # 补充 (4)
    DEVisaPolicyStudentPipe,
    AIRegulationPipe,
    CyberCompanyEarningsPipe,
    AitalentFlowPipe,
    # ── Macro 域 (宏观经济, 5) ──
    IMFWEOPipe,
    FREDMacroPipe,
    WorldBankPipe,
    OECDCLIPipe,
    EconomicCalendarPipe,
    # ── Tech 域 (科技) ──
    # AI & 通用科技 (7)
    SemiconductorSalesPipe,
    AIComputeDemandPipe,
    CompanyEarningsPipe,
    AIStartupFundingPipe,
    NewsFinancialPipe,
    BenchmarkPipe,
    TechGiantsPipe,
    # 网络安全 (18)
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
    # ── Real Estate 域 (房地产, 6) ──
    DLDTransactionsPipe,
    ValustratIndexPipe,
    MortgageRatesPipe,
    SupplyPipelinePipe,
    PopulationDemographicsPipe,
    RealEstateNewsPipe,
]


def ensure_all_pipes_registered():
    """确保所有内置管道已注册.程序启动时调用."""
    runner = get_runner()

    pipe_classes = []

    # ── 显式定义的静态管道 ──
    pipe_classes.extend(_ALL_STATIC_PIPE_CLASSES)

    # ── 留学管道 (动态生成) ──
    try:
        pipe_classes.extend(_study_abroad_get_all())
    except Exception as e:
        logger.warning(f"留学管道加载失败: {e}")

    # ── 注册所有收集到的管道 ──
    from src.data_engine import register_pipe

    registered = 0
    for cls in pipe_classes:
        try:
            if cls.pipe_id and cls.pipe_id not in runner._pipe_registry:
                register_pipe(cls)
                registered += 1
                logger.debug(f"自动注册管道: {cls.pipe_id}")
        except Exception as e:
            logger.warning(f"注册管道失败 {cls.__name__}: {e}")

    total = len(runner.list_pipes())
    logger.info(f"数据管道就绪: 共 {total} 条 (本次新注册 {registered} 条)")
