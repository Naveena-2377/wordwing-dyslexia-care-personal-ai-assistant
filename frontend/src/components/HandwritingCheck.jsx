import { useState } from "react";
import { checkHandwriting } from "../api";

const LABELS = {
  normal: "Looks correct",
  reversal: "Possible letter reversal",
  corrected: "Self-corrected",
};

export default function HandwritingCheck() {
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError(null);
    setLoading(true);
    try {
      const res = await checkHandwriting(file);
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
        <label>Upload a photo of a single handwritten letter</label>
        <input type="file" accept="image/*" onChange={handleUpload} />
        {loading && <p className="hint">Checking...</p>}
        {error && <p className="error-msg">{error}</p>}
      </div>

      {preview && (
        <div className="card">
          <img
            src={preview}
            alt="uploaded letter"
            style={{ maxWidth: 160, borderRadius: "var(--radius-sm)", border: "1px solid var(--border)" }}
          />
        </div>
      )}

      {result && (
        <div className="card">
          <span className="badge" data-band={result.verdict === "reversal" ? "monitor" : "low_indicator"}>
            {LABELS[result.verdict]}
          </span>
          <div className="stat-grid" style={{ marginTop: 16 }}>
            <div className="stat">
              <div className="value">{(result.normal * 100).toFixed(0)}%</div>
              <div className="label">normal</div>
            </div>
            <div className="stat">
              <div className="value">{(result.reversal * 100).toFixed(0)}%</div>
              <div className="label">reversal</div>
            </div>
            <div className="stat">
              <div className="value">{(result.corrected * 100).toFixed(0)}%</div>
              <div className="label">corrected</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}