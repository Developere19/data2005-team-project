import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.patches as mpatch
import seaborn as sns

from preprocessing import run_pipeline
from analysis import (fuel_mix, yearly_mix, hourly_profile,
                      seasonal_profile, correlations)

# Calculate the absolute path to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to save generated charts relative to the project root
FIG_DIR = os.path.join(BASE_DIR, "outputs", "figures")
SOURCE = "Source: CSO MEG01 - Metered Electricity Generation (2020-2023)"

# Color scheme for consistent visualization across charts
FUEL_COLOURS = {
    "Wind": "#5DADE2", "Solar": "#F4D03F", "Renewable Hydro": "#1ABC9C",
    "Gas": "#E67E22", "Coal": "#4A4A4A", "Oil": "#7D3C98",
    "Biomass/Peat": "#935116",
}
CAT_COLOURS = {"Renewable": "#27AE60", "Fossil": "#C0392B"}

# Set a clean, professional Seaborn style suitable for presentations
sns.set_theme(style="whitegrid", context="talk")


def _style(ax, title, subtitle):
    """Applies title and subtitle styling."""
    ax.set_title(title, fontsize=17, pad=32)
    # Add a slightly smaller, italicized subtitle below the main title
    ax.text(0.5, 1.12, subtitle, transform=ax.transAxes, ha="center",
            fontsize=11, style="italic", color="#555")


def _save(fig, name):
    """Adds a source footer and saves the figure."""
    os.makedirs(FIG_DIR, exist_ok=True)
    
    # Add a consistent source credit to the bottom left of every chart
    fig.text(0.01, 0.005, SOURCE, fontsize=9, style="italic", color="#555")
    
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# --- Charts ---

def plot_fuel_mix(df_in):
    """Plots a horizontal bar chart showing the overall electricity mix."""
    # Get the overall fuel mix data
    mix = fuel_mix(df_in)
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Create a horizontal bar chart
    sns.barplot(data=mix, x="share_pct", y="fuel", hue="category",
                palette=CAT_COLOURS, ax=ax, dodge=False)
                
    # Add percentage labels to the end of each bar
    for i, row in mix.iterrows():
        ax.text(row["share_pct"] + 0.4, i, f"{row['share_pct']:.1f}%",
                va="center", fontsize=11, color="#333")
                
    _style(ax, "Ireland's Electricity Mix (2020 - 2023)",
           "Gas and Wind together supply 83% of Ireland's electricity")
           
    # Extend x-axis slightly to make room for text labels
    ax.set(xlabel="Share of total generation (%)", ylabel="",
           xlim=(0, mix["share_pct"].max() * 1.15))
    ax.legend(title="", loc="lower right")
    _save(fig, "1_fuel_mix.png")


def plot_yearly_trend(df_in):
    """Plots the trend of renewable vs fossil fuel generation over time."""
    # Get the yearly percentage breakdown
    yr = yearly_mix(df_in)
    fig, ax = plt.subplots(figsize=(11, 7))
    
    # Plot two lines: one for renewables, one for fossil fuels
    for col, cat, offset in [("renewable_pct", "Renewable", 12),
                              ("fossil_pct", "Fossil", -20)]:
        ax.plot(yr["year"], yr[col], marker="o", markersize=11, linewidth=3,
                label=cat, color=CAT_COLOURS[cat])
                
        # Annotate each data point with its percentage
        for _, r in yr.iterrows():
            ax.annotate(f"{r[col]:.1f}%", (r["year"], r[col]),
                        textcoords="offset points", xytext=(0, offset),
                        ha="center", fontsize=11, fontweight="bold",
                        color=CAT_COLOURS[cat])
                        
    _style(ax, "Renewable vs Fossil Share by Year",
           "2023 is Ireland's greenest year on record at 45% renewable")
           
    ax.set(xlabel="Year", ylabel="Share of generation (%)", ylim=(0, 80))
    # Ensure only whole years are shown on the x-axis
    ax.set_xticks(yr["year"])
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.legend(loc="center right")
    _save(fig, "2_yearly_trend.png")


def plot_hourly_profile(df_in):
    """Plots the average generation by hour of the day for the top 4 fuels."""
    # Get the hourly generation profile
    hp = hourly_profile(df_in)
    
    # Identify the top 4 fuels by total generation
    top4 = fuel_mix(df_in).head(4)["fuel"].tolist()
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot a line for each of the top 4 fuels
    for fuel in top4:
        ax.plot(hp.index, hp[fuel], marker="o", linewidth=2.5,
                label=fuel, color=FUEL_COLOURS.get(fuel, "#444"))
                
    _style(ax, "Average Generation by Hour of Day",
           "Gas ramps up during the evening peak, wind stays roughly flat")
           
    ax.set(xlabel="Hour of day", ylabel="Average MWh per half-hour")
    # Show every second hour on the x-axis
    ax.set_xticks(range(0, 24, 2))
    # Place legend below the chart
    ax.legend(loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.22))
    _save(fig, "3_hourly_profile.png")


def plot_seasonal(df_in):
    """Plots a grouped bar chart showing average generation by season."""
    # Get the top 4 fuels
    top4 = fuel_mix(df_in).head(4)["fuel"].tolist()
    
    # Reshape the data to a 'long' format suitable for Seaborn
    long = seasonal_profile(df_in).reset_index().melt(
        id_vars="season", value_vars=top4, var_name="fuel", value_name="avg_mwh")
        
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Create grouped bar chart
    sns.barplot(data=long, x="season", y="avg_mwh", hue="fuel", ax=ax,
                palette=[FUEL_COLOURS.get(f, "#444") for f in top4])
                
    # Add generation values to the top of each bar
    for c in ax.containers:
        ax.bar_label(c, fmt="%.0f", padding=3, fontsize=9, color="#333")
        
    _style(ax, "Seasonal Generation Patterns",
           "Wind halves from winter to summer; gas output rises to compensate")
    ax.set(xlabel="", ylabel="Average MWh per half-hour")
    ax.legend(title="", loc="upper right")
    _save(fig, "4_seasonal.png")



def plot_renewable_distribution(df_in):
    """Plots a histogram of the renewable generation share."""
    # Filter out missing data
    data = df_in["renewable_pct"].dropna()
    
    # Calculate how often renewables provide more than 50% of power
    pct_above = (data >= 50).mean() * 100
    
    fig, ax = plt.subplots(figsize=(11, 7))
    
    # Create a histogram showing the distribution of renewable generation
    sns.histplot(data, bins=40, color=CAT_COLOURS["Renewable"],
                 edgecolor="white", ax=ax)
                 
    # Draw a dashed line at the 50% mark
    ax.axvline(50, color="black", linestyle="--", linewidth=2)
    ax.text(51, ax.get_ylim()[1] * 0.9,
            f"50% renewable\n{pct_above:.1f}% of half-hours above", fontsize=11)
            
    _style(ax, "How Often Does Ireland Run on Renewables?",
           f"Ireland runs on >=50% renewables {pct_above:.0f}% of the time")
           
    ax.set(xlabel="Renewable share of generation (%)",
           ylabel="Number of half-hours")
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    _save(fig, "6_renewable_distribution.png")


def make_all_plots(df_in):
    """Generates all visualizations and saves them to the output directory."""
    for fn in [plot_fuel_mix, plot_yearly_trend, plot_hourly_profile,
               plot_seasonal, plot_renewable_distribution]:
        fn(df_in)


if __name__ == "__main__":
    print("Running pipeline...")
    final_df, _ = run_pipeline()
    if final_df.empty:
        print("Pipeline failed. Cannot plot.")
    else:
        print("Building charts...\n")
        make_all_plots(final_df)
        print(f"\nDone! Charts saved in: {FIG_DIR}/")
