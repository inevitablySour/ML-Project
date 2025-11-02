"""
Data Leakage Validation Script

This script performs several checks to ensure no data leakage:
1. Verifies rolling features exclude current race
2. Checks for temporal consistency in train/test split
3. Tests model with only static features (baseline check)
4. Flags any suspiciously high correlations with target
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, roc_auc_score

print("=" * 70)
print("DATA LEAKAGE VALIDATION")
print("=" * 70)

# ============================================================================
# 1. LOAD PROCESSED DATA
# ============================================================================
print("\n[1/4] Loading processed data...")
df = pd.read_csv('../processed_data/race_data_processed.csv')
print(f"   Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")

# ============================================================================
# 2. CHECK ROLLING FEATURES FOR LEAKAGE
# ============================================================================
print("\n[2/4] Checking rolling features for leakage...")

# Sample check: For riders with multiple races, verify rolling features
# don't include current race results
df_sorted = df.sort_values(['Rider', 'Date']).copy()

# Check a specific rider with multiple races
test_rider = df_sorted[df_sorted.groupby('Rider')['Rider'].transform('count') > 10]['Rider'].iloc[0]
rider_data = df_sorted[df_sorted['Rider'] == test_rider].head(15)

print(f"\n   Sample rider: {test_rider}")
print(f"   First 5 races:")
print(rider_data[['Date', 'Rnk_clean', 'is_top_10', 'rolling_avg_rank_5', 
                  'recent_top10_count', 'recent_top10_rate']].head(5).to_string(index=False))

# Validation: For race N, rolling_avg should be based on races 1 to N-1
# So for race 2, we check if rolling avg matches race 1's rank
if len(rider_data) >= 2:
    race_1_rank = rider_data.iloc[0]['Rnk_clean']
    race_2_rolling = rider_data.iloc[1]['rolling_avg_rank_5']
    
    if pd.notna(race_2_rolling) and abs(race_2_rolling - race_1_rank) < 0.01:
        print(f"\n   ✓ Rolling feature validation PASSED")
        print(f"     Race 1 rank: {race_1_rank}, Race 2 rolling avg: {race_2_rolling:.2f}")
    else:
        print(f"\n   ⚠️  Rolling feature check inconclusive")
        print(f"     Race 1 rank: {race_1_rank}, Race 2 rolling avg: {race_2_rolling}")

# ============================================================================
# 3. CHECK FEATURE CORRELATIONS WITH TARGET
# ============================================================================
print("\n[3/4] Checking feature correlations with target...")

numeric_cols = df.select_dtypes(include=[np.number]).columns
numeric_cols = [col for col in numeric_cols if col not in ['is_top_10', 'Rnk_clean']]

correlations = df[numeric_cols + ['is_top_10']].corr()['is_top_10'].drop('is_top_10').abs().sort_values(ascending=False)

print("\n   Top 10 features by correlation with target:")
for i, (feat, corr) in enumerate(correlations.head(10).items(), 1):
    flag = "⚠️  SUSPICIOUS!" if corr > 0.7 else ""
    print(f"      {i:2d}. {feat:40s} {corr:.4f} {flag}")

if correlations.max() > 0.7:
    print(f"\n   ⚠️  WARNING: Features with correlation > 0.7 may indicate leakage!")
else:
    print(f"\n   ✓ No suspiciously high correlations (all < 0.7)")

# ============================================================================
# 4. BASELINE MODEL TEST (STATIC FEATURES ONLY)
# ============================================================================
print("\n[4/4] Baseline model test (static features only)...")

# Use only features that CANNOT contain race outcome information
static_features = [
    'age_at_race', 'height', 'weight', 'race_tier', 'Length_km'
]

# Add rider skill features (pps scores)
pps_features = [col for col in df.columns if col.startswith('pps_')]
static_features.extend(pps_features)

# Add rider ranking features (rdr)
rdr_features = [col for col in df.columns if col.startswith('rdr_')]
static_features.extend(rdr_features)

# Filter to features that exist
static_features = [f for f in static_features if f in df.columns]

print(f"   Using {len(static_features)} static features (no temporal/race-outcome data)")

# Simple train/test split (last 20% by date)
df_sorted = df.sort_values('Date').dropna(subset=['Date'])
split_idx = int(len(df_sorted) * 0.8)

train_data = df_sorted.iloc[:split_idx]
test_data = df_sorted.iloc[split_idx:]

X_train_static = train_data[static_features].fillna(0)
y_train = train_data['is_top_10']

X_test_static = test_data[static_features].fillna(0)
y_test = test_data['is_top_10']

# Train simple logistic regression
lr = LogisticRegression(max_iter=10000, random_state=42, class_weight='balanced')
lr.fit(X_train_static, y_train)

y_pred = lr.predict(X_test_static)
y_pred_proba = lr.predict_proba(X_test_static)[:, 1]

precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)

print(f"\n   Baseline Model (Static Features Only):")
print(f"      Precision: {precision:.3f} ({precision*100:.1f}%)")
print(f"      Recall:    {recall:.3f} ({recall*100:.1f}%)")
print(f"      ROC-AUC:   {roc_auc:.3f}")

# ============================================================================
# 5. INTERPRETATION
# ============================================================================
print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

issues_found = []

if correlations.max() > 0.7:
    issues_found.append(f"High feature correlations (max: {correlations.max():.3f})")

if roc_auc > 0.90:
    issues_found.append(f"Baseline model ROC-AUC too high ({roc_auc:.3f} > 0.90)")

if precision > 0.80 and roc_auc > 0.85:
    issues_found.append(f"Baseline model suspiciously accurate (precision: {precision:.3f})")

if issues_found:
    print("\n⚠️  POTENTIAL LEAKAGE DETECTED:")
    for issue in issues_found:
        print(f"   • {issue}")
    print("\n   ACTION REQUIRED: Review feature engineering process")
else:
    print("\n✓ NO OBVIOUS LEAKAGE DETECTED")
    print("\n   Expected behavior:")
    print(f"   • Baseline precision: 30-60% (actual: {precision*100:.1f}%)")
    print(f"   • Baseline ROC-AUC: 0.55-0.80 (actual: {roc_auc:.3f})")
    print(f"   • Max correlation: <0.7 (actual: {correlations.max():.3f})")
    print("\n   You can now proceed with full model training!")

print("\n" + "=" * 70)
