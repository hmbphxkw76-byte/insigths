"""
auto_register.py — 自动发现并注册所有内置数据管道

任何其他模块都可以通过以下方式导入:

    from src.data_engine.pipes import auto_register  # noqa: F401

初始化时自动将本目录下所有 DataPipe 子类注册到全局 PipeRunner.
"""

from loguru import logger

from src.data_engine import get_runner

# ── 导入各管道模块（触发注册） ──
from src.data_engine.pipes import macro_pipes  # noqa: F401
from src.data_engine.pipes import tech_pipes  # noqa: F401
from src.data_engine.pipes import cyber_pipes  # noqa: F401
from src.data_engine.pipes import realestate_pipes  # noqa: F401
from src.data_engine.pipes import migration_pipes  # noqa: F401
from src.data_engine.pipes import study_abroad_pipes  # noqa: F401
from src.data_engine.pipes import driver_pipes  # noqa: F401
from src.data_engine.pipes import nz_driver_pipes  # noqa: F401
from src.data_engine.pipes import profession_pipes  # noqa: F401
from src.data_engine.pipes import extra_pipes  # noqa: F401

# ── 显式导入所有管道类（按模块分组） ──

# macro_pipes
from src.data_engine.pipes.macro_pipes import (  # noqa: F401
    IMFWEOPipe,
    FREDMacroPipe,
    WorldBankPipe,
    OECDCLIPipe,
    EconomicCalendarPipe,
)

# tech_pipes
from src.data_engine.pipes.tech_pipes import (  # noqa: F401
    SemiconductorSalesPipe,
    AIComputeDemandPipe,
    CompanyEarningsPipe,
    AIStartupFundingPipe,
    NewsFinancialPipe,
    BenchmarkPipe,
    TechGiantsPipe,
)

# cyber_pipes
from src.data_engine.pipes.cyber_pipes import (  # noqa: F401
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

# realestate_pipes
from src.data_engine.pipes.realestate_pipes import (  # noqa: F401
    DLDTransactionsPipe,
    ValustratIndexPipe,
    MortgageRatesPipe,
    SupplyPipelinePipe,
    PopulationDemographicsPipe,
    RealEstateNewsPipe,
)

# migration_pipes
from src.data_engine.pipes.migration_pipes import (  # noqa: F401
    JapanImmigrationPolicyPipe,
    HSPUniversityListPipe,
    HSPApprovalStatsPipe,
    JapanArrivalRequirementsPipe,
    JapanLaborLawForeignWorkersPipe,
    JapanPRNaturalizationStatsPipe,
)

# driver_pipes
from src.data_engine.pipes.driver_pipes import (  # noqa: F401
    JapanSSWPolicyPipe,
    JapanDriverLicenseConversionPipe,
    JapanTruckingIndustryStatsPipe,
    JapanSSWDriverExamPipe,
    Japan2024ProblemTruckPipe,
    JapanDriverSalaryPipe,
    JapanSSWApprovalStatsPipe,
)

# profession_pipes
from src.data_engine.pipes.profession_pipes import (  # noqa: F401
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

# nz_driver_pipes
from src.data_engine.pipes.nz_driver_pipes import (  # noqa: F401
    NZImmigrationPolicyDriverPipe,
    NZTruckingIndustryStatsPipe,
    NZDriverLicenseConversionPipe,
    NZDriverSalaryPipe,
    NZLaborLawForeignWorkersPipe,
    NZArrivalRequirementsPipe,
    NZPRPathwayDriverPipe,
    NZDriverShortageOutlookPipe,
)

# extra_pipes (补充缺失管道)
from src.data_engine.pipes.extra_pipes import (  # noqa: F401
    DEVisaPolicyStudentPipe,
    AIRegulationPipe,
    CyberCompanyEarningsPipe,
    AitalentFlowPipe,
)

# ── 收集所有显式定义的静态管道类 ──
_ALL_STATIC_PIPE_CLASSES = [
    # macro (5)
    IMFWEOPipe,
    FREDMacroPipe,
    WorldBankPipe,
    OECDCLIPipe,
    EconomicCalendarPipe,
    # tech (7)
    SemiconductorSalesPipe,
    AIComputeDemandPipe,
    CompanyEarningsPipe,
    AIStartupFundingPipe,
    NewsFinancialPipe,
    BenchmarkPipe,
    TechGiantsPipe,
    # cyber (18)
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
    # realestate (6)
    DLDTransactionsPipe,
    ValustratIndexPipe,
    MortgageRatesPipe,
    SupplyPipelinePipe,
    PopulationDemographicsPipe,
    RealEstateNewsPipe,
    # migration (6)
    JapanImmigrationPolicyPipe,
    HSPUniversityListPipe,
    HSPApprovalStatsPipe,
    JapanArrivalRequirementsPipe,
    JapanLaborLawForeignWorkersPipe,
    JapanPRNaturalizationStatsPipe,
    # driver (7)
    JapanSSWPolicyPipe,
    JapanDriverLicenseConversionPipe,
    JapanTruckingIndustryStatsPipe,
    JapanSSWDriverExamPipe,
    Japan2024ProblemTruckPipe,
    JapanDriverSalaryPipe,
    JapanSSWApprovalStatsPipe,
    # profession (16)
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
    # extra (4)
    DEVisaPolicyStudentPipe,
    AIRegulationPipe,
    CyberCompanyEarningsPipe,
    AitalentFlowPipe,
    # nz driver (8)
    NZImmigrationPolicyDriverPipe,
    NZTruckingIndustryStatsPipe,
    NZDriverLicenseConversionPipe,
    NZDriverSalaryPipe,
    NZLaborLawForeignWorkersPipe,
    NZArrivalRequirementsPipe,
    NZPRPathwayDriverPipe,
    NZDriverShortageOutlookPipe,
]


def ensure_all_pipes_registered():
    """确保所有内置管道已注册.程序启动时调用."""
    runner = get_runner()

    pipe_classes = []

    # ── 显式定义的静态管道 ──
    pipe_classes.extend(_ALL_STATIC_PIPE_CLASSES)

    # ── 留学管道 (动态生成) ──
    pipe_classes.extend(study_abroad_pipes.get_all_pipes())

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
