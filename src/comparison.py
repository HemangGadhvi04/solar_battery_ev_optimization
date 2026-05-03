# src/comparison.py

import pandas as pd

from src.simulator import run_simulation


def run_controller_comparison():
    controllers = [
        "no_battery",
        "naive",
        "rule_based",
        "optimization",
        "degradation_aware"
    ]

    summary_results = []
    all_results = []

    for controller in controllers:
        df = run_simulation(controller_type=controller)

        total_import = df["grid_import_kw"].sum()
        total_export = df["grid_export_kw"].sum()
        total_energy_cost = df["energy_net_cost_rs"].sum()
        total_degradation_cost = df["degradation_cost_rs"].sum()
        total_cost = df["net_cost_rs"].sum()
        final_soc = df["battery_soc"].iloc[-1] * 100
        final_soh = df["battery_soh"].iloc[-1] * 100
        capacity_loss = df["battery_capacity_loss_percent"].iloc[-1]
        throughput = df["battery_throughput_kwh"].iloc[-1]

        summary_results.append({
            "controller": controller,
            "total_grid_import_kwh": total_import,
            "total_grid_export_kwh": total_export,
            "total_energy_cost_rs": total_energy_cost,
            "total_degradation_cost_rs": total_degradation_cost,
            "total_net_cost_rs": total_cost,
            "final_soc_percent": final_soc,
            "final_soh_percent": final_soh,
            "capacity_loss_percent": capacity_loss,
            "battery_throughput_kwh": throughput
        })

        all_results.append(df)

    summary_df = pd.DataFrame(summary_results)
    detailed_df = pd.concat(all_results, ignore_index=True)

    return summary_df, detailed_df