"""
analysis.py
-----------
Answers the core research question: Where does Ireland get its electricity from?
Uses NumPy vectorisation and broadcasting throughout for efficient processing.
"""

import numpy as np
import pandas as pd
from preprocessing import run_pipeline

RENEWABLE = ["Wind", "Solar", "Renewable Hydro", "Other Renewable", "Pumped Storage Hydro"]
FOSSIL = ["Gas", "Coal", "Oil", "Distillate", "Biomass/Peat", "Waste",
          "Other Non-Renewable", "Battery Storage"]
ALL_FUELS = RENEWABLE + FOSSIL

# Rough Irish installed capacities in MW (for capacity factor demo)
CAPACITIES_MW = {
    "Wind": 4500, "Gas": 4800, "Coal": 855, "Solar": 700,
    "Biomass/Peat": 380, "Renewable Hydro": 530, "Oil": 200,
    "Waste": 80, "Pumped Storage Hydro": 292,
}


#---------------|
# Core Analysis |
#---------------|

def fuel_mix(df):
    """Calculates total MWh and % share per fuel."""
    totals = df[ALL_FUELS].sum()
    out = pd.DataFrame({
        "fuel": totals.index, #fuel names become columns
        "total_mwh": totals.values,  # raw MWh per fuel
        "share_pct": totals.values / totals.sum() * 100, # each fuel as % of grand total
    }).sort_values("share_pct", ascending=False).reset_index(drop=True) # rank highest % first
    out["category"] = np.where(out["fuel"].isin(RENEWABLE), "Renewable", "Fossil")  # label each fuel as Renewable or Fossil
    return out

def yearly_mix(df):
    """Shows the shift between renewable and fossil generation over the years."""
    g = df.groupby("year") # group by year
    out = pd.DataFrame({
        "renewable_mwh": g[RENEWABLE].sum().sum(axis=1), # total renewable MWh per year
        "fossil_mwh": g[FOSSIL].sum().sum(axis=1), # total fossil MWh per year
    })
    out["renewable_pct"] = out["renewable_mwh"] / (out["renewable_mwh"] + out["fossil_mwh"]) * 100 # renewable as % of total per year
    out["fossil_pct"] = 100 - out["renewable_pct"] # fossil is whatever is left
    return out.reset_index()

def hourly_profile(df):
    """Calculates average MWh per fuel by hour of the day."""
    return df.groupby("hour")[ALL_FUELS].mean()

def seasonal_profile(df):
    """Calculates average MWh per fuel by season."""
    order = ["Winter", "Spring", "Summer", "Autumn"]
    return df.groupby("season")[ALL_FUELS].mean().reindex(order)

def correlations(df):
    """Finds correlations between different fuel sources."""
    return df[ALL_FUELS].corr()

def get_headline_stats(df):
    """Generates a high-level summary of the dataset."""
    mix = fuel_mix(df)
    renew = mix.loc[mix["category"] == "Renewable", "share_pct"].sum()

    return {
        "top_fuel": str(mix.iloc[0]["fuel"]), # name of the highest ranked fuel (Gas)
        "top_share_pct": float(round(mix.iloc[0]["share_pct"], 1)), # its % share rounded to 1 decimal
        "renewable_pct": float(round(renew, 1)), # total renewable share %
        "fossil_pct": float(round(100 - renew, 1)),     # total fossil share % (remainder)
        "total_twh": float(round(mix["total_mwh"].sum() / 1_000_000, 1)), # convert MWh to TWh
    }

def calc_capacity_factor(df, capacities=CAPACITIES_MW):
    """
    Shows how hard each fuel works vs its capacity.
    Broadcast: (T, N) MWh matrix ÷ (N,) capacity vector -> (T, N) factor matrix
    """
    fuels = [f for f in capacities if f in df.columns] # only keep fuels that exist in both the data and the capacity dictionary
    data = df[fuels].to_numpy(dtype=float) # convert fuel columns to a NumPy matrix (T rows x N fuels)
    cap_vec = np.array([capacities[f] for f in fuels]) # build a capacity vector (N,) one value per fuel

    cf = data / (cap_vec * 0.5)  # 0.5 because data is half-hourly
    return pd.DataFrame(cf, columns=fuels).mean().sort_values(ascending=False)

def zscore_fuels(df):
    """
    Standardizes each fuel to mean=0, std=1.
    Broadcast: ((T, N) - (N,)) / (N,)
    """
    data = df[ALL_FUELS].to_numpy(dtype=float) # convert all fuel columns to a NumPy matrix (T rows x N fuels)
    mu = data.mean(axis=0) # calculate the mean for each fuel column (N,)
    sigma = data.std(axis=0, ddof=1) # calculate the std for each fuel column (N,)
    sigma[sigma == 0] = 1.0  # if std is 0 (no variation), set to 1 to avoid dividing by zero

    z = (data - mu) / sigma
    return pd.DataFrame(z, columns=ALL_FUELS, index=df["timestamp"])

def calc_fuel_shares(df):
    """
    Calculates each fuel's percentage share of generation per half-hour.
    Broadcast: (T, N) MWh ÷ (T, 1) row totals -> (T, N) shares
    """
    data = df[ALL_FUELS].to_numpy(dtype=float)
    row_totals = data.sum(axis=1, keepdims=True)
    row_totals[row_totals == 0] = 1.0 # if a row total is 0, set to 1 to avoid dividing by zero

    shares = data / row_totals * 100
    return pd.DataFrame(shares, columns=ALL_FUELS, index=df["timestamp"])

if __name__ == "__main__":
    print("Running analysis pipeline...")
    df, _ = run_pipeline()

    if df.empty:
        print("Failed to load data. Exiting analysis.")
        exit()

    h = get_headline_stats(df)
    print("\n=== HEADLINE STATS ===")
    print(f"Top Fuel Source: {h['top_fuel']} ({h['top_share_pct']}%)")
    print(f"Renewable Mix:   {h['renewable_pct']}%")
    print(f"Fossil Mix:      {h['fossil_pct']}%")
    print(f"Total Energy:    {h['total_twh']} TWh")

    print("\n--- Overall Fuel Mix ---")
    print(fuel_mix(df).to_string(index=False))

    print("\n--- Yearly Trend ---")
    print(yearly_mix(df).round(1).to_string(index=False))

    print("\n--- Seasonal Averages (MWh per half-hour) ---")
    print(seasonal_profile(df).round(1))

    print("\n=== BROADCASTING DEMOS ===")
    print("\nMean Capacity Factor per fuel:")
    print(calc_capacity_factor(df).round(3))

    print("\nZ-score sanity check (Wind):")
    z = zscore_fuels(df)
    print(f"Mean: {z['Wind'].mean():.4f}, Std: {z['Wind'].std():.4f}")

    print("\nAverage fuel share per half-hour:")
    print(calc_fuel_shares(df).mean().round(2).sort_values(ascending=False))