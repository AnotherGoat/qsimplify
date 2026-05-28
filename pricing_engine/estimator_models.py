from typing import Any, Optional
from pydantic import BaseModel

class BackendProfile(BaseModel):
    phase_cost: float
    single_qubit_cost: float
    sqrt_cost: float
    two_qubit_cost: float
    three_qubit_cost: float
    swap_cost: float
    measure_cost: float
    reset_cost: float
    repetition_delay_cost: float
    base_time_ns: float = 30.0  # Base time in nanoseconds to multiply the proportions by

class EstimationRequest(BaseModel):
    gates: list[dict[str, Any]]
    shots: int
    backend_profile: BackendProfile

class EstimatedCost(BaseModel):
    provider: str
    plan_name: str
    price_label: str
    cost_usd: Optional[float]

class ProviderCostEstimates(BaseModel):
    provider: str
    status: str
    estimates: list[EstimatedCost]

class EstimationResponse(BaseModel):
    execution_time: float
    costs: list[ProviderCostEstimates]
