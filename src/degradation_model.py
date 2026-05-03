# src/degradation_model.py

class BatteryDegradation:
    def __init__(self, initial_soh=1.0):
        self.soh = initial_soh
        self.total_throughput_kwh = 0.0
        self.total_capacity_loss = 0.0

        self.calendar_fade_per_day = 0.00002
        self.cycle_fade_per_kwh = 0.00001

    def update(self, charge_kwh, discharge_kwh, timestep_hours):
        throughput = abs(charge_kwh) + abs(discharge_kwh)
        self.total_throughput_kwh += throughput

        calendar_loss = self.calendar_fade_per_day * (timestep_hours / 24)
        cycle_loss = self.cycle_fade_per_kwh * throughput

        step_loss = calendar_loss + cycle_loss

        self.total_capacity_loss += step_loss
        self.soh = max(1.0 - self.total_capacity_loss, 0.0)

        return {
            "soh": self.soh,
            "capacity_loss_percent": self.total_capacity_loss * 100,
            "throughput_kwh": self.total_throughput_kwh
        }