export type ForecastRow = {
  date: string;
  product_id: string;
  product_name: string;
  category: string;
  store_id: string;
  store_name: string;
  stock_on_hand: number;
  sales_units: number;
  predicted_sales: number;
  prediction_lower: number;
  prediction_upper: number;
};

export type Recommendation = {
  product_id: string;
  product_name: string;
  category: string;
  store_id: string;
  store_name: string;
  stock_on_hand: number;
  predicted_sales: number;
  days_of_cover: number;
  stockout_probability: number;
  overstock_probability: number;
  recommendation: string;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

export const api = {
  forecasts: (limit = 600) => fetchJson<ForecastRow[]>(`/forecasts?limit=${limit}`),
  recommendations: (limit = 60) => fetchJson<Recommendation[]>(`/recommendations?limit=${limit}`),
  metrics: () => fetchJson<any>("/model/metrics"),
  features: () => fetchJson<any>("/model/features"),
};

