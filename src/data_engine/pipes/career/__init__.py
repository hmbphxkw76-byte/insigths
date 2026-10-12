"""
Career Domain — 海外就业与职业移民数据管道

覆盖: 签证移民(日本/新西兰/通用) × 职业分析(人才需求/薪资/技能/认证)
对齐: prompts/career/
"""

from src.data_engine.pipes.career.japan_visa_pipes import (
    # 日本签证管道
    JapanSSWPolicyPipe,
    JapanDriverLicenseConversionPipe,
    JapanTruckingIndustryStatsPipe,
    JapanSSWDriverExamPipe,
    Japan2024ProblemTruckPipe,
    JapanDriverSalaryPipe,
    JapanSSWApprovalStatsPipe,
)

from src.data_engine.pipes.career.nz_visa_pipes import (
    # 新西兰签证管道
    NZImmigrationPolicyDriverPipe,
    NZTruckingIndustryStatsPipe,
    NZDriverLicenseConversionPipe,
    NZDriverSalaryPipe,
    NZLaborLawForeignWorkersPipe,
    NZArrivalRequirementsPipe,
    NZPRPathwayDriverPipe,
    NZDriverShortageOutlookPipe,
)

from src.data_engine.pipes.career.migration_pipes import (
    # 日本高度人才管道
    JapanImmigrationPolicyPipe,
    HSPUniversityListPipe,
    HSPApprovalStatsPipe,
    JapanArrivalRequirementsPipe,
    JapanLaborLawForeignWorkersPipe,
    JapanPRNaturalizationStatsPipe,
)

from src.data_engine.pipes.career.profession_pipes import (
    # 职业分析管道
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

from src.data_engine.pipes.career.extra_pipes import (
    # 扩展管道
    DEVisaPolicyStudentPipe,
)

__all__ = [
    # 日本签证
    "JapanSSWPolicyPipe",
    "JapanDriverLicenseConversionPipe",
    "JapanTruckingIndustryStatsPipe",
    "JapanSSWDriverExamPipe",
    "Japan2024ProblemTruckPipe",
    "JapanDriverSalaryPipe",
    "JapanSSWApprovalStatsPipe",
    # 新西兰签证
    "NZImmigrationPolicyDriverPipe",
    "NZTruckingIndustryStatsPipe",
    "NZDriverLicenseConversionPipe",
    "NZDriverSalaryPipe",
    "NZLaborLawForeignWorkersPipe",
    "NZArrivalRequirementsPipe",
    "NZPRPathwayDriverPipe",
    "NZDriverShortageOutlookPipe",
    # 移民通用
    "JapanImmigrationPolicyPipe",
    "HSPUniversityListPipe",
    "HSPApprovalStatsPipe",
    "JapanArrivalRequirementsPipe",
    "JapanLaborLawForeignWorkersPipe",
    "JapanPRNaturalizationStatsPipe",
    # 职业分析
    "CountryLaborMarketPipe",
    "ProfessionTalentDemandPipe",
    "ProfessionSalaryBenchmarkPipe",
    "CountryDigitalTransformationPipe",
    "ProfessionSkillRequirementsPipe",
    "CountryExpatVisaPolicyPipe",
    "CountryCostOfLivingPipe",
    "GlobalCityComparisonPipe",
    "AIDisruptionRiskPipe",
    "ComplianceFrameworkPipe",
    "CandidateSupplyMetricsPipe",
    "EmployerMicroIntelligencePipe",
    "VisaProcessTimelinePipe",
    "CrossCulturalAdaptationPipe",
    "SalaryNegotiationTacticsPipe",
    "ProfessionalCertificationPathPipe",
    # 扩展
    "DEVisaPolicyStudentPipe",
]
