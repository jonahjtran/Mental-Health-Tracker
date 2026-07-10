import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Analytics as AnalyticsData, RiskFlag } from "../api/types";
import { MoodLineChart } from "../components/MoodLineChart";

export function Analytics() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [riskFlags, setRiskFlags] = useState<RiskFlag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const [a, flags] = await Promise.all([
          api.get<AnalyticsData>("/me/analytics"),
          api.get<RiskFlag[]>("/insights/me/risk-flags"),
        ]);
        setAnalytics(a);
        setRiskFlags(flags);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load analytics");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="page"><p>Loading...</p></div>;
  if (error) return <div className="page"><p className="error-text">{error}</p></div>;
  if (!analytics) return null;

  const maxCount = Math.max(1, ...Object.values(analytics.mood_distribution));

  return (
    <div className="page">
      <h2>Analytics</h2>

      <div className="stat-grid">
        <div className="card stat-card">
          <span className="stat-value">{analytics.average_mood?.toFixed(1) ?? "—"}</span>
          <span className="stat-label">Average mood</span>
        </div>
        <div className="card stat-card">
          <span className="stat-value">{analytics.entry_count}</span>
          <span className="stat-label">Entries</span>
        </div>
        <div className="card stat-card">
          <span className="stat-value">{analytics.current_streak_days}</span>
          <span className="stat-label">Day streak</span>
        </div>
        <div className="card stat-card">
          <span className="stat-value">{analytics.risk_flag_count}</span>
          <span className="stat-label">Risk flags</span>
        </div>
      </div>

      <div className="card">
        <h3>Mood distribution</h3>
        <div className="bar-chart">
          {[1, 2, 3, 4, 5].map((rating) => {
            const count = analytics.mood_distribution[rating] ?? 0;
            return (
              <div className="bar-row" key={rating}>
                <span className="bar-label">{rating}</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${(count / maxCount) * 100}%` }} />
                </div>
                <span className="bar-count">{count}</span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="card">
        <h3>Mood over time</h3>
        {analytics.mood_by_date.length === 0 && <p>No mood data yet.</p>}
        {analytics.mood_by_date.length > 0 && <MoodLineChart points={analytics.mood_by_date} />}
      </div>

      {riskFlags.length > 0 && (
        <div className="card risk-list">
          <h3>Risk flags</h3>
          <ul>
            {riskFlags.map((flag) => (
              <li key={flag.journal_id}>
                <strong>{flag.date}</strong> — {flag.risk_reason ?? "Flagged for review"}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
