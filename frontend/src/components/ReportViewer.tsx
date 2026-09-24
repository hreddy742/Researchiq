import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  report: string;
  companyName: string;
  ticker: string;
  totalMs: number;
  isStreaming?: boolean;
}

export function ReportViewer({
  report,
  companyName,
  ticker,
  totalMs,
  isStreaming = false,
}: Props) {
  const totalSec = (totalMs / 1000).toFixed(0);

  return (
    <div className="report-viewer">
      <div className="report-viewer__header">
        <div className="report-viewer__company">
          <span className="report-viewer__name">{companyName}</span>
          <span className="report-viewer__ticker badge">{ticker}</span>
        </div>
        {!isStreaming && totalMs > 0 && (
          <span className="report-viewer__time">
            Research complete in {totalSec}s
          </span>
        )}
        {isStreaming && (
          <span className="report-viewer__streaming">
            <span className="spinner spinner--sm" /> Generating…
          </span>
        )}
      </div>

      <div className="report-viewer__body">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h2: ({ children }) => (
              <h2 className="report-h2">{children}</h2>
            ),
            p: ({ children }) => (
              <p className="report-p">{children}</p>
            ),
            li: ({ children }) => (
              <li className="report-li">{children}</li>
            ),
            strong: ({ children }) => (
              <strong className="report-strong">{children}</strong>
            ),
            a: ({ href, children }) => (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="report-link"
              >
                {children}
              </a>
            ),
            table: ({ children }) => (
              <table className="report-table">{children}</table>
            ),
            tr: ({ children }) => (
              <tr className="report-tr">{children}</tr>
            ),
            td: ({ children }) => (
              <td className="report-td">{children}</td>
            ),
            th: ({ children }) => (
              <th className="report-th">{children}</th>
            ),
          }}
        >
          {report}
        </ReactMarkdown>
        {isStreaming && <span className="cursor-blink">▋</span>}
      </div>
    </div>
  );
}
