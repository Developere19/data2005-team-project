import os
from preprocessing import run_pipeline
from analysis import get_headline_stats
from visualization import make_all_plots

# Calculate the path relative to the script location for robust execution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FILE = os.path.join(BASE_DIR, "data", "raw", "MEG01.csv")

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

    print("\nData exported to 'data/processed' folder.")

    print("\nRunning analysis...")
    stats = get_headline_stats(df)
    print(f"Top Fuel: {stats['top_fuel']} ({stats['top_share_pct']}%)")
    print(f"Total Renewable: {stats['renewable_pct']}%")

    print("\nGenerating visualisations...")
    make_all_plots(df)
    
    fig_dir = os.path.join(BASE_DIR, 'outputs', 'figures')
    print(f"\nDone! Visualisations saved to '{fig_dir}' folder.")


if __name__ == "__main__":
    main()
