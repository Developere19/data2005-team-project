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
