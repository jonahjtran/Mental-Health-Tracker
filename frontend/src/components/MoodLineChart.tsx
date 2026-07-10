import type { MoodPoint } from "../api/types";

const WIDTH = 600;
const HEIGHT = 180;
const PAD_X = 16;
const PAD_Y = 16;

export function MoodLineChart({ points }: { points: MoodPoint[] }) {
  const innerW = WIDTH - PAD_X * 2;
  const innerH = HEIGHT - PAD_Y * 2;

  const xFor = (i: number) =>
    PAD_X + (points.length === 1 ? innerW / 2 : (i / (points.length - 1)) * innerW);
  const yFor = (mood: number) => PAD_Y + innerH - ((mood - 1) / 4) * innerH;

  const linePath = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${xFor(i)} ${yFor(p.mood_rating)}`)
    .join(" ");

  const areaPath = `${linePath} L ${xFor(points.length - 1)} ${PAD_Y + innerH} L ${xFor(0)} ${PAD_Y + innerH} Z`;

  return (
    <svg
      className="mood-line-chart"
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      preserveAspectRatio="none"
      width="100%"
      height={HEIGHT}
    >
      <defs>
        <linearGradient id="moodLineFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.25" />
          <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
        </linearGradient>
      </defs>

      {[1, 2, 3, 4, 5].map((mood) => (
        <line
          key={mood}
          x1={PAD_X}
          x2={WIDTH - PAD_X}
          y1={yFor(mood)}
          y2={yFor(mood)}
          className="mood-line-gridline"
        />
      ))}

      <path d={areaPath} fill="url(#moodLineFill)" stroke="none" />
      <path d={linePath} fill="none" className="mood-line-stroke" />

      {points.map((p, i) => (
        <circle key={p.date} cx={xFor(i)} cy={yFor(p.mood_rating)} r={4} className="mood-line-dot">
          <title>{`${p.date}: ${p.mood_rating}/5`}</title>
        </circle>
      ))}
    </svg>
  );
}
