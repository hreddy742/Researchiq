import { AgentTimeline } from "./components/AgentTimeline";
import { NewsHeadlines } from "./components/NewsHeadlines";
import { ReportViewer } from "./components/ReportViewer";
import { SearchBar } from "./components/SearchBar";
import { SentimentGauge } from "./components/SentimentGauge";
import { StockChart } from "./components/StockChart";
import { StockMetrics } from "./components/StockMetrics";
import { useResearch } from "./hooks/useResearch";

export default function App() {
  const { state, submit, reset } = useResearch();
  const { phase, agentSteps, stockData, newsData, sentiment, report, totalMs, error } = state;

  const isIdle = phase === "idle";
  const isLoading = phase === "loading";
  const isComplete = phase === "complete";
  const isError = phase === "error";

  return (
    <div className={`app ${isIdle ? "app--landing" : "app--dashboard"}`}>
      {/* Header */}
      <header className="app-header">
        <button className="app-logo" onClick={reset} aria-label="Go to home">
          <span className="app-logo__mark">R</span>
          <span className="app-logo__text">ResearchIQ</span>
        </button>
        {!isIdle && (
          <div className="app-header__search">
            <SearchBar onSubmit={submit} isLoading={isLoading} compact />
          </div>
        )}
      </header>

      {/* Landing */}
      {isIdle && (
        <main className="landing">
          <div className="landing__hero">
            <h1 className="landing__title">
              Company research in&nbsp;
              <span className="landing__accent">90 seconds</span>
            </h1>
            <p className="landing__sub">
              Four AI agents — real financial data, SEC filings, news sentiment.
              <br />
              100% open source. Zero paid APIs.
            </p>
            <SearchBar onSubmit={submit} isLoading={isLoading} />
          </div>

          <div className="landing__badges">
            <span className="badge badge--outline">llama3.2:3b via Ollama</span>
            <span className="badge badge--outline">LangGraph agents</span>
            <span className="badge badge--outline">yfinance · EDGAR · RSS</span>
            <span className="badge badge--outline">$0.00 per report</span>
          </div>
        </main>
      )}

      {/* Dashboard */}
      {(isLoading || isComplete || isError) && (
        <main className="dashboard">
          {/* Left: timeline */}
          <AgentTimeline steps={agentSteps} phase={phase} />

          {/* Center: charts + report */}
          <section className="dashboard__main">
            {/* Stock data */}
            {stockData && (
              <>
                <StockMetrics data={stockData} />
                <StockChart history={stockData.price_history} currentPrice={stockData.current_price} />
              </>
            )}

            {/* Loading skeleton */}
            {isLoading && !stockData && (
              <div className="skeleton-block" style={{ height: 200 }} />
            )}

            {/* Report */}
            {(report || isLoading) && (
              <ReportViewer
                report={report}
                companyName={stockData?.company_name ?? state.agentSteps[0]?.output ?? ""}
                ticker={stockData?.ticker ?? ""}
                totalMs={totalMs}
                isStreaming={isLoading && !!report}
              />
            )}

            {/* Error */}
            {isError && (
              <div className="error-card">
                <h3>Research failed</h3>
                <p>{error}</p>
                <button className="btn btn--primary" onClick={reset}>Try again</button>
              </div>
            )}
          </section>

          {/* Right: sentiment + news */}
          <aside className="dashboard__side">
            {sentiment && (
              <SentimentGauge sentiment={sentiment} newsData={newsData} />
            )}
            {newsData && newsData.headlines.length > 0 && (
              <NewsHeadlines newsData={newsData} />
            )}
          </aside>
        </main>
      )}
    </div>
  );
}
