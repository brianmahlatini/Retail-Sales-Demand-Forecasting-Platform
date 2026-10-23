# Retail Sales & Demand Forecasting Platform

A senior-level full-stack machine learning project that forecasts product-store demand, evaluates time-series and supervised ML models, estimates forecast uncertainty, and recommends inventory actions to reduce stockouts and overstocking.

## Features

- Synthetic daily retail sales generation with products, stores, categories, prices, promotions, holidays, seasonality, and stock levels
- Time-series feature engineering with calendar fields, lag variables, rolling means, and rolling volatility
- Time-based train/test split to prevent future information leaking into model training
- Baseline model: seasonal naive forecasting using previous-week sales
- Statistical model: SARIMA on aggregate daily demand
- Supervised ML baseline: `RandomForestRegressor`
- Stronger supervised ML model: `LightGBMRegressor`
- Prediction intervals using residual quantiles from the holdout set
- Inventory recommendation scoring using model-predicted sales, days of cover, stockout probability, and overstock probability
- FastAPI backend for forecasts, model metrics, feature explanations, and inventory recommendations
- React TypeScript dashboard for actual vs predicted sales, model quality, forecast uncertainty, and replenishment actions
- PostgreSQL schema and Power BI reporting notes

## Tech Stack

### Machine Learning

- Python
- pandas
- NumPy
- scikit-learn
- LightGBM
- statsmodels
- joblib

### Backend

- FastAPI
- Uvicorn
- pytest

### Frontend

- React
- TypeScript
- Vite
- Recharts
- Lucide React

### Database & Reporting

- PostgreSQL schema
- Docker Compose
- Power BI report design notes

## Project Structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- main.py
|   |   |-- db/
|   |   |   |-- schema.sql
|   |   |-- ml/
|   |   |   |-- artifacts/
|   |   |   |-- features.py
|   |   |   |-- prediction_model.py
|   |-- scripts/
|   |   |-- train_model.py
|   |-- tests/
|   |   |-- test_api.py
|   |   |-- test_features.py
|   |-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- App.tsx
|   |   |-- main.tsx
|   |   |-- components/
|   |   |-- services/
|   |   |-- styles/
|   |-- package.json
|   |-- tsconfig.json
|   |-- vite.config.ts
|-- infra/
|   |-- docker-compose.yml
|-- reports/
|   |-- powerbi_model_notes.md
|-- .gitignore
|-- README.md
```

## ML Design

### Dataset

The training script generates a deterministic retail demand dataset with:

- Product profile: product ID, product name, category, base price
- Store profile: store ID, store name, store type, demand multiplier
- Commercial signals: price, discount percentage, promotion flag
- Calendar signals: day of week, week of year, month, quarter, weekend flag, holiday flag, annual seasonality
- Inventory signal: stock on hand
- Demand label: daily unit sales

Latest generated dataset:

| Raw Rows | Supervised Rows | Products | Stores | Date Range |
|---:|---:|---:|---:|---|
| 82,140 | 80,460 | 12 | 5 | 2023-01-01 to 2026-09-30 |

### Features X

The supervised models use product-store-day features:

- Price and discount features
- Promotion and holiday indicators
- Current stock on hand
- Calendar and cyclical seasonality features
- Encoded category and store type
- Previous demand lags: `lag_7`, `lag_14`, `lag_28`
- Rolling demand statistics: 7, 14, and 28 day rolling means plus 7 day rolling standard deviation

### Target y

`sales_units` is the daily number of units sold for a specific product and store.

### Models Trained

- `Seasonal Naive` baseline
- `SARIMA Aggregate` statistical model
- `RandomForestRegressor` supervised ML baseline
- `LightGBMRegressor` stronger supervised ML model

Latest training run:

| Model | MAE | RMSE | WAPE | Forecast Bias |
|---|---:|---:|---:|---:|
| Seasonal Naive | 19.63 | 26.17 | 23.20% | -1.10% |
| SARIMA Aggregate | 263.03 | 417.47 | 5.18% | -4.56% |
| RandomForestRegressor | 9.27 | 12.06 | 10.95% | -1.56% |
| LightGBMRegressor | 8.79 | 11.26 | 10.38% | -1.27% |

Selected runtime model: `LightGBMRegressor`.

SARIMA is evaluated on aggregate daily demand, while RandomForest and LightGBM are row-level product-store supervised models.

Artifacts are saved to:

- `backend/app/ml/artifacts/demand_model.joblib`
- `backend/app/ml/artifacts/metrics.json`
- `backend/app/ml/artifacts/retail_sales_history.csv`
- `backend/app/ml/artifacts/forecast_sample.json`
- `backend/app/ml/artifacts/inventory_recommendations.json`

## Inventory Recommendations

The recommendation layer uses the trained model's predicted demand as the ranking input. It calculates:

- Predicted daily sales
- Prediction lower and upper bounds
- Days of stock cover
- Stockout probability
- Overstock probability
- Recommended action

Actions returned by the API:

- `Reorder soon`
- `Reduce replenishment`
- `Maintain plan`

## Local Setup

### 1. Backend

```bash
python -m pip install -r backend/requirements.txt
python backend/scripts/train_model.py
uvicorn app.main:app --app-dir backend --reload
```

Backend API:

```text
http://localhost:8000/health
```

Optional PostgreSQL service:

```bash
docker compose -f infra/docker-compose.yml up -d
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend dashboard:

```text
http://localhost:5173
```

Set `VITE_API_BASE_URL` if the API runs on a different port.

## API Endpoints

- `GET /health`
- `GET /model/features`
- `GET /model/metrics`
- `GET /forecasts?limit=600`
- `GET /recommendations?limit=60`

The recommendation response includes:

- Product and store profile
- Model-predicted sales
- Current stock on hand
- Days of cover
- Stockout probability
- Overstock probability
- Inventory action

## Retraining

Run:

```bash
python backend/scripts/train_model.py
```

This regenerates:

- Synthetic retail sales dataset
- Feature matrix
- Seasonal naive baseline
- SARIMA aggregate model comparison
- RandomForest baseline
- LightGBM stronger model
- Model comparison metrics
- Forecast sample with uncertainty bounds
- Inventory recommendation queue
- Saved model artifacts

## Testing

```bash
pytest backend/tests
```

Frontend production build:

```bash
cd frontend
npm run build
```

## Repository

Owner: `brianmahlatini`

Repository: `Retail-Sales-Demand-Forecasting-Platform`

GitHub: [Retail-Sales-Demand-Forecasting-Platform](https://github.com/brianmahlatini/Retail-Sales-Demand-Forecasting-Platform)

