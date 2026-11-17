# PIVOT

**Student Performance Intelligence and Prediction System Using Multi-Task Deep Neural Networks**

PIVOT is a research prototype for estimating final Portuguese course grades and performance bands. It contains independent full-information and early-prediction models, a FastAPI service and a Streamlit interface. Outputs are decision support for educators, not automated student decisions.

## Environment

Target runtime is Python **3.13.7**. A CPython 3.13.7 interpreter was verified in the workspace. The dependency set is pinned in `requirements.txt`; TensorFlow 2.20.0 installed successfully with Python 3.13 on this Windows environment. Create/reuse an environment from PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `.venv` already exists, activate it and install requirements. No Python downgrade is needed.

## Dataset

The original UCI Portuguese CSV is kept unchanged at `data/raw/student-por.csv`. Provenance and limitations are in [data/README.md](data/README.md). To validate it:

```powershell
python -c "from src.data.ingestion import load_dataset; print(load_dataset().shape)"
```

## Train and evaluate

```powershell
python -m src.training.train
python -m src.training.train --ablation
```

The first command trains separate Random Forest regression/classification baselines and separate multi-task DNNs for both modes. The optional ablation command trains the specified hidden widths/dropout variants. Models and preprocessors go under `artifacts/versions`; measured results are written to `reports/experiments/training_results.json`. Development cross-validation is stratified by G3 category. The 20% test split is held out from fitting and scored after model fit. Re-run only when intentionally replacing artifacts/results.

## API and app

Start API:

```powershell
uvicorn api.main:app --reload
```

Open API documentation at `http://127.0.0.1:8000/docs`. Start the six-page app in another shell:

```powershell
streamlit run app/streamlit_app.py
```

Set `PIVOT_API_URL` only when the API is not at its default local address. `/predict`, `/predict/batch`, `/scenario`, `/students`, and `/health` are available. Both modes select independent versioned RF artifacts as the API baseline. The API reports explicit head disagreement.

## MongoDB Atlas and MLflow

Copy `.env.example` to `.env`, fill in an Atlas URI and database name, and load environment variables before starting the API. No credentials belong in source control. The application does not start a local database fallback. Prediction history is available only when Atlas is configured and reachable.

MLflow uses local SQLite metadata and local artifacts:

```powershell
$env:MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"
mlflow ui
```

## Tests and checks

```powershell
python -m compileall -q src api app
pytest -q
```

The Atlas test uses a separate `pivot_test` database and one temporary marker record:

```powershell
$env:PIVOT_RUN_MONGO_TESTS = "1"
python -c "from dotenv import dotenv_values; import os,pytest; os.environ.update({k:v for k,v in dotenv_values('atlas-credentials.env').items() if v}); raise SystemExit(pytest.main(['-q','tests/test_database.py']))"
```

GitHub Actions installs Python 3.13.7 dependencies and runs import compilation/tests without retraining models or downloading data.

## Repository map

- `src/data`: ingestion, schema validation and stratified split
- `src/preprocessing`: feature contracts and fold-fitted transformers
- `src/models`, `src/training`: multi-task Keras network and training entry point
- `src/evaluation`: metrics, calibration helper, fairness and feature analysis
- `api`: prediction, batch, scenario and history endpoints
- `app/streamlit_app.py`: Overview, Student, Simulator, Educator, Batch Analytics and Research Lab
- `artifacts/versions`: versioned learned model bundles
- `reports/model_card.md`: intended use, limitations and ethical considerations

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for verified completion and remaining gaps. Dataset acquisition and run results must not be represented as completed unless backed by the files and commands recorded there.
