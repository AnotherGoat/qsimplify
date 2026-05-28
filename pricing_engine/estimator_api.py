import os
import sys

# Add the project root to sys.path so we can import pricing_engine and qsimplify modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pricing_engine.estimator_models import (
    EstimationRequest,
    EstimationResponse,
    EstimatedCost,
    ProviderCostEstimates,
)
from pricing_engine.time_estimator import estimate_execution_time
from pricing_engine.scraperv2 import get_pricing_data

app = FastAPI(
    title="QSimplify Pricing Estimator",
    description="API for estimating execution time and costs of quantum circuits.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/estimate", response_model=EstimationResponse)
def estimate_cost(request: EstimationRequest) -> EstimationResponse:
    try:
        execution_time_sec = estimate_execution_time(
            request.gates, request.shots, request.backend_profile
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error estimating time: {e}")

    try:
        pricing_data = get_pricing_data(force_refresh=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pricing data: {e}")

    providers = pricing_data.get("providers", {})
    provider_estimates = []

    # 1. AWS Braket
    aws_data = providers.get("aws_braket", {})
    aws_estimates = []
    if aws_data.get("status") == "success":
        qpu_prices = aws_data.get("data", {}).get("qpu_prices", [])
        for item in qpu_prices:
            provider_name = item.get("hardware_provider", "-")
            family = item.get("qpu_family", "-")
            per_task = item.get("per_task_usd")
            per_shot = item.get("per_shot_usd")
            
            cost = None
            if per_task is not None and per_shot is not None:
                cost = per_task + (request.shots * per_shot)
                
            aws_estimates.append(
                EstimatedCost(
                    provider=provider_name,
                    plan_name=family,
                    price_label="Per task + per shot",
                    cost_usd=cost,
                )
            )
    
    provider_estimates.append(
        ProviderCostEstimates(
            provider="AWS Braket",
            status=aws_data.get("status", "error"),
            estimates=aws_estimates,
        )
    )

    # Convert heuristic time to real seconds
    # execution_time_sec contains the heuristic score. 
    # Real time = (heuristic * base_time_ns) / 1,000,000,000
    real_time_seconds = (execution_time_sec * request.backend_profile.base_time_ns) / 1e9

    # 2. IBM Quantum
    ibm_data = providers.get("ibm_quantum", {})
    ibm_estimates = []
    if ibm_data.get("status") == "success":
        plans = ibm_data.get("data", {}).get("plans", [])
        for plan in plans:
            plan_name = plan.get("plan", "-")
            price_sec = plan.get("price_usd_per_second")
            label = plan.get("price_label", "-")
            
            cost = None
            if price_sec is not None:
                cost = real_time_seconds * price_sec
                
            ibm_estimates.append(
                EstimatedCost(
                    provider="IBM",
                    plan_name=plan_name,
                    price_label=label,
                    cost_usd=cost,
                )
            )
            
    provider_estimates.append(
        ProviderCostEstimates(
            provider="IBM Quantum",
            status=ibm_data.get("status", "error"),
            estimates=ibm_estimates,
        )
    )

    return EstimationResponse(
        execution_time=execution_time_sec,
        costs=provider_estimates,
    )


if __name__ == "__main__":
    uvicorn.run("pricing_engine.estimator_api:app", host="127.0.0.1", port=5002, reload=True)
