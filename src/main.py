import os
from data_processing import run_pipeline
from analysis import get_headline_stats
from visualisation import make_all_plots

RAW_FILE = "MEG01.20260408163129.csv"

def main():
    if not os.path.exists(RAW_FILE):
        print(f"Error: Missing data file at {RAW_FILE}")
        return

    print("Running data processing pipeline...")
    df, resampled = run_pipeline(RAW_FILE)

