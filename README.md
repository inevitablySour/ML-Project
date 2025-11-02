# CAICLE Cycling ML Project - Rider Performance Prediction

**Machine Learning for Professional Cycling Recruitment**

This project uses machine learning to predict whether a professional cyclist will finish in the **top 10** of a race, helping CAICLE investment firm make data-driven multi-million dollar recruitment decisions for their professional cycling "super team".

## Project Goal

**Problem**: Binary classification to predict top-10 finishers  
**Success Criteria**: Precision > 75% for "Top 10 Finisher" class  
**Why Precision**: Minimize false positives (bad investments) while maintaining reasonable recall to avoid missing breakthrough talent

---

## Repository Structure

Top-level overview. Phase 2 contains the working pipeline you will use.

```
ML-Project/
├── data/                      # Raw data (gitignored)
│   ├── cycling_big.db        # SQLite database with 225k+ results
│   └── data/
│       └── rider_infos.csv   # 1042 riders with stats & profiles
├── phases/
│   ├── phase1/               # Business understanding & data exploration
│   └── phase2/               # Data preparation, modelling, dashboard (active)
│       ├── data_preperation/ # Scripts to process & prepare data
│       ├── model_trainers/   # Model training pipelines
│       ├── dashboard/        # Streamlit dashboard & tools
│       ├── processed_data/   # Output: cleaned dataset
│       ├── training_data/    # Output: ML-ready datasets
│       ├── models/           # Output: baseline models (.pkl)
│       └── model_runs/       # Output: versioned tuned runs
├── data_summary/             # Data dictionary and analysis
├── notebooks/                # Notebooks (exploration & analysis)
├── project_brief/            # Client brief and presentation artifacts
├── requirements.txt          # Python dependencies (pin as needed)
└── README.md
```

## Quickstart

1) Create venv and install deps
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2) Run the Phase 2 main dashboard
```bash
cd phases/phase2
python main_dashboard.py
```
This interactive CLI orchestrates data prep, model training, comparisons, and opens the dashboard.

## Phase 2 Components (Active)

- data_preperation/
  - process_data.py
    - Reads raw data from ../../data/
    - Cleans dates/times, parses nested pps/rdr dicts, engineers leakage-safe features
    - Writes processed_data/race_data_processed.csv
  - ML_prepare.py
    - Loads processed dataset, encodes categoricals, temporal split, SMOTE, scaling
    - Writes training_data/{train_data.csv,test_data.csv,feature_names.csv,scaler.pkl}
  - validate_no_leakage.py
    - Validates temporal features (rolling excludes current race), correlations, and static-feature baseline
  - check_leakage.py
    - Forensic check of Pnt features for leakage (rank monotonicity, thresholds)

- model_trainers/
  - model.py (Baseline)
    - Trains Logistic Regression, Random Forest, Gradient Boosting
    - Writes models/*.pkl and processed_data/{comparison,feature_importance}.csv
  - model_tuned.py (Recommended)
    - GridSearchCV + threshold optimization to hit Precision ~75%
    - Writes versioned run in model_runs/run_YYYYMMDD_HHMMSS/
  - model_advanced.py (Optional)
    - Adds XGBoost/LightGBM and ensembles if installed

- dashboard/
  - compare_runs.py
    - Aggregates model_runs into a consolidated comparison CSV
  - convert_results_to_dashboard.py
    - Converts comparison CSV to model_results.json
  - model_dashboard.py (Streamlit)
    - Interactive visualization of metrics, thresholds, recommendations

## Data Leakage Guardrails

We prioritize correctness over inflated metrics.
- Temporal split by date (no random shuffle on time data)
- Rolling features use past races only (shift before roll)
- Drop/avoid post-race features (e.g., current-race points)
- validate_no_leakage.py and check_leakage.py must pass before training

## Target & Metrics

- Primary: Precision (target > 75%)
- Secondary: Recall (reasonable to avoid missing talent)
- Also track ROC-AUC and feature importance
- Threshold optimization used to trade precision vs recall

## Typical Workflow

```bash
cd phases/phase2
# 1) Data preparation
python data_preperation/process_data.py
python data_preperation/ML_prepare.py
python data_preperation/validate_no_leakage.py

# 2) Train models
python model_trainers/model_tuned.py

# 3) Compare & visualize
python dashboard/compare_runs.py
python dashboard/convert_results_to_dashboard.py
streamlit run dashboard/model_dashboard.py
```

Or use: `python main_dashboard.py` for an end-to-end menu-driven flow.

## Large Files Policy

- CSV and PKL are gitignored. Regenerate via scripts.
- See `phases/phase2/DATA_FILES_README.md` for regeneration instructions
- If you must track large artifacts, use Git LFS (not required here)

## Data Context (Short)

- race_results (SQLite): 225k+ rows (placements, times, points, stages)  
- rider_infos.csv: 1,042 riders (height, weight, birthdate, country; includes pps/rdr dicts)
- Key engineered features include rider skills (pps_*), rankings (rdr_*), rolling performance, age_at_race, race_tier

## Development Notes

- Use feature branches; do not commit to main directly
- Pin dependencies in requirements.txt as they’re added
- Notebooks are exploratory; scripts in phase2 are the main focus for the pipeline

## For Teammates

Helpful references:
- Model selection map: https://scikit-learn.org/stable/machine_learning_map.html
- Supervised overview: https://scikit-learn.org/stable/supervised_learning.html
- Model evaluation: https://scikit-learn.org/stable/model_selection.html
- Preprocessing: https://scikit-learn.org/stable/modules/preprocessing.html
- Pipelines: https://scikit-learn.org/stable/modules/compose.html#pipeline
- Friendly video series: https://www.youtube.com/@statquest

**Tasks:**
- Identify what “future race performance” means in measurable terms (e.g., race placement, finishing time, probability of finishing in top 10).  
- Define success criteria (e.g., acceptable prediction error, business usefulness).  
- Summarize the client’s goals and the impact on CAICLE’s rider selection strategy.  

**Responsibilities:**
- Translate the business problem into an ML target.  
- Write up the business problem and success criteria.  
- Research similar problems in sports analytics and summarize findings.  

---

## Step 2: Data Understanding (The rest is graded)
**Goal:** Explore the provided race result dataset.  

**Tasks:**
- Inspect the structure of the data (rows, columns, variable types).  
- Identify missing values, inconsistencies, or unusual patterns.  
- Produce descriptive statistics and visualizations.  

**Responsibilities:**
- Load and explore the dataset.  
- Summarize the main observations in text and visuals.  
- Create charts or tables highlighting data quality and patterns.  

---

## Step 3: Data Preparation
**Goal:** Prepare the dataset for modeling.  

**Tasks:**
1. **Data Selection:** Decide which features are relevant and document reasons for inclusion/exclusion.  
2. **Exploratory Data Analysis (EDA):** Summarize key findings and patterns, supported by visualizations.  
3. **Data Cleaning:** Handle missing values, duplicates, and errors.  
4. **Specialization Topic:** Choose one (data cleaning/imputation, dimensionality reduction, or outlier detection). Conduct research and propose methods for applying it to the dataset.  

**Responsibilities:**
- Implement cleaning and preprocessing steps.  
- Generate visualizations and summary statistics for EDA.  
- Research methods relevant to the chosen specialization topic and document a detailed plan for implementation.  
- Prepare an interim presentation with data preparation results and the specialization topic deep dive.  

**Deliverables:**  
- Cleaned dataset ready for modeling.  
- Documented EDA results with visuals.  
- Detailed specialization topic report.  
- Interim presentation for week 7.  

---

## Step 4: Modelling
**Goal:** Build and test machine learning models.  

**Tasks:**  
- Select suitable algorithms (e.g., Linear Regression, Random Forest, Gradient Boosting).  
- Design test methodology (train/test split, cross-validation).  
- Train and evaluate models using appropriate performance metrics (e.g., RMSE for regression, accuracy/F1 for classification).  

**Responsibilities:**  
- Implement and train models.  
- Collect and summarize performance metrics.  
- Research and document algorithm characteristics, advantages, and limitations.  
- Design a testing strategy and interpret results.  

---

## Step 5: Evaluation
**Goal:** Evaluate and optimize the chosen models.  

**Tasks:**  
- Perform hyperparameter tuning (e.g., grid search, random search).  
- Assess robustness and generalizability of models.  
- Compare results against business success criteria.  
- Determine which model(s) best meet CAICLE’s goals.  

**Responsibilities:**  
- Conduct model optimization and record results.  
- Summarize performance comparison in tables or charts.  
- Provide a business-focused explanation of model effectiveness and robustness.  

---

## Step 6: Deployment & Presentation
**Goal:** Deliver a prototype and present results to CAICLE.  

**Tasks:**  
- Build a pipeline from data input to prediction.  
- Prepare the final report and presentation.  
- Present results and explain the reasoning behind all choices.  

**Responsibilities:**  
- Implement the pipeline and demo its functionality.  
- Prepare written report and presentation slides.  
- Communicate results clearly, emphasizing business relevance and insights.  

---

## Suggested Task Division Table

| Step | Task | Responsibilities |
|------|------|-----------------|
| 1. Business Understanding | Define ML problem, success criteria | Translate problem into ML targets, write explanation, research similar problems |
| 2. Data Understanding | Load data, statistics, plots | Explore dataset, summarize observations, create charts/tables |
| 3. Data Preparation | Cleaning, EDA, transformations | Implement preprocessing, generate visualizations, research specialization topic, prepare interim presentation |
| 4. Modelling | Implement and test models | Train models, collect performance metrics, document algorithm details, design test strategy |
| 5. Evaluation | Hyperparameter tuning, metrics | Optimize models, compare results, summarize performance in business terms |
| 6. Deployment & Presentation | Build pipeline, demo, report | Implement pipeline, prepare final report and slides, present results and insights |

## Optional features to get a 10 ranked in order of importance
1. Suggested Priorities for Maximum Impact

2. Build a deployable pipeline that can take new rider data.

3. Include explainable AI elements (SHAP/LIME) to show insights.

4. Create interactive visualizations or dashboards for stakeholders.

5. Add advanced evaluation metrics to show robustness.

6. Experiment with ensembles or stacking to improve predictions.

## Getting Started with adding code and git(for teammates)

### 1. Clone the repository
```sh
git clone <repository-url>
cd <project-folder>
```

### 2. Create and activate a virtual environment
```sh
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```sh
pip install -r requirements.txt
```

## Workflow Guidelines

- **Branching:** Create a new branch for each feature or bugfix.
- **Pull Requests:** Open a pull request for code review before merging to `main`.
- **Commits:** Use clear, descriptive commit messages.
- **.gitignore:** Do not commit your `venv` folder or data files.
- **requirements.txt:** After installing new packages, run `pip freeze > requirements.txt` and commit the changes.

Ive created a file with the data summary that you can feed to an llm to get more insights into the data if you want in here [Data Summary LLM](data_summary.md)

## Usefull docs for teammates
- choosing the right model map:
https://scikit-learn.org/stable/machine_learning_map.html
- overview of supervised models:
https://scikit-learn.org/stable/supervised_learning.html
- choosing right model and evaluation:
https://scikit-learn.org/stable/model_selection.html
- data preprocessing scaling etc data prep:
https://scikit-learn.org/stable/modules/preprocessing.html
- pipelines and composite estimators:
https://scikit-learn.org/stable/modules/compose.html#pipeline

### EASY ML EXPLANATIONS IF YOU DONT UNDERSTAND:
https://www.youtube.com/@statquest
