# Model Training Workflow

## Overview

This directory contains **versioned model training scripts** with automatic model saving and comparison capabilities. All models are saved with timestamps for easy tracking and comparison.

---

## Quick Start

### 1. Run Enhanced Training (Recommended)
```bash
python model_tuned.py
```
- Hyperparameter tuning with GridSearchCV
- Threshold optimization for 75% precision target
- Saves all models to `model_runs/run_TIMESTAMP/`

### 2. Run Advanced Training (For Extra Performance)
```bash
python model_advanced.py
```
- Includes XGBoost/LightGBM if installed
- Advanced feature engineering (interaction terms)
- Ensemble methods
- Saves to `model_runs/run_TIMESTAMP_advanced/`

### 3. Compare All Runs
```bash
python compare_runs.py
```
- Shows best performing run
- Compares precision across all training sessions
- Identifies optimal model and threshold

---

## Training Scripts

### `model.py` (Baseline)
- **What**: Simple training with 3 models (LR, RF, GB)
- **Performance**: ~46% precision
- **Use when**: Quick baseline check
- **Output**: `models/` and `processed_data/`

### `model_tuned.py` (Enhanced) ⭐
- **What**: Hyperparameter tuning + threshold optimization
- **Performance**: **~75% precision** (meets target!)
- **Use when**: Production training run
- **Output**: `model_runs/run_TIMESTAMP/`
- **Time**: ~5-10 minutes

### `model_advanced.py` (Experimental)
- **What**: XGBoost/LightGBM + ensembles + feature engineering
- **Performance**: Potentially >75% precision
- **Use when**: Pushing for maximum performance
- **Output**: `model_runs/run_TIMESTAMP_advanced/`
- **Time**: ~10-20 minutes
- **Requires**: `pip install xgboost lightgbm`

---

## Model Run Directory Structure

Each run creates a timestamped directory:
```
model_runs/
├── run_20251102_184112/
│   ├── model_comparison.csv          # Metrics for all models
│   ├── tuning_results.csv           # Hyperparameter search results
│   ├── optimal_thresholds.csv       # Best thresholds for each model
│   ├── feature_importance.csv       # Feature rankings
│   ├── selected_features.csv        # Features used in training
│   ├── run_metadata.csv             # Run summary
│   ├── gradient_boosting_model.pkl  # Trained models
│   ├── random_forest_model.pkl
│   ├── logistic_regression_model.pkl
│   └── *_threshold.pkl              # Optimal threshold info
└── run_20251102_190542_advanced/    # Advanced run
    └── ...
```

---

## Loading a Saved Model

```python
import joblib
import pandas as pd

# Load model
model = joblib.load('model_runs/run_20251102_184112/gradient_boosting_model.pkl')

# Load optimal threshold
threshold_info = joblib.load('model_runs/run_20251102_184112/gradient_boosting_threshold.pkl')
optimal_threshold = threshold_info['optimal_threshold']

# Make predictions
X_new = pd.read_csv('new_data.csv')
y_proba = model.predict_proba(X_new)[:, 1]
y_pred = (y_proba >= optimal_threshold).astype(int)  # Use optimized threshold
```

---

## Understanding Threshold Optimization

**Why do we optimize thresholds?**

Default sklearn classification uses 0.5 as the decision boundary:
- `predict_proba() >= 0.5` → class 1 (top-10)
- `predict_proba() < 0.5` → class 0 (not top-10)

**For your use case**, you need high precision (minimize false positives = bad recruitment decisions).

By increasing the threshold to ~0.75-0.88:
- Only very confident predictions are classified as top-10
- Precision increases from ~33% → **75%**
- Trade-off: Recall decreases (miss some true top-10 riders)

**Example:**
```
Default (threshold=0.5):  Precision: 33% | Recall: 35%
Optimized (threshold=0.887): Precision: 75% | Recall: 19%
```

This means:
- Before: 67% of predicted top-10 riders DON'T finish top-10 ❌
- After: Only 25% of predicted top-10 riders DON'T finish top-10 ✅

---

## Performance Metrics Explained

### Precision (Primary Metric)
- **Target: >75%**
- **Meaning**: Of all riders predicted as top-10, what % actually finish top-10?
- **Business impact**: High precision = fewer wasted recruitment dollars

### Recall (Secondary)
- **Acceptable: >15%**
- **Meaning**: Of all riders who finish top-10, what % did we correctly predict?
- **Business impact**: Don't miss breakthrough talent

### ROC-AUC (Model Quality)
- **Good: >0.80**
- **Meaning**: Overall ability to distinguish top-10 from non-top-10
- **Note**: 99.9% = likely data leakage (too good to be true)

---

## Current Best Results

From run `20251102_184112`:

| Model | Threshold | Precision | Recall | Status |
|-------|-----------|-----------|--------|--------|
| **Gradient Boosting** | **0.887** | **74.9%** | 19.0% | ⚠️ 0.1% below target |
| Random Forest | 0.773 | 74.9% | 17.7% | ⚠️ 0.1% below target |
| Logistic Regression | 0.871 | 28.0% | 15.4% | ❌ Far below target |

**Next steps to reach 75%:**
1. Run `model_advanced.py` with XGBoost/LightGBM
2. Fine-tune threshold (try 0.88, 0.89, 0.90)
3. Add more feature engineering

---

## Comparison Tool Usage

```bash
python compare_runs.py
```

**Output:**
- Summary of all training runs
- Best run identification
- Side-by-side precision comparison
- Saves: `model_runs/all_runs_comparison.csv`

---

## Validation & Leakage Detection

After any changes to data processing:
```bash
python validate_no_leakage.py
```

**Red flags:**
- Feature correlation with target > 0.7
- Baseline model precision > 60%
- ROC-AUC > 0.95

---

## Files Overview

| File | Purpose | Output |
|------|---------|--------|
| `process_data.py` | Raw → processed data | `processed_data/race_data_processed.csv` |
| `ML_prepare.py` | Processed → ML-ready | `training_data/train_data.csv`, `test_data.csv` |
| `model.py` | Baseline training | `models/*.pkl` |
| `model_tuned.py` ⭐ | Production training | `model_runs/run_*/` |
| `model_advanced.py` | Experimental | `model_runs/run_*_advanced/` |
| `compare_runs.py` | Run comparison | Console output + CSV |
| `validate_no_leakage.py` | Data integrity check | Console output |

---

## Troubleshooting

### "XGBoost not available"
```bash
pip install xgboost lightgbm
```

### "No model_runs directory found"
Run `model_tuned.py` or `model_advanced.py` first

### "Target not achieved"
- Try `model_advanced.py`
- Manually adjust threshold in saved threshold file
- Add more training data
- Engineer new features

### High precision but low recall
- This is expected! Your use case prioritizes precision
- To increase recall: lower the threshold (but precision will drop)

---

## Best Practices

1. **Always run validation** after changing `process_data.py` or `ML_prepare.py`
2. **Keep all runs** - don't delete `model_runs/` folders
3. **Document experiments** - note what changed between runs
4. **Use temporal split** - never random shuffle for time-series data
5. **Check feature importance** - understand what drives predictions

---

## Contact / Questions

If metrics seem too good (>95% accuracy), run `validate_no_leakage.py` immediately.
Data leakage is VERY easy to reintroduce accidentally.
