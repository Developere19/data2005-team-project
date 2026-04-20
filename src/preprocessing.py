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
