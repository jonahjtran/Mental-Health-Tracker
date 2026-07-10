import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Journal, JournalCreate } from "../api/types";
import { JournalCard } from "../components/JournalCard";
import { JournalForm } from "../components/JournalForm";

export function Journals() {
  const [journals, setJournals] = useState<Journal[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const data = await api.get<Journal[]>("/me/journals");
      data.sort((a, b) => b.date.localeCompare(a.date));
      setJournals(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load journals");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (data: JournalCreate) => {
    const created = await api.post<Journal>("/me/journals", data);
    setJournals((prev) => [created, ...prev].sort((a, b) => b.date.localeCompare(a.date)));
    setShowForm(false);
  };

  const handleUpdated = (updated: Journal) => {
    setJournals((prev) => prev.map((j) => (j.id === updated.id ? updated : j)));
  };

  const handleDeleted = (id: number) => {
    setJournals((prev) => prev.filter((j) => j.id !== id));
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Journals</h2>
        <button className="btn btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Close" : "New entry"}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <JournalForm onSubmit={handleCreate} submitLabel="Create" />
        </div>
      )}

      {error && <p className="error-text">{error}</p>}
      {loading && <p>Loading...</p>}
      {!loading && journals.length === 0 && <p>No journal entries yet. Create your first one above.</p>}

      <div className="journal-list">
        {journals.map((j) => (
          <JournalCard key={j.id} journal={j} onUpdated={handleUpdated} onDeleted={handleDeleted} />
        ))}
      </div>
    </div>
  );
}
