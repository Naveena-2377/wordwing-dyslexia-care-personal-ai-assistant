import { useState } from "react";
import { simplifyText, ocrImage } from "../api";

export default function Simplify() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);  
  const [ocrLoading, setOcrLoading] = useState(false);

  async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setOcrLoading(true);
    try {
      const res = await ocrImage(file);
      setText(res.text);
    } catch (err) {
      setError(err.message);
    } finally {
      setOcrLoading(false);
    }
  }


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
          <div style={{ marginTop: 8 }}>
            <label className="btn-outline" style={{ display: "inline-block", padding: "8px 16px", fontSize: "0.85em" }}>
              {ocrLoading ? "Reading photo..." : "📷 Or upload an image/PDF"}
              <input type="file" accept="image/*,.pdf" onChange={handleFileUpload} hidden disabled={ocrLoading} />
            </label>
          </div>
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
            {result.source === "gemini" && <p className="hint">Simplified with AI.</p>}
        </div>
      )}
    </div>
  );
}