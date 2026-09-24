import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { PricePoint } from "../types";

interface Props {
  history: PricePoint[];
  currentPrice: number;
}

function abbrevMonth(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", { month: "short" });
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip__date">{label}</div>
      <div className="chart-tooltip__price">${payload[0].value.toFixed(2)}</div>
    </div>
  );
};

// Show ~12 evenly-spaced X-axis ticks
function buildTicks(data: PricePoint[]): string[] {
  if (data.length === 0) return [];
  const step = Math.floor(data.length / 12);
  return data.filter((_, i) => i % step === 0).map((d) => d.date);
}

export function StockChart({ history, currentPrice }: Props) {
  if (!history.length) {
    return <div className="chart-skeleton" />;
  }

  const ticks = buildTicks(history);
  const prices = history.map((d) => d.close);
  const minY = Math.min(...prices) * 0.97;
  const maxY = Math.max(...prices) * 1.03;

  return (
    <div className="stock-chart">
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={history} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
          <defs>
            <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid stroke="#2a2a2a" strokeDasharray="3 3" vertical={false} />

          <XAxis
            dataKey="date"
            ticks={ticks}
            tickFormatter={abbrevMonth}
            tick={{ fill: "#888", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[minY, maxY]}
            tickFormatter={(v) => `$${v.toFixed(0)}`}
            tick={{ fill: "#888", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={58}
          />

          <Tooltip content={<CustomTooltip />} />

          <ReferenceLine
            y={currentPrice}
            stroke="#3b82f6"
            strokeDasharray="4 4"
            strokeOpacity={0.6}
          />

          <Area
            type="monotone"
            dataKey="close"
            stroke="#3b82f6"
            strokeWidth={2}
            fill="url(#blueGrad)"
            dot={false}
            activeDot={{ r: 4, fill: "#3b82f6" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
