"""
Model Run Comparison Tool
Compares results across multiple training runs
"""

import pandas as pd
import os
from pathlib import Path

print("=" * 70)
print("MODEL RUN COMPARISON")
print("=" * 70)

# Find all run directories - use path relative to this script
script_dir = Path(__file__).parent
runs_dir = script_dir.parent / "model_runs"
if not runs_dir.exists():
    print("\nNo model_runs directory found. Run model_tuned.py first.")
    exit(0)

run_dirs = sorted([d for d in runs_dir.iterdir() if d.is_dir()])

if len(run_dirs) == 0:
    print("\nNo training runs found. Run model_tuned.py first.")
    exit(0)

print(f"\nFound {len(run_dirs)} training runs")

# Collect metadata from all runs
all_metadata = []
for run_dir in run_dirs:
    metadata_file = run_dir / "run_metadata.csv"
    if metadata_file.exists():
        df = pd.read_csv(metadata_file)
        df['run_dir'] = run_dir.name
        all_metadata.append(df)

if all_metadata:
    metadata_df = pd.concat(all_metadata, ignore_index=True)
    print("\n" + "=" * 70)
    print("RUN SUMMARY")
    print("=" * 70)
    print(metadata_df[['run_id', 'best_model', 'best_precision', 'target_achieved']].to_string(index=False))
    
    # Find best run
    best_run = metadata_df.loc[metadata_df['best_precision'].idxmax()]
    print(f"\n" + "=" * 70)
    print(f"BEST RUN: {best_run['run_id']}")
    print("=" * 70)
    print(f"  Model: {best_run['best_model']}")
    print(f"  Precision: {best_run['best_precision']:.1%}")
    print(f"  Location: model_runs/run_{best_run['run_id']}/")
    
    # Show detailed comparison for best run
    best_run_dir = runs_dir / f"run_{best_run['run_id']}"
    comparison_file = best_run_dir / "model_comparison.csv"
    
    if comparison_file.exists():
        print(f"\n" + "=" * 70)
        print(f"BEST RUN DETAILS")
        print("=" * 70)
        comparison_df = pd.read_csv(comparison_file)
        print("\n" + comparison_df.to_string(index=False))

# Compare all runs side by side
print(f"\n" + "=" * 70)
print("PRECISION COMPARISON ACROSS RUNS")
print("=" * 70)

all_comparisons = []
for run_dir in run_dirs:
    comparison_file = run_dir / "model_comparison.csv"
    if comparison_file.exists():
        df = pd.read_csv(comparison_file)
        df['run_id'] = run_dir.name.replace('run_', '')
        all_comparisons.append(df)

if all_comparisons:
    all_comp_df = pd.concat(all_comparisons, ignore_index=True)
    
    # Pivot to show runs side by side
    pivot = all_comp_df.pivot_table(
        index=['Model', 'Threshold'],
        columns='run_id',
        values='Precision'
    )
    
    print("\n" + pivot.to_string())
    
    # Save consolidated comparison
    output_path = runs_dir / 'all_runs_comparison.csv'
    all_comp_df.to_csv(output_path, index=False)
    print(f"\n✓ Saved consolidated comparison to: {output_path}")

print("\n" + "=" * 70)
