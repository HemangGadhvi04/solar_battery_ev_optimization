# src/pv_model.py

import pandas as pd
import pvlib

from src.config import (
    LATITUDE,
    LONGITUDE,
    TIMEZONE,
    PV_SIZE_KW,
    PV_TILT_DEGREES,
    PV_AZIMUTH_DEGREES,
    PV_DERATE_FACTOR
)


def generate_pv_profile(hours=8760):
    """
    Generates PV power profile using Ahmedabad PVGIS TMY weather data.

    PVGIS gives timestamps in UTC. This file converts those timestamps
    to Ahmedabad local time using Asia/Kolkata.
    """

    weather, metadata = pvlib.iotools.get_pvgis_tmy(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        map_variables=True
    )

    weather = weather.reset_index()

    time_column = weather.columns[0]

    # Convert PVGIS UTC timestamp to Ahmedabad local time
    timestamps_utc = pd.to_datetime(weather[time_column], utc=True)
    timestamps_local = timestamps_utc.dt.tz_convert(TIMEZONE)

    weather["timestamp_utc"] = timestamps_utc
    weather["timestamp_local"] = timestamps_local
    weather["local_hour"] = weather["timestamp_local"].dt.hour

    # Sort by Ahmedabad local timestamp
    weather = weather.sort_values("timestamp_local").reset_index(drop=True)

    # Use first requested number of local-time rows
    weather = weather.iloc[:hours].copy()

    timestamps_local = weather["timestamp_local"]

    location = pvlib.location.Location(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        tz=TIMEZONE,
        name="Ahmedabad"
    )

    solar_position = location.get_solarposition(times=timestamps_local)

    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=PV_TILT_DEGREES,
        surface_azimuth=PV_AZIMUTH_DEGREES,
        dni=weather["dni"].to_numpy(),
        ghi=weather["ghi"].to_numpy(),
        dhi=weather["dhi"].to_numpy(),
        solar_zenith=solar_position["apparent_zenith"].to_numpy(),
        solar_azimuth=solar_position["azimuth"].to_numpy()
    )

    poa_global = pd.Series(poa["poa_global"]).fillna(0)

    pv_power_kw = (
        PV_SIZE_KW
        * (poa_global / 1000)
        * PV_DERATE_FACTOR
    )

    pv_power_kw = pv_power_kw.clip(lower=0, upper=PV_SIZE_KW)

    df = pd.DataFrame({
        "hour": list(range(len(weather))),
        "local_hour": weather["local_hour"].to_numpy(),
        "timestamp_utc": weather["timestamp_utc"].astype(str).to_numpy(),
        "timestamp": weather["timestamp_local"].astype(str).to_numpy(),
        "ghi_wm2": weather["ghi"].to_numpy(),
        "dni_wm2": weather["dni"].to_numpy(),
        "dhi_wm2": weather["dhi"].to_numpy(),
        "temp_air_c": weather["temp_air"].to_numpy(),
        "pv_power_kw": pv_power_kw.to_numpy()
    })

    return df