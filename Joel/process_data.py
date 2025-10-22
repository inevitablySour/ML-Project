import pandas as pd
import numpy as np
import sqlite3
import ast
import re
from datetime import datetime

# Load race results from SQLite database
conn = sqlite3.connect("../data/cycling_big.db")
race_results = pd.read_sql_query("SELECT * FROM race_results", conn)
conn.close()

# Load rider information
rider_infos = pd.read_csv("../data/data/rider_infos.csv")

print(f"Race Results Shape: {race_results.shape}")
print(f"Rider Info Shape: {rider_infos.shape}")

# ============================================================================
# CLEAN TIME COLUMN (fix formatting issues)
# ============================================================================
def clean_time(time_str):
    """Clean and standardize time formats"""
    if pd.isna(time_str) or time_str == '-':
        return None
    
    time_str = str(time_str).strip()
    
    # Remove comma prefix (e.g., ",,0:00" -> "0:00")
    time_str = time_str.replace(',,', '')
    
    # Fix duplicated times (e.g., "1:201:20" -> "1:20")
    # Pattern: finds something like "1:201:20" and extracts "1:20"
    match = re.search(r'^(\d+):(\d{2})(\d+):(\d{2})$', time_str)
    if match:
        # It's duplicated: "H:MM" is repeated
        return f"{match.group(1)}:{match.group(2)}"
    
    # Fix other duplication patterns like "2:082:08"
    match = re.search(r'^(\d+):(\d{2,})(\d+):(\d{2})$', time_str)
    if match:
        # Take the last occurrence
        return f"{match.group(3)}:{match.group(4)}"
    
    # If it contains invalid characters, return None
    if not re.match(r'^[\d:]+$', time_str):
        return None
    
    return time_str

race_results['Time_clean'] = race_results['Time'].apply(clean_time)
print(f"\nTime cleaning: {race_results['Time_clean'].notna().sum()}/{len(race_results)} valid times")

# ============================================================================
# CLEAN DATE COLUMN
# ============================================================================
# Convert dates - handle "17 January 2012" format
race_results['Date_clean'] = pd.to_datetime(race_results['Date'], format='%d %B %Y', errors='coerce')

print(f"Date parsing: {race_results['Date_clean'].notna().sum()}/{len(race_results)} valid dates")

# For rows with missing dates, try to infer from Race_ID and Stage_Number
# Group by Race_ID and find the date pattern
def fill_missing_dates(df):
    """Fill missing dates by interpolating from race context"""
    df = df.copy()
    
    # For each race, if some stages have dates, fill missing ones
    for race_id in df['Race_ID'].unique():
        race_mask = df['Race_ID'] == race_id
        race_dates = df.loc[race_mask, 'Date_clean'].dropna()
        
        if len(race_dates) > 0:
            # Get the earliest date for this race
            min_date = race_dates.min()
            
            # Fill missing dates based on Stage_Number
            missing_mask = race_mask & df['Date_clean'].isna()
            if missing_mask.any():
                # Use the min date as a baseline
                df.loc[missing_mask, 'Date_clean'] = min_date
    
    return df

race_results = fill_missing_dates(race_results)
print(f"After date filling: {race_results['Date_clean'].notna().sum()}/{len(race_results)} valid dates")

# Replace original columns
race_results['Date'] = race_results['Date_clean']
race_results['Time'] = race_results['Time_clean']
race_results = race_results.drop(columns=['Date_clean', 'Time_clean'])

# ============================================================================
# FILTER AND CLEAN
# ============================================================================
# Filter out classification summaries
classification_keywords = ['classification', 'standings', 'overall', 'general']
mask = race_results['Stage_Name'].str.lower().str.contains('|'.join(classification_keywords), na=False)

print(f"\nRows with classification summaries: {mask.sum()}")
race_results = race_results[~mask].copy()
print(f"Shape after filtering: {race_results.shape}")

# Clean Rank Column
def clean_rank(rank):
    try:
        return int(rank)
    except (ValueError, TypeError):
        return 999

race_results['Rnk_clean'] = race_results['Rnk'].apply(clean_rank)
race_results['is_top_10'] = (race_results['Rnk_clean'] <= 10).astype(int)

print(f"Top 10 finishes: {race_results['is_top_10'].sum()} ({race_results['is_top_10'].mean()*100:.2f}%)")

# Clean Length Column
race_results['Length_km'] = race_results['Length'].str.replace('km', '').str.strip()
race_results['Length_km'] = pd.to_numeric(race_results['Length_km'], errors='coerce')

# ============================================================================
# PARSE RIDER INFO (pps and rdr)
# ============================================================================
def parse_dict(cell):
    if pd.isna(cell) or not isinstance(cell, str) or not cell.strip():
        return {}
    try:
        return ast.literal_eval(cell)
    except Exception:
        return {}

rider_infos['pps_parsed'] = rider_infos['pps'].apply(parse_dict)
pps_expanded = rider_infos['pps_parsed'].apply(pd.Series)
pps_expanded.columns = [f"pps_{col}" for col in pps_expanded.columns]

rider_infos['rdr_parsed'] = rider_infos['rdr'].apply(parse_dict)
rdr_expanded = rider_infos['rdr_parsed'].apply(pd.Series)
rdr_expanded.columns = [f"rdr_{col}" for col in rdr_expanded.columns]

rider_infos_expanded = pd.concat([rider_infos, pps_expanded, rdr_expanded], axis=1)

print(f"Expanded rider info columns: {rider_infos_expanded.shape[1]}")

# ============================================================================
# UCI AND PNT FEATURES
# ============================================================================
race_results['has_uci_points'] = race_results['UCI'].notna().astype(int)
race_results['has_race_points'] = race_results['Pnt'].notna().astype(int)

race_results['UCI_filled'] = race_results['UCI'].fillna(0)

uci_agg = race_results.groupby('Rider').agg({
    'UCI_filled': ['sum', 'mean', 'max', 'std'],
    'has_uci_points': 'sum'
}).reset_index()

uci_agg.columns = ['Rider', 'UCI_total', 'UCI_avg', 'UCI_max', 'UCI_std', 'UCI_race_count']
uci_agg['UCI_elite_status'] = (uci_agg['UCI_race_count'] > 0).astype(int)
uci_agg['UCI_points_per_race'] = uci_agg['UCI_total'] / uci_agg['UCI_race_count']
uci_agg['UCI_points_per_race'] = uci_agg['UCI_points_per_race'].fillna(0)

# Pnt aggregation
race_results['Pnt_filled'] = race_results['Pnt'].fillna(0)

pnt_agg = race_results.groupby('Rider').agg({
    'Pnt_filled': ['sum', 'mean', 'max', 'std'],
    'has_race_points': 'sum'
}).reset_index()

pnt_agg.columns = ['Rider', 'Pnt_total', 'Pnt_avg', 'Pnt_max', 'Pnt_std', 'Pnt_race_count']
pnt_agg['Pnt_points_per_race'] = pnt_agg['Pnt_total'] / pnt_agg['Pnt_race_count']
pnt_agg['Pnt_points_per_race'] = pnt_agg['Pnt_points_per_race'].fillna(0)

# ============================================================================
# DATE FEATURES
# ============================================================================
rider_infos_expanded['birthdate'] = pd.to_datetime(rider_infos_expanded['birthdate'], errors='coerce')

race_results['race_year'] = race_results['Date'].dt.year
race_results['race_month'] = race_results['Date'].dt.month
race_results['race_day_of_week'] = race_results['Date'].dt.dayofweek

# Fill missing date features with median (more robust than mode for sparse data)
race_results['race_year'] = race_results['race_year'].fillna(race_results['race_year'].median())
race_results['race_month'] = race_results['race_month'].fillna(race_results['race_month'].median())
race_results['race_day_of_week'] = race_results['race_day_of_week'].fillna(race_results['race_day_of_week'].median())

print(f"\nDate missing after processing: {race_results['Date'].isna().sum()} rows ({race_results['Date'].isna().sum()/len(race_results)*100:.1f}%)")

# ============================================================================
# IMPROVED MERGE
# ============================================================================
# Clean rider names for better matching
race_results['Rider_clean'] = race_results['Rider'].str.strip().str.upper()
rider_infos_expanded['fullname_clean'] = rider_infos_expanded['fullname'].str.strip().str.upper()

df = race_results.merge(
    rider_infos_expanded[['fullname', 'fullname_clean', 'birthdate', 'country', 'height', 'weight'] + 
                         list(pps_expanded.columns) + list(rdr_expanded.columns)],
    left_on='Rider_clean',
    right_on='fullname_clean',
    how='left'
)

print(f"\nAfter merge: {df['birthdate'].notna().sum()}/{len(df)} rows matched ({df['birthdate'].notna().sum()/len(df)*100:.1f}%)")

# Calculate median physical stats by Age group
age_medians = df.groupby('Age').agg({
    'height': 'median',
    'weight': 'median'
}).add_suffix('_age_median')

df = df.merge(age_medians, left_on='Age', right_index=True, how='left')

# Fill missing physical stats
df['height'] = df['height'].fillna(df['height_age_median']).fillna(df['height'].median())
df['weight'] = df['weight'].fillna(df['weight_age_median']).fillna(df['weight'].median())

# Fill pps and rdr with 0
pps_cols = list(pps_expanded.columns)
rdr_cols = list(rdr_expanded.columns)

for col in pps_cols + rdr_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Merge aggregations
df = df.merge(uci_agg, on='Rider', how='left')
df = df.merge(pnt_agg, on='Rider', how='left')

print(f"Merged dataset shape: {df.shape}")

# ============================================================================
# AGE AT RACE
# ============================================================================
mask = df['Date'].notna() & df['birthdate'].notna()
df.loc[mask, 'age_at_race'] = (df.loc[mask, 'Date'] - df.loc[mask, 'birthdate']).dt.days / 365.25
df['age_at_race'] = df['age_at_race'].fillna(df['Age'])

# ============================================================================
# RACE TIER
# ============================================================================
grand_tours = ['Tour de France', 'Giro d\'Italia', 'Vuelta a España', 'La Vuelta ciclista a España']

df['race_tier'] = 3
df.loc[df['Race_Name'].isin(grand_tours), 'race_tier'] = 1
df.loc[df['has_uci_points'] == 1, 'race_tier'] = df.loc[df['has_uci_points'] == 1, 'race_tier'].apply(
    lambda x: 2 if x == 3 else x
)

# ============================================================================
# ROLLING PERFORMANCE
# ============================================================================
df = df.sort_values(['Rider', 'Date']).reset_index(drop=True)

df['rolling_avg_rank_5'] = df.groupby('Rider')['Rnk_clean'].transform(
    lambda x: x.rolling(window=5, min_periods=1).mean()
)

df['rolling_avg_rank_10'] = df.groupby('Rider')['Rnk_clean'].transform(
    lambda x: x.rolling(window=10, min_periods=1).mean()
)

df['recent_top10_count'] = df.groupby('Rider')['is_top_10'].transform(
    lambda x: x.rolling(window=10, min_periods=1).sum()
)

df['recent_top10_rate'] = df['recent_top10_count'] / 10

print("Rolling performance metrics created!")

# ============================================================================
# DROP UNNECESSARY COLUMNS
# ============================================================================
cols_to_drop = [
    'id', 'Circuit', 'Category',
    'Race_url', 'Stage_url', 'rider_id',
    'Rnk', 'Length',
    'BiB', 'GC',
    'fullname', 'Unnamed: 0', 'Rider_clean', 'fullname_clean',
    'height_age_median', 'weight_age_median',
    'UCI', 'Pnt'
]

cols_to_drop = [col for col in cols_to_drop if col in df.columns]
df_clean = df.drop(columns=cols_to_drop)

print(f"\nFinal dataset shape: {df_clean.shape}")

# ============================================================================
# FINAL QUALITY CHECK
# ============================================================================
missing_pct = (df_clean.isnull().sum() / len(df_clean) * 100).sort_values(ascending=False)
missing_pct = missing_pct[missing_pct > 0]

print("\n" + "="*60)
print("MISSING VALUES SUMMARY")
print("="*60)
if len(missing_pct) > 0:
    print(missing_pct)
else:
    print("✅ No missing values!")

print("\n" + "="*60)
print("DATASET SUMMARY")
print("="*60)
print(f"Total records: {len(df_clean):,}")
print(f"Unique riders: {df_clean['Rider'].nunique()}")
print(f"Unique races: {df_clean['Race_Name'].nunique()}")
print(f"Date range: {df_clean['Date'].min()} to {df_clean['Date'].max()}")
print(f"\nTarget variable distribution:")
print(df_clean['is_top_10'].value_counts())

# Save
import os
os.makedirs('processed_data', exist_ok=True)
output_path = 'processed_data/race_data_processed.csv'
df_clean.to_csv(output_path, index=False)
print(f"\n Processed data saved to: {output_path}")
