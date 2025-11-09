"""
ML Preprocessing Pipeline
Prepares race_data_processed.csv for machine learning model training
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("ML PREPROCESSING PIPELINE")
print("="*70)

# Get paths relative to script location
script_dir = Path(__file__).parent
phase2_dir = script_dir.parent

# ============================================================================
# DATASET SELECTION
# ============================================================================
print("\nWhich dataset would you like to use?")
print("  1) Original (race_data_processed.csv)")
print("  2) Enhanced with new features (race_data_processed_enhanced.csv)")

choice = input("\nEnter your choice (1 or 2): ").strip()

if choice == "2":
    dataset_name = 'race_data_processed_enhanced.csv'
    print("\n✓ Using ENHANCED dataset with Tier 1-2 features")
else:
    dataset_name = 'race_data_processed.csv'
    print("\n✓ Using ORIGINAL dataset")

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("\n[1/7] Loading processed data...")
input_path = phase2_dir / 'processed_data' / dataset_name
df = pd.read_csv(input_path)
print(f"   Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")

initial_rows = len(df)

# ============================================================================
# 2. HANDLE MISSING VALUES
# ============================================================================
print("\n[2/7] Handling missing values...")

# Drop columns with high missingness that aren't critical
cols_to_drop_missing = ['birthdate', 'Timelag', 'Time']
df = df.drop(columns=[col for col in cols_to_drop_missing if col in df.columns])
print(f"   Dropped high-missingness columns: {cols_to_drop_missing}")

# Drop rows with missing target or Date (critical for modeling)
df = df.dropna(subset=['is_top_10'])
print(f"   Dropped rows with missing target")

# Fill remaining missing values
if 'Date' in df.columns:
    # For remaining Date nulls, drop those rows (can't train without temporal context)
    df = df.dropna(subset=['Date'])

if 'country' in df.columns:
    df['country'] = df['country'].fillna('Unknown')

if 'Team' in df.columns:
    df['Team'] = df['Team'].fillna('Unknown')

if 'Stage_Name' in df.columns:
    df['Stage_Name'] = df['Stage_Name'].fillna('Unknown')

# Fill numeric columns with median
numeric_cols = df.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    if df[col].isnull().any():
        df[col] = df[col].fillna(df[col].median())

print(f"   Rows after cleaning: {len(df):,} (lost {initial_rows - len(df):,})")
print(f"   Remaining missing: {df.isnull().sum().sum()}")

# ============================================================================
# 3. DROP NON-PREDICTIVE COLUMNS & DATA LEAKAGE FEATURES
# ============================================================================
print("\n[3/7] Dropping non-predictive columns and data leakage features...")

# CRITICAL: Save Date column for temporal split BEFORE dropping
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    temporal_split_date = df['Date'].quantile(0.8)  # 80/20 split by date
    print(f"   Temporal split date: {temporal_split_date.date()}")
else:
    temporal_split_date = None
    print("   WARNING: No Date column found, will use random split")

# Drop ID columns, URLs, and high-cardinality text that won't generalize
cols_to_drop = [
    'Rider',           # Too many unique riders (2107) - would overfit
    'Date',            # Used for temporal split, not a feature (will be dropped later)
    'Start',           # Too many unique locations
    'Finish',          # Too many unique locations
    'Stage_Name',      # Too many unique stage names
    'Race_ID',         # Just an ID
    'Stage_Number',    # Already captured in other features
    'Rnk_clean',       # This is derived from target - would be data leakage
    
    # DATA LEAKAGE: Points awarded AFTER race based on finish position
    'Pnt_total',       # Includes current race points (LEAKAGE!)
    'Pnt_max',         # Includes current race points (LEAKAGE!)
    'Pnt_std',         # Standard deviation includes current race (LEAKAGE!)
]

# Don't drop Date yet - we need it for temporal split
cols_to_drop_now = [col for col in cols_to_drop if col in df.columns and col != 'Date']
leakage_cols = ['Pnt_total', 'Pnt_max', 'Pnt_std']
leakage_found = [col for col in leakage_cols if col in df.columns]

df_features = df.drop(columns=cols_to_drop_now)

if leakage_found:
    print(f"   Removed DATA LEAKAGE features: {leakage_found}")
print(f"   Dropped other columns: {[c for c in cols_to_drop_now if c not in leakage_found]}")
print(f"   Remaining columns: {df_features.shape[1]} (Date kept for temporal split)")
print(f"\n   Kept historical Pnt features (no leakage):")
historical_pnt = [c for c in df_features.columns if 'Pnt' in c or 'pnt' in c]
if historical_pnt:
    print(f"      {historical_pnt}")
else:
    print(f"      None (all Pnt features removed)")

# ============================================================================
# 4. ENCODE CATEGORICAL VARIABLES
# ============================================================================
print("\n[4/7] Encoding categorical variables...")

# Separate target before encoding
y = df_features['is_top_10'].copy()
X = df_features.drop('is_top_10', axis=1)

# One-hot encode low cardinality categoricals
low_cardinality_cols = []
for col in X.select_dtypes(include='object').columns:
    if X[col].nunique() <= 10:  # Threshold for one-hot
        low_cardinality_cols.append(col)

if low_cardinality_cols:
    print(f"   One-hot encoding: {low_cardinality_cols}")
    X = pd.get_dummies(X, columns=low_cardinality_cols, drop_first=True)

# Target encode medium cardinality (Team, Race_Name)
medium_cardinality_cols = []
for col in X.select_dtypes(include='object').columns:
    if X[col].nunique() > 10:  # Higher cardinality
        medium_cardinality_cols.append(col)

if medium_cardinality_cols:
    print(f"   Target encoding: {medium_cardinality_cols}")
    for col in medium_cardinality_cols:
        # Calculate mean target for each category
        encoding_map = df_features.groupby(col)['is_top_10'].mean().to_dict()
        X[col + '_encoded'] = X[col].map(encoding_map)
        # Fill unseen categories with global mean
        X[col + '_encoded'] = X[col + '_encoded'].fillna(y.mean())
        X = X.drop(columns=[col])

print(f"   Final feature count: {X.shape[1]}")

# Convert boolean columns to int
bool_cols = X.select_dtypes(include='bool').columns
if len(bool_cols) > 0:
    X[bool_cols] = X[bool_cols].astype(int)

# ============================================================================
# 5. TRAIN/TEST SPLIT (TEMPORAL SPLIT - NO RANDOM SHUFFLE)
# ============================================================================
print("\n[5/7] Splitting into train/test sets (TEMPORAL)...")

if temporal_split_date is not None:
    # TEMPORAL SPLIT: Train on earlier data, test on later data
    train_mask = df['Date'] < temporal_split_date
    test_mask = df['Date'] >= temporal_split_date
    
    X_train = X[train_mask].copy()
    X_test = X[test_mask].copy()
    y_train = y[train_mask].copy()
    y_test = y[test_mask].copy()
    
    # NOW drop Date from features (not needed for modeling)
    if 'Date' in X_train.columns:
        X_train = X_train.drop(columns=['Date'])
        X_test = X_test.drop(columns=['Date'])
    
    print(f"   ✓ Using TEMPORAL split (prevents look-ahead bias)")
    print(f"   Train: races before {temporal_split_date.date()}")
    print(f"   Test:  races on/after {temporal_split_date.date()}")
else:
    # Fallback to stratified random split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    print(f"   ⚠️  Using RANDOM split (Date column not available)")

print(f"   Train set: {len(X_train):,} samples")
print(f"   Test set:  {len(X_test):,} samples")
print(f"   Train positive class: {y_train.mean()*100:.2f}%")
print(f"   Test positive class: {y_test.mean()*100:.2f}%")

# ============================================================================
# 6. HANDLE CLASS IMBALANCE - SKIPPED (use class_weight instead)
# ============================================================================
print("\n[6/7] Class imbalance handling...")

print(f"   Train distribution (keeping natural imbalance):")
print(f"      Class 0: {(y_train==0).sum():,} ({(y_train==0).sum()/len(y_train)*100:.1f}%)")
print(f"      Class 1: {(y_train==1).sum():,} ({(y_train==1).sum()/len(y_train)*100:.1f}%)")

# Don't use SMOTE - it creates distribution mismatch with test set
# Instead, rely on class_weight='balanced' in models
X_train_balanced = X_train
y_train_balanced = y_train

print(f"   ℹ️  Not using SMOTE - models will use class_weight='balanced' instead")
print(f"   This ensures train/test distribution match for better generalization")

# ============================================================================
# 7. FEATURE SCALING
# ============================================================================
print("\n[7/7] Scaling features (StandardScaler)...")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_balanced)
X_test_scaled = scaler.transform(X_test)

# Convert back to DataFrames for easier handling
X_train_scaled = pd.DataFrame(
    X_train_scaled,
    columns=X_train.columns,
    index=range(len(X_train_scaled))
)
X_test_scaled = pd.DataFrame(
    X_test_scaled,
    columns=X_test.columns,
    index=range(len(X_test_scaled))
)

print(f"   Features scaled to mean=0, std=1")

# ============================================================================
# 8. SAVE PROCESSED DATA
# ============================================================================
print("\n" + "="*70)
print("SAVING ML-READY DATA")
print("="*70)

import joblib

# Create output directory
output_dir = phase2_dir / 'training_data'
output_dir.mkdir(parents=True, exist_ok=True)

# Determine suffix for file names
file_suffix = '_enhanced' if 'enhanced' in dataset_name else ''

# Save train set (balanced and scaled)
X_train_scaled['is_top_10'] = y_train_balanced.values
train_path = output_dir / f'train_data{file_suffix}.csv'
X_train_scaled.to_csv(train_path, index=False)
print(f"Saved: {train_path} ({len(X_train_scaled):,} rows)")

# Save test set (scaled, NOT balanced)
X_test_scaled['is_top_10'] = y_test.values
test_path = output_dir / f'test_data{file_suffix}.csv'
X_test_scaled.to_csv(test_path, index=False)
print(f"Saved: {test_path} ({len(X_test_scaled):,} rows)")

# Save feature names
feature_names = X_train.columns.tolist()
features_path = output_dir / f'feature_names{file_suffix}.csv'
pd.DataFrame({'feature': feature_names}).to_csv(features_path, index=False)
print(f"Saved: {features_path} ({len(feature_names)} features)")

# Save scaler for future use
scaler_path = output_dir / 'scaler.pkl'
joblib.dump(scaler, scaler_path)
print(f"Saved: {scaler_path}")

# Save dataset info
dataset_info_path = output_dir / 'dataset_info.txt'
with open(dataset_info_path, 'w') as f:
    f.write(f"Dataset Used: {dataset_name}\n")
    f.write(f"Timestamp: {pd.Timestamp.now()}\n")
    f.write(f"Total Features: {len(feature_names)}\n")
print(f"Saved: {dataset_info_path}")

# ============================================================================
# 9. SUMMARY REPORT
# ============================================================================
print("\n" + "="*70)
print("FINAL SUMMARY")
print("="*70)
print(f"""
Training Data (NATURAL IMBALANCE):
  • Samples: {len(X_train_scaled):,}
  • Features: {len(feature_names)}
  • Positive class: {(y_train_balanced==1).sum():,} ({(y_train_balanced==1).sum()/len(y_train_balanced)*100:.1f}%)
  • Negative class: {(y_train_balanced==0).sum():,} ({(y_train_balanced==0).sum()/len(y_train_balanced)*100:.1f}%)

Test Data (ORIGINAL DISTRIBUTION):
  • Samples: {len(X_test_scaled):,}
  • Features: {len(feature_names)}
  • Positive class: {(y_test==1).sum():,} ({(y_test==1).sum()/len(y_test)*100:.1f}%)
  • Negative class: {(y_test==0).sum():,} ({(y_test==0).sum()/len(y_test)*100:.1f}%)

Feature Types:
  • Numeric features: {len([f for f in feature_names if not f.endswith('_encoded')])}
  • Encoded features: {len([f for f in feature_names if f.endswith('_encoded')])}
  
DATA IS NOW READY FOR ML MODEL TRAINING!

Next Steps:
  1. Load train_data.csv for model training
  2. Use test_data.csv for final evaluation
  3. Try models: Logistic Regression, Random Forest, XGBoost, LightGBM
  4. Focus on Precision metric (minimize false positives for recruitment)
""")

print("="*70)
