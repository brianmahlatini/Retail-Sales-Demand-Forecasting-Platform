import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ForecastRow } from "../services/api";

type ForecastChartProps = {
  rows: ForecastRow[];
};

export function ForecastChart({ rows }: ForecastChartProps) {
  const chartRows = rows.slice(-120).map((row) => ({
    date: row.date,
    actual: row.sales_units,
    predicted: row.predicted_sales,
    lower: row.prediction_lower,
    upper: row.prediction_upper,
  }));

  return (
    <section className="panel chart-panel">
      <div className="panel-heading">
        <h2>Actual vs Predicted Sales</h2>
        <span>Daily product-store demand with uncertainty</span>
      </div>
      <ResponsiveContainer width="100%" height={360}>
        <LineChart data={chartRows} margin={{ top: 12, right: 18, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#d8dee8" />
          <XAxis dataKey="date" minTickGap={28} tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="actual" stroke="#0f766e" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="predicted" stroke="#b42318" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="lower" stroke="#64748b" strokeDasharray="4 4" dot={false} />
          <Line type="monotone" dataKey="upper" stroke="#64748b" strokeDasharray="4 4" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </section>
  );
}

