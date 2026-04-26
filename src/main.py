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

    if df.empty:
        print("Pipeline failed.")
        return
        
    print("\n--- Summary ---")
    print(f"Rows Processed: {len(df):,}")
    
    if "total_generation" in df.columns:
        print(f"Average Generation: {df['total_generation'].mean():.2f} MW")
    if "renewable_pct" in df.columns:
        print(f"Average Renewable Mix: {df['renewable_pct'].mean():.1f}%")
