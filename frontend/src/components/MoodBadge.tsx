const MOOD_EMOJI: Record<number, string> = {
  1: "😞",
  2: "🙁",
  3: "😐",
  4: "🙂",
  5: "😄",
};

export function MoodBadge({ rating }: { rating: number }) {
  return (
    <span className="mood-badge" title={`Mood: ${rating}/5`}>
      {MOOD_EMOJI[rating] ?? "•"} {rating}/5
    </span>
  );
}
