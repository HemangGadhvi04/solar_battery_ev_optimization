# src/controller_no_battery.py


def run_no_battery_controller(pv_power, total_load):
    """
    No battery case.
    PV directly supplies load.
    If PV is not enough, grid imports.
    If PV is extra, grid exports.
    """

    battery_charge = 0.0
    battery_discharge = 0.0

    net_power = pv_power - total_load

    if net_power >= 0:
        grid_import = 0.0
        grid_export = net_power
    else:
        grid_import = abs(net_power)
        grid_export = 0.0

    return {
        "battery_charge": battery_charge,
        "battery_discharge": battery_discharge,
        "grid_import": grid_import,
        "grid_export": grid_export
    }