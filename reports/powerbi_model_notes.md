# Power BI Report Design Notes

## Pages

- Executive overview: total forecast demand, WAPE, bias, stockout risks, and overstock risks
- Forecast accuracy: actual vs predicted sales by date, category, product, and store
- Inventory actions: reorder soon, reduce replenishment, and maintain plan queues
- Model monitoring: MAE, RMSE, WAPE, forecast bias, and selected model

## Suggested Tables

- `retail_sales`
- `demand_forecasts`
- `inventory_recommendations`
- `model_metrics`

## Suggested Measures

- Total actual units
- Total predicted units
- Forecast error
- Absolute forecast error
- WAPE
- Forecast bias
- Average days of cover
- Stockout risk count
- Overstock risk count

