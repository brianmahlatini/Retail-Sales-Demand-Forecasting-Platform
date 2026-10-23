import { Activity, Boxes, Gauge, Target } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { ForecastChart } from "./components/ForecastChart";
import { KpiCard } from "./components/KpiCard";
import { RecommendationTable } from "./components/RecommendationTable";
import { api, type ForecastRow, type Recommendation } from "./services/api";
import "./styles/app.css";

export default function App() {
  const [forecasts, setForecasts] = useState<ForecastRow[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [features, setFeatures] = useState<any>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    Promise.all([api.forecasts(), api.recommendations(), api.metrics(), api.features()])
      .then(([forecastRows, recommendationRows, metricPayload, featurePayload]) => {
        setForecasts(forecastRows);
        setRecommendations(recommendationRows);
        setMetrics(metricPayload);
        setFeatures(featurePayload);
      })
      .catch((err) => setError(err.message));
  }, []);

  const bestMetrics = metrics?.metrics?.[metrics?.best_model];
  const stockoutCount = useMemo(
    () => recommendations.filter((row) => row.recommendation === "Reorder soon").length,
    [recommendations],
  );
  const overstockCount = useMemo(
    () => recommendations.filter((row) => row.recommendation === "Reduce replenishment").length,
    [recommendations],
  );

  return (
    <main>
      <header className="topbar">
        <div>
          <p>Retail Sales & Demand Forecasting Platform</p>
          <h1>Demand intelligence for product, store, and inventory planning</h1>
        </div>
        <div className="model-pill">
          <Gauge size={18} />
          {metrics?.best_model ?? "Model loading"}
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <section className="kpi-grid">
        <KpiCard label="Best MAE" value={bestMetrics ? bestMetrics.MAE.toFixed(2) : "..."} detail="Average absolute unit error" />
        <KpiCard label="WAPE" value={bestMetrics ? `${(bestMetrics.WAPE * 100).toFixed(2)}%` : "..."} detail="Weighted absolute percent error" />
        <KpiCard label="Stockout Risks" value={String(stockoutCount)} detail="Product-store pairs needing reorder" />
        <KpiCard label="Overstock Risks" value={String(overstockCount)} detail="Pairs with excess coverage" />
      </section>

      <ForecastChart rows={forecasts} />

      <section className="insight-grid">
        <section className="panel">
          <div className="panel-heading">
            <h2>Model Comparison</h2>
            <span>Time-based holdout evaluation</span>
          </div>
          <div className="metric-list">
            {metrics?.models_trained?.map((name: string) => {
              const row = metrics.metrics[name];
              return (
                <article key={name}>
                  <div>
                    <Activity size={18} />
                    <strong>{name}</strong>
                  </div>
                  <span>MAE {row.MAE.toFixed(2)}</span>
                  <span>RMSE {row.RMSE.toFixed(2)}</span>
                  <span>Bias {(row["Forecast Bias"] * 100).toFixed(2)}%</span>
                </article>
              );
            })}
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <h2>Prediction Design</h2>
            <span>Supervised ML target and feature set</span>
          </div>
          <div className="feature-block">
            <div>
              <Target size={20} />
              <strong>Target</strong>
              <span>{features?.target ?? "sales_units"}</span>
            </div>
            <div>
              <Boxes size={20} />
              <strong>Feature count</strong>
              <span>{features?.features?.length ?? 0}</span>
            </div>
          </div>
          <p className="feature-copy">{features?.prediction}</p>
        </section>
      </section>

      <RecommendationTable rows={recommendations} />
    </main>
  );
}

