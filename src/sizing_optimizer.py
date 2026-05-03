# src/sizing_optimizer.py

import pandas as pd

from src.config import (
    TIME_STEP_HOURS,
    SOC_INITIAL,
    PV_SIZE_KW,
    BATTERY_CAPACITY_KWH,
    HOURS_PER_DAY
)

from src.long_term_simulation import prepare_full_year_dataframe
from src.controller_optimization import run_optimization_controller
from src.degradation_model import BatteryDegradation
from src.tariff_model import calculate_cost


def run_sizing_optimization():
    """
    Runs PV + battery sizing optimization for Ahmedabad case study.

    To keep runtime manageable, this version uses representative days from
    the full PVGIS TMY year and annualizes the result.

    It tests multiple PV sizes and battery sizes using the same real
    Ahmedabad weather dataset.
    """

    pv_sizes_kw = [3, 4, 5, 6, 7, 8]
    battery_sizes_kwh = [5, 7.5, 10, 12.5, 15]

    # Representative days spread across the year
    representative_days = [
        15, 45, 75, 105, 135, 165,
        195, 225, 255, 285, 315, 345
    ]

    annualization_factor = 365 / len(representative_days)

    print("Preparing full-year Ahmedabad dataframe...")
    full_df = prepare_full_year_dataframe()

    # Convert current PV column into 1 kW base PV profile
    full_df["pv_per_kw"] = full_df["pv_power_kw"] / PV_SIZE_KW

    results = []

    for pv_size in pv_sizes_kw:
        for battery_size in battery_sizes_kwh:
            print(f"Testing PV={pv_size} kW, Battery={battery_size} kWh")

            degradation = BatteryDegradation(initial_soh=1.0)
            current_soc = SOC_INITIAL

            total_grid_import = 0.0
            total_grid_export = 0.0
            total_energy_cost = 0.0
            total_degradation_cost = 0.0
            total_net_cost = 0.0
            total_throughput = 0.0

            for day in representative_days:
                daily_df = full_df[full_df["day"] == day].copy().reset_index(drop=True)

                # Scale PV power according to tested PV size
                daily_df["pv_power_kw"] = daily_df["pv_per_kw"] * pv_size

                # Battery power rating assumption:
                # max power = 0.5C, limited between 2 kW and 7.5 kW
                max_battery_power_kw = min(max(0.5 * battery_size, 2.0), 7.5)

                optimized = run_optimization_controller(
                    daily_df,
                    degradation_aware=True,
                    initial_soc=current_soc,
                    battery_capacity_kwh=battery_size,
                    max_charge_kw=max_battery_power_kw,
                    max_discharge_kw=max_battery_power_kw
                )

                daily_grid_import = 0.0
                daily_grid_export = 0.0
                daily_energy_cost = 0.0
                daily_degradation_cost = 0.0
                daily_net_cost = 0.0
                daily_throughput = 0.0

                total_daily_throughput = sum(
                    optimized["battery_charge"] + optimized["battery_discharge"]
                ) * TIME_STEP_HOURS

                for i, row in daily_df.iterrows():
                    battery_charge = float(optimized["battery_charge"][i])
                    battery_discharge = float(optimized["battery_discharge"][i])
                    grid_import = float(optimized["grid_import"][i])
                    grid_export = float(optimized["grid_export"][i])

                    charge_energy_kwh = battery_charge * TIME_STEP_HOURS
                    discharge_energy_kwh = battery_discharge * TIME_STEP_HOURS

                    degradation_data = degradation.update(
                        charge_energy_kwh,
                        discharge_energy_kwh,
                        TIME_STEP_HOURS
                    )

                    import_cost, export_revenue, energy_net_cost = calculate_cost(
                        grid_import * TIME_STEP_HOURS,
                        grid_export * TIME_STEP_HOURS
                    )

                    if total_daily_throughput > 0:
                        step_throughput = (
                            battery_charge + battery_discharge
                        ) * TIME_STEP_HOURS

                        degradation_cost_rs = (
                            optimized["degradation_cost_rs"]
                            * step_throughput
                            / total_daily_throughput
                        )
                    else:
                        degradation_cost_rs = 0.0

                    net_cost = energy_net_cost + degradation_cost_rs

                    daily_grid_import += grid_import * TIME_STEP_HOURS
                    daily_grid_export += grid_export * TIME_STEP_HOURS
                    daily_energy_cost += energy_net_cost
                    daily_degradation_cost += degradation_cost_rs
                    daily_net_cost += net_cost
                    daily_throughput += charge_energy_kwh + discharge_energy_kwh

                current_soc = float(optimized["soc"][-1])

                total_grid_import += daily_grid_import
                total_grid_export += daily_grid_export
                total_energy_cost += daily_energy_cost
                total_degradation_cost += daily_degradation_cost
                total_net_cost += daily_net_cost
                total_throughput += daily_throughput

            annual_grid_import = total_grid_import * annualization_factor
            annual_grid_export = total_grid_export * annualization_factor
            annual_energy_cost = total_energy_cost * annualization_factor
            annual_degradation_cost = total_degradation_cost * annualization_factor
            annual_net_cost = total_net_cost * annualization_factor
            annual_throughput = total_throughput * annualization_factor

            final_soh_percent = degradation.soh * 100
            estimated_usable_capacity_kwh = battery_size * degradation.soh

            results.append({
                "pv_size_kw": pv_size,
                "battery_size_kwh": battery_size,
                "battery_power_limit_kw": max_battery_power_kw,
                "annual_grid_import_kwh": annual_grid_import,
                "annual_grid_export_kwh": annual_grid_export,
                "annual_energy_cost_rs": annual_energy_cost,
                "annual_degradation_cost_rs": annual_degradation_cost,
                "annual_net_cost_rs": annual_net_cost,
                "annual_battery_throughput_kwh": annual_throughput,
                "final_soh_percent": final_soh_percent,
                "estimated_usable_capacity_kwh": estimated_usable_capacity_kwh
            })

    result_df = pd.DataFrame(results)

    best_result = result_df.sort_values("annual_net_cost_rs").iloc[0]

    return result_df, best_result