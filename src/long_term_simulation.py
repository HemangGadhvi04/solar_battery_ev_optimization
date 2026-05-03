# src/long_term_simulation.py

import pandas as pd

from src.config import (
    FULL_YEAR_HOURS,
    HOURS_PER_DAY,
    TIME_STEP_HOURS,
    SOC_INITIAL,
    BATTERY_CAPACITY_KWH
)

from src.pv_model import generate_pv_profile
from src.load_model import generate_home_load_profile
from src.ev_model import generate_ev_availability_profile
from src.controller_optimization import run_optimization_controller
from src.degradation_model import BatteryDegradation
from src.tariff_model import calculate_cost


def prepare_full_year_dataframe():
    """
    Creates a full-year Ahmedabad weather-based PV dataframe.
    Home load and EV charging are repeated daily.
    """

    pv_df = generate_pv_profile(hours=FULL_YEAR_HOURS)

    all_days = []

    for day in range(365):
        load_df = generate_home_load_profile(HOURS_PER_DAY)
        ev_df = generate_ev_availability_profile(HOURS_PER_DAY)

        daily_df = pv_df.iloc[
            day * HOURS_PER_DAY:(day + 1) * HOURS_PER_DAY
        ].copy()

        daily_df = daily_df.reset_index(drop=True)
        load_df = load_df.reset_index(drop=True)
        ev_df = ev_df.reset_index(drop=True)

        daily_df["day"] = day + 1
        daily_df["hour_of_day"] = load_df["hour"]
        daily_df["home_load_kw"] = load_df["home_load_kw"]
        daily_df["ev_plugged"] = ev_df["ev_plugged"]

        remaining_ev_energy = ev_df["ev_required_energy_kwh"].iloc[0]
        ev_charge_values = []

        for _, row in daily_df.iterrows():
            if row["ev_plugged"] == 1 and remaining_ev_energy > 0:
                ev_charge_power = min(
                    ev_df["ev_charger_power_kw"].iloc[0],
                    remaining_ev_energy / TIME_STEP_HOURS
                )
                remaining_ev_energy -= ev_charge_power * TIME_STEP_HOURS
            else:
                ev_charge_power = 0.0

            ev_charge_values.append(ev_charge_power)

        daily_df["ev_charge_kw"] = ev_charge_values
        daily_df["total_load_kw"] = daily_df["home_load_kw"] + daily_df["ev_charge_kw"]

        all_days.append(daily_df)

    full_df = pd.concat(all_days, ignore_index=True)

    return full_df


def run_long_term_simulation():
    """
    Runs degradation-aware optimization day by day for one year.

    The optimizer solves one 24-hour dispatch problem each day.
    Battery degradation is tracked across the full year.
    """

    full_df = prepare_full_year_dataframe()

    degradation = BatteryDegradation(initial_soh=1.0)

    all_hourly_results = []
    daily_summary_results = []

    current_soc = SOC_INITIAL

    for day in range(1, 366):
        daily_df = full_df[full_df["day"] == day].copy().reset_index(drop=True)

      # Start each day from the previous day's final SOC
        optimized = run_optimization_controller(
    daily_df,
    degradation_aware=True,
    initial_soc=current_soc
)

        hourly_results = []

        for i, row in daily_df.iterrows():
            battery_charge = float(optimized["battery_charge"][i])
            battery_discharge = float(optimized["battery_discharge"][i])
            grid_import = float(optimized["grid_import"][i])
            grid_export = float(optimized["grid_export"][i])
            battery_soc = float(optimized["soc"][i])

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

            total_daily_throughput = sum(
                optimized["battery_charge"] + optimized["battery_discharge"]
            ) * TIME_STEP_HOURS

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

            hourly_results.append({
                "day": day,
                "hour_of_day": row["hour_of_day"],
                "local_hour": row["local_hour"],
                "timestamp_utc": row["timestamp_utc"],
                "timestamp": row["timestamp"],
                "ghi_wm2": row["ghi_wm2"],
                "dni_wm2": row["dni_wm2"],
                "dhi_wm2": row["dhi_wm2"],
                "temp_air_c": row["temp_air_c"],
                "pv_power_kw": row["pv_power_kw"],
                "home_load_kw": row["home_load_kw"],
                "ev_charge_kw": row["ev_charge_kw"],
                "total_load_kw": row["total_load_kw"],
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
                "net_cost_rs": net_cost
            })

        day_df = pd.DataFrame(hourly_results)

        daily_summary_results.append({
            "day": day,
            "daily_grid_import_kwh": day_df["grid_import_kw"].sum(),
            "daily_grid_export_kwh": day_df["grid_export_kw"].sum(),
            "daily_energy_cost_rs": day_df["energy_net_cost_rs"].sum(),
            "daily_degradation_cost_rs": day_df["degradation_cost_rs"].sum(),
            "daily_net_cost_rs": day_df["net_cost_rs"].sum(),
            "daily_battery_throughput_kwh": (
                day_df["battery_charge_kw"].sum()
                + day_df["battery_discharge_kw"].sum()
            ),
            "final_daily_soc_percent": day_df["battery_soc"].iloc[-1] * 100,
            "final_daily_soh_percent": day_df["battery_soh"].iloc[-1] * 100,
            "capacity_loss_percent": day_df["battery_capacity_loss_percent"].iloc[-1]
        })

        all_hourly_results.append(day_df)

        current_soc = day_df["battery_soc"].iloc[-1]

    hourly_df = pd.concat(all_hourly_results, ignore_index=True)
    daily_summary_df = pd.DataFrame(daily_summary_results)

    annual_summary = {
        "annual_grid_import_kwh": hourly_df["grid_import_kw"].sum(),
        "annual_grid_export_kwh": hourly_df["grid_export_kw"].sum(),
        "annual_energy_cost_rs": hourly_df["energy_net_cost_rs"].sum(),
        "annual_degradation_cost_rs": hourly_df["degradation_cost_rs"].sum(),
        "annual_net_cost_rs": hourly_df["net_cost_rs"].sum(),
        "annual_battery_throughput_kwh": (
            hourly_df["battery_charge_kw"].sum()
            + hourly_df["battery_discharge_kw"].sum()
        ),
        "final_soh_percent": hourly_df["battery_soh"].iloc[-1] * 100,
        "final_capacity_loss_percent": hourly_df["battery_capacity_loss_percent"].iloc[-1],
        "estimated_usable_capacity_kwh": (
            BATTERY_CAPACITY_KWH * hourly_df["battery_soh"].iloc[-1]
        )
    }

    annual_summary_df = pd.DataFrame([annual_summary])

    return hourly_df, daily_summary_df, annual_summary_df