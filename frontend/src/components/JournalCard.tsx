import { useState } from "react";
import { api, ApiError } from "../api/client";
import type { Journal, JournalAnalysis, JournalCreate, JournalUpdate } from "../api/types";
import { MoodBadge } from "./MoodBadge";
import { JournalForm } from "./JournalForm";
import { InsightsPanel } from "./InsightsPanel";

interface Props {
  journal: Journal;
  onUpdated: (journal: Journal) => void;
  onDeleted: (id: number) => void;
}

export function JournalCard({ journal, onUpdated, onDeleted }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [editing, setEditing] = useState(false);
  const [insights, setInsights] = useState<JournalAnalysis | null | undefined>(undefined);
  const [deleting, setDeleting] = useState(false);

  const loadInsights = async () => {
    if (insights !== undefined) return;
    try {
      const result = await api.get<JournalAnalysis>(`/insights/me/journals/${journal.id}/insights`);
      setInsights(result);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setInsights(null);
      }
    }
  };

  const toggleExpanded = () => {
    const next = !expanded;
    setExpanded(next);
    if (next) loadInsights();
  };

  const handleUpdate = async (data: JournalCreate) => {
    const patch: JournalUpdate = data;
    const updated = await api.patch<Journal>(`/me/journals/${journal.id}`, patch);
    onUpdated(updated);
    setEditing(false);
  };

  const handleDelete = async () => {
    if (!confirm("Delete this journal entry?")) return;
    setDeleting(true);
    try {
      await api.delete(`/me/journals/${journal.id}`);
      onDeleted(journal.id);
    } finally {
      setDeleting(false);
    }
  };

  if (editing) {
    return (
      <div className="card journal-card">
        <JournalForm
          initial={journal}
          onSubmit={handleUpdate}
          onCancel={() => setEditing(false)}
          submitLabel="Update"
        />
      </div>
    );
  }

  return (
    <div className="card journal-card">
      <div className="journal-card-header" onClick={toggleExpanded}>
        <div>
          <strong>{journal.date}</strong>
          <MoodBadge rating={journal.mood_rating} />
        </div>
        <span className="expand-icon">{expanded ? "−" : "+"}</span>
      </div>
      {!expanded && <p className="journal-preview">{journal.entry.slice(0, 120)}</p>}
      {expanded && (
        <>
          <p className="journal-entry-full">{journal.entry}</p>
          <div className="journal-actions">
            <button className="btn btn-ghost" onClick={() => setEditing(true)}>
              Edit
            </button>
            <button className="btn btn-danger" disabled={deleting} onClick={handleDelete}>
              {deleting ? "Deleting..." : "Delete"}
            </button>
          </div>
          <InsightsPanel
            journalId={journal.id}
            insights={insights ?? null}
            onChange={setInsights}
          />
        </>
      )}
    </div>
  );
}
