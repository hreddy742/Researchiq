import { NewsData } from "../types";

interface Props {
  newsData: NewsData;
}

export function NewsHeadlines({ newsData }: Props) {
  return (
    <div className="news-headlines">
      <h3 className="news-headlines__title">Recent Headlines</h3>
      {newsData.headlines.length === 0 ? (
        <p className="news-headlines__empty">No recent headlines found.</p>
      ) : (
        <ul className="news-headlines__list">
          {newsData.headlines.map((h, i) => (
            <li key={i} className="news-card">
              <a
                href={h.link}
                target="_blank"
                rel="noopener noreferrer"
                className="news-card__title"
              >
                {h.title}
              </a>
              <div className="news-card__meta">
                <span className="news-card__date">{h.published}</span>
                <span className="news-card__source badge">{h.source}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
