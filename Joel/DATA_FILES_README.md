# Data Files Not Included in Repository

Due to GitHub's file size limits, the following large files are **not included** in this repository but can be regenerated:

## Excluded Files

### Training Data (130+ MB)
- `training_data/train_data.csv`
- `training_data/test_data.csv`
- `training_data/scaler.pkl`

### Processed Data (50+ MB)
- `processed_data/race_data_processed.csv`
- `original_processed/race_data_processed.csv`

### Model Files (PKL files)
- `models/*.pkl` - Baseline trained models
- `model_runs/*/*.pkl` - Tuned model runs

## How to Regenerate These Files

### Option 1: Use the Main Dashboard (Recommended)
```bash
python main_dashboard.py
```
Then select:
1. **Data Preparation** → Run full pipeline
2. **Model Training** → Train tuned models

### Option 2: Manual Step-by-Step

#### Step 1: Prepare Training Data
```bash
cd Joel/data_preperation
python process_data.py      # Creates processed_data/race_data_processed.csv
python ML_prepare.py         # Creates training_data/train_data.csv & test_data.csv
```

#### Step 2: Train Models
```bash
cd ../model_trainers
python model_tuned.py        # Creates model_runs/run_TIMESTAMP/
```

## Prerequisites

Ensure you have the raw data files in `../data/`:
- `cycling_big.db` (SQLite database)
- `rider_infos.csv`

These files should be obtained from the project data source (not included due to size).

## Expected File Sizes

| File | Size | Purpose |
|------|------|---------|
| `train_data.csv` | ~130 MB | ML training dataset |
| `test_data.csv` | ~40 MB | ML test dataset |
| `race_data_processed.csv` | ~50-60 MB | Cleaned race data |
| Model PKL files | 5-70 MB each | Trained model weights |

## Note on .gitignore

All `.csv` and `.pkl` files are excluded via `.gitignore` to prevent accidentally committing large files.
