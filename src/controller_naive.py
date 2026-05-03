# src/controller_naive.py


def run_naive_controller(pv_power, total_load, battery, timestep_hours):
    """
    Naive controller:
    - If extra solar is available, charge battery first.
    - If load is higher than solar, discharge battery first.
    - Remaining surplus goes to grid export.
    - Remaining deficit comes from grid import.
    """

    battery_charge = 0.0
    battery_discharge = 0.0
    grid_import = 0.0
    grid_export = 0.0

    net_power = pv_power - total_load

    if net_power > 0:
        battery_charge = battery.charge(net_power, timestep_hours)
        remaining_surplus = net_power - battery_charge
        grid_export = max(remaining_surplus, 0.0)

    else:
        deficit = abs(net_power)
        battery_discharge = battery.discharge(deficit, timestep_hours)
        remaining_deficit = deficit - battery_discharge
        grid_import = max(remaining_deficit, 0.0)

    return {
        "battery_charge": battery_charge,
        "battery_discharge": battery_discharge,
        "grid_import": grid_import,
        "grid_export": grid_export
    }