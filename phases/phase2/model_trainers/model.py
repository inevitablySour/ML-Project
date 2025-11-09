"""
ML Model Training Pipeline
Trains multiple models to predict is_top_10 (top 10 finish prediction)
Includes feature selection and model comparison
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix,
    precision_score, recall_score, f1_score, roc_auc_score
)
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
import joblib
import warnings
warnings.filterwarnings('ignore')

# Get paths relative to script location
script_dir = Path(__file__).parent
phase2_dir = script_dir.parent

print("="*70)
print("ML MODEL TRAINING PIPELINE")
print("="*70)

# Dataset selection
print("\nWhich dataset would you like to train on?")
print("  1) Original (from race_data_processed.csv)")
print("  2) Enhanced (from race_data_processed_enhanced.csv)")

choice = input("\nEnter your choice (1 or 2): ").strip()

if choice == "2":
    dataset_suffix = "_enhanced"
    print("\n✓ Using ENHANCED training data with Tier 1-2 features")
else:
    dataset_suffix = ""
    print("\n✓ Using ORIGINAL training data")

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("\n[1/5] Loading preprocessed data...")
train_path = phase2_dir / 'training_data' / f'train_data{dataset_suffix}.csv'
test_path = phase2_dir / 'training_data' / f'test_data{dataset_suffix}.csv'
X_train = pd.read_csv(train_path)
X_test = pd.read_csv(test_path)

y_train = X_train['is_top_10']
X_train = X_train.drop('is_top_10', axis=1)

y_test = X_test['is_top_10']
X_test = X_test.drop('is_top_10', axis=1)

print(f"   Train: {X_train.shape[0]:,} samples × {X_train.shape[1]} features")
print(f"   Test:  {X_test.shape[0]:,} samples × {X_test.shape[1]} features")

# ============================================================================
# FEATURE SELECTION (reduce dimensionality)
# ============================================================================
print("\n[2/5] Feature selection analysis...")

# Option 1: Use ALL features (tree-based models handle this well)
USE_FEATURE_SELECTION = True  # Set to False to use all features
K_BEST = 25  # Number of top features to keep

if USE_FEATURE_SELECTION:
    print(f"   Selecting top {K_BEST} features using mutual information...")

    # Mutual information (good for non-linear relationships)
    selector = SelectKBest(score_func=mutual_info_classif, k=K_BEST)
    X_train_selected = selector.fit_transform(X_train, y_train)
    X_test_selected = selector.transform(X_test)

    # Get selected feature names
    selected_mask = selector.get_support()
    selected_features = X_train.columns[selected_mask].tolist()

    print(f"   Selected features:")
    for i, feat in enumerate(selected_features, 1):
        score = selector.scores_[X_train.columns.get_loc(feat)]
        print(f"      {i:2d}. {feat:40s} (score: {score:.4f})")

    # Convert back to DataFrame
    X_train_final = pd.DataFrame(X_train_selected, columns=selected_features)
    X_test_final = pd.DataFrame(X_test_selected, columns=selected_features)

    # Save selected features
    output_dir = phase2_dir / 'processed_data'
    output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({'feature': selected_features}).to_csv(
        output_dir / 'selected_features.csv', index=False
    )
else:
    print(f"   Using all {X_train.shape[1]} features")
    X_train_final = X_train
    X_test_final = X_test
    selected_features = X_train.columns.tolist()

# ============================================================================
# 3. TRAIN MULTIPLE MODELS
# ============================================================================
print("\n[3/5] Training models...")

models = {
    'Logistic Regression': LogisticRegression(
        max_iter=1000,
        class_weight='balanced',  # Handles any remaining imbalance
        random_state=42
    ),
    'Random Forest': RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=50,
        min_samples_leaf=20,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    ),
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=50,
        min_samples_leaf=20,
        random_state=42
    )
}

trained_models = {}
results = []

for name, model in models.items():
    print(f"\n   Training {name}...")

    # Train
    model.fit(X_train_final, y_train)

    # Predict on test set
    y_pred = model.predict(X_test_final)
    y_pred_proba = model.predict_proba(X_test_final)[:, 1]

    # Calculate metrics
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)

    results.append({
        'Model': name,
        'Precision': precision,
        'Recall': recall,
        'F1-Score': f1,
        'ROC-AUC': roc_auc
    })

    # Save model
    trained_models[name] = model
    models_dir = phase2_dir / 'models'
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, models_dir / f'{name.replace(" ", "_").lower()}_model.pkl')

    print(f"      ✓ Precision: {precision:.3f} | Recall: {recall:.3f} | F1: {f1:.3f} | ROC-AUC: {roc_auc:.3f}")

# ============================================================================
# 4. COMPARE MODELS
# ============================================================================
print("\n[4/5] Model comparison...")
results_df = pd.DataFrame(results).sort_values('Precision', ascending=False)
print("\n" + results_df.to_string(index=False))

# Find best model by Precision (your primary metric)
best_model_name = results_df.iloc[0]['Model']
best_model = trained_models[best_model_name]
best_precision = results_df.iloc[0]['Precision']

print(f"\nBEST MODEL: {best_model_name}")
print(f"   Precision: {best_precision:.1%} (Target: >75%)")

if best_precision >= 0.75:
    print(f"   SUCCESS! Exceeds 75% precision threshold")
else:
    print(f"    Below 75% target - consider hyperparameter tuning")

# Save comparison
processed_dir = phase2_dir / 'processed_data'
processed_dir.mkdir(parents=True, exist_ok=True)
results_df.to_csv(processed_dir / 'model_comparison.csv', index=False)

# ============================================================================
# 5. FEATURE IMPORTANCE (for best tree-based model)
# ============================================================================
print("\n[5/5] Feature importance analysis...")

# Get best tree-based model for feature importance
tree_models = {k: v for k, v in trained_models.items() if 'Forest' in k or 'Boosting' in k}

if tree_models:
    best_tree_model = max(
        tree_models.items(),
        key=lambda x: precision_score(y_test, x[1].predict(X_test_final))
    )
    tree_name, tree_model = best_tree_model

    # Get feature importances
    importances = tree_model.feature_importances_
    feature_importance_df = pd.DataFrame({
        'feature': selected_features,
        'importance': importances
    }).sort_values('importance', ascending=False)

    print(f"\n   Top 10 features (by {tree_name}):")
    for i, row in feature_importance_df.head(10).iterrows():
        print(f"      {row['feature']:40s} {row['importance']:.4f}")

    # Save feature importance
    feature_importance_df.to_csv(processed_dir / 'feature_importance.csv', index=False)

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*70)
print("TRAINING COMPLETE")
print("="*70)
print(f"""
Trained {len(models)} models
Best model: {best_model_name}
Best precision: {best_precision:.1%}

Saved files:
  - processed_data/{best_model_name.replace(' ', '_').lower()}_model.pkl
  - processed_data/model_comparison.csv
  - processed_data/feature_importance.csv
  - processed_data/selected_features.csv

Next step: Run 'python models.py' to see detailed performance
""")
print("="*70)
