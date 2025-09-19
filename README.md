# ML-Project
## Getting Started (for teammates)

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

## Folder Structure initially
```
project-folder/ 
│
├── src/            # Source code
├── data/           # Data files (not tracked by git)
├── notebooks/      # Jupyter notebooks
├── requirements.txt
├── .gitignore
└── README.md
```