import { useState } from "react";
import { simplifyText } from "../api";

export default function Simplify() {
    const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleSimplify() {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await simplifyText(text);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="card">
        <div className="field">
          <label htmlFor="complex-text">Text to simplify</label>
            <textarea
            id="complex-text"
            rows={4}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste or type a sentence here..."
          />
        </div>
        <button className="btn" onClick={handleSimplify} disabled={loading}>
          {loading ? "Simplifying..." : "Simplify"}
        </button>
        {error && <p className="error-msg">{error}</p>}
      </div>

      {result && (
        <div className="card">
          <label>Result</label>
          <p style={{ fontSize: "1.1em", margin: "8px 0 16px" }}>{result.simplified}</p>
          <div className="stat-grid">
            <div className="stat">
              <div className="value">{result.grade_level_before.toFixed(1)}</div>
              <div className="label">reading grade — before</div>
            </div>
            <div className="stat">
              <div className="value">{result.grade_level_after.toFixed(1)}</div>
              <div className="label">reading grade — after</div>
            </div>
          </div>
          {result.source === "original" && (
            <p className="hint">
              Our simplifier couldn't make this genuinely easier to read, so we've shown you the original sentence unchanged.
            </p>
          )}
        </div>
      )}
    </div>
  );
}