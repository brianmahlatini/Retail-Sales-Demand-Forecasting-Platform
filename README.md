# Retail Sales & Demand Forecasting Platform

[brianmahlatini](https://github.com/brianmahlatini) / [Retail-Sales-Demand-Forecasting-Platform](https://github.com/brianmahlatini/Retail-Sales-Demand-Forecasting-Platform)

## Repository Navigation

- [Code](https://github.com/brianmahlatini/Retail-Sales-Demand-Forecasting-Platform)
- [Issues](https://github.com/brianmahlatini/Retail-Sales-Demand-Forecasting-Platform/issues)
- [Pull Requests](https://github.com/brianmahlatini/Retail-Sales-Demand-Forecasting-Platform/pulls)
- [Actions](https://github.com/brianmahlatini/Retail-Sales-Demand-Forecasting-Platform/actions)
- [Projects](https://github.com/brianmahlatini/Retail-Sales-Demand-Forecasting-Platform/projects)
- [Wiki](https://github.com/brianmahlatini/Retail-Sales-Demand-Forecasting-Platform/wiki)
- [Security and Quality](https://github.com/brianmahlatini/Retail-Sales-Demand-Forecasting-Platform/security)

## Objective

This project predicts future retail sales by product, store, category, and time period so planners can reduce stockouts and overstocking. It combines generated historical sales with prices, promotions, holidays, seasonality, lag variables, rolling averages, and inventory levels.

## Senior-Level ML Implementation

This is not a rule-only or keyword-based project. The forecasting and recommendation workflow uses supervised regression models trained on a time-series retail dataset.

**Target variable:** `sales_units`

**Input features X include:**

- Price and discount fields: `base_price`, `price`, `discount_pct`
- Promotion and holiday indicators: `promo_flag`, `holiday_flag`
- Inventory signal: `stock_on_hand`
- Calendar features: day of week, week of year, month, quarter, weekend flag, yearly sine/cosine seasonality
- Encoded context: category and store type codes
- Time-series demand history: `lag_7`, `lag_14`, `lag_28`
- Rolling demand features: 7, 14, and 28 day rolling means plus rolling standard deviation

**Models trained:**

- Seasonal naive baseline using previous-week sales
- SARIMA statistical model for aggregate daily demand
- `RandomForestRegressor` baseline supervised ML model
- `LightGBMRegressor` stronger boosted model when LightGBM is installed
- `GradientBoostingRegressor` fallback if LightGBM is unavailable

**Evaluation metrics:**

- MAE
- RMSE
- WAPE
- Forecast bias

**Prediction intervals:** residual p10/p90 quantiles from the time-based holdout set are applied to the best model's predictions.

## Recommendations

Inventory recommendations are ranked using model-predicted demand. The backend calculates days of cover, stockout probability, and overstock probability from forecasted sales and current stock. The UI clearly shows the predicted demand and the resulting inventory action:

- `Reorder soon`
- `Reduce replenishment`
- `Maintain plan`

## Project Structure

```text
backend/
  app/
    main.py
    db/
      schema.sql
    ml/
      features.py
      prediction_model.py
      artifacts/
  scripts/
    train_model.py
  tests/
frontend/
  src/
    components/
    services/
    styles/
infra/
  docker-compose.yml
README.md
```

## Run Locally

Create the backend environment:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

Train the models and generate artifacts:

```bash
python backend/scripts/train_model.py
```

Start the API:

```bash
uvicorn app.main:app --app-dir backend --reload
```

Optional PostgreSQL service:

```bash
docker compose -f infra/docker-compose.yml up -d
```

Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

The dashboard reads from `http://localhost:8000` by default. Set `VITE_API_BASE_URL` if the API runs elsewhere.

## Testing and Build

Backend tests:

```bash
pytest backend/tests
```

Frontend build:

```bash
cd frontend
npm run build
```

## API Endpoints

- `GET /health`
- `GET /model/features`
- `GET /model/metrics`
- `GET /forecasts`
- `GET /recommendations`

## Retraining

Run:

```bash
python backend/scripts/train_model.py
```

The script regenerates the dataset, builds supervised features, performs a time-based train/test split, trains the baseline and boosted models, evaluates them, and writes:

- `backend/app/ml/artifacts/demand_model.joblib`
- `backend/app/ml/artifacts/metrics.json`
- `backend/app/ml/artifacts/retail_sales_history.csv`
- `backend/app/ml/artifacts/forecast_sample.json`
- `backend/app/ml/artifacts/inventory_recommendations.json`

