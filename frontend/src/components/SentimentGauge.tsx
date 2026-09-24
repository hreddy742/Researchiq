import { NewsData, Sentiment } from "../types";

interface Props {
  sentiment: Sentiment;
  newsData: NewsData | null;
}

// Half-circle SVG gauge
// score: -1.0 → 1.0  maps to 180° → 0° (needle angle from left)
function scoreToAngle(score: number): number {
  // -1 → 180deg, 0 → 90deg, +1 → 0deg
  return 90 - score * 90;
}

function labelColor(label: string): string {
  if (label === "positive") return "#22c55e";
  if (label === "negative") return "#ef4444";
  return "#f59e0b";
}

export function SentimentGauge({ sentiment, newsData }: Props) {
  const angle = scoreToAngle(sentiment.score);
  const cx = 100;
  const cy = 100;
  const r = 72;

  // Needle tip
  const rad = ((angle - 90) * Math.PI) / 180;
  const nx = cx + r * Math.cos(rad);
  const ny = cy + r * Math.sin(rad);

  const color = labelColor(sentiment.label);

  return (
    <div className="sentiment-gauge">
      <h3 className="sentiment-gauge__title">Market Sentiment</h3>

      <div className="sentiment-gauge__svg-wrap">
        <svg viewBox="0 0 200 110" className="sentiment-gauge__svg">
          {/* Background arc segments */}
          {/* Red: -1 → -0.3 — 180° to 117° */}
          <path
            d="M 28 100 A 72 72 0 0 1 62.6 35.6"
            stroke="#ef4444" strokeWidth="10" fill="none" strokeLinecap="round"
          />
          {/* Amber: -0.3 → +0.3 — 117° to 63° */}
          <path
            d="M 62.6 35.6 A 72 72 0 0 1 137.4 35.6"
            stroke="#f59e0b" strokeWidth="10" fill="none" strokeLinecap="round"
          />
          {/* Green: +0.3 → +1.0 — 63° to 0° */}
          <path
            d="M 137.4 35.6 A 72 72 0 0 1 172 100"
            stroke="#22c55e" strokeWidth="10" fill="none" strokeLinecap="round"
          />

          {/* Needle */}
          <line
            x1={cx} y1={cy}
            x2={nx} y2={ny}
            stroke={color}
            strokeWidth="3"
            strokeLinecap="round"
          />
          <circle cx={cx} cy={cy} r={5} fill={color} />

          {/* Score text */}
          <text x={cx} y={90} textAnchor="middle" fill="#e8e8e8" fontSize="22" fontWeight="bold">
            {sentiment.score.toFixed(2)}
          </text>
        </svg>

        <div className="sentiment-gauge__label" style={{ color }}>
          {sentiment.label.charAt(0).toUpperCase() + sentiment.label.slice(1)} sentiment
        </div>
        <p className="sentiment-gauge__summary">{sentiment.summary}</p>
      </div>

      {newsData && newsData.headlines.length > 0 && (
        <ul className="sentiment-gauge__headlines">
          {newsData.headlines.slice(0, 5).map((h, i) => (
            <li key={i} className="news-item">
              <a href={h.link} target="_blank" rel="noopener noreferrer" className="news-item__title">
                {h.title}
              </a>
              <div className="news-item__meta">
                <span className="news-item__date">{h.published}</span>
                <span className="news-item__source">{h.source}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
