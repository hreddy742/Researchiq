import { KeyboardEvent, useEffect, useRef, useState } from "react";

interface Props {
  onSubmit: (query: string) => void;
  isLoading: boolean;
  compact?: boolean;
}

const SUGGESTIONS = ["Apple", "Tesla", "NVDA", "Microsoft", "Amazon"];
const LS_KEY = "researchiq_recent";

function getRecent(): string[] {
  try {
    return JSON.parse(localStorage.getItem(LS_KEY) ?? "[]");
  } catch {
    return [];
  }
}

function saveRecent(query: string) {
  const prev = getRecent().filter((q) => q !== query);
  localStorage.setItem(LS_KEY, JSON.stringify([query, ...prev].slice(0, 5)));
}

export function SearchBar({ onSubmit, isLoading, compact = false }: Props) {
  const [value, setValue] = useState("");
  const [recent, setRecent] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setRecent(getRecent());
    if (!compact) inputRef.current?.focus();
  }, [compact]);

  function handleSubmit() {
    const q = value.trim();
    if (!q || isLoading) return;
    saveRecent(q);
    setRecent(getRecent());
    onSubmit(q);
  }

  function handleKey(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") handleSubmit();
  }

  function pick(q: string) {
    setValue(q);
    setTimeout(() => {
      saveRecent(q);
      setRecent(getRecent());
      onSubmit(q);
    }, 50);
  }

  return (
    <div className={`search-bar ${compact ? "search-bar--compact" : ""}`}>
      <div className="search-bar__input-row">
        <span className="search-bar__icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
        </span>
        <input
          ref={inputRef}
          className="search-bar__input"
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Enter any company name… try Apple, Tesla, or NVDA"
          disabled={isLoading}
          aria-label="Company search"
        />
        <button
          className="search-bar__btn"
          onClick={handleSubmit}
          disabled={isLoading || !value.trim()}
        >
          {isLoading ? (
            <span className="spinner" />
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          )}
        </button>
      </div>

      {!compact && (recent.length > 0 || SUGGESTIONS.length > 0) && (
        <div className="search-bar__chips">
          {recent.length > 0 ? (
            <>
              <span className="search-bar__chips-label">Recent:</span>
              {recent.map((q) => (
                <button key={q} className="chip chip--recent" onClick={() => pick(q)}>
                  {q}
                </button>
              ))}
            </>
          ) : (
            <>
              <span className="search-bar__chips-label">Try:</span>
              {SUGGESTIONS.map((q) => (
                <button key={q} className="chip" onClick={() => pick(q)}>
                  {q}
                </button>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}
