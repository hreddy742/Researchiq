import { StockData } from "../types";

interface Props {
  data: StockData;
}

function fmt(n: number | null | undefined, prefix = "", suffix = ""): string {
  if (n == null) return "N/A";
  return `${prefix}${n.toLocaleString()}${suffix}`;
}

function formatMarketCap(value: number): string {
  if (!value) return "N/A";
  if (value >= 1_000_000_000_000) return `$${(value / 1_000_000_000_000).toFixed(2)}T`;
  if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(2)}B`;
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}M`;
  return `$${value.toLocaleString()}`;
}

export function StockMetrics({ data }: Props) {
  const changePositive = data.change_percent >= 0;
  const rangeMin = data.week_52_low;
  const rangeMax = data.week_52_high;
  const rangePct =
    rangeMax > rangeMin
      ? ((data.current_price - rangeMin) / (rangeMax - rangeMin)) * 100
      : 50;

  return (
    <div className="stock-metrics">
      {/* Header row */}
      <div className="stock-metrics__header">
        <div>
          <span className="stock-metrics__price">
            {data.currency === "USD" ? "$" : data.currency + " "}
            {data.current_price.toFixed(2)}
          </span>
          <span
            className={`stock-metrics__change ${
              changePositive ? "stock-metrics__change--up" : "stock-metrics__change--down"
            }`}
          >
            {changePositive ? "▲" : "▼"} {Math.abs(data.change_percent).toFixed(2)}%
          </span>
        </div>
        <div className="stock-metrics__meta">
          <span>{data.ticker}</span>
          <span className="stock-metrics__name">{data.company_name}</span>
        </div>
      </div>

      {/* Metric pills */}
      <div className="stock-metrics__grid">
        <div className="metric">
          <span className="metric__label">Volume</span>
          <span className="metric__value">{formatMarketCap(data.volume)}</span>
        </div>
        <div className="metric">
          <span className="metric__label">Market Cap</span>
          <span className="metric__value">{formatMarketCap(data.market_cap ?? 0)}</span>
        </div>
        <div className="metric">
          <span className="metric__label">P/E Ratio</span>
          <span className="metric__value">{fmt(data.pe_ratio)}</span>
        </div>
        <div className="metric">
          <span className="metric__label">Prev Close</span>
          <span className="metric__value">${data.previous_close.toFixed(2)}</span>
        </div>
      </div>

      {/* 52-week range */}
      <div className="stock-metrics__range">
        <span className="range__label">52W Low ${data.week_52_low.toFixed(2)}</span>
        <div className="range__bar">
          <div
            className="range__fill"
            style={{ width: `${Math.min(100, Math.max(0, rangePct))}%` }}
          />
          <span
            className="range__dot"
            style={{ left: `${Math.min(100, Math.max(0, rangePct))}%` }}
          />
        </div>
        <span className="range__label">52W High ${data.week_52_high.toFixed(2)}</span>
      </div>
    </div>
  );
}
