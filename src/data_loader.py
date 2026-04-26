import pandas as pd

def load_raw_csv(filepath):
    """Reads the raw CSV file in chunks and converts 'VALUE' to numeric."""
    chunks = []
    # Read the file in chunks of 200,000 rows to prevent memory overload
    for chunk in pd.read_csv(filepath, encoding="utf-8-sig", dtype=str, chunksize=200_000):
        chunks.append(chunk)

    # Combine all the chunks into one big DataFrame
    raw_df = pd.concat(chunks, ignore_index=True)
    
    # Safely convert the 'VALUE' column to numbers, setting unparseable data to NaN
    raw_df["VALUE"] = pd.to_numeric(raw_df["VALUE"], errors="coerce")

    # Keep only the columns we actually need for the analysis
    cols_to_keep = ["Day", "Time Bands", "Primary Fuel Output", "VALUE"]
    return raw_df[cols_to_keep].copy()

def filter_aggregates(df):
    """Drops rows that are pre-aggregated daily totals."""
    # We drop 'All time periods' because keeping them would double-count our generation data
    return df[df["Time Bands"] != "All time periods"].copy()

def parse_timestamps(df):
    """Combines 'Day' and 'Time Bands' into a proper datetime column."""
    # Extract the starting time from strings like '00:00 < 00:30'
    start_time = df["Time Bands"].str.extract(r"(\d{2}:\d{2})\s*<")[0]
    
    # Combine the date and the starting time into a single string
    datetime_str = df["Day"].str.strip() + " " + start_time.str.strip()
    
    # Convert the string to a proper pandas datetime object
    df["timestamp"] = pd.to_datetime(datetime_str, format="%Y %B %d %H:%M", errors="coerce")
    
    return df

def pivot_wide(df):
    """Reshapes data so each fuel type gets its own column."""
    # Pivot the data to have timestamps as rows and fuel types as columns
    wide_df = df.pivot_table(
        index="timestamp",
        columns="Primary Fuel Output",
        values="VALUE",
        aggfunc="mean", # Average any duplicate records
    )
    
    # Clean up the column names
    wide_df.columns.name = None
    
    # Turn the timestamp index back into a regular column
    return wide_df.reset_index()

def load_data(filepath):
    """Runs all the loading and parsing steps in order."""
    df = load_raw_csv(filepath)
    df = filter_aggregates(df)
    df = parse_timestamps(df)
    return pivot_wide(df)
