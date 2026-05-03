# main.py

from src.simulator import run_simulation
from src.comparison import run_controller_comparison
from src.plotting import plot_results, plot_controller_comparison


def main():
    # Run main Level 3 controller
    df = run_simulation(controller_type="degradation_aware")

    print("\nDegradation-Aware Optimization Controller Simulation Results:")
    print(df)

    total_import = df["grid_import_kw"].sum()
    total_export = df["grid_export_kw"].sum()
    total_energy_cost = df["energy_net_cost_rs"].sum()
    total_degradation_cost = df["degradation_cost_rs"].sum()
    total_cost = df["net_cost_rs"].sum()
    final_soc = df["battery_soc"].iloc[-1] * 100
    final_soh = df["battery_soh"].iloc[-1] * 100
    total_capacity_loss = df["battery_capacity_loss_percent"].iloc[-1]
    total_throughput = df["battery_throughput_kwh"].iloc[-1]

    print("\nDegradation-Aware Optimization Controller Summary:")
    print(f"Total Grid Import: {total_import:.2f} kWh")
    print(f"Total Grid Export: {total_export:.2f} kWh")
    print(f"Total Energy Cost: Rs {total_energy_cost:.2f}")
    print(f"Total Degradation Cost: Rs {total_degradation_cost:.2f}")
    print(f"Total Net Cost: Rs {total_cost:.2f}")
    print(f"Final Battery SOC: {final_soc:.2f}%")
    print(f"Final Battery SOH: {final_soh:.4f}%")
    print(f"Battery Capacity Loss: {total_capacity_loss:.4f}%")
    print(f"Battery Throughput: {total_throughput:.2f} kWh")

    # Save main simulation result
    df.to_csv("results/simulation_results_degradation_aware.csv", index=False)

    # Save plots for main simulation
    plot_results(df)

    # Run full controller comparison
    summary_df, detailed_df = run_controller_comparison()

    print("\nController Comparison Summary:")
    print(summary_df)

    # Save comparison results
    summary_df.to_csv("results/controller_comparison_summary.csv", index=False)
    detailed_df.to_csv("results/controller_comparison_detailed.csv", index=False)

    # Save comparison plots
    plot_controller_comparison(summary_df)


if __name__ == "__main__":
    main()