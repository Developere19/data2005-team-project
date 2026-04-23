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