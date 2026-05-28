import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from pricing_engine.estimator_models import BackendProfile
from pricing_engine.time_estimator import estimate_execution_time

def test_estimate_execution_time():
    # Profile with easy numbers
    profile = BackendProfile(
        phase_cost=0.0,
        single_qubit_cost=1.0,
        sqrt_cost=2.0,
        two_qubit_cost=15.0,
        three_qubit_cost=80.0,
        swap_cost=45.0,
        measure_cost=200.0,
        reset_cost=200.0,
        repetition_delay_cost=100.0,
    )
    
    # Circuit:
    # q0: H -> CX(0,1) -> M
    # q1:        CX(0,1) -> M
    # Costs:
    # H: 1.0
    # CX: 15.0
    # M: 200.0
    # Critical path logic:
    # q0 after H = 1.0
    # CX starts at max(1.0, 0.0) = 1.0
    # CX ends at 1.0 + 15.0 = 16.0
    # q0, q1 both are at 16.0
    # M on q0 starts at 16.0, ends at 216.0
    # M on q1 starts at 16.0, ends at 216.0
    # Max time = 216.0
    # Total time = shots * (critical_path + repetition) = 1000 * (216.0 + 100.0) = 316000.0
    
    gates = [
        {"name": "h", "qubit": 0},
        {"name": "cx", "control_qubit": 0, "target_qubit": 1},
        {"name": "measure", "qubit": 0, "bit": 0},
        {"name": "measure", "qubit": 1, "bit": 1},
    ]
    
    total_time = estimate_execution_time(gates, 1000, profile)
    
    assert total_time == 316000.0

if __name__ == "__main__":
    test_estimate_execution_time()
    print("Tests passed!")
