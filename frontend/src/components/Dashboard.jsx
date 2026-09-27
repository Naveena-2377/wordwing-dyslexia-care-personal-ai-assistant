import { useEffect, useState } from "react";
import { getDashboard } from "../api";
import { useAuth } from "../AuthContext";
import Mascot from "./Mascot";

function computeStreak(sessions) {
  if (!sessions.length) return 0;
  const days = [...new Set(sessions.map((s) => new Date(s.created_at).toDateString()))]
    .map((d) => new Date(d))
    .sort((a, b) => b - a);
  let streak = 1;
  for (let i = 0; i < days.length - 1; i++) {
    const diff = (days[i] - days[i + 1]) / (1000 * 60 * 60 * 24);
    if (diff === 1) streak++;
    else break;
  }
  return streak;
}

function getLevel(total) {
  if (total >= 15) return { name: "Reading Champion", tier: 4, floor: 15, ceil: 15 };
  if (total >= 7) return { name: "Word Wizard", tier: 3, floor: 7, ceil: 15 };
  if (total >= 3) return { name: "Story Seeker", tier: 2, floor: 3, ceil: 7 };
  return { name: "Word Explorer", tier: 1, floor: 0, ceil: 3 };
}

export default function Dashboard() {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard(token)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) return <p className="empty">Loading your progress...</p>;
  if (error) return <p className="error-msg">{error}</p>;
  if (!data) return null;

  const streak = computeStreak(data.sessions);
  const level = getLevel(data.total_sessions);
  const progress = level.ceil === level.floor
    ? 100
    : Math.min(100, ((data.total_sessions - level.floor) / (level.ceil - level.floor)) * 100);

  const badges = [
    { id: "first", label: "First Steps", emoji: "🌱", earned: data.total_sessions >= 1 },
    { id: "five", label: "High Five", emoji: "🖐️", earned: data.total_sessions >= 5 },
    { id: "perfect", label: "Perfect Read", emoji: "⭐", earned: data.sessions.some((s) => s.accuracy >= 0.95) },
    { id: "streak", label: "On a Roll", emoji: "🔥", earned: streak >= 3 },
  ];

  return (
    <div>
      <div className="game-row">
        <div className="streak-card">
          <span className="streak-flame">🔥</span>
          <div className="streak-num">{streak} day{streak === 1 ? "" : "s"}</div>
          <div className="level-sub">current streak</div>
        </div>
        <div className="level-card">
          <div className="level-name">{level.name}</div>
          <div className="level-bar">
            <div className="level-bar-fill" style={{ width: `${progress}%` }} />
          </div>
          <div className="level-sub">
            {level.tier < 4
              ? `${data.total_sessions} / ${level.ceil} sessions to next level`
              : "Top level reached!"}
          </div>
        </div>
      </div>

      <label>Badges</label>
      <div className="badge-row">
        {badges.map((b) => (
          <div className="earned-badge" data-earned={b.earned} key={b.id}>
            <span className="emoji">{b.emoji}</span>
            <span className="label">{b.label}</span>
          </div>
        ))}
      </div>

      <div className="stat-grid" style={{ marginBottom: 24 }}>
        <div className="stat">
          <div className="value">{data.total_sessions}</div>
          <div className="label">sessions completed</div>
        </div>
        <div className="stat">
          <div className="value">{data.avg_wpm.toFixed(0)}</div>
          <div className="label">avg words / minute</div>
        </div>
        <div className="stat">
          <div className="value">{(data.avg_accuracy * 100).toFixed(0)}%</div>
          <div className="label">avg accuracy</div>
        </div>
      </div>

      <label>Session history</label>
      {data.sessions.length === 0 ? (
        <div style={{ textAlign: "center", padding: "24px 0" }}>
          <Mascot size={60} mood="neutral" />
          <p className="empty">No sessions yet — record one in the Reading session tab!</p>
        </div>
      ) : (
        <div className="history-list">
          {data.sessions.map((s) => (
            <div className="history-row" key={s.id}>
              <div>
                <div className="history-text">{s.target_text}</div>
                <div className="hint">{new Date(s.created_at).toLocaleString()}</div>
              </div>
              <div className="history-stats">
                <span>{s.wpm.toFixed(0)} wpm</span>
                <span>{(s.accuracy * 100).toFixed(0)}%</span>
                <span className="badge" data-band={s.risk_band}>
                  {s.risk_band.replace(/_/g, " ")}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}