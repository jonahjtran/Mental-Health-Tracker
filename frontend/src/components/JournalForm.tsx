import { useState, type FormEvent } from "react";
import type { Journal, JournalCreate } from "../api/types";

interface Props {
  initial?: Journal;
  onSubmit: (data: JournalCreate) => Promise<void>;
  onCancel?: () => void;
  submitLabel?: string;
}

export function JournalForm({ initial, onSubmit, onCancel, submitLabel = "Save" }: Props) {
  const [date, setDate] = useState(initial?.date ?? new Date().toISOString().slice(0, 10));
  const [moodRating, setMoodRating] = useState(initial?.mood_rating ?? 3);
  const [entry, setEntry] = useState(initial?.entry ?? "");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit({ date, mood_rating: moodRating, entry });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="journal-form" onSubmit={handleSubmit}>
      <div className="form-row">
        <label>
          Date
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
        </label>
        <label>
          Mood (1-5)
          <input
            type="number"
            min={1}
            max={5}
            value={moodRating}
            onChange={(e) => setMoodRating(Number(e.target.value))}
            required
          />
        </label>
      </div>
      <label>
        Entry
        <textarea
          value={entry}
          onChange={(e) => setEntry(e.target.value)}
          rows={5}
          required
          placeholder="How are you feeling today?"
        />
      </label>
      {error && <p className="error-text">{error}</p>}
      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? "Saving..." : submitLabel}
        </button>
        {onCancel && (
          <button type="button" className="btn btn-ghost" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
