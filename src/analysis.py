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
        "fuel": totals.index,
        "total_mwh": totals.values,
        "share_pct": totals.values / totals.sum() * 100,
    }).sort_values("share_pct", ascending=False).reset_index(drop=True)
    out["category"] = np.where(out["fuel"].isin(RENEWABLE), "Renewable", "Fossil")
    return out

def yearly_mix(df):
    """Shows the shift between renewable and fossil generation over the years."""
    g = df.groupby("year")
    out = pd.DataFrame({
        "renewable_mwh": g[RENEWABLE].sum().sum(axis=1),
        "fossil_mwh": g[FOSSIL].sum().sum(axis=1),
    })
    out["renewable_pct"] = out["renewable_mwh"] / (out["renewable_mwh"] + out["fossil_mwh"]) * 100
    out["fossil_pct"] = 100 - out["renewable_pct"]
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
        "top_fuel": str(mix.iloc[0]["fuel"]),
        "top_share_pct": float(round(mix.iloc[0]["share_pct"], 1)),
        "renewable_pct": float(round(renew, 1)),
        "fossil_pct": float(round(100 - renew, 1)),
        "total_twh": float(round(mix["total_mwh"].sum() / 1_000_000, 1)),
    }

def calc_capacity_factor(df, capacities=CAPACITIES_MW):
    """
    Shows how hard each fuel works vs its capacity.
    Broadcast: (T, N) MWh matrix ÷ (N,) capacity vector -> (T, N) factor matrix
    """
    fuels = [f for f in capacities if f in df.columns]
    data = df[fuels].to_numpy(dtype=float)
    cap_vec = np.array([capacities[f] for f in fuels])

    cf = data / (cap_vec * 0.5)  # 0.5 because data is half-hourly
    return pd.DataFrame(cf, columns=fuels).mean().sort_values(ascending=False)

def zscore_fuels(df):
    """
    Standardizes each fuel to mean=0, std=1.
    Broadcast: ((T, N) - (N,)) / (N,)
    """
    data = df[ALL_FUELS].to_numpy(dtype=float)
    mu = data.mean(axis=0)
    sigma = data.std(axis=0, ddof=1)
    sigma[sigma == 0] = 1.0

    z = (data - mu) / sigma
    return pd.DataFrame(z, columns=ALL_FUELS, index=df["timestamp"])