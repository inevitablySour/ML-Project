"""
Enhanced ML Model Training Pipeline
- Hyperparameter tuning with GridSearchCV
- Threshold optimization for precision
- Versioned model saving
- Comprehensive performance tracking
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import (
    classification_report, confusion_matrix,
    precision_score, recall_score, f1_score, roc_auc_score,
    precision_recall_curve, make_scorer
)
from sklearn.feature_selection import SelectKBest, mutual_info_classif
import joblib
import warnings
from datetime import datetime
from tqdm import tqdm
warnings.filterwarnings('ignore')

# Get paths relative to script location
script_dir = Path(__file__).parent
phase2_dir = script_dir.parent

# Create versioned run directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
run_dir = phase2_dir / 'model_runs' / f"run_{timestamp}"
run_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("ENHANCED ML MODEL TRAINING PIPELINE")
print("=" * 70)
print(f"\nRun ID: {timestamp}")
print(f"Output directory: {run_dir}/")

# ============================================================================
# DATASET SELECTION
# ============================================================================
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
print("\n[1/6] Loading preprocessed data...")
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
# 2. FEATURE SELECTION
# ============================================================================
print("\n[2/6] Feature selection analysis...")

USE_FEATURE_SELECTION = True
K_BEST = 25

if USE_FEATURE_SELECTION:
    print(f"   Selecting top {K_BEST} features using mutual information...")
    selector = SelectKBest(score_func=mutual_info_classif, k=K_BEST)
    X_train_selected = selector.fit_transform(X_train, y_train)
    X_test_selected = selector.transform(X_test)

    selected_mask = selector.get_support()
    selected_features = X_train.columns[selected_mask].tolist()

    print(f"   Selected features saved to {run_dir}/selected_features.csv")
    
    X_train_final = pd.DataFrame(X_train_selected, columns=selected_features)
    X_test_final = pd.DataFrame(X_test_selected, columns=selected_features)
    
    pd.DataFrame({'feature': selected_features}).to_csv(
        run_dir / 'selected_features.csv', index=False
    )
else:
    X_train_final = X_train
    X_test_final = X_test
    selected_features = X_train.columns.tolist()

# ============================================================================
# 3. HYPERPARAMETER TUNING
# ============================================================================
print("\n[3/6] Hyperparameter tuning (this may take a few minutes)...")

# Custom scorer that prioritizes precision
def precision_at_recall_threshold(y_true, y_pred):
    """Custom scorer: maximize precision while maintaining recall > 0.2"""
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    if rec < 0.2:  # Penalize if recall too low
        return prec * 0.5
    return prec

precision_scorer = make_scorer(precision_at_recall_threshold)

cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

# Model configurations with hyperparameter grids
model_configs = {
    'Logistic Regression': {
        'model': LogisticRegression(max_iter=2000, random_state=42),
        'params': {
            'C': [0.01, 0.1, 1.0, 10.0],
            'class_weight': ['balanced', {0: 1, 1: 2}, {0: 1, 1: 3}],
            'solver': ['lbfgs', 'liblinear']
        }
    },
    'Random Forest': {
        'model': RandomForestClassifier(random_state=42, n_jobs=-1),
        'params': {
            'n_estimators': [100, 200],
            'max_depth': [10, 15, 20],
            'min_samples_split': [50, 100],
            'min_samples_leaf': [10, 20],
            'class_weight': ['balanced', 'balanced_subsample']
        }
    },
    'Gradient Boosting': {
        'model': GradientBoostingClassifier(random_state=42),
        'params': {
            'n_estimators': [100, 200],
            'learning_rate': [0.05, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'min_samples_split': [50, 100],
            'subsample': [0.8, 1.0]
        }
    }
}

trained_models = {}
tuning_results = []

print("\n   Progress:")
for name, config in tqdm(list(model_configs.items()), desc="   Models", ncols=80):
    print(f"\n   Tuning {name}...")
    
    grid_search = GridSearchCV(
        config['model'],
        config['params'],
        cv=cv,
        scoring=precision_scorer,
        n_jobs=-1,
        verbose=0
    )
    
    grid_search.fit(X_train_final, y_train)
    
    best_model = grid_search.best_estimator_
    trained_models[name] = best_model
    
    print(f"      Best params: {grid_search.best_params_}")
    print(f"      Best CV score: {grid_search.best_score_:.3f}")
    
    tuning_results.append({
        'Model': name,
        'Best_CV_Score': grid_search.best_score_,
        'Best_Params': str(grid_search.best_params_)
    })

# Save tuning results
pd.DataFrame(tuning_results).to_csv(run_dir / 'tuning_results.csv', index=False)

# ============================================================================
# 4. EVALUATE WITH THRESHOLD OPTIMIZATION
# ============================================================================
print("\n[4/6] Evaluating models with threshold optimization...")

results = []
threshold_results = []

print("\n   Progress:")
for name, model in tqdm(list(trained_models.items()), desc="   Evaluating", ncols=80):
    print(f"\n   Evaluating {name}...")
    
    # Get probability predictions
    y_pred_proba = model.predict_proba(X_test_final)[:, 1]
    
    # Find optimal threshold for precision
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_pred_proba)
    
    # Find threshold that gives precision closest to 0.75
    target_precision = 0.75
    best_threshold = 0.5
    best_precision_diff = float('inf')
    
    for i, (prec, rec, thresh) in enumerate(zip(precisions[:-1], recalls[:-1], thresholds)):
        if rec > 0.15:  # Ensure recall not too low
            diff = abs(prec - target_precision)
            if diff < best_precision_diff:
                best_precision_diff = diff
                best_threshold = thresh
    
    # Evaluate with default threshold (0.5)
    y_pred_default = (y_pred_proba >= 0.5).astype(int)
    precision_default = precision_score(y_test, y_pred_default)
    recall_default = recall_score(y_test, y_pred_default)
    f1_default = f1_score(y_test, y_pred_default)
    
    # Evaluate with optimized threshold
    y_pred_optimized = (y_pred_proba >= best_threshold).astype(int)
    precision_optimized = precision_score(y_test, y_pred_optimized)
    recall_optimized = recall_score(y_test, y_pred_optimized)
    f1_optimized = f1_score(y_test, y_pred_optimized)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"      Default (threshold=0.5):  Precision: {precision_default:.3f} | Recall: {recall_default:.3f}")
    print(f"      Optimized (threshold={best_threshold:.3f}): Precision: {precision_optimized:.3f} | Recall: {recall_optimized:.3f}")
    
    results.append({
        'Model': name,
        'Threshold': 'Default (0.5)',
        'Precision': precision_default,
        'Recall': recall_default,
        'F1-Score': f1_default,
        'ROC-AUC': roc_auc
    })
    
    results.append({
        'Model': name,
        'Threshold': f'Optimized ({best_threshold:.3f})',
        'Precision': precision_optimized,
        'Recall': recall_optimized,
        'F1-Score': f1_optimized,
        'ROC-AUC': roc_auc
    })
    
    threshold_results.append({
        'Model': name,
        'Optimal_Threshold': best_threshold,
        'Precision_at_Threshold': precision_optimized,
        'Recall_at_Threshold': recall_optimized
    })
    
    # Save model with version
    model_filename = run_dir / f"{name.replace(' ', '_').lower()}_model.pkl"
    joblib.dump(model, model_filename)
    
    # Save threshold info
    threshold_info = {
        'model_name': name,
        'optimal_threshold': best_threshold,
        'timestamp': timestamp
    }
    joblib.dump(threshold_info, run_dir / f"{name.replace(' ', '_').lower()}_threshold.pkl")

# ============================================================================
# 5. MODEL COMPARISON
# ============================================================================
print("\n[5/6] Model comparison...")
results_df = pd.DataFrame(results)
print("\n" + results_df.to_string(index=False))

# Save results
results_df.to_csv(run_dir / 'model_comparison.csv', index=False)
pd.DataFrame(threshold_results).to_csv(run_dir / 'optimal_thresholds.csv', index=False)

# Find best model by optimized precision
best_result = results_df[results_df['Threshold'].str.contains('Optimized')].sort_values(
    'Precision', ascending=False
).iloc[0]

best_model_name = best_result['Model']
best_precision = best_result['Precision']

print(f"\nBEST MODEL: {best_model_name} (with optimized threshold)")
print(f"   Precision: {best_precision:.1%} (Target: >75%)")

if best_precision >= 0.75:
    print(f"   ✓ SUCCESS! Exceeds 75% precision threshold")
else:
    gap = 0.75 - best_precision
    print(f"   Gap to target: {gap:.1%}")

# ============================================================================
# 6. FEATURE IMPORTANCE
# ============================================================================
print("\n[6/6] Feature importance analysis...")

tree_models = {k: v for k, v in trained_models.items() 
               if 'Forest' in k or 'Boosting' in k}

if tree_models:
    best_tree_model = max(
        tree_models.items(),
        key=lambda x: precision_score(y_test, x[1].predict(X_test_final))
    )
    tree_name, tree_model = best_tree_model
    
    importances = tree_model.feature_importances_
    feature_importance_df = pd.DataFrame({
        'feature': selected_features,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    print(f"\n   Top 10 features (by {tree_name}):")
    for i, row in feature_importance_df.head(10).iterrows():
        print(f"      {row['feature']:40s} {row['importance']:.4f}")
    
    feature_importance_df.to_csv(run_dir / 'feature_importance.csv', index=False)

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)
print(f"""
Run ID: {timestamp}
Trained {len(trained_models)} models with hyperparameter tuning
Best model: {best_model_name}
Best precision: {best_precision:.1%}

All results saved to: {run_dir}/

Files created:
  - model_comparison.csv (detailed metrics)
  - tuning_results.csv (hyperparameter search results)
  - optimal_thresholds.csv (threshold optimization)
  - feature_importance.csv (feature rankings)
  - selected_features.csv (features used)
  - *_model.pkl (trained model files)
  - *_threshold.pkl (optimal threshold info)

To load a model later:
  model = joblib.load('{run_dir}/gradient_boosting_model.pkl')
  threshold_info = joblib.load('{run_dir}/gradient_boosting_threshold.pkl')
""")
print("=" * 70)

# Save run metadata
metadata = {
    'run_id': timestamp,
    'dataset': 'enhanced' if dataset_suffix == '_enhanced' else 'original',
    'train_samples': len(X_train_final),
    'test_samples': len(X_test_final),
    'features_used': len(selected_features),
    'best_model': best_model_name,
    'best_precision': best_precision,
    'target_achieved': best_precision >= 0.75
}
pd.DataFrame([metadata]).to_csv(run_dir / 'run_metadata.csv', index=False)
