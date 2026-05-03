# src/plotting.py

import matplotlib.pyplot as plt


def plot_results(df):
    # 1. Power flow plot
    plt.figure(figsize=(12, 6))
    plt.plot(df["hour"], df["pv_power_kw"], label="PV Power")
    plt.plot(df["hour"], df["home_load_kw"], label="Home Load")
    plt.plot(df["hour"], df["ev_charge_kw"], label="EV Charging")
    plt.plot(df["hour"], df["grid_import_kw"], label="Grid Import")
    plt.plot(df["hour"], df["grid_export_kw"], label="Grid Export")
    plt.xlabel("Hour")
    plt.ylabel("Power (kW)")
    plt.title("24-Hour Solar Battery EV Simulation")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/power_flow.png")
    plt.close()

    # 2. Battery SOC plot
    plt.figure(figsize=(12, 5))
    plt.plot(df["hour"], df["battery_soc"] * 100, label="Battery SOC")
    plt.xlabel("Hour")
    plt.ylabel("SOC (%)")
    plt.title("Battery State of Charge")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/battery_soc.png")
    plt.close()

    # 3. Battery SOH plot
    plt.figure(figsize=(12, 5))
    plt.plot(df["hour"], df["battery_soh"] * 100, label="Battery SOH")
    plt.xlabel("Hour")
    plt.ylabel("SOH (%)")
    plt.title("Battery State of Health")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/battery_soh.png")
    plt.close()

    # 4. Battery throughput plot
    plt.figure(figsize=(12, 5))
    plt.plot(df["hour"], df["battery_throughput_kwh"], label="Battery Throughput")
    plt.xlabel("Hour")
    plt.ylabel("Cumulative Throughput (kWh)")
    plt.title("Battery Throughput Over 24 Hours")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/battery_throughput.png")
    plt.close()

    print("Plots saved successfully:")
    print("results/power_flow.png")
    print("results/battery_soc.png")
    print("results/battery_soh.png")
    print("results/battery_throughput.png")


def plot_controller_comparison(summary_df):
    # Controller cost comparison
    plt.figure(figsize=(10, 6))
    plt.bar(summary_df["controller"], summary_df["total_net_cost_rs"])
    plt.xlabel("Controller")
    plt.ylabel("Net Cost (Rs)")
    plt.title("Controller Cost Comparison")
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig("results/controller_cost_comparison.png")
    plt.close()

    # Grid import comparison
    plt.figure(figsize=(10, 6))
    plt.bar(summary_df["controller"], summary_df["total_grid_import_kwh"])
    plt.xlabel("Controller")
    plt.ylabel("Grid Import (kWh)")
    plt.title("Controller Grid Import Comparison")
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig("results/controller_grid_import_comparison.png")
    plt.close()

    # Battery throughput comparison
    plt.figure(figsize=(10, 6))
    plt.bar(summary_df["controller"], summary_df["battery_throughput_kwh"])
    plt.xlabel("Controller")
    plt.ylabel("Battery Throughput (kWh)")
    plt.title("Battery Throughput Comparison")
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig("results/controller_throughput_comparison.png")
    plt.close()

    print("Controller comparison plots saved successfully:")
    print("results/controller_cost_comparison.png")
    print("results/controller_grid_import_comparison.png")
    print("results/controller_throughput_comparison.png")


def plot_long_term_results(daily_summary_df):
    # SOH over year
    plt.figure(figsize=(12, 6))
    plt.plot(daily_summary_df["day"], daily_summary_df["final_daily_soh_percent"])
    plt.xlabel("Day")
    plt.ylabel("Battery SOH (%)")
    plt.title("Battery State of Health Over One Year")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/long_term_soh.png")
    plt.close()

    # SOC over year
    plt.figure(figsize=(12, 6))
    plt.plot(daily_summary_df["day"], daily_summary_df["final_daily_soc_percent"])
    plt.xlabel("Day")
    plt.ylabel("Final Daily SOC (%)")
    plt.title("Battery Final Daily SOC Over One Year")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/long_term_soc.png")
    plt.close()

    # Daily net cost
    plt.figure(figsize=(12, 6))
    plt.plot(daily_summary_df["day"], daily_summary_df["daily_net_cost_rs"])
    plt.xlabel("Day")
    plt.ylabel("Daily Net Cost (Rs)")
    plt.title("Daily Net Cost Over One Year")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/long_term_daily_cost.png")
    plt.close()

    # Daily grid import
    plt.figure(figsize=(12, 6))
    plt.plot(daily_summary_df["day"], daily_summary_df["daily_grid_import_kwh"])
    plt.xlabel("Day")
    plt.ylabel("Daily Grid Import (kWh)")
    plt.title("Daily Grid Import Over One Year")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/long_term_grid_import.png")
    plt.close()

    # Daily battery throughput
    plt.figure(figsize=(12, 6))
    plt.plot(daily_summary_df["day"], daily_summary_df["daily_battery_throughput_kwh"])
    plt.xlabel("Day")
    plt.ylabel("Battery Throughput (kWh)")
    plt.title("Daily Battery Throughput Over One Year")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/long_term_battery_throughput.png")
    plt.close()

    print("Long-term plots saved successfully:")
    print("results/long_term_soh.png")
    print("results/long_term_soc.png")
    print("results/long_term_daily_cost.png")
    print("results/long_term_grid_import.png")
    print("results/long_term_battery_throughput.png")


def plot_sizing_results(sizing_df):
    # Annual cost by PV and battery size
    plt.figure(figsize=(12, 6))

    for battery_size in sorted(sizing_df["battery_size_kwh"].unique()):
        subset = sizing_df[sizing_df["battery_size_kwh"] == battery_size]
        plt.plot(
            subset["pv_size_kw"],
            subset["annual_net_cost_rs"],
            marker="o",
            label=f"Battery {battery_size} kWh"
        )

    plt.xlabel("PV Size (kW)")
    plt.ylabel("Annual Net Cost (Rs)")
    plt.title("Annual Net Cost vs PV Size and Battery Size")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/sizing_cost_comparison.png")
    plt.close()

    # Grid import by PV and battery size
    plt.figure(figsize=(12, 6))

    for battery_size in sorted(sizing_df["battery_size_kwh"].unique()):
        subset = sizing_df[sizing_df["battery_size_kwh"] == battery_size]
        plt.plot(
            subset["pv_size_kw"],
            subset["annual_grid_import_kwh"],
            marker="o",
            label=f"Battery {battery_size} kWh"
        )

    plt.xlabel("PV Size (kW)")
    plt.ylabel("Annual Grid Import (kWh)")
    plt.title("Annual Grid Import vs PV Size and Battery Size")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/sizing_grid_import_comparison.png")
    plt.close()

    # SOH by PV and battery size
    plt.figure(figsize=(12, 6))

    for battery_size in sorted(sizing_df["battery_size_kwh"].unique()):
        subset = sizing_df[sizing_df["battery_size_kwh"] == battery_size]
        plt.plot(
            subset["pv_size_kw"],
            subset["final_soh_percent"],
            marker="o",
            label=f"Battery {battery_size} kWh"
        )

    plt.xlabel("PV Size (kW)")
    plt.ylabel("Final SOH (%)")
    plt.title("Battery SOH vs PV Size and Battery Size")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/sizing_soh_comparison.png")
    plt.close()

    print("Sizing optimization plots saved successfully:")
    print("results/sizing_cost_comparison.png")
    print("results/sizing_grid_import_comparison.png")
    print("results/sizing_soh_comparison.png")