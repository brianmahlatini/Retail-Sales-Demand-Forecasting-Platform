from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PRODUCT_CATALOG = [
    ("P001", "Essentials Rice 2kg", "Grocery", 31.99),
    ("P002", "Sunrise Cereal 750g", "Grocery", 54.99),
    ("P003", "Fresh Milk 2L", "Dairy", 39.99),
    ("P004", "Greek Yogurt 1kg", "Dairy", 69.99),
    ("P005", "Laundry Detergent 2kg", "Household", 119.99),
    ("P006", "Dish Soap 750ml", "Household", 34.99),
    ("P007", "Premium Coffee 250g", "Beverage", 89.99),
    ("P008", "Sparkling Water 6pk", "Beverage", 49.99),
    ("P009", "Frozen Pizza", "Frozen", 74.99),
    ("P010", "Frozen Veg Mix 1kg", "Frozen", 45.99),
    ("P011", "Baby Wipes 80ct", "Personal Care", 42.99),
    ("P012", "Shampoo 400ml", "Personal Care", 64.99),
]

STORE_CATALOG = [
    ("S001", "Cape Town Central", "Urban", 1.20),
    ("S002", "Johannesburg North", "Urban", 1.35),
    ("S003", "Durban Beach", "Coastal", 1.05),
    ("S004", "Pretoria East", "Suburban", 0.95),
    ("S005", "Bloemfontein Mall", "Regional", 0.78),
]

CATEGORY_SEASONALITY = {
    "Grocery": 1.05,
    "Dairy": 0.90,
    "Household": 0.70,
    "Beverage": 1.25,
    "Frozen": 1.10,
    "Personal Care": 0.65,
}

FEATURE_COLUMNS = [
    "base_price",
    "price",
    "discount_pct",
    "promo_flag",
    "holiday_flag",
    "stock_on_hand",
    "day_of_week",
    "week_of_year",
    "month",
    "quarter",
    "is_weekend",
    "day_of_year_sin",
    "day_of_year_cos",
    "category_code",
    "store_type_code",
    "lag_7",
    "lag_14",
    "lag_28",
    "rolling_7_mean",
    "rolling_14_mean",
    "rolling_28_mean",
    "rolling_7_std",
]


def generate_retail_sales_data(
    output_path: str | Path | None = None,
    start_date: str = "2023-01-01",
    end_date: str = "2026-09-30",
    seed: int = 42,
) -> pd.DataFrame:
    """Create a synthetic retail sales dataset with seasonality and promotions."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start_date, end_date, freq="D")
    rows: list[dict[str, object]] = []

    holiday_windows = {(1, 1), (3, 21), (4, 27), (5, 1), (6, 16), (8, 9), (9, 24), (12, 16), (12, 25)}

    for product_idx, (product_id, product_name, category, base_price) in enumerate(PRODUCT_CATALOG):
        category_strength = CATEGORY_SEASONALITY[category]
        product_popularity = rng.uniform(0.75, 1.45)
        for store_idx, (store_id, store_name, store_type, store_multiplier) in enumerate(STORE_CATALOG):
            baseline = rng.uniform(16, 54) * product_popularity * store_multiplier
            inventory = int(rng.integers(120, 360))

            for date in dates:
                day_of_year = date.dayofyear
                is_weekend = int(date.dayofweek >= 5)
                holiday_flag = int((date.month, date.day) in holiday_windows)
                promo_flag = int(rng.random() < (0.18 if is_weekend else 0.10))
                discount_pct = float(rng.choice([0, 0.05, 0.10, 0.15, 0.20], p=[0.58, 0.14, 0.12, 0.10, 0.06]))
                if promo_flag:
                    discount_pct = max(discount_pct, float(rng.choice([0.10, 0.15, 0.20])))

                annual = 1 + category_strength * 0.16 * np.sin((2 * np.pi * day_of_year / 365) + product_idx / 3)
                weekly = 1 + (0.18 * is_weekend) - (0.04 * int(date.dayofweek == 1))
                holiday_lift = 1 + (0.30 * holiday_flag)
                promo_lift = 1 + (1.9 * discount_pct) + (0.22 * promo_flag)
                trend = 1 + (0.00045 * (date - dates[0]).days) + (0.015 * store_idx)
                noise = rng.normal(0, 5.5)
                expected_sales = max(2, baseline * annual * weekly * holiday_lift * promo_lift * trend + noise)
                sales_units = int(max(0, rng.poisson(expected_sales)))

                inventory = max(0, inventory + int(rng.integers(10, 45)) - sales_units)
                stock_on_hand = int(inventory + rng.integers(20, 90))
                price = round(base_price * (1 - discount_pct), 2)

                rows.append(
                    {
                        "date": date,
                        "product_id": product_id,
                        "product_name": product_name,
                        "category": category,
                        "store_id": store_id,
                        "store_name": store_name,
                        "store_type": store_type,
                        "base_price": round(base_price, 2),
                        "price": price,
                        "discount_pct": discount_pct,
                        "promo_flag": promo_flag,
                        "holiday_flag": holiday_flag,
                        "stock_on_hand": stock_on_hand,
                        "sales_units": sales_units,
                    }
                )

    df = pd.DataFrame(rows)
    if output_path is not None:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output, index=False)
    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    output = df.copy()
    output["date"] = pd.to_datetime(output["date"])
    iso = output["date"].dt.isocalendar()
    output["day_of_week"] = output["date"].dt.dayofweek
    output["week_of_year"] = iso.week.astype(int)
    output["month"] = output["date"].dt.month
    output["quarter"] = output["date"].dt.quarter
    output["is_weekend"] = (output["day_of_week"] >= 5).astype(int)
    day_of_year = output["date"].dt.dayofyear
    output["day_of_year_sin"] = np.sin(2 * np.pi * day_of_year / 365.25)
    output["day_of_year_cos"] = np.cos(2 * np.pi * day_of_year / 365.25)
    output["category_code"] = output["category"].astype("category").cat.codes
    output["store_type_code"] = output["store_type"].astype("category").cat.codes
    return output


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    output = df.sort_values(["product_id", "store_id", "date"]).copy()
    group = output.groupby(["product_id", "store_id"], sort=False)["sales_units"]
    for lag in (7, 14, 28):
        output[f"lag_{lag}"] = group.shift(lag)
    shifted = group.shift(1)
    output["rolling_7_mean"] = shifted.groupby([output["product_id"], output["store_id"]]).rolling(7).mean().reset_index(level=[0, 1], drop=True)
    output["rolling_14_mean"] = shifted.groupby([output["product_id"], output["store_id"]]).rolling(14).mean().reset_index(level=[0, 1], drop=True)
    output["rolling_28_mean"] = shifted.groupby([output["product_id"], output["store_id"]]).rolling(28).mean().reset_index(level=[0, 1], drop=True)
    output["rolling_7_std"] = shifted.groupby([output["product_id"], output["store_id"]]).rolling(7).std().reset_index(level=[0, 1], drop=True)
    return output


def build_supervised_frame(df: pd.DataFrame) -> pd.DataFrame:
    featured = add_lag_features(add_time_features(df))
    return featured.dropna(subset=FEATURE_COLUMNS + ["sales_units"]).reset_index(drop=True)


def time_based_split(df: pd.DataFrame, test_days: int = 90) -> tuple[pd.DataFrame, pd.DataFrame]:
    cutoff = pd.to_datetime(df["date"]).max() - pd.Timedelta(days=test_days)
    train = df[df["date"] <= cutoff].copy()
    test = df[df["date"] > cutoff].copy()
    return train, test


def compute_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    errors = y_true - y_pred
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(np.square(errors))))
    wape = float(np.sum(np.abs(errors)) / max(np.sum(np.abs(y_true)), 1))
    bias = float(np.sum(y_pred - y_true) / max(np.sum(y_true), 1))
    return {"MAE": mae, "RMSE": rmse, "WAPE": wape, "Forecast Bias": bias}

