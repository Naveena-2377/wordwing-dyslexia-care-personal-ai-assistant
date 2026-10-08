import { useState, useRef } from "react";
import { checkHandwriting, checkHandwritingPage } from "../api";

const LABELS = {
  normal: "Looks correct",
  reversal: "Possible letter reversal",
  corrected: "Self-corrected",
};
const COLORS = { normal: "#12B76A", reversal: "#EF6461", corrected: "#F2A93B" };

export default function HandwritingCheck() {
  const [mode, setMode] = useState("letter");
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [pageResult, setPageResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [imgSize, setImgSize] = useState({ w: 1, h: 1 });
  const imgRef = useRef(null);

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setPageResult(null);
    setError(null);
    setLoading(true);
    try {
      if (mode === "letter") setResult(await checkHandwriting(file));
      else setPageResult(await checkHandwritingPage(file));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function onImgLoad() {
    if (imgRef.current) {
      setImgSize({ w: imgRef.current.clientWidth, h: imgRef.current.clientHeight });
    }
  }

  const scaleX = pageResult ? imgSize.w / pageResult.image_width : 1;
  const scaleY = pageResult ? imgSize.h / pageResult.image_height : 1;
  const mistakes = pageResult ? pageResult.letters.filter((l) => l.verdict !== "normal") : [];

  return (
    <div>
      <div className="card">
        <label>What are you checking?</label>
        <div className="row">
          <button className={mode === "letter" ? "btn" : "btn btn-outline"} onClick={() => setMode("letter")}>
            Single letter
          </button>
            <button className={mode === "page" ? "btn" : "btn btn-outline"} onClick={() => setMode("page")}>
            Full passage (experimental)
          </button>
        </div>
        <p className="hint" style={{ marginTop: 10 }}>
          {mode === "letter"
            ? "Upload a photo of one handwritten letter."
            : "Works best with clear, spaced-out print handwriting — connected cursive won't separate into individual letters correctly."}
        </p>
        <input type="file" accept="image/*" onChange={handleUpload} style={{ marginTop: 10 }} />
        {loading && <p className="hint">Checking...</p>}
        {error && <p className="error-msg">{error}</p>}
      </div>

      {preview && mode === "letter" && (
        <div className="card">
          <img src={preview} alt="uploaded letter" style={{ maxWidth: 160, borderRadius: "var(--radius-sm)", border: "1px solid var(--border)" }} />
        </div>
      )}

      {preview && mode === "page" && pageResult && (
        <div className="card">
          <div style={{ position: "relative", display: "inline-block", maxWidth: "100%" }}>
            <img
              ref={imgRef}
              src={preview}
              alt="uploaded handwriting"
              onLoad={onImgLoad}
              style={{ maxWidth: "100%", display: "block", borderRadius: "var(--radius-sm)", border: "1px solid var(--border)" }}
            />
            {pageResult.letters.map((l) => (
              <div
                key={l.index}
                style={{
                  position: "absolute",
                  left: l.bbox[0] * scaleX,
                  top: l.bbox[1] * scaleY,
                  width: l.bbox[2] * scaleX,
                  height: l.bbox[3] * scaleY,
                  border: `2px solid ${COLORS[l.verdict]}`,
                  borderRadius: 3,
                  pointerEvents: "none",
                }}
                title={`${l.index + 1}: ${LABELS[l.verdict]}`}
              />
            ))}
          </div>
        </div>
      )}

      {result && (
        <div className="card">
          <span className="badge" data-band={result.verdict === "reversal" ? "monitor" : "low_indicator"}>
            {LABELS[result.verdict]}
          </span>
          <div className="stat-grid" style={{ marginTop: 16 }}>
            <div className="stat"><div className="value">{(result.normal * 100).toFixed(0)}%</div><div className="label">normal</div></div>
            <div className="stat"><div className="value">{(result.reversal * 100).toFixed(0)}%</div><div className="label">reversal</div></div>
            <div className="stat"><div className="value">{(result.corrected * 100).toFixed(0)}%</div><div className="label">corrected</div></div>
          </div>
        </div>
      )}

      {pageResult && (
        <div className="card">
          <div className="stat-grid">
            <div className="stat"><div className="value">{pageResult.total_detected}</div><div className="label">letters detected</div></div>
            <div className="stat"><div className="value">{pageResult.reversal_count}</div><div className="label">possible reversals</div></div>
            <div className="stat"><div className="value">{(pageResult.reversal_rate * 100).toFixed(0)}%</div><div className="label">reversal rate</div></div>
          </div>

          {mistakes.length > 0 && (
            <div style={{ marginTop: 18 }}>
              <label>Flagged letters</label>
              <div className="history-list">
                {mistakes.map((l) => (
                  <div className="history-row" key={l.index}>
                    <span>Letter #{l.index + 1}</span>
                    <span className="badge" data-band={l.verdict === "reversal" ? "monitor" : "low_indicator"}>
                      {LABELS[l.verdict]} ({(l.reversal_prob * 100).toFixed(0)}%)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <p className="hint" style={{ marginTop: 14 }}>
            Note: this detects reversal-like stroke patterns, not specific target letters — it isn't told which letter it's
            looking at. Treat results on cursive or connected writing as a rough indicator, not a precise reading.
          </p>
        </div>
      )}
    </div>
  );
}