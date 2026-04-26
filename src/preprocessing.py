import os
import json
import numpy as np
import pandas as pd
from data_loader import load_data

# Constants
RAW_FILE = r"data/raw/MEG01.csv"
PROCESSED_DIR = os.path.join("data", "processed")

# Fuel categories based on whether they are renewable or fossil
RENEWABLE_FUELS = [
    "Renewable Hydro", "Solar", "Wind",
    "Other Renewable", "Pumped Storage Hydro",
]

NON_RENEWABLE_FUELS = [
    "Biomass/Peat", "Coal", "Distillate", "Gas",
    "Oil", "Other Non-Renewable", "Waste", "Battery Storage",
]

# Map month numbers to their respective seasons
SEASON_MAP = {
    12: "Winter", 1: "Winter",  2: "Winter",
     3: "Spring", 4: "Spring",  5: "Spring",
     6: "Summer", 7: "Summer",  8: "Summer",
     9: "Autumn", 10: "Autumn", 11: "Autumn",
}

# The multiplier used for the Interquartile Range (IQR) method of detecting outliers
IQR_MULTIPLIER = 1.5

def handle_missing(df):
    """Fills missing values: first by carrying forward up to 1 hour, then using the column median."""
    # Find all the columns that contain fuel data
    fuel_cols = [c for c in df.columns if c != "timestamp"]
    
    # Step 1: Forward fill up to 2 half-hour periods (which is 1 hour)
    df[fuel_cols] = df[fuel_cols].ffill(limit=2)
    
    # Step 2: Fill any remaining missing values with the median for that column
    df[fuel_cols] = df[fuel_cols].fillna(df[fuel_cols].median())
    
    return df

def detect_outliers(df):
    """Flags outliers using the standard IQR method."""
    fuel_cols = [c for c in df.columns if c != "timestamp"]
    
    # Convert fuel data to a NumPy array for fast operations
    values = df[fuel_cols].to_numpy(dtype=float)

    # Calculate Q1 (25th percentile), Q3 (75th percentile), and IQR
    q1 = np.percentile(values, 25, axis=0)
    q3 = np.percentile(values, 75, axis=0)
    iqr = q3 - q1

    # Mark as outlier if below Q1 - 1.5*IQR or above Q3 + 1.5*IQR
    is_outlier = (values < q1 - IQR_MULTIPLIER * iqr) | (values > q3 + IQR_MULTIPLIER * iqr)

    # Create new outlier columns to flag the outliers
    for i, col in enumerate(fuel_cols):
        df[f"{col}_outlier"] = is_outlier[:, i]
        
    return df

def engineer_temporal_features(df):
    """Extracts date/time features from the timestamp."""
    ts = df["timestamp"]
    
    # Create new columns for different time components
    df["year"] = ts.dt.year.astype(np.int16)
    df["month"] = ts.dt.month.astype(np.int8)
    df["day_of_week"] = ts.dt.dayofweek.astype(np.int8)
    df["hour"] = ts.dt.hour.astype(np.int8)
    
    # A day is a weekend if the day of the week is >= 5 (Saturday or Sunday)
    df["is_weekend"] = ts.dt.dayofweek >= 5
    
    # Use our map to determine the season
    df["season"] = df["month"].map(SEASON_MAP)
    
    # Group the hour of the day into time of day categories
    df["time_of_day"] = pd.cut(
        df["hour"],
        bins=[-1, 5, 11, 17, 23],
        labels=["Night", "Morning", "Afternoon", "Evening"]
    ).astype(str)
    
    return df

def add_energy_mix(df):
    """Calculates total generation and the percentage from renewable vs non-renewable sources."""
    # Find out which renewable and fossil fuels are present in our data
    present_ren = [c for c in RENEWABLE_FUELS if c in df.columns]
    present_foss = [c for c in NON_RENEWABLE_FUELS if c in df.columns]

    # Convert the relevant columns into NumPy arrays
    ren_arr = df[present_ren].to_numpy(dtype=float)
    foss_arr = df[present_foss].to_numpy(dtype=float)
    
    # Calculate the total generation by summing the arrays along the rows (axis=1)
    df["total_renewable"] = np.sum(ren_arr, axis=1)
    df["total_non_renewable"] = np.sum(foss_arr, axis=1)
    df["total_generation"] = df["total_renewable"] + df["total_non_renewable"]

    total = df["total_generation"].to_numpy(dtype=float)
    
    # Calculate the percentages, using np.where to avoid dividing by zero
    df["renewable_pct"] = np.where(total > 0, df["total_renewable"].to_numpy() / total * 100, np.nan)
    df["fossil_pct"] = np.where(total > 0, df["total_non_renewable"].to_numpy() / total * 100, np.nan)
    
    return df

def normalise_and_detect_peaks(df):
    """Scales fuel columns to a 0-1 range and detects periods of peak generation."""
    # Define columns that shouldn't be normalised
    skip_cols = {"timestamp", "season", "time_of_day", "is_weekend", "year", "month", "day_of_week", "hour"}
    
    fuel_cols = [
        c for c in df.columns
        if c not in skip_cols and not c.endswith("_outlier") and not c.endswith("_norm")
        and pd.api.types.is_numeric_dtype(df[c])
    ]

    # Calculate min, max, and range for min-max scaling
    values = df[fuel_cols].to_numpy(dtype=float)
    col_min = values.min(axis=0)
    col_max = values.max(axis=0)
    
    # Avoid division by zero if min == max
    val_range = np.where(col_max - col_min == 0, 1, col_max - col_min)

    # Perform scaling and store the values
    normed = (values - col_min) / val_range
    for i, col in enumerate(fuel_cols):
        df[f"{col}_norm"] = normed[:, i]

    # Find the top 5% highest generation periods
    if "total_generation" in df.columns:
        peak_threshold = np.percentile(df["total_generation"].dropna(), 95)
        df["is_peak_period"] = df["total_generation"] >= peak_threshold

    # Save scaling params so we can reverse the process if needed later
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    params = {col: {"min": float(col_min[i]), "max": float(col_max[i])} for i, col in enumerate(fuel_cols)}
    
    with open(os.path.join(PROCESSED_DIR, "normalisation_params.json"), "w", encoding="utf-8") as out_file:
        out_file.write(json.dumps(params, indent=2))
        
    return df

def resample_and_summarize(df):
    """Rolls up the half-hourly data into hourly, daily, and weekly views."""
    skip_cols = {"timestamp", "season", "time_of_day", "is_weekend", "year", "month", "day_of_week", "hour"}
    
    fuel_cols = [
        c for c in df.columns
        if c not in skip_cols and not c.endswith("_outlier") and not c.endswith("_norm") and c != "is_peak_period"
    ]

    # Set timestamp as index so we can resample the dataframe
    df_ts = df.set_index("timestamp")[fuel_cols]
    
    resampled_results = {}
    
    # Sum the data at hourly ('h'), daily ('D'), and weekly ('W') intervals
    for freq, label in [("h", "hourly"), ("D", "daily"), ("W", "weekly")]:
        resampled_results[label] = df_ts.resample(freq).sum().reset_index()
        
    return resampled_results

def export_data(df, resampled_data):
    """Saves the final clean dataset and the rolled-up views to files."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Save the main dataset as a CSV
    df.to_csv(os.path.join(PROCESSED_DIR, "electricity_clean.csv"), index=False)
    
    # Save the main dataset as a JSON (timestamps must be strings)
    df_json = df.copy()
    df_json["timestamp"] = df_json["timestamp"].astype(str)
    df_json.to_json(os.path.join(PROCESSED_DIR, "electricity_clean.json"), orient="records", indent=2)

    # Save the summary datasets
    for label, agg_df in resampled_data.items():
        agg_df.to_csv(os.path.join(PROCESSED_DIR, f"{label}_generation.csv"), index=False)

def run_pipeline(filepath=RAW_FILE):
    """Runs all data processing steps."""
    try:
        df = load_data(filepath)
        df = handle_missing(df)
        df = detect_outliers(df)
        df = engineer_temporal_features(df)
        df = add_energy_mix(df)
        df = normalise_and_detect_peaks(df)
        
        resampled_views = resample_and_summarize(df)
        export_data(df, resampled_views)
        
        return df, resampled_views
    except Exception as e:
        print(f"Error during processing: {e}")
        return pd.DataFrame(), {}
