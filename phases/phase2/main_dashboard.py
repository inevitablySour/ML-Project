#!/usr/bin/env python3
"""
CAICLE Cycling ML Project - Main Dashboard
Interactive controller for running all phases of the ML pipeline
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}\n")

def print_section(text):
    """Print formatted section"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'-'*len(text)}{Colors.END}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠  {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ  {text}{Colors.END}")

def run_script(script_path, description):
    """Run a Python script and handle output"""
    print_info(f"Running: {description}")
    print(f"{Colors.CYAN}{'─'*70}{Colors.END}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True
        )
        
        print(f"{Colors.CYAN}{'─'*70}{Colors.END}")
        
        if result.returncode == 0:
            print_success(f"Completed: {description}")
            return True
        else:
            print_error(f"Failed: {description} (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print_error(f"Error running {description}: {str(e)}")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if Path(filepath).exists():
        print_success(f"{description} exists")
        return True
    else:
        print_warning(f"{description} not found")
        return False

def show_menu(title, options):
    """Display menu and get user choice"""
    print_section(title)
    for key, value in options.items():
        print(f"  {Colors.BOLD}[{key}]{Colors.END} {value}")
    print()
    
    choice = input(f"{Colors.CYAN}Enter choice: {Colors.END}").strip().lower()
    return choice

def data_preparation_menu():
    """Handle data preparation workflow"""
    print_header("DATA PREPARATION PHASE")
    
    # Check for required data files
    print_section("Checking Data Files")
    # Paths relative to phases/phase2/
    db_exists = check_file_exists("../../data/cycling_big.db", "SQLite database")
    csv_exists = check_file_exists("../../data/data/rider_infos.csv", "Rider info CSV")
    
    if not (db_exists or csv_exists):
        print_error("Required data files not found. Please ensure data is in ../data/ directory.")
        return
    
    # Data preparation options
    options = {
        '1': 'Process raw data (process_data.py) - Original',
        '2': 'Process with enhanced features (process_data_enhanced.py) ⭐ NEW',
        '3': 'Prepare ML-ready data (ML_prepare.py) - Select dataset at runtime',
        '4': 'Validate for data leakage (validate_no_leakage.py)',
        '5': 'Run full pipeline (all steps)',
        'b': 'Back to main menu'
    }
    
    choice = show_menu("Data Preparation Options", options)
    
    if choice == '1':
        run_script("data_preperation/process_data.py", "Process raw data (Original)")
    elif choice == '2':
        run_script("data_preperation/process_data_enhanced.py", "Process raw data (Enhanced with Tier 1-2 features)")
    elif choice == '3':
        print_info("Note: You will be prompted to select dataset (original or enhanced)")
        run_script("data_preperation/ML_prepare.py", "Prepare ML-ready data")
    elif choice == '4':
        if check_file_exists("training_data/train_data.csv", "Training data") or check_file_exists("training_data/train_data_enhanced.csv", "Enhanced training data"):
            run_script("data_preperation/validate_no_leakage.py", "Validate data")
        else:
            print_error("Training data not found. Run options 1-3 first.")
    elif choice == '5':
        print_info("Running full data preparation pipeline...")
        print_info("Step 1: Processing original data...")
        if run_script("data_preperation/process_data.py", "Process raw data (Original)"):
            print_info("Step 2: Processing enhanced data...")
            if run_script("data_preperation/process_data_enhanced.py", "Process raw data (Enhanced)"):
                print_info("Step 3: Preparing ML data (you'll select dataset)...")
                if run_script("data_preperation/ML_prepare.py", "Prepare ML-ready data"):
                    print_info("Step 4: Validating for leakage...")
                    run_script("data_preperation/validate_no_leakage.py", "Validate data")
    elif choice == 'b':
        return
    else:
        print_error("Invalid choice")

def model_training_menu():
    """Handle model training workflow"""
    print_header("MODEL TRAINING PHASE")
    
    # Check for training data
    print_section("Checking Prerequisites")
    train_exists = check_file_exists("training_data/train_data.csv", "Training data")
    test_exists = check_file_exists("training_data/test_data.csv", "Test data")
    
    if not (train_exists and test_exists):
        print_error("Training data not found. Please run data preparation first.")
        return
    
    # Model training options
    options = {
        '1': 'Train baseline models (model.py) - Dataset selection at runtime',
        '2': 'Train tuned models with optimization (model_tuned.py) ⭐ RECOMMENDED - Dataset selection at runtime',
        '3': 'Train advanced models with XGBoost (model_advanced.py)',
        '4': 'Run all training pipelines',
        'b': 'Back to main menu'
    }
    
    choice = show_menu("Model Training Options", options)
    
    if choice == '1':
        print_info("Note: You will be prompted to select dataset (original or enhanced)")
        run_script("model_trainers/model.py", "Train baseline models")
    elif choice == '2':
        print_info("Note: You will be prompted to select dataset (original or enhanced)")
        run_script("model_trainers/model_tuned.py", "Train tuned models")
    elif choice == '3':
        print_warning("Note: Requires xgboost and lightgbm packages")
        confirm = input(f"{Colors.CYAN}Continue? [y/N]: {Colors.END}").strip().lower()
        if confirm == 'y':
            run_script("model_trainers/model_advanced.py", "Train advanced models")
    elif choice == '4':
        print_info("Running all training pipelines (this will take time)...")
        print_info("You will be prompted to select dataset for each training step.")
        run_script("model_trainers/model.py", "Train baseline models")
        run_script("model_trainers/model_tuned.py", "Train tuned models")
        print_warning("Skipping advanced models (optional). Run separately if needed.")
    elif choice == 'b':
        return
    else:
        print_error("Invalid choice")

def comparison_dashboard_menu():
    """Handle model comparison and dashboard"""
    print_header("MODEL COMPARISON & DASHBOARD")
    
    # Check for model runs
    print_section("Checking Model Runs")
    model_runs_dir = Path("model_runs")
    
    if not model_runs_dir.exists() or not list(model_runs_dir.iterdir()):
        print_error("No model runs found. Please train models first.")
        return
    
    run_count = len([d for d in model_runs_dir.iterdir() if d.is_dir()])
    print_success(f"Found {run_count} model run(s)")
    
    # Comparison options
    options = {
        '1': 'Compare all training runs (compare_runs.py)',
        '2': 'Convert results for dashboard (convert_results_to_dashboard.py)',
        '3': 'Open interactive dashboard (Streamlit)',
        '4': 'Run full comparison workflow',
        'b': 'Back to main menu'
    }
    
    choice = show_menu("Comparison Options", options)
    
    if choice == '1':
        run_script("dashboard/compare_runs.py", "Compare training runs")
    elif choice == '2':
        run_script("dashboard/convert_results_to_dashboard.py", "Convert results")
    elif choice == '3':
        print_info("Opening Streamlit dashboard...")
        print_warning("Dashboard will open in your browser. Press Ctrl+C to stop.")
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", 
                "dashboard/model_dashboard.py"
            ], cwd=os.getcwd())
        except KeyboardInterrupt:
            print_info("\nDashboard closed")
    elif choice == '4':
        print_info("Running full comparison workflow...")
        if run_script("dashboard/compare_runs.py", "Compare training runs"):
            if run_script("dashboard/convert_results_to_dashboard.py", "Convert results"):
                print_success("Ready to view dashboard!")
                view = input(f"{Colors.CYAN}Open dashboard now? [y/N]: {Colors.END}").strip().lower()
                if view == 'y':
                    print_info("Opening Streamlit dashboard...")
                    try:
                        subprocess.run([
                            sys.executable, "-m", "streamlit", "run", 
                            "dashboard/model_dashboard.py"
                        ], cwd=os.getcwd())
                    except KeyboardInterrupt:
                        print_info("\nDashboard closed")
    elif choice == 'b':
        return
    else:
        print_error("Invalid choice")

def show_project_status():
    """Display current project status"""
    print_header("PROJECT STATUS")
    
    # Data files (all relative to phases/phase2/ directory)
    print_section("Data Files")
    check_file_exists("../../data/cycling_big.db", "Raw SQLite database")
    check_file_exists("../../data/data/rider_infos.csv", "Rider information CSV")
    check_file_exists("processed_data/race_data_processed.csv", "Processed race data")
    check_file_exists("training_data/train_data.csv", "Training data")
    check_file_exists("training_data/test_data.csv", "Test data")
    
    # Models
    print_section("Trained Models")
    models_dir = Path("models")
    if models_dir.exists():
        models = list(models_dir.glob("*.pkl"))
        if models:
            for model in models:
                print_success(f"{model.name}")
        else:
            print_warning("No baseline models found")
    else:
        print_warning("Models directory not found")
    
    # Model runs
    print_section("Training Runs")
    model_runs_dir = Path("model_runs")
    if model_runs_dir.exists():
        runs = sorted([d for d in model_runs_dir.iterdir() if d.is_dir()])
        if runs:
            for run in runs:
                metadata_file = run / "run_metadata.csv"
                if metadata_file.exists():
                    import pandas as pd
                    meta = pd.read_csv(metadata_file)
                    run_id = meta['run_id'].iloc[0]
                    precision = meta['best_precision'].iloc[0]
                    achieved = meta['target_achieved'].iloc[0]
                    status = "✓ TARGET MET" if achieved else "⚠ Below target"
                    print(f"  {Colors.GREEN if achieved else Colors.YELLOW}[{run_id}]{Colors.END} "
                          f"Precision: {precision:.1%} - {status}")
                else:
                    print_warning(f"{run.name} (metadata missing)")
        else:
            print_warning("No training runs found")
    else:
        print_warning("Model runs directory not found")
    
    # Dashboard files
    print_section("Dashboard Files")
    check_file_exists("dashboard/model_dashboard.py", "Streamlit dashboard")
    check_file_exists("model_runs/all_runs_comparison.csv", "Comparison results")

def main():
    """Main application loop"""
    while True:
        print_header("CAICLE CYCLING ML PROJECT DASHBOARD")
        print(f"{Colors.BOLD}Machine Learning Pipeline Controller{Colors.END}")
        print(f"Project: Top-10 Finisher Prediction")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        main_options = {
            '1': 'Data Preparation',
            '2': 'Model Training',
            '3': 'Model Comparison & Dashboard',
            '4': 'View Project Status',
            '5': 'Run Complete Pipeline',
            'q': 'Quit'
        }
        
        choice = show_menu("Main Menu", main_options)
        
        if choice == '1':
            data_preparation_menu()
        elif choice == '2':
            model_training_menu()
        elif choice == '3':
            comparison_dashboard_menu()
        elif choice == '4':
            show_project_status()
        elif choice == '5':
            print_header("COMPLETE PIPELINE EXECUTION")
            confirm = input(f"{Colors.YELLOW}This will run all steps. Continue? [y/N]: {Colors.END}").strip().lower()
            if confirm == 'y':
                print_info("Starting complete pipeline...")
                
                # Data preparation
                print_section("STEP 1: Data Preparation")
                if not run_script("data_preperation/process_data.py", "Process raw data"):
                    print_error("Pipeline failed at data processing")
                    continue
                if not run_script("data_preperation/ML_prepare.py", "Prepare ML-ready data"):
                    print_error("Pipeline failed at ML preparation")
                    continue
                run_script("data_preperation/validate_no_leakage.py", "Validate data")
                
                # Model training
                print_section("STEP 2: Model Training")
                run_script("model_trainers/model_tuned.py", "Train tuned models")
                
                # Comparison
                print_section("STEP 3: Model Comparison")
                if run_script("dashboard/compare_runs.py", "Compare training runs"):
                    run_script("dashboard/convert_results_to_dashboard.py", "Convert results")
                
                print_success("\n🎉 Complete pipeline finished!")
                print_info("Run option 3 to view results in dashboard")
        elif choice == 'q':
            print_success("Goodbye!")
            break
        else:
            print_error("Invalid choice")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\n\nInterrupted by user")
        sys.exit(0)
