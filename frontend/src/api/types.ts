export interface User {
  id: number;
  name: string;
  email: string;
  avatar_url?: string | null;
}

export interface Journal {
  id: number;
  date: string;
  mood_rating: number;
  entry: string;
}

export interface JournalCreate {
  date?: string;
  mood_rating: number;
  entry: string;
}

export interface JournalUpdate {
  date?: string;
  mood_rating?: number;
  entry?: string;
}

export interface Sentiment {
  label: string;
  score: number;
}

export interface JournalAnalysis {
  summary: string;
  themes: string[];
  sentiment: Sentiment;
  suggestions: string[];
  risk_flag: boolean;
  risk_reason: string | null;
}

export interface RiskFlag {
  journal_id: number;
  date: string;
  risk_reason: string | null;
}

export interface MoodPoint {
  date: string;
  mood_rating: number;
}

export interface Analytics {
  average_mood: number | null;
  mood_by_date: MoodPoint[];
  mood_distribution: Record<number, number>;
  entry_count: number;
  current_streak_days: number;
  risk_flag_count: number;
}
