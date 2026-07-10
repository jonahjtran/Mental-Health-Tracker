import { useState } from "react";
import { api, ApiError } from "../api/client";
import type { JournalAnalysis } from "../api/types";

interface Props {
  journalId: number;
  insights: JournalAnalysis | null;
  onChange: (insights: JournalAnalysis | null) => void;
}

export function InsightsPanel({ journalId, insights, onChange }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async (force: boolean) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.post<JournalAnalysis>(
        `/insights/me/journals/${journalId}/analyze?force=${force}`
      );
      onChange(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze entry");
    } finally {
      setLoading(false);
    }
  };

  const remove = async () => {
    setLoading(true);
    setError(null);
    try {
      await api.delete(`/insights/me/journals/${journalId}/insights`);
      onChange(null);
    } catch (err) {
      if (!(err instanceof ApiError && err.status === 404)) {
        setError(err instanceof Error ? err.message : "Failed to delete insights");
      }
      onChange(null);
    } finally {
      setLoading(false);
    }
  };

  if (!insights) {
    return (
      <div className="insights-panel insights-empty">
        <button className="btn btn-secondary" disabled={loading} onClick={() => analyze(false)}>
          {loading ? "Analyzing..." : "Generate AI insights"}
        </button>
        {error && <p className="error-text">{error}</p>}
      </div>
    );
  }

  return (
    <div className={`insights-panel ${insights.risk_flag ? "insights-risk" : ""}`}>
      {insights.risk_flag && (
        <div className="risk-banner">⚠ Flagged: {insights.risk_reason ?? "Potential risk detected"}</div>
      )}
      <p className="insights-summary">{insights.summary}</p>
      <div className="insights-meta">
        <span className="sentiment-badge">
          {insights.sentiment.label} ({Math.round(insights.sentiment.score * 100)}%)
        </span>
        {insights.themes.map((theme) => (
          <span key={theme} className="theme-chip">
            {theme}
          </span>
        ))}
      </div>
      {insights.suggestions.length > 0 && (
        <ul className="suggestions-list">
          {insights.suggestions.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      )}
      <div className="insights-actions">
        <button className="btn btn-ghost" disabled={loading} onClick={() => analyze(true)}>
          Re-analyze
        </button>
        <button className="btn btn-ghost" disabled={loading} onClick={remove}>
          Clear insights
        </button>
      </div>
      {error && <p className="error-text">{error}</p>}
    </div>
  );
}
