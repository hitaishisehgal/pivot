# PIVOT

**Student Performance Intelligence and Prediction System Using Multi-Task Deep Neural Networks**

PIVOT is a research prototype for estimating final Portuguese course grades and performance bands using independent full-information and early-prediction models, a FastAPI service, and a Streamlit interface designed for educator decision support.

## Environment & Dataset

Target runtime is Python **3.11+** (verified on Python 3.11 in CI and CPython 3.13.7 locally). Setup via PowerShell:
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
The UCI Portuguese dataset resides at `data/raw/student-por.csv` (see `data/README.md`). Validate it with:
```powershell
python -c "from src.data.ingestion import load_dataset; print(load_dataset().shape)"
```

## Training, API, and Operations

* **Training & Evaluation:** Execute training, ablation, feature analysis, and fairness scripts via `python -m src.training.train` and related modules. Results export to `reports/experiments/training_results.json` and artifacts to `artifacts/versions`.
* **API & App:** Launch FastAPI (`uvicorn api.main:app --reload`, docs at `/docs`) and Streamlit (`streamlit run app/streamlit_app.py`). Endpoints cover prediction, batch evaluation, scenarios, student profiles, and history.
* **Database & Tracking:** Configure MongoDB Atlas via `.env` for prediction history (no local fallback). Track experiments locally using MLflow:
  ```powershell
  mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts
  ```
* **Tests & Checks:** Run compilation and test suites:
  ```powershell
  python -m compileall -q src api app
  python -m pytest -q
  ```
  *(Mongo integration tests can be enabled using `\$env:PIVOT_RUN_MONGO_TESTS = "1"` alongside `tests/test_database.py`).* GitHub Actions automatically installs Python 3.11 dependencies and executes test/import checks.

## Repository Structure & Documentation

* `notebooks/`, `src/data/`, `src/preprocessing/`, `src/models/`, `src/training/`, `src/evaluation/`: Core pipelines and research notebooks.
* `api/` & `app/streamlit_app.py`: Service endpoints and the multi-page dashboard.
* `reports/`: Review `reports/model_card.md` for ethical/limitations guidelines and `reports/leakage_audit.md` for leakage checks. See `IMPLEMENTATION_STATUS.md` for project completion tracking.
