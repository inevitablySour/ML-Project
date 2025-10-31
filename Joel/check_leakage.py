"""
Data Leakage Detection Script
Checks if Pnt_filled has data leakage with is_top_10 target
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("="*70)
print("DATA LEAKAGE CHECK: Pnt_filled vs is_top_10")
print("="*70)

# Load original processed data
df = pd.read_csv('original_processed/race_data_processed.csv')

print(f"\nDataset: {len(df):,} rows\n")

# ============================================================================
# 1. CORRELATION ANALYSIS
# ============================================================================
print("[1/5] Correlation Analysis")
print("-" * 70)

correlation = df[['Pnt_filled', 'is_top_10']].corr().iloc[0, 1]
print(f"Correlation (Pnt_filled vs is_top_10): {correlation:.4f}")

if correlation > 0.7:
    print("⚠️  HIGH CORRELATION - Strong potential for data leakage!")
elif correlation > 0.5:
    print("⚠️  MODERATE CORRELATION - Possible data leakage")
else:
    print("✓ Low correlation - Less concern for leakage")

# ============================================================================
# 2. DISTRIBUTION BY TARGET CLASS
# ============================================================================
print("\n[2/5] Pnt_filled Distribution by Target Class")
print("-" * 70)

grouped = df.groupby('is_top_10')['Pnt_filled'].agg(['mean', 'median', 'std', 'min', 'max'])
grouped.index = ['Not Top 10 (0)', 'Top 10 (1)']
print(grouped)

mean_ratio = grouped.loc['Top 10 (1)', 'mean'] / grouped.loc['Not Top 10 (0)', 'mean']
print(f"\nMean ratio (Top10/NotTop10): {mean_ratio:.2f}x")

if mean_ratio > 5:
    print("⚠️  Top 10 finishers have MUCH higher Pnt values - likely leakage!")
elif mean_ratio > 2:
    print("⚠️  Top 10 finishers have notably higher Pnt values")
else:
    print("✓ Similar distributions - less concern")

# ============================================================================
# 3. CHECK IF POINTS ARE ZERO FOR NON-TOP-10
# ============================================================================
print("\n[3/5] Zero Points Analysis")
print("-" * 70)

zero_pnt_analysis = df.groupby('is_top_10').agg({
    'Pnt_filled': [
        ('zero_count', lambda x: (x == 0).sum()),
        ('nonzero_count', lambda x: (x > 0).sum()),
        ('pct_with_points', lambda x: (x > 0).sum() / len(x) * 100)
    ]
})

print(zero_pnt_analysis.to_string())

top10_pct_with_points = (df[df['is_top_10'] == 1]['Pnt_filled'] > 0).mean()
nottop10_pct_with_points = (df[df['is_top_10'] == 0]['Pnt_filled'] > 0).mean()

print(f"\nTop 10 finishers with points: {top10_pct_with_points*100:.1f}%")
print(f"Non-top-10 finishers with points: {nottop10_pct_with_points*100:.1f}%")

if top10_pct_with_points > 0.9 and nottop10_pct_with_points < 0.3:
    print("⚠️  STRONG LEAKAGE SIGNAL - Points are clearly position-based!")

# ============================================================================
# 4. RANK vs PNT RELATIONSHIP
# ============================================================================
print("\n[4/5] Rank vs Pnt_filled Relationship")
print("-" * 70)

# Check if Pnt decreases as rank increases (sign of position-based points)
rank_pnt = df[df['Rnk_clean'] <= 20].groupby('Rnk_clean')['Pnt_filled'].mean()
print("\nAverage Pnt_filled by finishing position (Ranks 1-20):")
print(rank_pnt.to_string())

# Check if there's a clear trend
if len(rank_pnt) >= 10:
    # Calculate if points monotonically decrease
    decreasing_trend = all(rank_pnt.iloc[i] >= rank_pnt.iloc[i+1] for i in range(min(10, len(rank_pnt)-1)))

    if decreasing_trend:
        print("\n⚠️  CLEAR TREND: Points decrease with worse finish position")
        print("    This confirms Pnt is awarded BASED ON finish position!")
        print("    → DATA LEAKAGE CONFIRMED")
    else:
        print("\n✓ No clear monotonic trend - points may be independent")

# ============================================================================
# 5. PREDICTIVE POWER TEST
# ============================================================================
print("\n[5/5] Predictive Power Test")
print("-" * 70)

# Create simple rule: "If Pnt > threshold, predict top 10"
thresholds = [0, 10, 20, 50, 100]
print("\nSimple rule accuracy: 'If Pnt_filled > X, predict top_10 = 1'\n")
print(f"{'Threshold':>10} | {'Accuracy':>8} | {'Precision':>9}")
print("-" * 35)

for threshold in thresholds:
    predictions = (df['Pnt_filled'] > threshold).astype(int)
    accuracy = (predictions == df['is_top_10']).mean()

    # Calculate precision
    true_positives = ((predictions == 1) & (df['is_top_10'] == 1)).sum()
    predicted_positives = (predictions == 1).sum()
    precision = true_positives / predicted_positives if predicted_positives > 0 else 0

    print(f"{threshold:>10} | {accuracy*100:>7.2f}% | {precision*100:>8.2f}%")

best_threshold_acc = max([(t, ((df['Pnt_filled'] > t).astype(int) == df['is_top_10']).mean()) 
                          for t in range(0, 200, 10)], key=lambda x: x[1])

print(f"\nBest threshold: Pnt > {best_threshold_acc[0]} → Accuracy: {best_threshold_acc[1]*100:.2f}%")

if best_threshold_acc[1] > 0.85:
    print("⚠️  EXTREME LEAKAGE: Can predict target with >85% accuracy using Pnt alone!")

# ============================================================================
# FINAL VERDICT
# ============================================================================
print("\n" + "="*70)
print("FINAL VERDICT")
print("="*70)

leakage_score = 0
reasons = []

if correlation > 0.7:
    leakage_score += 3
    reasons.append("• Very high correlation with target")
elif correlation > 0.5:
    leakage_score += 2
    reasons.append("• Moderate correlation with target")

if mean_ratio > 5:
    leakage_score += 3
    reasons.append("• Top 10 finishers have 5x+ higher Pnt values")
elif mean_ratio > 2:
    leakage_score += 2
    reasons.append("• Top 10 finishers have notably higher Pnt values")

if top10_pct_with_points > 0.9 and nottop10_pct_with_points < 0.3:
    leakage_score += 3
    reasons.append("• 90%+ of top 10 have points vs <30% of non-top-10")

if best_threshold_acc[1] > 0.85:
    leakage_score += 3
    reasons.append("• Can predict target with >85% accuracy using Pnt alone")

print(f"\nLeakage Score: {leakage_score}/12\n")

if leakage_score >= 8:
    print("🚨 SEVERE DATA LEAKAGE DETECTED")
    print("\nPnt_filled is clearly derived FROM the target variable.")
    print("Your model is essentially 'cheating' by seeing the answer.\n")
    print("RECOMMENDATION:")
    print("  1. Remove Pnt_filled, Pnt_total, Pnt_max from features")
    print("  2. Keep only historical aggregates: Pnt_avg, Pnt_points_per_race")
    print("  3. Or: Recalculate Pnt features using ONLY past races (lagged features)")
    print("  4. Retrain model and expect lower (but more realistic) performance")

elif leakage_score >= 5:
    print("⚠️  LIKELY DATA LEAKAGE")
    print("\nEvidence of leakage:")
    for reason in reasons:
        print(f"  {reason}")
    print("\nRECOMMENDATION: Remove Pnt_filled and use historical features only")

else:
    print("✓ Low risk of data leakage")
    print("Pnt_filled appears to be independent enough of target")

print("\n" + "="*70)