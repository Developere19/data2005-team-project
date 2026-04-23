"""
Publication-ready charts for Ireland's electricity mix.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.patches as mpatches
import seaborn as sns

from preprocessing import run_pipeline
from analysis import (fuel_mix, yearly_mix, hourly_profile,
                      seasonal_profile, correlations)

FIG_DIR = os.path.join("outputs", "figures")
SOURCE = "Source: CSO MEG01 - Metered Electricity Generation (2020-2023)"

FUEL_COLOURS = {
    "Wind": "#5DADE2", "Solar": "#F4D03F", "Renewable Hydro": "#1ABC9C",
    "Gas": "#E67E22", "Coal": "#4A4A4A", "Oil": "#7D3C98",
    "Biomass/Peat": "#935116",
}
CAT_COLOURS = {"Renewable": "#27AE60", "Fossil": "#C0392B"}

sns.set_theme(style="whitegrid", context="talk")


def _style(ax, title, subtitle):
    """Applies title and subtitle styling."""
    ax.set_title(title, fontsize=17, pad=32)
    ax.text(0.5, 1.12, subtitle, transform=ax.transAxes, ha="center",
            fontsize=11, style="italic", color="#555")


def _save(fig, name):
    """Adds a source footer and saves the figure."""
    os.makedirs(FIG_DIR, exist_ok=True)
    fig.text(0.01, 0.005, SOURCE, fontsize=9, style="italic", color="#555")
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Saved: {path}")
    plt.close(fig)


def plot_fuel_mix(df_in):
    mix = fuel_mix(df_in)
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(data=mix, x="share_pct", y="fuel", hue="category",
                palette=CAT_COLOURS, ax=ax, dodge=False)
    for i, row in mix.iterrows():
        ax.text(row["share_pct"] + 0.4, i, f"{row['share_pct']:.1f}%",
                va="center", fontsize=11, color="#333")
    _style(ax, "Ireland's Electricity Mix (2020-2023)",
           "Gas and Wind together supply 83% of Ireland's electricity")
    ax.set(xlabel="Share of total generation (%)", ylabel="",
           xlim=(0, mix["share_pct"].max() * 1.15))
    ax.legend(title="", loc="lower right")
    _save(fig, "1_fuel_mix.png")


def plot_yearly_trend(df_in):
    yr = yearly_mix(df_in)
    fig, ax = plt.subplots(figsize=(11, 7))
    for col, cat, offset in [("renewable_pct", "Renewable", 12),
                              ("fossil_pct", "Fossil", -20)]:
        ax.plot(yr["year"], yr[col], marker="o", markersize=11, linewidth=3,
                label=cat, color=CAT_COLOURS[cat])
        for _, r in yr.iterrows():
            ax.annotate(f"{r[col]:.1f}%", (r["year"], r[col]),
                        textcoords="offset points", xytext=(0, offset),
                        ha="center", fontsize=11, fontweight="bold",
                        color=CAT_COLOURS[cat])
    _style(ax, "Renewable vs Fossil Share by Year",
           "2023 is Ireland's greenest year on record at 45% renewable")
    ax.set(xlabel="Year", ylabel="Share of generation (%)", ylim=(0, 80))
    ax.set_xticks(yr["year"])
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.legend(loc="center right")
    _save(fig, "2_yearly_trend.png")

def plot_hourly_profile(df_in):
    hp = hourly_profile(df_in)
    top4 = fuel_mix(df_in).head(4)["fuel"].tolist()
    fig, ax = plt.subplots(figsize=(12, 7))
    for fuel in top4:
        ax.plot(hp.index, hp[fuel], marker="o", linewidth=2.5,
                label=fuel, color=FUEL_COLOURS.get(fuel, "#444"))
    _style(ax, "Average Generation by Hour of Day",
           "Gas ramps up during the evening peak, wind stays roughly flat")
    ax.set(xlabel="Hour of day", ylabel="Average MWh per half-hour")
    ax.set_xticks(range(0, 24, 2))
    ax.legend(loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.22))
    _save(fig, "3_hourly_profile.png")
