from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from app.ml.features import FEATURE_COLUMNS, build_supervised_frame


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "demand_model.joblib"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"
HISTORY_PATH = ARTIFACT_DIR / "retail_sales_history.csv"
FORECAST_PATH = ARTIFACT_DIR / "forecast_sample.json"
RECOMMENDATIONS_PATH = ARTIFACT_DIR / "inventory_recommendations.json"


class DemandForecastService:
    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        if not model_path.exists():
            raise FileNotFoundError(
                f"Missing model artifact at {model_path}. Run `python backend/scripts/train_model.py` first."
            )
        self.bundle: dict[str, Any] = joblib.load(model_path)
        self.model = self.bundle["model"]
        self.feature_columns = self.bundle["feature_columns"]
        self.residual_quantiles = self.bundle["residual_quantiles"]

    def predict_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        featured = build_supervised_frame(frame)
        predictions = self.model.predict(featured[self.feature_columns])
        lower = np.maximum(0, predictions + self.residual_quantiles["p10"])
        upper = np.maximum(0, predictions + self.residual_quantiles["p90"])
        output = featured[
            ["date", "product_id", "product_name", "category", "store_id", "store_name", "stock_on_hand", "sales_units"]
        ].copy()
        output["predicted_sales"] = np.maximum(0, predictions).round(2)
        output["prediction_lower"] = lower.round(2)
        output["prediction_upper"] = upper.round(2)
        return output


def load_metrics() -> dict[str, Any]:
    if not METRICS_PATH.exists():
        return {}
    return json.loads(METRICS_PATH.read_text())


def load_dashboard_forecast(limit: int = 240) -> list[dict[str, Any]]:
    if not FORECAST_PATH.exists():
        return []
    data = json.loads(FORECAST_PATH.read_text())
    return data[:limit]


def load_inventory_recommendations(limit: int = 50) -> list[dict[str, Any]]:
    if not RECOMMENDATIONS_PATH.exists():
        return []
    data = json.loads(RECOMMENDATIONS_PATH.read_text())
    return data[:limit]


def explain_features() -> dict[str, Any]:
    return {
        "target": "sales_units",
        "features": FEATURE_COLUMNS,
        "prediction": "Expected daily unit sales for a product-store-date row, with residual-based uncertainty bounds.",
    }

