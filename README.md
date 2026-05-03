# Degradation-Aware Solar + Battery + EV Charging Optimization Framework

This project is a Python-based simulation and optimization framework for a residential solar PV, battery storage, and EV charging system using Ahmedabad, India as the case-study location.

The project uses real Ahmedabad PVGIS Typical Meteorological Year (TMY) weather data to estimate PV generation, models household and EV electricity demand, tracks battery state of charge (SOC) and state of health (SOH), and compares multiple energy management controllers including degradation-aware optimization.

---

## Project Objective

The main objective of this project is to answer:

> How should a residential solar + battery + EV charging system be controlled and sized so that it reduces grid electricity cost while also limiting battery degradation?

This is not only a solar generation calculator. The project combines:

- PV generation modeling
- EV charging demand
- battery storage dispatch
- battery degradation tracking
- grid import/export cost calculation
- controller comparison
- long-term SOH projection
- PV and battery sizing optimization
- Streamlit dashboard visualization

---

## Case Study Location

**City:** Ahmedabad, Gujarat, India  
**Time zone:** Asia/Kolkata  
**Weather source:** PVGIS Typical Meteorological Year (TMY) data  

PVGIS weather timestamps are converted from UTC to Ahmedabad local time before being used in the simulation.

---

## Main Features

### 1. Real Ahmedabad PV Modeling

The PV model uses PVGIS TMY weather data and calculates PV generation using:

- Global horizontal irradiance (GHI)
- Direct normal irradiance (DNI)
- Diffuse horizontal irradiance (DHI)
- Air temperature
- solar position
- plane-of-array irradiance
- PV derating factor

Output includes:

- timestamp UTC
- timestamp local
- local hour
- irradiance values
- air temperature
- PV output in kW

---

### 2. Load and EV Charging Model

The project includes:

- residential home load profile
- EV plugged-in window
- EV charging power limit
- daily EV energy requirement

Current EV assumption:

- EV arrives at 6 PM
- EV leaves at 8 AM
- EV requires 18 kWh
- charger power is 7.2 kW

---

### 3. Battery SOC Model

The battery model tracks:

- SOC
- charge power
- discharge power
- efficiency
- minimum SOC
- maximum SOC

Current battery assumptions:

- capacity: 10 kWh
- SOC minimum: 20%
- SOC maximum: 90%
- charge/discharge efficiency: 95%

---

### 4. Battery Degradation Model

Battery degradation is modeled using a simple control-oriented approach:

```text
capacity loss = calendar aging + cycle aging
The model tracks:

battery SOH
capacity loss percentage
cumulative battery throughput
estimated usable capacity

This allows the controller to consider not only electricity cost but also battery wear.

5. Controller Comparison

The project compares five control strategies:

No battery
Naive controller
Rule-based controller
Optimization controller
Degradation-aware optimization controller

The comparison includes:

grid import
grid export
energy cost
degradation cost
total net cost
battery throughput
final SOH
6. Degradation-Aware Optimization

The degradation-aware controller uses CVXPY optimization.

The objective is:

minimize grid import cost - export revenue + battery degradation cost

Decision variables include:

battery charge power
battery discharge power
grid import
grid export
battery SOC

Constraints include:

energy balance
SOC limits
battery charge/discharge power limits
non-negative grid import/export
7. 365-Day Long-Term Simulation

The project includes a full-year Ahmedabad simulation using real PVGIS TMY weather data.

The long-term simulation:

runs 24-hour optimization day by day
carries battery SOC from one day to the next
tracks SOH across the year
calculates annual energy cost
calculates annual degradation cost
estimates remaining usable battery capacity

Outputs include:

hourly long-term results
daily summary
annual summary
SOH plot
SOC plot
daily cost plot
grid import plot
battery throughput plot
8. PV + Battery Sizing Optimization

The sizing optimizer tests different PV and battery sizes.

Example tested sizes:

PV sizes: 3 kW to 8 kW
Battery sizes: 5 kWh to 15 kWh

The optimizer evaluates each design based on:

annual grid import
annual grid export
annual energy cost
degradation cost
total net cost
battery throughput
final battery SOH
estimated usable capacity

The best design is selected based on the lowest annual net cost.

9. Streamlit Dashboard

The project includes an interactive Streamlit dashboard.

Dashboard pages:

Overview
24-Hour Simulation
Controller Comparison
365-Day Simulation
Sizing Optimization
Generated Files

Run the dashboard using:

python3 -m streamlit run app.py
Project Structure
solar_battery_ev_optimization/
│
├── src/
│   ├── config.py
│   ├── pv_model.py
│   ├── load_model.py
│   ├── ev_model.py
│   ├── battery_model.py
│   ├── degradation_model.py
│   ├── tariff_model.py
│   ├── controller_no_battery.py
│   ├── controller_naive.py
│   ├── controller_rule_based.py
│   ├── controller_optimization.py
│   ├── simulator.py
│   ├── comparison.py
│   ├── long_term_simulation.py
│   ├── sizing_optimizer.py
│   └── plotting.py
│
├── results/
│   └── .gitkeep
│
├── data/
├── notebooks/
├── tests/
├── report/
│
├── app.py
├── main.py
├── run_long_term.py
├── run_sizing.py
├── requirements.txt
├── .gitignore
└── README.md
How to Run
1. Clone or open the project folder
cd solar_battery_ev_optimization
2. Install dependencies
python3 -m pip install -r requirements.txt
3. Run 24-hour degradation-aware simulation
python3 main.py

This generates:

simulation_results_degradation_aware.csv
controller_comparison_summary.csv
controller_comparison_detailed.csv
power_flow.png
battery_soc.png
battery_soh.png
battery_throughput.png
controller_cost_comparison.png
controller_grid_import_comparison.png
controller_throughput_comparison.png
4. Run 365-day long-term simulation
python3 run_long_term.py

This generates:

long_term_hourly_results.csv
long_term_daily_summary.csv
long_term_annual_summary.csv
long_term_soh.png
long_term_soc.png
long_term_daily_cost.png
long_term_grid_import.png
long_term_battery_throughput.png
5. Run PV + battery sizing optimization
python3 run_sizing.py

This generates:

sizing_optimization_results.csv
sizing_cost_comparison.png
sizing_grid_import_comparison.png
sizing_soh_comparison.png
6. Run Streamlit dashboard
python3 -m streamlit run app.py
Example 24-Hour Result

For the degradation-aware optimization controller, one sample run produced:

Total Grid Import: 28.84 kWh
Total Grid Export: 9.55 kWh
Total Energy Cost: Rs 202.06
Total Degradation Cost: Rs 25.30
Total Net Cost: Rs 227.36
Final Battery SOC: 20.00%
Final Battery SOH: 99.9811%
Battery Capacity Loss: 0.0189%
Battery Throughput: 16.87 kWh
Engineering Significance

This project is useful because it shows how residential solar, battery storage, and EV charging can be controlled more intelligently.

Instead of only minimizing the electricity bill, the final controller also considers battery degradation. This is important because aggressive battery use may reduce short-term grid cost but increase long-term battery wear.

The project demonstrates how a degradation-aware controller can balance:

energy cost reduction
PV self-consumption
EV charging demand
battery cycling
long-term battery health
Current Limitations

This project is a simulation framework, so some assumptions are simplified:

household load is modeled using a synthetic daily profile
EV charging demand is modeled using a fixed daily pattern
battery degradation model is simplified and semi-empirical
tariff is modeled using fixed import/export prices
PV sizing optimization uses representative days for faster runtime
Future Improvements

