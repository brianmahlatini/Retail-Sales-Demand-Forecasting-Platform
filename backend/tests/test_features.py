import pandas as pd

from app.ml.features import FEATURE_COLUMNS, build_supervised_frame, generate_retail_sales_data, time_based_split


def test_feature_engineering_creates_supervised_columns():
    df = generate_retail_sales_data(start_date="2024-01-01", end_date="2024-03-15", seed=7)
    supervised = build_supervised_frame(df)

    assert not supervised.empty
    assert set(FEATURE_COLUMNS).issubset(supervised.columns)
    assert supervised[FEATURE_COLUMNS].isna().sum().sum() == 0
    assert "sales_units" in supervised.columns


def test_time_split_keeps_future_out_of_training():
    frame = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=120), "sales_units": range(120)})
    train, test = time_based_split(frame, test_days=30)

    assert train["date"].max() < test["date"].min()
    assert len(test) == 30

