"""
Real Estate Domain — 海外房地产数据管道

覆盖: 迪拜DLD交易数据、Valustrat价格指数、抵押贷款、供应管道、人口统计
对齐: prompts/realestate/
"""

from src.data_engine.pipes.realestate.realestate_pipes import (
    DLDTransactionsPipe,
    ValustratIndexPipe,
    MortgageRatesPipe,
    SupplyPipelinePipe,
    PopulationDemographicsPipe,
    RealEstateNewsPipe,
)

__all__ = [
    "DLDTransactionsPipe",
    "ValustratIndexPipe",
    "MortgageRatesPipe",
    "SupplyPipelinePipe",
    "PopulationDemographicsPipe",
    "RealEstateNewsPipe",
]
