# =========================
# 0️⃣ Imports
# =========================
import pandas as pd
import numpy as np
import sqlite3
import ast
import re
import os
from datetime import datetime

# =========================
# Load Data
# =========================
from pathlib import Path

# Get script directory and project root
script_dir = Path(__file__).parent
phase2_dir = script_dir.parent
project_root = phase2_dir.parent.parent

# Paths to data files
db_path = project_root / "data" / "cycling_big.db"
rider_infos_path = project_root / "data" / "data" / "rider_infos.csv"

# load data
conn = sqlite3.connect(db_path)
race_results = pd.read_sql_query("SELECT * FROM race_results", conn)
conn.close()

rider_infos = pd.read_csv(rider_infos_path)

print(f"Race Results Shape: {race_results.shape}")
print(f"Rider Info Shape: {rider_infos.shape}")

# =========================
# Clean Time
# =========================
def clean_time(time_str):
    if pd.isna(time_str) or time_str == '-':
        return None
    time_str = str(time_str).strip().replace(',,', '')
    match = re.search(r'^(\d+):(\d{2})(\d+):(\d{2})$', time_str)
    if match:
        return f"{match.group(1)}:{match.group(2)}"
    match = re.search(r'^(\d+):(\d{2,})(\d+):(\d{2})$', time_str)
    if match:
        return f"{match.group(3)}:{match.group(4)}"
    if not re.match(r'^[\d:]+$', time_str):
        return None
    return time_str

race_results['Time_clean'] = race_results['Time'].apply(clean_time)

# =========================
# Clean Date
# =========================
race_results['Date_clean'] = pd.to_datetime(race_results['Date'], format='%d %B %Y', errors='coerce')

def fill_missing_dates(df):
    df = df.copy()
    for race_id in df['Race_ID'].unique():
        race_mask = df['Race_ID'] == race_id
        race_dates = df.loc[race_mask, 'Date_clean'].dropna()
        if len(race_dates) > 0:
            min_date = race_dates.min()
            missing_mask = race_mask & df['Date_clean'].isna()
            df.loc[missing_mask, 'Date_clean'] = min_date
    return df

race_results = fill_missing_dates(race_results)
race_results['Date'] = race_results['Date_clean']
race_results['Time'] = race_results['Time_clean']
race_results = race_results.drop(columns=['Date_clean', 'Time_clean'])

# =========================
# Filter classification stages
# =========================
classification_keywords = ['classification', 'standings', 'overall', 'general']
mask = race_results['Stage_Name'].str.lower().str.contains('|'.join(classification_keywords), na=False)
race_results = race_results[~mask].copy()

# =========================
# Clean Rank
# =========================
def clean_rank(rank):
    try:
        return int(rank)
    except (ValueError, TypeError):
        return 999

race_results['Rnk_clean'] = race_results['Rnk'].apply(clean_rank)
race_results['is_top_10'] = (race_results['Rnk_clean'] <= 10).astype(int)

# =========================
# Clean Length
# =========================
race_results['Length_km'] = pd.to_numeric(race_results['Length'].str.replace('km','').str.strip(), errors='coerce')

# =========================
# Parse Rider Info (pps/rdr)
# =========================
def parse_dict(cell):
    if pd.isna(cell) or not isinstance(cell, str) or not cell.strip():
        return {}
    try:
        return ast.literal_eval(cell)
    except Exception:
        return {}

rider_infos['pps_parsed'] = rider_infos['pps'].apply(parse_dict)
pps_expanded = rider_infos['pps_parsed'].apply(pd.Series).fillna(0)
pps_expanded.columns = [f"pps_{col}" for col in pps_expanded.columns]

rider_infos['rdr_parsed'] = rider_infos['rdr'].apply(parse_dict)
rdr_expanded = rider_infos['rdr_parsed'].apply(pd.Series).fillna(0)
rdr_expanded.columns = [f"rdr_{col}" for col in rdr_expanded.columns]

rider_infos_expanded = pd.concat([rider_infos, pps_expanded, rdr_expanded], axis=1)

# =========================
# UCI & Pnt Features (NO LEAKAGE - current race excluded)
# =========================
# IMPORTANT: We create binary indicators AFTER aggregations to avoid leakage
race_results['UCI_filled'] = race_results['UCI'].fillna(0)
race_results['Pnt_filled'] = race_results['Pnt'].fillna(0)

# Store original for later dropping (these contain current race info)
race_results['has_uci_points'] = race_results['UCI'].notna().astype(int)

# These aggregations will be replaced with historical rolling versions later
# For now, we create placeholders that will be overwritten
uci_agg = race_results.groupby('Rider').agg({
    'UCI_filled':['sum','mean','max','std'],
    'has_uci_points':'sum'
}).reset_index()
uci_agg.columns = ['Rider','UCI_total','UCI_avg','UCI_max','UCI_std','UCI_race_count']
uci_agg['UCI_elite_status'] = (uci_agg['UCI_race_count']>0).astype(int)
uci_agg['UCI_points_per_race'] = uci_agg['UCI_total']/uci_agg['UCI_race_count'].replace(0,np.nan)
uci_agg['UCI_points_per_race'] = uci_agg['UCI_points_per_race'].fillna(0)

pnt_agg = race_results.groupby('Rider').agg({
    'Pnt_filled':['sum','mean','max','std']
}).reset_index()
pnt_agg.columns = ['Rider','Pnt_total','Pnt_avg','Pnt_max','Pnt_std']
pnt_agg['Pnt_race_count'] = race_results.groupby('Rider')['Pnt_filled'].apply(lambda x: (x>0).sum()).values
pnt_agg['Pnt_points_per_race'] = pnt_agg['Pnt_total']/pnt_agg['Pnt_race_count'].replace(0,np.nan)
pnt_agg['Pnt_points_per_race'] = pnt_agg['Pnt_points_per_race'].fillna(0)

# =========================
# Merge Race + Rider Info
# =========================
rider_infos_expanded['birthdate'] = pd.to_datetime(rider_infos_expanded['birthdate'], errors='coerce')
race_results['Rider_clean'] = race_results['Rider'].str.strip().str.upper()
rider_infos_expanded['fullname_clean'] = rider_infos_expanded['fullname'].str.strip().str.upper()

df = race_results.merge(
    rider_infos_expanded[['fullname_clean','birthdate','country','height','weight'] + 
                         list(pps_expanded.columns) + list(rdr_expanded.columns)],
    left_on='Rider_clean', right_on='fullname_clean', how='left'
)

# =========================
# Track Imputations for height/weight
# =========================
df['height_imputed'] = False
df['weight_imputed'] = False

# Fill height/weight by age median then overall median
age_medians = df.groupby('Age')[['height','weight']].median()
df = df.merge(age_medians.add_suffix('_age_median'), left_on='Age', right_index=True, how='left')

for col, median_col, flag in [('height','height_age_median','height_imputed'), 
                              ('weight','weight_age_median','weight_imputed')]:
    missing_mask = df[col].isna() | (df[col]==0)
    df.loc[missing_mask, col] = df.loc[missing_mask, median_col].fillna(df[col].median())
    df.loc[missing_mask, flag] = True

# Cap extreme values
df['height'] = df['height'].clip(1.5,2.1)
df['weight'] = df['weight'].clip(50,100)

# =========================
# Ensure all pps/rdr numeric (fill median instead of 0)
# =========================
for col in list(pps_expanded.columns) + list(rdr_expanded.columns):
    if col in df.columns:
        # convert column to numeric first (invalid strings -> NaN)
        df[col] = pd.to_numeric(df[col], errors='coerce')
        median_val = df[col].median()  # now safe
        df[col] = df[col].fillna(median_val)

# =========================
# Merge UCI/Pnt
# =========================
df = df.merge(uci_agg, on='Rider', how='left')
df = df.merge(pnt_agg, on='Rider', how='left')

# =========================
# Age at Race
# =========================
mask = df['Date'].notna() & df['birthdate'].notna()
df.loc[mask,'age_at_race'] = (df.loc[mask,'Date'] - df.loc[mask,'birthdate']).dt.days/365.25
df['age_at_race'] = df['age_at_race'].fillna(df['Age'])

# =========================
#  Drop duplicates carefully
# =========================
before = len(df)
df = df.sort_values(['Rider','Date']).drop_duplicates(subset=['Rider','Race_ID','Stage_Number'], keep='first')
print(f"Dropped {before-len(df)} duplicate Rider/Stage rows")

# =========================
# Race Tier & Rolling Metrics (FIXED - EXCLUDE CURRENT RACE)
# =========================
grand_tours = ['Tour de France','Giro d\'Italia','Vuelta a España','La Vuelta ciclista a España']
df['race_tier'] = 3
df.loc[df['Race_Name'].isin(grand_tours),'race_tier'] = 1
df.loc[df['has_uci_points']==1,'race_tier'] = df.loc[df['has_uci_points']==1,'race_tier'].apply(lambda x: 2 if x==3 else x)

# Sort by rider and date for proper temporal order
df = df.sort_values(['Rider','Date']).reset_index(drop=True)

# CRITICAL FIX: shift(1) BEFORE rolling to exclude current race
# This ensures we only use PAST performance to predict CURRENT race
df['rolling_avg_rank_5'] = df.groupby('Rider')['Rnk_clean'].transform(
    lambda x: x.shift(1).rolling(5, min_periods=1).mean()
)
df['rolling_avg_rank_10'] = df.groupby('Rider')['Rnk_clean'].transform(
    lambda x: x.shift(1).rolling(10, min_periods=1).mean()
)
df['recent_top10_count'] = df.groupby('Rider')['is_top_10'].transform(
    lambda x: x.shift(1).rolling(10, min_periods=1).sum()
)
df['recent_top10_rate'] = df['recent_top10_count'] / 10

# Fill NaN for riders with no history (first race)
df['rolling_avg_rank_5'] = df['rolling_avg_rank_5'].fillna(df['Rnk_clean'].median())
df['rolling_avg_rank_10'] = df['rolling_avg_rank_10'].fillna(df['Rnk_clean'].median())
df['recent_top10_count'] = df['recent_top10_count'].fillna(0)
df['recent_top10_rate'] = df['recent_top10_rate'].fillna(0)

# =========================
# Drop unnecessary columns + DATA LEAKAGE FEATURES
# =========================
cols_to_drop = ['id','Circuit','Category','Race_url','Stage_url','rider_id','Rnk','Length',
                'BiB','GC','fullname','Rider_clean','fullname_clean','height_age_median','weight_age_median',
                'UCI','Pnt',
                # DATA LEAKAGE: Remove current race point indicators
                'has_uci_points',  # Whether THIS race awarded UCI points (reveals outcome)
                'UCI_filled',      # Current race UCI points (LEAKAGE!)
                'Pnt_filled']      # Current race Pnt points (LEAKAGE!)

cols_to_drop = [c for c in cols_to_drop if c in df.columns]
df_clean = df.drop(columns=cols_to_drop)

# =========================
# Final Checks
# =========================
missing_pct = (df_clean.isnull().sum()/len(df_clean)*100).sort_values(ascending=False)
missing_pct = missing_pct[missing_pct>0]
print("\nMissing values summary:")
print(missing_pct if len(missing_pct)>0 else "No missing values!")

print(f"\nFinal shape: {df_clean.shape}")
print(f"Total records: {len(df_clean):,}")
print(f"Unique riders: {df_clean['Rider'].nunique()}")
print(f"Unique races: {df_clean['Race_Name'].nunique()}")
print(f"Date range: {df_clean['Date'].min()} to {df_clean['Date'].max()}")

# =========================
# Save processed data
# =========================
output_dir = phase2_dir / 'processed_data'
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / 'race_data_processed.csv'
df_clean.to_csv(output_path, index=False)
print(f"Processed data saved to: {output_path}")
