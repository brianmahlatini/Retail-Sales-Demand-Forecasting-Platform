import { AlertTriangle, CheckCircle2, TrendingDown } from "lucide-react";
import type { Recommendation } from "../services/api";

type RecommendationTableProps = {
  rows: Recommendation[];
};

function iconForRecommendation(label: string) {
  if (label === "Reorder soon") return <AlertTriangle size={18} />;
  if (label === "Reduce replenishment") return <TrendingDown size={18} />;
  return <CheckCircle2 size={18} />;
}

export function RecommendationTable({ rows }: RecommendationTableProps) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Inventory Recommendations</h2>
        <span>Ranked using model-predicted demand and coverage risk</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Action</th>
              <th>Product</th>
              <th>Store</th>
              <th>Predicted</th>
              <th>Stock</th>
              <th>Cover</th>
              <th>Stockout</th>
              <th>Overstock</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.product_id}-${row.store_id}`}>
                <td>
                  <span className={`status ${row.recommendation.toLowerCase().replaceAll(" ", "-")}`}>
                    {iconForRecommendation(row.recommendation)}
                    {row.recommendation}
                  </span>
                </td>
                <td>
                  <strong>{row.product_name}</strong>
                  <small>{row.category}</small>
                </td>
                <td>{row.store_name}</td>
                <td>{row.predicted_sales.toFixed(1)}</td>
                <td>{row.stock_on_hand}</td>
                <td>{row.days_of_cover.toFixed(1)} days</td>
                <td>{(row.stockout_probability * 100).toFixed(1)}%</td>
                <td>{(row.overstock_probability * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

