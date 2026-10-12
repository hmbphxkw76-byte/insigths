"""
Career Domain — 海外就业与职业移民数据管道

覆盖: 签证移民(日本/新西兰/通用) × 职业分析(人才需求/薪资/技能/认证)
对齐: prompts/career/
"""

from src.data_engine.pipes.career.visa import (
    # 日本签证管道
    JapanSSWPolicyPipe,
    JapanDriverLicenseConversionPipe,
    JapanTruckingIndustryStatsPipe,
    JapanSSWDriverExamPipe,
    Japan2024ProblemTruckPipe,
    JapanDriverSalaryPipe,
    JapanSSWApprovalStatsPipe,
    JapanArrivalRequirementsPipe,
    JapanLaborLawForeignWorkersPipe,
    JapanPRNaturalizationStatsPipe,
    # 新西兰签证管道
    NZImmigrationPolicyDriverPipe,
    NZTruckingIndustryStatsPipe,
    NZDriverLicenseConversionPipe,
    NZDriverSalaryPipe,
    NZLaborLawForeignWorkersPipe,
    NZArrivalRequirementsPipe,
    NZPRPathwayDriverPipe,
    NZDriverShortageOutlookPipe,
    # 日本高度人才管道
    JapanImmigrationPolicyPipe,
    HSPUniversityListPipe,
    HSPApprovalStatsPipe,
    # 通用签证管道
    DEVisaPolicyStudentPipe,
)

from src.data_engine.pipes.career.profession import (
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

__all__ = [
    # 日本签证
    "JapanSSWPolicyPipe",
    "JapanDriverLicenseConversionPipe",
    "JapanTruckingIndustryStatsPipe",
    "JapanSSWDriverExamPipe",
    "Japan2024ProblemTruckPipe",
    "JapanDriverSalaryPipe",
    "JapanSSWApprovalStatsPipe",
    "JapanArrivalRequirementsPipe",
    "JapanLaborLawForeignWorkersPipe",
    "JapanPRNaturalizationStatsPipe",
    # 新西兰签证
    "NZImmigrationPolicyDriverPipe",
    "NZTruckingIndustryStatsPipe",
    "NZDriverLicenseConversionPipe",
    "NZDriverSalaryPipe",
    "NZLaborLawForeignWorkersPipe",
    "NZArrivalRequirementsPipe",
    "NZPRPathwayDriverPipe",
    "NZDriverShortageOutlookPipe",
    # 日本高度人才
    "JapanImmigrationPolicyPipe",
    "HSPUniversityListPipe",
    "HSPApprovalStatsPipe",
    # 通用签证
    "DEVisaPolicyStudentPipe",
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
]
