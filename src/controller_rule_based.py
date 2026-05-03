# src/controller_rule_based.py


def run_rule_based_controller(pv_power, total_load, battery, timestep_hours, hour):
    """
    Rule-based smart controller:
    - Charge battery from surplus PV.
    - During evening peak hours, use battery more actively.
    - During non-peak hours, preserve some battery energy.
    - This reduces unnecessary cycling compared with naive control.
    """

    battery_charge = 0.0
    battery_discharge = 0.0
    grid_import = 0.0
    grid_export = 0.0

    net_power = pv_power - total_load

    evening_peak = 18 <= hour <= 22

    if net_power > 0:
        # Charge only from extra solar
        battery_charge = battery.charge(net_power, timestep_hours)
        remaining_surplus = net_power - battery_charge
        grid_export = max(remaining_surplus, 0.0)

    else:
        deficit = abs(net_power)

        if evening_peak:
            # Use battery during expensive/evening load hours
            battery_discharge = battery.discharge(deficit, timestep_hours)
            remaining_deficit = deficit - battery_discharge
            grid_import = max(remaining_deficit, 0.0)

        else:
            # Preserve battery outside evening peak
            grid_import = deficit

    return {
        "battery_charge": battery_charge,
        "battery_discharge": battery_discharge,
        "grid_import": grid_import,
        "grid_export": grid_export
    }