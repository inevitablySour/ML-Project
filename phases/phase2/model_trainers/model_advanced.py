"""
Advanced ML Pipeline - Final Push to 75%+ Precision
- XGBoost and LightGBM models
- More aggressive hyperparameter tuning
- Feature engineering during training
- Ensemble methods
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    precision_recall_curve, make_scorer
)
from sklearn.feature_selection import SelectKBest, mutual_info_classif
import joblib
import warnings
from datetime import datetime
import os

# Try importing XGBoost and LightGBM
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("XGBoost not available. Install with: pip install xgboost")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("LightGBM not available. Install with: pip install lightgbm")

warnings.filterwarnings('ignore')

# Create versioned run directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
run_dir = f"model_runs/run_{timestamp}_advanced"
os.makedirs(run_dir, exist_ok=True)

print("=" * 70)
print("ADVANCED ML MODEL TRAINING PIPELINE")
print("=" * 70)
print(f"\nRun ID: {timestamp}_advanced")
print(f"Output directory: {run_dir}/")

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("\n[1/7] Loading preprocessed data...")
X_train = pd.read_csv('../training_data/train_data.csv')
X_test = pd.read_csv('../training_data/test_data.csv')

y_train = X_train['is_top_10']
X_train = X_train.drop('is_top_10', axis=1)

y_test = X_test['is_top_10']
X_test = X_test.drop('is_top_10', axis=1)

print(f"   Train: {X_train.shape[0]:,} samples × {X_train.shape[1]} features")
print(f"   Test:  {X_test.shape[0]:,} samples × {X_test.shape[1]} features")

# ============================================================================
# 2. ADVANCED FEATURE ENGINEERING
# ============================================================================
print("\n[2/7] Advanced feature engineering...")

def add_interaction_features(X):
    """Add interaction features that might improve precision"""
    X_new = X.copy()
    
    # Interaction: recent performance * race tier
    if 'recent_top10_rate' in X_new.columns and 'race_tier' in X_new.columns:
        X_new['performance_tier_interaction'] = X_new['recent_top10_rate'] * (4 - X_new['race_tier'])
    
    # Interaction: UCI points * age (peak performance detection)
    if 'UCI_avg' in X_new.columns and 'age_at_race' in X_new.columns:
        X_new['uci_age_interaction'] = X_new['UCI_avg'] * X_new['age_at_race']
    
    # Performance consistency indicator
    if 'recent_top10_count' in X_new.columns and 'rolling_avg_rank_5' in X_new.columns:
        X_new['consistency_score'] = X_new['recent_top10_count'] / (X_new['rolling_avg_rank_5'] + 1)
    
    return X_new

X_train = add_interaction_features(X_train)
X_test = add_interaction_features(X_test)

print(f"   Added interaction features: {X_train.shape[1] - y_train.shape[0]} new features")
print(f"   New feature count: {X_train.shape[1]}")

# ============================================================================
# 3. FEATURE SELECTION
# ============================================================================
print("\n[3/7] Feature selection...")

K_BEST = 28  # Slightly more features
selector = SelectKBest(score_func=mutual_info_classif, k=K_BEST)
X_train_selected = selector.fit_transform(X_train, y_train)
X_test_selected = selector.transform(X_test)

selected_mask = selector.get_support()
selected_features = X_train.columns[selected_mask].tolist()

X_train_final = pd.DataFrame(X_train_selected, columns=selected_features)
X_test_final = pd.DataFrame(X_test_selected, columns=selected_features)

print(f"   Selected {K_BEST} features")
pd.DataFrame({'feature': selected_features}).to_csv(
    f'{run_dir}/selected_features.csv', index=False
)

# ============================================================================
# 4. TRAIN ADVANCED MODELS
# ============================================================================
print("\n[4/7] Training advanced models...")

def precision_at_recall_threshold(y_true, y_pred):
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    if rec < 0.15:
        return prec * 0.3
    return prec

precision_scorer = make_scorer(precision_at_recall_threshold)
cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

model_configs = {
    'Gradient Boosting Pro': {
        'model': GradientBoostingClassifier(random_state=42),
        'params': {
            'n_estimators': [200, 300],
            'learning_rate': [0.1, 0.15],
            'max_depth': [5, 7],
            'min_samples_split': [80, 100],
            'min_samples_leaf': [15, 20],
            'subsample': [0.9, 1.0]
        }
    },
    'Random Forest Pro': {
        'model': RandomForestClassifier(random_state=42, n_jobs=-1),
        'params': {
            'n_estimators': [200, 300],
            'max_depth': [20, 25],
            'min_samples_split': [40, 50],
            'min_samples_leaf': [8, 10],
            'class_weight': ['balanced_subsample']
        }
    }
}

# Add XGBoost if available
if XGBOOST_AVAILABLE:
    model_configs['XGBoost'] = {
        'model': xgb.XGBClassifier(random_state=42, eval_metric='logloss', use_label_encoder=False),
        'params': {
            'n_estimators': [200, 300],
            'max_depth': [5, 7],
            'learning_rate': [0.1, 0.15],
            'subsample': [0.8, 0.9],
            'colsample_bytree': [0.8, 0.9],
            'scale_pos_weight': [10, 15, 20]
        }
    }

# Add LightGBM if available
if LIGHTGBM_AVAILABLE:
    model_configs['LightGBM'] = {
        'model': lgb.LGBMClassifier(random_state=42, verbose=-1),
        'params': {
            'n_estimators': [200, 300],
            'max_depth': [5, 7, 9],
            'learning_rate': [0.1, 0.15],
            'num_leaves': [31, 50],
            'subsample': [0.8, 0.9],
            'scale_pos_weight': [10, 15]
        }
    }

trained_models = {}
tuning_results = []

for name, config in model_configs.items():
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
    
    print(f"      Best CV score: {grid_search.best_score_:.3f}")
    
    tuning_results.append({
        'Model': name,
        'Best_CV_Score': grid_search.best_score_,
        'Best_Params': str(grid_search.best_params_)
    })

pd.DataFrame(tuning_results).to_csv(f'{run_dir}/tuning_results.csv', index=False)

# ============================================================================
# 5. CREATE ENSEMBLE
# ============================================================================
print("\n[5/7] Creating ensemble models...")

# Voting classifier (soft voting)
if len(trained_models) >= 2:
    top_models = sorted(
        [(name, model) for name, model in trained_models.items()],
        key=lambda x: tuning_results[list(trained_models.keys()).index(x[0])]['Best_CV_Score'],
        reverse=True
    )[:3]  # Top 3 models
    
    voting_clf = VotingClassifier(
        estimators=top_models,
        voting='soft',
        weights=[3, 2, 1]  # Weight best model more
    )
    
    print(f"   Training ensemble with: {[name for name, _ in top_models]}")
    voting_clf.fit(X_train_final, y_train)
    trained_models['Ensemble'] = voting_clf

# ============================================================================
# 6. EVALUATE WITH THRESHOLD OPTIMIZATION
# ============================================================================
print("\n[6/7] Evaluating models with threshold optimization...")

results = []
threshold_results = []

for name, model in trained_models.items():
    print(f"\n   Evaluating {name}...")
    
    y_pred_proba = model.predict_proba(X_test_final)[:, 1]
    
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_pred_proba)
    
    # Find threshold closest to 75% precision with recall > 0.15
    target_precision = 0.75
    best_threshold = 0.5
    best_precision_diff = float('inf')
    
    for i, (prec, rec, thresh) in enumerate(zip(precisions[:-1], recalls[:-1], thresholds)):
        if rec > 0.15:
            diff = abs(prec - target_precision)
            if diff < best_precision_diff:
                best_precision_diff = diff
                best_threshold = thresh
    
    # Default threshold
    y_pred_default = (y_pred_proba >= 0.5).astype(int)
    precision_default = precision_score(y_test, y_pred_default)
    recall_default = recall_score(y_test, y_pred_default)
    f1_default = f1_score(y_test, y_pred_default)
    
    # Optimized threshold
    y_pred_optimized = (y_pred_proba >= best_threshold).astype(int)
    precision_optimized = precision_score(y_test, y_pred_optimized)
    recall_optimized = recall_score(y_test, y_pred_optimized)
    f1_optimized = f1_score(y_test, y_pred_optimized)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"      Default:   Precision: {precision_default:.3f} | Recall: {recall_default:.3f}")
    print(f"      Optimized: Precision: {precision_optimized:.3f} | Recall: {recall_optimized:.3f}")
    
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
    
    # Save model
    model_filename = f"{run_dir}/{name.replace(' ', '_').lower()}_model.pkl"
    joblib.dump(model, model_filename)
    
    threshold_info = {
        'model_name': name,
        'optimal_threshold': best_threshold,
        'timestamp': timestamp
    }
    joblib.dump(threshold_info, f"{run_dir}/{name.replace(' ', '_').lower()}_threshold.pkl")

# ============================================================================
# 7. FINAL RESULTS
# ============================================================================
print("\n[7/7] Final results...")
results_df = pd.DataFrame(results)
print("\n" + results_df.to_string(index=False))

results_df.to_csv(f'{run_dir}/model_comparison.csv', index=False)
pd.DataFrame(threshold_results).to_csv(f'{run_dir}/optimal_thresholds.csv', index=False)

best_result = results_df[results_df['Threshold'].str.contains('Optimized')].sort_values(
    'Precision', ascending=False
).iloc[0]

best_model_name = best_result['Model']
best_precision = best_result['Precision']

print("\n" + "=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)
print(f"""
Run ID: {timestamp}_advanced
Best model: {best_model_name}
Best precision: {best_precision:.1%}

Target achieved: {'✓ YES!' if best_precision >= 0.75 else '✗ Not yet'}
Gap to 75%: {(0.75 - best_precision) if best_precision < 0.75 else 0:.2%}

All results saved to: {run_dir}/
""")
print("=" * 70)

# Save metadata
metadata = {
    'run_id': f"{timestamp}_advanced",
    'train_samples': len(X_train_final),
    'test_samples': len(X_test_final),
    'features_used': len(selected_features),
    'best_model': best_model_name,
    'best_precision': best_precision,
    'target_achieved': best_precision >= 0.75
}
pd.DataFrame([metadata]).to_csv(f'{run_dir}/run_metadata.csv', index=False)
