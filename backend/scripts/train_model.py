from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from statsmodels.tsa.statespace.sarimax import SARIMAX

try:
    from lightgbm import LGBMRegressor
except Exception:  # pragma: no cover - optional dependency fallback
    LGBMRegressor = None

from app.ml.features import (
    FEATURE_COLUMNS,
    build_supervised_frame,
    compute_regression_metrics,
    generate_retail_sales_data,
    time_based_split,
)


ARTIFACT_DIR = BACKEND / "app" / "ml" / "artifacts"
DATA_PATH = ARTIFACT_DIR / "retail_sales_history.csv"
MODEL_PATH = ARTIFACT_DIR / "demand_model.joblib"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"
FORECAST_PATH = ARTIFACT_DIR / "forecast_sample.json"
RECOMMENDATIONS_PATH = ARTIFACT_DIR / "inventory_recommendations.json"


def train() -> dict:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    raw = generate_retail_sales_data(DATA_PATH)
    supervised = build_supervised_frame(raw)
    train_df, test_df = time_based_split(supervised, test_days=90)

    x_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["sales_units"].to_numpy()
    x_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["sales_units"].to_numpy()

    seasonal_naive_pred = test_df["lag_7"].to_numpy()
    models = {
        "Seasonal Naive": seasonal_naive_pred,
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=120,
            max_depth=18,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        ),
    }

    if LGBMRegressor is not None:
        boosted_model_name = "LightGBMRegressor"
        boosted_model = LGBMRegressor(
            objective="regression",
            n_estimators=350,
            learning_rate=0.045,
            num_leaves=48,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            verbose=-1,
        )
    else:
        boosted_model_name = "GradientBoostingRegressor"
        boosted_model = GradientBoostingRegressor(
            n_estimators=260,
            learning_rate=0.045,
            max_depth=4,
            random_state=42,
        )
    models[boosted_model_name] = boosted_model

    predictions: dict[str, np.ndarray] = {"Seasonal Naive": seasonal_naive_pred}
    metrics: dict[str, dict[str, float]] = {
        "Seasonal Naive": compute_regression_metrics(y_test, seasonal_naive_pred)
    }
    aggregate_train = train_df.groupby("date", as_index=True)["sales_units"].sum().asfreq("D")
    aggregate_test = test_df.groupby("date", as_index=True)["sales_units"].sum().asfreq("D")
    sarima = SARIMAX(
        aggregate_train,
        order=(1, 0, 1),
        seasonal_order=(1, 1, 1, 7),
        enforce_stationarity=False,
        enforce_invertibility=False,
    ).fit(method="powell", maxiter=80, disp=False)
    sarima_pred = np.maximum(0, sarima.forecast(steps=len(aggregate_test)).to_numpy())
    metrics["SARIMA Aggregate"] = compute_regression_metrics(aggregate_test.to_numpy(), sarima_pred)

    trained_models = {}
    for name, model in models.items():
        if isinstance(model, np.ndarray):
            continue
        model.fit(x_train, y_train)
        pred = np.maximum(0, model.predict(x_test))
        trained_models[name] = model
        predictions[name] = pred
        metrics[name] = compute_regression_metrics(y_test, pred)

    row_level_model_names = ["Seasonal Naive", "RandomForestRegressor", boosted_model_name]
    best_model_name = min(row_level_model_names, key=lambda model_name: metrics[model_name]["RMSE"])
    if best_model_name in {"Seasonal Naive", "SARIMA Aggregate"}:
        best_model_name = boosted_model_name
    best_model = trained_models[best_model_name]
    best_predictions = predictions[best_model_name]
    residuals = y_test - best_predictions
    residual_quantiles = {
        "p10": float(np.quantile(residuals, 0.10)),
        "p90": float(np.quantile(residuals, 0.90)),
    }

    bundle = {
        "model": best_model,
        "model_name": best_model_name,
        "feature_columns": FEATURE_COLUMNS,
        "target": "sales_units",
        "residual_quantiles": residual_quantiles,
        "training_window": {
            "min_date": str(train_df["date"].min().date()),
            "max_date": str(train_df["date"].max().date()),
            "test_start": str(test_df["date"].min().date()),
            "test_end": str(test_df["date"].max().date()),
        },
    }
    joblib.dump(bundle, MODEL_PATH)

    forecast = test_df[
        ["date", "product_id", "product_name", "category", "store_id", "store_name", "stock_on_hand", "sales_units"]
    ].copy()
    forecast["predicted_sales"] = best_predictions.round(2)
    forecast["prediction_lower"] = np.maximum(0, best_predictions + residual_quantiles["p10"]).round(2)
    forecast["prediction_upper"] = np.maximum(0, best_predictions + residual_quantiles["p90"]).round(2)
    forecast["date"] = forecast["date"].dt.strftime("%Y-%m-%d")
    forecast.sort_values(["date", "store_id", "product_id"]).tail(900).to_json(FORECAST_PATH, orient="records", indent=2)

    latest = forecast.sort_values("date").groupby(["product_id", "store_id"], as_index=False).tail(1).copy()
    latest["days_of_cover"] = latest["stock_on_hand"] / latest["predicted_sales"].clip(lower=1)
    latest["stockout_probability"] = (1 / (1 + np.exp((latest["days_of_cover"] - 7) / 2))).round(4)
    latest["overstock_probability"] = (1 / (1 + np.exp(-(latest["days_of_cover"] - 28) / 6))).round(4)
    latest["recommendation"] = np.select(
        [latest["stockout_probability"] >= 0.60, latest["overstock_probability"] >= 0.60],
        ["Reorder soon", "Reduce replenishment"],
        default="Maintain plan",
    )
    latest[
        [
            "product_id",
            "product_name",
            "category",
            "store_id",
            "store_name",
            "stock_on_hand",
            "predicted_sales",
            "days_of_cover",
            "stockout_probability",
            "overstock_probability",
            "recommendation",
        ]
    ].sort_values(["stockout_probability", "overstock_probability"], ascending=False).to_json(
        RECOMMENDATIONS_PATH, orient="records", indent=2
    )

    metrics_payload = {
        "best_model": best_model_name,
        "models_trained": list(metrics.keys()),
        "metrics": metrics,
        "feature_columns": FEATURE_COLUMNS,
        "target": "sales_units",
        "dataset": {
            "rows_raw": int(len(raw)),
            "rows_supervised": int(len(supervised)),
            "products": int(raw["product_id"].nunique()),
            "stores": int(raw["store_id"].nunique()),
            "date_min": str(raw["date"].min().date()),
            "date_max": str(raw["date"].max().date()),
        },
        "prediction_intervals": "Residual p10/p90 quantiles from the time-based holdout set.",
        "statistical_model_note": "SARIMA is evaluated on aggregate daily demand, while RandomForest and LightGBM are row-level product-store supervised models.",
    }
    METRICS_PATH.write_text(json.dumps(metrics_payload, indent=2))
    return metrics_payload


if __name__ == "__main__":
    payload = train()
    print(json.dumps(payload, indent=2))

