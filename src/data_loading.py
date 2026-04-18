import pandas as pd

def load_raw_csv(filepath):
    """Reads the raw CSV file in chunks (to prevent crashing the system) and converts 'VALUE' to numeric."""
    chunks = []
    for chunk in pd.read_csv(filepath, encoding="utf-8-sig", dtype=str, chunksize=200_000):
        chunks.append(chunk)

    raw_df = pd.concat(chunks, ignore_index=True)
    raw_df["VALUE"] = pd.to_numeric(raw_df["VALUE"], errors="coerce")

    # Keep only the columns we actually need
    cols_to_keep = ["Day", "Time Bands", "Primary Fuel Output", "VALUE"]
    return raw_df[cols_to_keep].copy()

def filter_aggregates(df):
    """Drops rows that are pre-aggregated daily totals."""
    return df[df["Time Bands"] != "All time periods"].copy()

def parse_timestamps(df):
    """Combines 'Day' and 'Time Bands' into a proper datetime column."""
    # Extract the starting time from strings like '00:00 < 00:30'
    start_time = df["Time Bands"].str.extract(r"(\d{2}:\d{2})\s*<")[0]
    
    datetime_str = df["Day"].str.strip() + " " + start_time.str.strip()
    df["timestamp"] = pd.to_datetime(datetime_str, format="%Y %B %d %H:%M", errors="coerce")
    
    return df

def pivot_wide(df):
    """Reshapes data so each fuel type gets its own column."""
    wide_df = df.pivot_table(
        index="timestamp",
        columns="Primary Fuel Output",
        values="VALUE",
        aggfunc="mean",
    )
    wide_df.columns.name = None
    return wide_df.reset_index()

