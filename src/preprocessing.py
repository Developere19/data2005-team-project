import os
import json
import numpy as np
import pandas as pd
from data_loader import load_data

# Constants
RAW_FILE = r"C:\Users\Mohammedrog\PycharmProjects\PythonProject1\dcp2\MEG01.20260408163129.csv"
PROCESSED_DIR = os.path.join("data", "processed")

RENEWABLE_FUELS = [
    "Renewable Hydro", "Solar", "Wind",
    "Other Renewable", "Pumped Storage Hydro",
]

NON_RENEWABLE_FUELS = [
    "Biomass/Peat", "Coal", "Distillate", "Gas",
    "Oil", "Other Non-Renewable", "Waste", "Battery Storage",
]

SEASON_MAP = {
    12: "Winter", 1: "Winter",  2: "Winter",
     3: "Spring", 4: "Spring",  5: "Spring",
     6: "Summer", 7: "Summer",  8: "Summer",
     9: "Autumn", 10: "Autumn", 11: "Autumn",
}

IQR_MULTIPLIER = 1.5

def handle_missing(df):
    """Fills missing values: first by carrying forward up to 1 hour, then using the column median."""
    fuel_cols = [c for c in df.columns if c != "timestamp"]
    df[fuel_cols] = df[fuel_cols].ffill(limit=2)
    df[fuel_cols] = df[fuel_cols].fillna(df[fuel_cols].median())
    return df

def detect_outliers(df):
    """Flags outliers using the standard IQR method."""
    fuel_cols = [c for c in df.columns if c != "timestamp"]
    values = df[fuel_cols].to_numpy(dtype=float)

    q1 = np.percentile(values, 25, axis=0)
    q3 = np.percentile(values, 75, axis=0)
    iqr = q3 - q1

    # Mark as outlier if below Q1 - 1.5*IQR or above Q3 + 1.5*IQR
    is_outlier = (values < q1 - IQR_MULTIPLIER * iqr) | (values > q3 + IQR_MULTIPLIER * iqr)

    for i, col in enumerate(fuel_cols):
        df[f"{col}_outlier"] = is_outlier[:, i]
    return df

def engineer_temporal_features(df):
    """Extracts date/time features from the timestamp."""
    ts = df["timestamp"]
    df["year"] = ts.dt.year.astype(np.int16)
    df["month"] = ts.dt.month.astype(np.int8)
    df["day_of_week"] = ts.dt.dayofweek.astype(np.int8)
    df["hour"] = ts.dt.hour.astype(np.int8)
    df["is_weekend"] = ts.dt.dayofweek >= 5
    df["season"] = df["month"].map(SEASON_MAP)
    
    df["time_of_day"] = pd.cut(
        df["hour"],
        bins=[-1, 5, 11, 17, 23],
        labels=["Night", "Morning", "Afternoon", "Evening"]
    ).astype(str)
    return df

def add_energy_mix(df):
    """Calculates total generation and the percentage from renewable vs non-renewable sources."""
    present_ren = [c for c in RENEWABLE_FUELS if c in df.columns]
    present_foss = [c for c in NON_RENEWABLE_FUELS if c in df.columns]

    ren_arr = df[present_ren].to_numpy(dtype=float)
    foss_arr = df[present_foss].to_numpy(dtype=float)
    
    df["total_renewable"] = np.sum(ren_arr, axis=1)
    df["total_non_renewable"] = np.sum(foss_arr, axis=1)
    df["total_generation"] = df["total_renewable"] + df["total_non_renewable"]

    total = df["total_generation"].to_numpy(dtype=float)
    
    df["renewable_pct"] = np.where(total > 0, df["total_renewable"].to_numpy() / total * 100, np.nan)
    df["fossil_pct"] = np.where(total > 0, df["total_non_renewable"].to_numpy() / total * 100, np.nan)
    return df

