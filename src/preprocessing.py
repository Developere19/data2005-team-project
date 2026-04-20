import os
import json
import numpy as np
import pandas as pd
from data_loader import load_data

# Constants
RAW_FILE = r"C:\Users\Mohammedrog\PycharmProjects\PythonProject1\dcp2\MEG01.20260408163129.csv"
PROCESSED_DIR = os.path.join("data", "processed")

RENEWABLE_FUELS = [
    "Renewable Hydro", "Solar", "Wind",
    "Other Renewable", "Pumped Storage Hydro",
]

NON_RENEWABLE_FUELS = [
    "Biomass/Peat", "Coal", "Distillate", "Gas",
    "Oil", "Other Non-Renewable", "Waste", "Battery Storage",
]

SEASON_MAP = {
    12: "Winter", 1: "Winter",  2: "Winter",
     3: "Spring", 4: "Spring",  5: "Spring",
     6: "Summer", 7: "Summer",  8: "Summer",
     9: "Autumn", 10: "Autumn", 11: "Autumn",
}

IQR_MULTIPLIER = 1.5
