# src/simulator.py

import pandas as pd

from src.config import (
    SIMULATION_HOURS,
    TIME_STEP_HOURS,
    SOC_INITIAL,
    EV_REQUIRED_ENERGY_KWH,
    EV_CHARGER_POWER_KW
)

from src.pv_model import generate_pv_profile
from src.load_model import generate_home_load_profile
from src.ev_model import generate_ev_availability_profile
from src.battery_model import Battery
from src.tariff_model import calculate_cost
from src.degradation_model import BatteryDegradation

from src.controller_no_battery import run_no_battery_controller
from src.controller_naive import run_naive_controller
from src.controller_rule_based import run_rule_based_controller
from src.controller_optimization import run_optimization_controller


def prepare_base_dataframe():
    pv_df = generate_pv_profile(SIMULATION_HOURS)
    load_df = generate_home_load_profile(SIMULATION_HOURS)
    ev_df = generate_ev_availability_profile(SIMULATION_HOURS)

    df = pv_df.merge(load_df, on="hour").merge(ev_df, on="hour")

    remaining_ev_energy = EV_REQUIRED_ENERGY_KWH
    ev_charge_values = []

    for _, row in df.iterrows():
        ev_plugged = row["ev_plugged"]

        if ev_plugged == 1 and remaining_ev_energy > 0:
            ev_charge_power = min(
                EV_CHARGER_POWER_KW,
                remaining_ev_energy / TIME_STEP_HOURS
            )
            remaining_ev_energy -= ev_charge_power * TIME_STEP_HOURS
        else:
            ev_charge_power = 0.0

        ev_charge_values.append(ev_charge_power)

    df["ev_charge_kw"] = ev_charge_values
    df["total_load_kw"] = df["home_load_kw"] + df["ev_charge_kw"]

    return df


def run_simulation(controller_type="naive"):
    df = prepare_base_dataframe()

    battery = Battery(initial_soc=SOC_INITIAL)
    degradation = BatteryDegradation(initial_soh=1.0)

    results = []

    if controller_type in ["optimization", "degradation_aware"]:
        optimized = run_optimization_controller(
            df,
            degradation_aware=(controller_type == "degradation_aware")
        )

    for i, row in df.iterrows():
        hour = int(row["hour"])
        pv_power = row["pv_power_kw"]
        home_load = row["home_load_kw"]
        ev_charge_power = row["ev_charge_kw"]
        total_load = row["total_load_kw"]

        degradation_cost_rs = 0.0

        if controller_type == "no_battery":
            control = run_no_battery_controller(
                pv_power=pv_power,
                total_load=total_load
            )

            battery_charge = control["battery_charge"]
            battery_discharge = control["battery_discharge"]
            grid_import = control["grid_import"]
            grid_export = control["grid_export"]
            battery_soc = 0.0

        elif controller_type == "naive":
            control = run_naive_controller(
                pv_power=pv_power,
                total_load=total_load,
                battery=battery,
                timestep_hours=TIME_STEP_HOURS
            )

            battery_charge = control["battery_charge"]
            battery_discharge = control["battery_discharge"]
            grid_import = control["grid_import"]
            grid_export = control["grid_export"]
            battery_soc = battery.soc

        elif controller_type == "rule_based":
            control = run_rule_based_controller(
                pv_power=pv_power,
                total_load=total_load,
                battery=battery,
                timestep_hours=TIME_STEP_HOURS,
                hour=hour
            )

            battery_charge = control["battery_charge"]
            battery_discharge = control["battery_discharge"]
            grid_import = control["grid_import"]
            grid_export = control["grid_export"]
            battery_soc = battery.soc

        elif controller_type in ["optimization", "degradation_aware"]:
            battery_charge = float(optimized["battery_charge"][i])
            battery_discharge = float(optimized["battery_discharge"][i])
            grid_import = float(optimized["grid_import"][i])
            grid_export = float(optimized["grid_export"][i])
            battery_soc = float(optimized["soc"][i])

            if controller_type == "degradation_aware":
                total_throughput = sum(
                    optimized["battery_charge"] + optimized["battery_discharge"]
                ) * TIME_STEP_HOURS

                if total_throughput > 0:
                    step_throughput = (
                        battery_charge + battery_discharge
                    ) * TIME_STEP_HOURS

                    degradation_cost_rs = (
                        optimized["degradation_cost_rs"]
                        * step_throughput
                        / total_throughput
                    )

        else:
            raise ValueError(
                "Invalid controller_type. Use: no_battery, naive, rule_based, optimization, or degradation_aware"
            )

        charge_energy_kwh = battery_charge * TIME_STEP_HOURS
        discharge_energy_kwh = battery_discharge * TIME_STEP_HOURS

        if controller_type == "no_battery":
            degradation_data = {
                "soh": 1.0,
                "capacity_loss_percent": 0.0,
                "throughput_kwh": 0.0
            }
        else:
            degradation_data = degradation.update(
                charge_energy_kwh,
                discharge_energy_kwh,
                TIME_STEP_HOURS
            )

        import_cost, export_revenue, energy_net_cost = calculate_cost(
            grid_import * TIME_STEP_HOURS,
            grid_export * TIME_STEP_HOURS
        )

        total_net_cost = energy_net_cost + degradation_cost_rs

        results.append({
            "local_hour": row["local_hour"],
"timestamp_utc": row["timestamp_utc"],
            "timestamp": row["timestamp"],
            "ghi_wm2": row["ghi_wm2"],
            "dni_wm2": row["dni_wm2"],
            "dhi_wm2": row["dhi_wm2"],
            "temp_air_c": row["temp_air_c"],
            "controller_type": controller_type,
            "hour": hour,
            "pv_power_kw": pv_power,
            "home_load_kw": home_load,
            "ev_charge_kw": ev_charge_power,
            "total_load_kw": total_load,
            "battery_charge_kw": battery_charge,
            "battery_discharge_kw": battery_discharge,
            "battery_soc": battery_soc,
            "battery_soh": degradation_data["soh"],
            "battery_capacity_loss_percent": degradation_data["capacity_loss_percent"],
            "battery_throughput_kwh": degradation_data["throughput_kwh"],
            "grid_import_kw": grid_import,
            "grid_export_kw": grid_export,
            "import_cost_rs": import_cost,
            "export_revenue_rs": export_revenue,
            "energy_net_cost_rs": energy_net_cost,
            "degradation_cost_rs": degradation_cost_rs,
            "net_cost_rs": total_net_cost
        })

    result_df = pd.DataFrame(results)

    return result_df