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
