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