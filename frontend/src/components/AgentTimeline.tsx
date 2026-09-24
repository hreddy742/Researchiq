import { AgentStep } from "../types";

interface Props {
  steps: AgentStep[];
  phase: string;
}

const AGENT_LABELS: Record<string, { label: string; detail: string }> = {
  ticker:    { label: "Ticker Resolution",  detail: "extracting stock ticker" },
  financial: { label: "Financial Data",     detail: "fetching from Yahoo Finance" },
  news:      { label: "News Analysis",      detail: "headlines + sentiment" },
  filings:   { label: "SEC Filings",        detail: "EDGAR lookup" },
  report:    { label: "Report Generation",  detail: "synthesizing brief" },
};

// Ordered pipeline steps
const PIPELINE = ["ticker", "financial", "news", "filings", "report"];

function StatusDot({ status }: { status: string }) {
  if (status === "complete") {
    return (
      <span className="timeline__dot timeline__dot--complete">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
          <path d="M20 6 9 17l-5-5" />
        </svg>
      </span>
    );
  }
  if (status === "error") {
    return (
      <span className="timeline__dot timeline__dot--error">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
          <path d="M18 6 6 18M6 6l12 12" />
        </svg>
      </span>
    );
  }
  if (status === "running") {
    return <span className="timeline__dot timeline__dot--running" />;
  }
  return <span className="timeline__dot timeline__dot--pending" />;
}

export function AgentTimeline({ steps, phase }: Props) {
  const stepMap = new Map(steps.map((s) => [s.agent, s]));

  return (
    <aside className="timeline">
      <h3 className="timeline__title">Research Progress</h3>
      <ul className="timeline__list">
        {PIPELINE.map((key, i) => {
          const step = stepMap.get(key);
          const meta = AGENT_LABELS[key];
          const isActive = phase === "loading" && !step;
          const status = step?.status ?? (isActive ? "running" : "pending");

          return (
            <li key={key} className={`timeline__item timeline__item--${status}`}>
              <div className="timeline__connector">
                <StatusDot status={status} />
                {i < PIPELINE.length - 1 && (
                  <span
                    className={`timeline__line ${
                      step?.status === "complete" ? "timeline__line--done" : ""
                    }`}
                  />
                )}
              </div>
              <div className="timeline__content">
                <span className="timeline__name">{meta.label}</span>
                {step ? (
                  <>
                    <span className="timeline__output">{step.output}</span>
                    <span className="timeline__duration">
                      {(step.duration_ms / 1000).toFixed(1)}s
                    </span>
                  </>
                ) : (
                  <span className="timeline__detail">{meta.detail}</span>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
