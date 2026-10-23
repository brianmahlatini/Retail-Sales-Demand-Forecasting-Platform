CREATE TABLE IF NOT EXISTS retail_sales (
    sale_date DATE NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    store_id TEXT NOT NULL,
    store_name TEXT NOT NULL,
    store_type TEXT NOT NULL,
    base_price NUMERIC(10, 2) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    discount_pct NUMERIC(5, 4) NOT NULL,
    promo_flag BOOLEAN NOT NULL,
    holiday_flag BOOLEAN NOT NULL,
    stock_on_hand INTEGER NOT NULL,
    sales_units INTEGER NOT NULL,
    PRIMARY KEY (sale_date, product_id, store_id)
);

CREATE TABLE IF NOT EXISTS demand_forecasts (
    forecast_date DATE NOT NULL,
    product_id TEXT NOT NULL,
    store_id TEXT NOT NULL,
    predicted_sales NUMERIC(12, 2) NOT NULL,
    prediction_lower NUMERIC(12, 2) NOT NULL,
    prediction_upper NUMERIC(12, 2) NOT NULL,
    model_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (forecast_date, product_id, store_id, model_name)
);

