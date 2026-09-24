import { useCallback, useRef, useState } from "react";
import { openResearchStream, startResearch } from "../api/client";
import type { AgentStep, NewsData, ResearchState, Sentiment, StockData } from "../types";

const INITIAL_STATE: ResearchState = {
  phase: "idle",
  agentSteps: [],
  stockData: null,
  newsData: null,
  sentiment: null,
  report: "",
  totalMs: 0,
  error: null,
};

export function useResearch() {
  const [state, setState] = useState<ResearchState>(INITIAL_STATE);
  const startTimeRef = useRef<number>(0);
  const esRef = useRef<EventSource | null>(null);

  const submit = useCallback(async (query: string) => {
    // Clean up any previous stream
    esRef.current?.close();

    setState({ ...INITIAL_STATE, phase: "loading" });
    startTimeRef.current = Date.now();

    try {
      const sessionId = await startResearch(query);
      const es = openResearchStream(sessionId);
      esRef.current = es;

      es.addEventListener("agent_step", (e: MessageEvent) => {
        const step: AgentStep = JSON.parse(e.data);
        setState((prev) => ({
          ...prev,
          agentSteps: [...prev.agentSteps, step],
        }));
      });

      es.addEventListener("complete", (e: MessageEvent) => {
        const data = JSON.parse(e.data);
        setState((prev) => ({
          ...prev,
          phase: "complete",
          stockData: (data.stock_data as StockData) ?? null,
          newsData: (data.news_data as NewsData) ?? null,
          sentiment: (data.sentiment as Sentiment) ?? null,
          report: data.report ?? "",
          agentSteps: data.agent_steps ?? prev.agentSteps,
          totalMs: Date.now() - startTimeRef.current,
        }));
        es.close();
      });

      es.addEventListener("error", (e: MessageEvent) => {
        const data = JSON.parse(e.data ?? "{}");
        setState((prev) => ({
          ...prev,
          phase: "error",
          error: data.message ?? "An unexpected error occurred",
          totalMs: Date.now() - startTimeRef.current,
        }));
        es.close();
      });

      es.onerror = () => {
        setState((prev) => {
          if (prev.phase === "loading") {
            return {
              ...prev,
              phase: "error",
              error: "Connection to server lost",
            };
          }
          return prev;
        });
        es.close();
      };
    } catch (err) {
      setState((prev) => ({
        ...prev,
        phase: "error",
        error: err instanceof Error ? err.message : "Failed to start research",
      }));
    }
  }, []);

  const reset = useCallback(() => {
    esRef.current?.close();
    setState(INITIAL_STATE);
  }, []);

  return { state, submit, reset };
}
