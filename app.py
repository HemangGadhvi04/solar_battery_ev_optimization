# app.py

import os
import pandas as pd
import streamlit as st

from src.simulator import run_simulation
from src.comparison import run_controller_comparison
from src.long_term_simulation import run_long_term_simulation
from src.sizing_optimizer import run_sizing_optimization


st.set_page_config(
    page_title="Ahmedabad Solar Battery EV Optimization",
    layout="wide"
)


RESULTS_DIR = "results"


def ensure_results_dir():
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)


def load_csv_if_exists(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


def show_metric_row(metrics):
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)


def page_overview():
    st.title("Ahmedabad Solar + Battery + EV Optimization Dashboard")

    st.write(
        """
        This dashboard presents a degradation-aware solar PV, battery storage,
        and EV charging optimization framework for Ahmedabad, India.
        The project uses Ahmedabad PVGIS TMY weather data for PV generation,
        simulates home and EV demand, tracks battery SOC/SOH, and compares
        multiple control strategies.
        """
    )

    st.subheader("Project Modules")

    st.write(
        """
        - Real Ahmedabad PVGIS weather-based PV generation
        - Residential home load model
        - EV charging demand model
        - Battery SOC model
        - Battery degradation and SOH tracking
        - No-battery, naive, rule-based, optimization, and degradation-aware controllers
        - 365-day long-term simulation
        - PV and battery sizing optimization
        """
    )

    st.subheader("Recommended Workflow")

    st.write(
        """
        1. Run 24-hour degradation-aware simulation  
        2. Run controller comparison  
        3. Run 365-day long-term simulation  
        4. Run PV + battery sizing optimization  
        5. Review generated CSV files and plots  
        """
    )


def page_24_hour_simulation():
    st.title("24-Hour Degradation-Aware Simulation")

    controller_type = st.selectbox(
        "Select controller",
        [
            "no_battery",
            "naive",
            "rule_based",
            "optimization",
            "degradation_aware"
        ],
        index=4
    )

    if st.button("Run 24-Hour Simulation"):
        ensure_results_dir()

        with st.spinner("Running 24-hour simulation..."):
            df = run_simulation(controller_type=controller_type)

        output_path = f"{RESULTS_DIR}/dashboard_24h_{controller_type}.csv"
        df.to_csv(output_path, index=False)

        st.success(f"Simulation complete. Saved to {output_path}")
        st.session_state["sim_24h_df"] = df

    df = st.session_state.get("sim_24h_df")

    if df is None:
        df = load_csv_if_exists(f"{RESULTS_DIR}/simulation_results_degradation_aware.csv")

    if df is not None:
        total_import = df["grid_import_kw"].sum()
        total_export = df["grid_export_kw"].sum()
        total_energy_cost = df["energy_net_cost_rs"].sum()
        total_degradation_cost = df["degradation_cost_rs"].sum()
        total_cost = df["net_cost_rs"].sum()
        final_soc = df["battery_soc"].iloc[-1] * 100
        final_soh = df["battery_soh"].iloc[-1] * 100
        throughput = df["battery_throughput_kwh"].iloc[-1]

        show_metric_row([
            ("Grid Import", f"{total_import:.2f} kWh"),
            ("Grid Export", f"{total_export:.2f} kWh"),
            ("Energy Cost", f"Rs {total_energy_cost:.2f}"),
            ("Degradation Cost", f"Rs {total_degradation_cost:.2f}"),
        ])

        show_metric_row([
            ("Net Cost", f"Rs {total_cost:.2f}"),
            ("Final SOC", f"{final_soc:.2f}%"),
            ("Final SOH", f"{final_soh:.4f}%"),
            ("Throughput", f"{throughput:.2f} kWh"),
        ])

        st.subheader("Power Flow")
        st.line_chart(
            df.set_index("hour")[
                [
                    "pv_power_kw",
                    "home_load_kw",
                    "ev_charge_kw",
                    "grid_import_kw",
                    "grid_export_kw"
                ]
            ]
        )

        st.subheader("Battery SOC and SOH")
        battery_plot_df = df[["hour", "battery_soc", "battery_soh"]].copy()
        battery_plot_df["battery_soc_percent"] = battery_plot_df["battery_soc"] * 100
        battery_plot_df["battery_soh_percent"] = battery_plot_df["battery_soh"] * 100

        st.line_chart(
            battery_plot_df.set_index("hour")[
                ["battery_soc_percent", "battery_soh_percent"]
            ]
        )

        st.subheader("Simulation Data")
        st.dataframe(df, use_container_width=True)


def page_controller_comparison():
    st.title("Controller Comparison")

    if st.button("Run Controller Comparison"):
        ensure_results_dir()

        with st.spinner("Running controller comparison..."):
            summary_df, detailed_df = run_controller_comparison()

        summary_df.to_csv(f"{RESULTS_DIR}/controller_comparison_summary.csv", index=False)
        detailed_df.to_csv(f"{RESULTS_DIR}/controller_comparison_detailed.csv", index=False)

        st.success("Controller comparison complete.")
        st.session_state["controller_summary_df"] = summary_df
        st.session_state["controller_detailed_df"] = detailed_df

    summary_df = st.session_state.get("controller_summary_df")

    if summary_df is None:
        summary_df = load_csv_if_exists(f"{RESULTS_DIR}/controller_comparison_summary.csv")

    if summary_df is not None:
        st.subheader("Comparison Summary")
        st.dataframe(summary_df, use_container_width=True)

        st.subheader("Annual/Period Net Cost by Controller")
        st.bar_chart(summary_df.set_index("controller")["total_net_cost_rs"])

        st.subheader("Grid Import by Controller")
        st.bar_chart(summary_df.set_index("controller")["total_grid_import_kwh"])

        st.subheader("Battery Throughput by Controller")
        st.bar_chart(summary_df.set_index("controller")["battery_throughput_kwh"])

        st.subheader("Final Battery SOH by Controller")
        st.bar_chart(summary_df.set_index("controller")["final_soh_percent"])


def page_long_term():
    st.title("365-Day Long-Term Simulation")

    st.warning(
        "This simulation can take some time because it solves one optimization problem per day."
    )

    if st.button("Run 365-Day Simulation"):
        ensure_results_dir()

        with st.spinner("Running 365-day Ahmedabad simulation..."):
            hourly_df, daily_summary_df, annual_summary_df = run_long_term_simulation()

        hourly_df.to_csv(f"{RESULTS_DIR}/long_term_hourly_results.csv", index=False)
        daily_summary_df.to_csv(f"{RESULTS_DIR}/long_term_daily_summary.csv", index=False)
        annual_summary_df.to_csv(f"{RESULTS_DIR}/long_term_annual_summary.csv", index=False)

        st.success("365-day simulation complete.")
        st.session_state["long_hourly_df"] = hourly_df
        st.session_state["long_daily_df"] = daily_summary_df
        st.session_state["long_annual_df"] = annual_summary_df

    daily_summary_df = st.session_state.get("long_daily_df")
    annual_summary_df = st.session_state.get("long_annual_df")

    if daily_summary_df is None:
        daily_summary_df = load_csv_if_exists(f"{RESULTS_DIR}/long_term_daily_summary.csv")

    if annual_summary_df is None:
        annual_summary_df = load_csv_if_exists(f"{RESULTS_DIR}/long_term_annual_summary.csv")

    if annual_summary_df is not None:
        st.subheader("Annual Summary")
        st.dataframe(annual_summary_df, use_container_width=True)

        row = annual_summary_df.iloc[0]

        show_metric_row([
            ("Annual Grid Import", f"{row['annual_grid_import_kwh']:.2f} kWh"),
            ("Annual Grid Export", f"{row['annual_grid_export_kwh']:.2f} kWh"),
            ("Annual Energy Cost", f"Rs {row['annual_energy_cost_rs']:.2f}"),
            ("Annual Degradation Cost", f"Rs {row['annual_degradation_cost_rs']:.2f}"),
        ])

        show_metric_row([
            ("Annual Net Cost", f"Rs {row['annual_net_cost_rs']:.2f}"),
            ("Annual Throughput", f"{row['annual_battery_throughput_kwh']:.2f} kWh"),
            ("Final SOH", f"{row['final_soh_percent']:.2f}%"),
            ("Usable Capacity", f"{row['estimated_usable_capacity_kwh']:.2f} kWh"),
        ])

    if daily_summary_df is not None:
        st.subheader("Daily SOH")
        st.line_chart(
            daily_summary_df.set_index("day")["final_daily_soh_percent"]
        )

        st.subheader("Daily SOC")
        st.line_chart(
            daily_summary_df.set_index("day")["final_daily_soc_percent"]
        )

        st.subheader("Daily Net Cost")
        st.line_chart(
            daily_summary_df.set_index("day")["daily_net_cost_rs"]
        )

        st.subheader("Daily Grid Import")
        st.line_chart(
            daily_summary_df.set_index("day")["daily_grid_import_kwh"]
        )

        st.subheader("Daily Summary Data")
        st.dataframe(daily_summary_df, use_container_width=True)


def page_sizing():
    st.title("PV + Battery Sizing Optimization")

    st.warning(
        "This can take time because it tests many PV and battery combinations."
    )

    if st.button("Run Sizing Optimization"):
        ensure_results_dir()

        with st.spinner("Running PV + battery sizing optimization..."):
            sizing_df, best_result = run_sizing_optimization()

        sizing_df.to_csv(f"{RESULTS_DIR}/sizing_optimization_results.csv", index=False)

        st.success("Sizing optimization complete.")
        st.session_state["sizing_df"] = sizing_df

    sizing_df = st.session_state.get("sizing_df")

    if sizing_df is None:
        sizing_df = load_csv_if_exists(f"{RESULTS_DIR}/sizing_optimization_results.csv")

    if sizing_df is not None:
        st.subheader("Sizing Results")
        st.dataframe(sizing_df, use_container_width=True)

        best = sizing_df.sort_values("annual_net_cost_rs").iloc[0]

        st.subheader("Best Design Based on Lowest Annual Net Cost")

        show_metric_row([
            ("PV Size", f"{best['pv_size_kw']:.1f} kW"),
            ("Battery Size", f"{best['battery_size_kwh']:.1f} kWh"),
            ("Annual Net Cost", f"Rs {best['annual_net_cost_rs']:.2f}"),
            ("Final SOH", f"{best['final_soh_percent']:.2f}%"),
        ])

        st.subheader("Annual Net Cost by System Size")
        chart_df = sizing_df.pivot(
            index="pv_size_kw",
            columns="battery_size_kwh",
            values="annual_net_cost_rs"
        )
        st.line_chart(chart_df)

        st.subheader("Annual Grid Import by System Size")
        grid_df = sizing_df.pivot(
            index="pv_size_kw",
            columns="battery_size_kwh",
            values="annual_grid_import_kwh"
        )
        st.line_chart(grid_df)

        st.subheader("Final SOH by System Size")
        soh_df = sizing_df.pivot(
            index="pv_size_kw",
            columns="battery_size_kwh",
            values="final_soh_percent"
        )
        st.line_chart(soh_df)


def page_files():
    st.title("Generated Results Files")

    ensure_results_dir()

    files = sorted(os.listdir(RESULTS_DIR))

    if not files:
        st.info("No result files found yet.")
        return

    for file in files:
        path = os.path.join(RESULTS_DIR, file)
        size_kb = os.path.getsize(path) / 1024

        st.write(f"**{file}** — {size_kb:.1f} KB")

        if file.endswith(".csv"):
            with open(path, "rb") as f:
                st.download_button(
                    label=f"Download {file}",
                    data=f,
                    file_name=file,
                    mime="text/csv"
                )


def main():
    ensure_results_dir()

    st.sidebar.title("Navigation")

    page = st.sidebar.radio(
        "Go to",
        [
            "Overview",
            "24-Hour Simulation",
            "Controller Comparison",
            "365-Day Simulation",
            "Sizing Optimization",
            "Generated Files"
        ]
    )

    if page == "Overview":
        page_overview()
    elif page == "24-Hour Simulation":
        page_24_hour_simulation()
    elif page == "Controller Comparison":
        page_controller_comparison()
    elif page == "365-Day Simulation":
        page_long_term()
    elif page == "Sizing Optimization":
        page_sizing()
    elif page == "Generated Files":
        page_files()


if __name__ == "__main__":
    main()