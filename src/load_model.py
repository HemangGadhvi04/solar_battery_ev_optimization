# src/load_model.py

import numpy as np
import pandas as pd


def generate_home_load_profile(hours=24):
    """
    Generates a simple residential home load profile.
    Higher load in morning and evening.
    """

    time = np.arange(hours)
    load = []

    for hour in time:
        if 0 <= hour < 6:
            value = 0.6
        elif 6 <= hour < 9:
            value = 1.5
        elif 9 <= hour < 17:
            value = 1.0
        elif 17 <= hour < 22:
            value = 2.4
        else:
            value = 0.9

        load.append(value)

    df = pd.DataFrame({
        "hour": time,
        "home_load_kw": load
    })

    return df