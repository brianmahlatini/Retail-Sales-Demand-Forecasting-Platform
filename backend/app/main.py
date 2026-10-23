from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.ml.prediction_model import (
    explain_features,
    load_dashboard_forecast,
    load_inventory_recommendations,
    load_metrics,
)


app = FastAPI(
    title="Retail Sales & Demand Forecasting API",
    description="Supervised ML API for sales forecasts and inventory recommendations.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/model/metrics")
def metrics() -> dict:
    return load_metrics()


@app.get("/model/features")
def features() -> dict:
    return explain_features()


@app.get("/forecasts")
def forecasts(limit: int = Query(default=240, ge=1, le=2000)) -> list[dict]:
    return load_dashboard_forecast(limit=limit)


@app.get("/recommendations")
def recommendations(limit: int = Query(default=50, ge=1, le=500)) -> list[dict]:
    return load_inventory_recommendations(limit=limit)

