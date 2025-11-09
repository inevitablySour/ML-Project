# =========================
# ENHANCED DATA PROCESSING
# Tier 1 & Tier 2 Feature Engineering
# =========================
import pandas as pd
import numpy as np
import sqlite3
import ast
import re
import os
from datetime import datetime
from pathlib import Path

# Get script directory and project root
script_dir = Path(__file__).parent
phase2_dir = script_dir.parent
project_root = phase2_dir.parent.parent

# Paths to data files
db_path = project_root / "data" / "cycling_big.db"
rider_infos_path = project_root / "data" / "data" / "rider_infos.csv"

# =========================
# 1. LOAD DATA
# =========================
print("="*70)
print("ENHANCED DATA PROCESSING WITH FEATURE ENGINEERING")
print("="*70)
print("\n[1/10] Loading raw data...")

conn = sqlite3.connect(db_path)
race_results = pd.read_sql_query("SELECT * FROM race_results", conn)
conn.close()

rider_infos = pd.read_csv(rider_infos_path)

print(f"   Race Results Shape: {race_results.shape}")
print(f"   Rider Info Shape: {rider_infos.shape}")

# =========================
# 2. CLEAN TIME
# =========================
print("\n[2/10] Cleaning time format...")

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
# 3. CLEAN DATE
# =========================
print("\n[3/10] Cleaning date format...")

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
# 4. FILTER CLASSIFICATION STAGES
# =========================
print("\n[4/10] Filtering classification stages...")

classification_keywords = ['classification', 'standings', 'overall', 'general']
mask = race_results['Stage_Name'].str.lower().str.contains('|'.join(classification_keywords), na=False)
race_results = race_results[~mask].copy()

# =========================
# 5. CLEAN RANK
# =========================
print("\n[5/10] Cleaning rank...")

def clean_rank(rank):
    try:
        return int(rank)
    except (ValueError, TypeError):
        return 999

race_results['Rnk_clean'] = race_results['Rnk'].apply(clean_rank)
race_results['is_top_10'] = (race_results['Rnk_clean'] <= 10).astype(int)

# =========================
# 6. CLEAN LENGTH
# =========================
print("\n[6/10] Cleaning length...")

race_results['Length_km'] = pd.to_numeric(race_results['Length'].str.replace('km','').str.strip(), errors='coerce')

# =========================
# 7. PARSE RIDER INFO
# =========================
print("\n[7/10] Parsing rider specialization scores...")

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
# 8. UCI & PNT AGGREGATIONS
# =========================
print("\n[8/10] Creating historical aggregations (UCI & Pnt)...")

race_results['UCI_filled'] = race_results['UCI'].fillna(0)
race_results['Pnt_filled'] = race_results['Pnt'].fillna(0)
race_results['has_uci_points'] = race_results['UCI'].notna().astype(int)

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
# 9. MERGE RACE + RIDER INFO
# =========================
print("\n[9/10] Merging race results with rider information...")

rider_infos_expanded['birthdate'] = pd.to_datetime(rider_infos_expanded['birthdate'], errors='coerce')
race_results['Rider_clean'] = race_results['Rider'].str.strip().str.upper()
rider_infos_expanded['fullname_clean'] = rider_infos_expanded['fullname'].str.strip().str.upper()

df = race_results.merge(
    rider_infos_expanded[['fullname_clean','birthdate','country','height','weight'] + 
                         list(pps_expanded.columns) + list(rdr_expanded.columns)],
    left_on='Rider_clean', right_on='fullname_clean', how='left'
)

# =========================
# 10. IMPUTE HEIGHT/WEIGHT
# =========================
print("\n[10/10] Feature engineering...")

df['height_imputed'] = False
df['weight_imputed'] = False

age_medians = df.groupby('Age')[['height','weight']].median()
df = df.merge(age_medians.add_suffix('_age_median'), left_on='Age', right_index=True, how='left')

for col, median_col, flag in [('height','height_age_median','height_imputed'), 
                              ('weight','weight_age_median','weight_imputed')]:
    missing_mask = df[col].isna() | (df[col]==0)
    df.loc[missing_mask, col] = df.loc[missing_mask, median_col].fillna(df[col].median())
    df.loc[missing_mask, flag] = True

df['height'] = df['height'].clip(1.5,2.1)
df['weight'] = df['weight'].clip(50,100)

# =========================
# ENSURE NUMERIC PPS/RDR
# =========================
for col in list(pps_expanded.columns) + list(rdr_expanded.columns):
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)

# =========================
# MERGE AGGREGATIONS
# =========================
df = df.merge(uci_agg, on='Rider', how='left')
df = df.merge(pnt_agg, on='Rider', how='left')

# =========================
# AGE AT RACE
# =========================
mask = df['Date'].notna() & df['birthdate'].notna()
df.loc[mask,'age_at_race'] = (df.loc[mask,'Date'] - df.loc[mask,'birthdate']).dt.days/365.25
df['age_at_race'] = df['age_at_race'].fillna(df['Age'])

# =========================
# DROP DUPLICATES
# =========================
before = len(df)
df = df.sort_values(['Rider','Date']).drop_duplicates(subset=['Rider','Race_ID','Stage_Number'], keep='first')
print(f"   Dropped {before-len(df)} duplicate Rider/Stage rows")

# =========================
# RACE TIER & ROLLING METRICS
# =========================
grand_tours = ['Tour de France','Giro d\'Italia','Vuelta a España','La Vuelta ciclista a España']
df['race_tier'] = 3
df.loc[df['Race_Name'].isin(grand_tours),'race_tier'] = 1
df.loc[df['has_uci_points']==1,'race_tier'] = df.loc[df['has_uci_points']==1,'race_tier'].apply(lambda x: 2 if x==3 else x)

df = df.sort_values(['Rider','Date']).reset_index(drop=True)

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

df['rolling_avg_rank_5'] = df['rolling_avg_rank_5'].fillna(df['Rnk_clean'].median())
df['rolling_avg_rank_10'] = df['rolling_avg_rank_10'].fillna(df['Rnk_clean'].median())
df['recent_top10_count'] = df['recent_top10_count'].fillna(0)
df['recent_top10_rate'] = df['recent_top10_rate'].fillna(0)

# ============================================================================
# TIER 1 FEATURES: Peak Age Indicators
# ============================================================================
print("\n   Adding Tier 1 features: Peak age indicators...")

PEAK_AGE = 27.3
df['age_to_peak'] = (df['age_at_race'] - PEAK_AGE).abs()
df['is_peak_age'] = ((df['age_at_race'] >= 26) & (df['age_at_race'] <= 29)).astype(int)
df['years_past_peak'] = (df['age_at_race'] - PEAK_AGE).clip(lower=0)

# ============================================================================
# TIER 1 FEATURES: Physical Indicators (BMI & Physique)
# ============================================================================
print("   Adding Tier 1 features: Physical indicators...")

df['BMI'] = df['weight'] / (df['height'] ** 2)
df['weight_per_height'] = df['weight'] / df['height']

# Z-scores for physical attributes
df['height_zscore'] = (df['height'] - df['height'].mean()) / df['height'].std()
df['weight_zscore'] = (df['weight'] - df['weight'].mean()) / df['weight'].std()
df['bmi_zscore'] = (df['BMI'] - df['BMI'].mean()) / df['BMI'].std()

# ============================================================================
# TIER 1 FEATURES: Stage-Type Specialization
# ============================================================================
print("   Adding Tier 1 features: Stage-type specialization...")

for stage_type in ['RR', 'ITT']:
    stage_mask = df['Stage_Type'] == stage_type
    stage_data = df[stage_mask].groupby('Rider').agg({
        'is_top_10': ['sum', 'count']
    }).reset_index()
    stage_data.columns = ['Rider', f'{stage_type}_top10_count', f'{stage_type}_total_races']
    stage_data[f'{stage_type}_success_rate'] = (
        stage_data[f'{stage_type}_top10_count'] / 
        stage_data[f'{stage_type}_total_races'].replace(0, np.nan)
    ).fillna(0)
    
    # Ensure 'Rider' column has consistent data type across both dataframes
    df['Rider'] = df['Rider'].astype(str)
    stage_data['Rider'] = stage_data['Rider'].astype(str)

    df = df.merge(stage_data[['Rider', f'{stage_type}_success_rate']], 
                  on='Rider', how='left')
    df[f'{stage_type}_success_rate'] = df[f'{stage_type}_success_rate'].fillna(0)

df['rr_specialist'] = (df['RR_success_rate'] > df['ITT_success_rate']).astype(int)
df['itt_specialist'] = (df['ITT_success_rate'] > df['RR_success_rate']).astype(int)

# ============================================================================
# TIER 1 FEATURES: Team Context
# ============================================================================
print("   Adding Tier 1 features: Team context...")

team_top10_rate = df.groupby('Team')['is_top_10'].mean()
df['team_top10_rate'] = df['Team'].map(team_top10_rate)
df['team_top10_rate'] = df['team_top10_rate'].fillna(df['is_top_10'].mean())

team_median_rank = df.groupby('Team')['Rnk_clean'].median()
df['team_median_rank'] = df['Team'].map(team_median_rank)
df['team_median_rank'] = df['team_median_rank'].fillna(df['Rnk_clean'].median())

# ============================================================================
# TIER 1 FEATURES: Country Context
# ============================================================================
print("   Adding Tier 1 features: Country context...")

country_top10_rate = df.groupby('country')['is_top_10'].mean()
df['country_top10_rate'] = df['country'].map(country_top10_rate)
df['country_top10_rate'] = df['country_top10_rate'].fillna(df['is_top_10'].mean())

country_avg_rank = df.groupby('country')['rolling_avg_rank_5'].median()
df['country_cycling_strength'] = df['country'].map(country_avg_rank)
df['country_cycling_strength'] = df['country_cycling_strength'].fillna(df['rolling_avg_rank_5'].median())

# ============================================================================
# TIER 1 FEATURES: Seasonal Indicators
# ============================================================================
print("   Adding Tier 1 features: Seasonal indicators...")

df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['race_month'] = df['Date'].dt.month
df['race_quarter'] = df['Date'].dt.quarter
df['is_spring_classics'] = df['race_month'].isin([3, 4]).astype(int)
df['is_grand_tour_season'] = df['race_month'].isin([5, 7, 8, 9]).astype(int)
df['is_winter'] = df['race_month'].isin([11, 12, 1]).astype(int)

# ============================================================================
# TIER 2 FEATURES: Performance Trend Detection
# ============================================================================
print("   Adding Tier 2 features: Performance trends...")

def calculate_trend(series):
    """Calculate slope of rank over last 20 races (negative = improving)"""
    if len(series) < 3:
        return 0
    recent_ranks = series.tail(20).values
    x = np.arange(len(recent_ranks))
    try:
        slope = np.polyfit(x, recent_ranks, 1)[0]
        return slope
    except:
        return 0

df['rank_trend_slope'] = df.groupby('Rider')['rolling_avg_rank_5'].transform(calculate_trend)

# Recent consistency (variance in rank)
df['recent_rank_variance'] = df.groupby('Rider')['rolling_avg_rank_10'].transform(
    lambda x: x.shift(1).rolling(10).std()
).fillna(0)

# Career duration
df['days_in_career'] = df.groupby('Rider')['Date'].transform(
    lambda x: (x - x.min()).dt.days
)
df['career_years'] = df['days_in_career'] / 365.25

# ============================================================================
# TIER 2 FEATURES: Race Difficulty Context
# ============================================================================
print("   Adding Tier 2 features: Race difficulty context...")

elite_threshold = df['rolling_avg_rank_5'].quantile(0.25)
df['is_elite_rider'] = (df['rolling_avg_rank_5'] <= elite_threshold).astype(int)

df['race_elite_count'] = df.groupby(['Race_ID', 'Date'])['is_elite_rider'].transform('sum')

elite_sum_per_group = df.groupby(['Race_ID', 'Date'])['is_elite_rider'].transform('sum')
total_riders_per_group = df.groupby(['Race_ID', 'Date'])['Rider'].transform('count')
df['race_difficulty_score'] = (elite_sum_per_group / total_riders_per_group).fillna(0)

# ============================================================================
# DROP UNNECESSARY COLUMNS & DATA LEAKAGE FEATURES
# ============================================================================
print("\n   Dropping unnecessary columns and data leakage features...")

cols_to_drop = ['id','Circuit','Category','Race_url','Stage_url','rider_id','Rnk','Length',
                'BiB','GC','fullname','Rider_clean','fullname_clean','height_age_median','weight_age_median',
                'UCI','Pnt',
                'has_uci_points',
                'UCI_filled',
                'Pnt_filled',
                'pps_parsed','rdr_parsed']

cols_to_drop = [c for c in cols_to_drop if c in df.columns]
df_clean = df.drop(columns=cols_to_drop)

# ============================================================================
# FINAL CHECKS
# ============================================================================
print("\n   Checking for missing values...")

missing_pct = (df_clean.isnull().sum()/len(df_clean)*100).sort_values(ascending=False)
missing_pct = missing_pct[missing_pct>0]
if len(missing_pct)>0:
    print("   Missing values summary:")
    print(missing_pct)
else:
    print("   No missing values!")

print(f"\n   Final shape: {df_clean.shape}")
print(f"   Total records: {len(df_clean):,}")
print(f"   Unique riders: {df_clean['Rider'].nunique()}")
print(f"   Unique races: {df_clean['Race_Name'].nunique()}")
print(f"   Date range: {df_clean['Date'].min()} to {df_clean['Date'].max()}")

# ============================================================================
# SAVE PROCESSED DATA
# ============================================================================
print("\n   Saving processed data...")

output_dir = phase2_dir / 'processed_data'
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / 'race_data_processed_enhanced.csv'
df_clean.to_csv(output_path, index=False)
print(f"✓ Processed data saved to: {output_path}")

print("\n" + "="*70)
print("FEATURE ENGINEERING SUMMARY")
print("="*70)
print("""
Tier 1 Features Added (23 total):
  Peak Age (3): age_to_peak, is_peak_age, years_past_peak
  Physical (5): BMI, weight_per_height, height_zscore, weight_zscore, bmi_zscore
  Stage Specialization (4): RR_success_rate, ITT_success_rate, rr_specialist, itt_specialist
  Team Context (2): team_top10_rate, team_median_rank
  Country Context (2): country_top10_rate, country_cycling_strength
  Seasonal (5): race_month, race_quarter, is_spring_classics, is_grand_tour_season, is_winter
  Career (2): days_in_career, career_years

Tier 2 Features Added (5 total):
  Performance Trends (2): rank_trend_slope, recent_rank_variance
  Race Difficulty (3): is_elite_rider, race_elite_count, race_difficulty_score

""")
print("="*70)
print("="*70)
