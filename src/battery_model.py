# src/battery_model.py

from src.config import (
    BATTERY_CAPACITY_KWH,
    BATTERY_MAX_CHARGE_KW,
    BATTERY_MAX_DISCHARGE_KW,
    BATTERY_EFFICIENCY,
    SOC_MIN,
    SOC_MAX
)


class Battery:
    def __init__(self, initial_soc):
        self.capacity_kwh = BATTERY_CAPACITY_KWH
        self.soc = initial_soc

    def available_charge_capacity(self):
        return max((SOC_MAX - self.soc) * self.capacity_kwh, 0.0)

    def available_discharge_capacity(self):
        return max((self.soc - SOC_MIN) * self.capacity_kwh, 0.0)

    def charge(self, requested_power_kw, timestep_hours):
        max_energy_possible = self.available_charge_capacity()
        requested_energy = requested_power_kw * timestep_hours * BATTERY_EFFICIENCY

        actual_energy_stored = min(
            requested_energy,
            max_energy_possible,
            BATTERY_MAX_CHARGE_KW * timestep_hours
        )

        self.soc += actual_energy_stored / self.capacity_kwh

        actual_grid_side_energy = actual_energy_stored / BATTERY_EFFICIENCY
        actual_power_kw = actual_grid_side_energy / timestep_hours

        return actual_power_kw

    def discharge(self, requested_power_kw, timestep_hours):
        max_energy_available = self.available_discharge_capacity()
        requested_energy = requested_power_kw * timestep_hours / BATTERY_EFFICIENCY

        actual_energy_removed = min(
            requested_energy,
            max_energy_available,
            BATTERY_MAX_DISCHARGE_KW * timestep_hours
        )

        self.soc -= actual_energy_removed / self.capacity_kwh

        actual_load_side_energy = actual_energy_removed * BATTERY_EFFICIENCY
        actual_power_kw = actual_load_side_energy / timestep_hours

        return actual_power_kw