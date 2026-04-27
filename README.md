# ireland-energy-data-analysis
# Energy - DATA 2005 Team Project

**Course:** DATA 2005 - Data-Centric Programming  
**Assessment:** Team Data Processing Project (20%)
**Research Question:** Where does Ireland get most of it's electricity from? 

## Team Members

| Name             | Role | GitHub |
|------------------|------|--------|
| Mohammed         | Data Engineer | [@Mohammedyounis18-github] |
| Hamza            | Data Analyst | [@Developere19-github] |
| Mohammed & Hamza | Visualization Lead | [@Mohammedyounis18-github, @Developere19-github] |
| Hamza            | Documentation Lead | [@Developere19-github] |


## Project Description

Analysis of Ireland's electricity generation mix from 2020 to 2023 using half-hourly CSO data. The project builds a full data pipeline - loading, cleaning, analysing, and visualising - to answer the research question of where Ireland gets its electricity from.

## Dataset

- **Name:** MEG01 - Metered Electricity Generation  
- **Source:** [Ireland Open Data](https://data.gov.ie/dataset/meg01-metered-electricity-generation?utm_source=chatgpt.com)  
- **Size:** ~1,000,000+ records  
- **Period:** January 2020 - December 2023
- **Format:** CSV / JSON / XLSX

## Project Structure

```
data2005-team-project/
├── data/
│   ├── raw/                    # Original dataset (MEG01.csv)
│   └── processed/              # Cleaned and transformed data
├── src/
│   ├── data_loader.py          # Data loading and format parsing
│   ├── data_processing.py      # Cleaning, feature engineering, normalisation
│   ├── analysis.py             # NumPy/Pandas statistical analysis
│   ├── visualization.py        # Seaborn/Matplotlib charts
│   └── main.py                 # Single entry point - runs everything
├── outputs/
│   ├── figures/                # Generated charts (PNG)
│   └── reports/                # Processed data exports
├── requirements.txt            # Project dependencies
└── README.md                   # This file
```
## Setup Instructions

1. **Clone the repository:**


git clone https://github.com/Developere19/data2005-team-project.git
cd data2005-team-project

2. **Install Dependencies**

pip install -r requirements.txt

3. **Add the dataset**
Place the raw CSV file in the data/raw/ folder and name it MEG01.csv

data/raw/MEG01.csv

4. **Run the full pipeline**
python src/main.py

This will run the four files automatically step by step.

## Dependencies

pandas
numpy
matplotlib
seaborn

Install with pip install -r requirements.txt

## Pipeline Architecture

```
MEG01.csv
    │
    ▼
data_loader.py       → loads CSV, parses timestamps, pivots wide
    │
    ▼
data_processing.py   → fills missing, flags outliers, engineers features
    │
    ▼
analysis.py          → fuel mix, trends, correlations, NumPy broadcasting
    │
    ▼
visualization.py     → 6 Seaborn charts saved to outputs/figures/
```
