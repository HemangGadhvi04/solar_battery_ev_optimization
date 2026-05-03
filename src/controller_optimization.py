# src/controller_optimization.py

import cvxpy as cp
import numpy as np

from src.config import (
    TIME_STEP_HOURS,
    BATTERY_CAPACITY_KWH,
    BATTERY_MAX_CHARGE_KW,
    BATTERY_MAX_DISCHARGE_KW,
    BATTERY_EFFICIENCY,
    SOC_MIN,
    SOC_MAX,
    SOC_INITIAL,
    GRID_IMPORT_PRICE,
    GRID_EXPORT_PRICE
)

# Simple economic battery wear cost assumption
BATTERY_DEGRADATION_COST_PER_KWH = 1.50  # Rs per kWh throughput


def run_optimization_controller(
    df,
    degradation_aware=True,
    initial_soc=SOC_INITIAL,
    battery_capacity_kwh=BATTERY_CAPACITY_KWH,
    max_charge_kw=BATTERY_MAX_CHARGE_KW,
    max_discharge_kw=BATTERY_MAX_DISCHARGE_KW
):
    """
    24-hour optimization controller.

    Objective:
    minimize grid import cost - export revenue + battery degradation cost

    degradation_aware=True:
        includes battery degradation cost

    degradation_aware=False:
        only optimizes electricity cost
    """

    n = len(df)

    pv = df["pv_power_kw"].to_numpy()
    load = df["total_load_kw"].to_numpy()

    battery_charge = cp.Variable(n, nonneg=True)
    battery_discharge = cp.Variable(n, nonneg=True)
    grid_import = cp.Variable(n, nonneg=True)
    grid_export = cp.Variable(n, nonneg=True)
    soc = cp.Variable(n + 1)

    constraints = []

    constraints.append(soc[0] == initial_soc)

    for t in range(n):
        constraints.append(
            pv[t] + battery_discharge[t] + grid_import[t]
            == load[t] + battery_charge[t] + grid_export[t]
        )

        constraints.append(battery_charge[t] <= BATTERY_MAX_CHARGE_KW)
        constraints.append(battery_discharge[t] <= BATTERY_MAX_DISCHARGE_KW)

        constraints.append(
            soc[t + 1] == soc[t]
            + (battery_charge[t] * BATTERY_EFFICIENCY * TIME_STEP_HOURS / BATTERY_CAPACITY_KWH)
            - (battery_discharge[t] * TIME_STEP_HOURS / (BATTERY_EFFICIENCY * BATTERY_CAPACITY_KWH))
        )

        constraints.append(soc[t + 1] >= SOC_MIN)
        constraints.append(soc[t + 1] <= SOC_MAX)

    import_cost = cp.sum(grid_import * TIME_STEP_HOURS * GRID_IMPORT_PRICE)
    export_revenue = cp.sum(grid_export * TIME_STEP_HOURS * GRID_EXPORT_PRICE)

    battery_throughput = cp.sum(
        (battery_charge + battery_discharge) * TIME_STEP_HOURS
    )

    if degradation_aware:
        degradation_cost = battery_throughput * BATTERY_DEGRADATION_COST_PER_KWH
    else:
        degradation_cost = 0

    cycling_penalty = 0.01 * cp.sum(battery_charge + battery_discharge)

    objective = cp.Minimize(
        import_cost
        - export_revenue
        + degradation_cost
        + cycling_penalty
    )

    problem = cp.Problem(objective, constraints)

    try:
        problem.solve(solver=cp.CLARABEL)
    except Exception:
        problem.solve(solver=cp.SCS)

    if problem.status not in ["optimal", "optimal_inaccurate"]:
        raise ValueError(f"Optimization failed. Status: {problem.status}")

    return {
        "battery_charge": np.maximum(battery_charge.value, 0),
        "battery_discharge": np.maximum(battery_discharge.value, 0),
        "grid_import": np.maximum(grid_import.value, 0),
        "grid_export": np.maximum(grid_export.value, 0),
        "soc": np.maximum(soc.value[1:], 0),
        "degradation_cost_rs": float(degradation_cost.value) if degradation_aware else 0.0
    }