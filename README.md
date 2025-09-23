# MA01 Machine Learning Group Project - CAICLE

This document outlines the steps, tasks, and responsibilities for the group project focused on predicting professional cycling performance for CAICLE.

---

## Step 1: Business Understanding
**Goal:** Understand CAICLE’s needs and define the machine learning problem clearly.  

**Tasks:**
- Identify what “future race performance” means in measurable terms (e.g., race placement, finishing time, probability of finishing in top 10).  
- Define success criteria (e.g., acceptable prediction error, business usefulness).  
- Summarize the client’s goals and the impact on CAICLE’s rider selection strategy.  

**Responsibilities:**
- Translate the business problem into an ML target.  
- Write up the business problem and success criteria.  
- Research similar problems in sports analytics and summarize findings.  

---

## Step 2: Data Understanding
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
