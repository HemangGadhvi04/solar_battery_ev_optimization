# src/ev_model.py

import numpy as np
import pandas as pd
from src.config import (
    EV_ARRIVAL_HOUR,
    EV_DEPARTURE_HOUR,
    EV_REQUIRED_ENERGY_KWH,
    EV_CHARGER_POWER_KW
)


def is_ev_plugged(hour):
    """
    EV is plugged from 6 PM to 8 AM.
    Since the period crosses midnight, we use OR logic.
    """

    return hour >= EV_ARRIVAL_HOUR or hour < EV_DEPARTURE_HOUR


def generate_ev_availability_profile(hours=24):
    """
    Creates EV plugged-in availability profile.
    """

    time = np.arange(hours)
    plugged = []

    for hour in time:
        plugged.append(1 if is_ev_plugged(hour) else 0)

    df = pd.DataFrame({
        "hour": time,
        "ev_plugged": plugged,
        "ev_required_energy_kwh": EV_REQUIRED_ENERGY_KWH,
        "ev_charger_power_kw": EV_CHARGER_POWER_KW
    })

    return df