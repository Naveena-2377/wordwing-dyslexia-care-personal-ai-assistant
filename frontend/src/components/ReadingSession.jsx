import { useState, useRef } from "react";
import { analyzeSession, sendFeedback } from "../api";
import { useAuth } from "../AuthContext";

const DEFAULT_TEXT = "The cat sat on the warm mat.";

export default function ReadingSession({ childId }) {
  const { token } = useAuth();
  const [targetText, setTargetText] = useState(DEFAULT_TEXT);
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const mediaRecorder = useRef(null);
  const chunks = useRef([]);

  async function startRecording() {
    setError(null);
    setResult(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      chunks.current = [];
      mr.ondataavailable = (e) => chunks.current.push(e.data);
      mr.onstop = () => {
        const blob = new Blob(chunks.current, { type: "audio/webm" });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach((t) => t.stop());
      };
      mr.start();
      mediaRecorder.current = mr;
      setRecording(true);
    } catch {
      setError("Couldn't access your microphone. Check browser permissions, or upload a file instead.");
    }
  }

  function stopRecording() {
    mediaRecorder.current?.stop();
    setRecording(false);
  }

  function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setAudioBlob(file);
    setAudioUrl(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  }

  async function handleAnalyze() {
    if (!audioBlob || !targetText.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await analyzeSession(audioBlob, targetText, childId,token);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleFeedback(improved) {
    if (!result) return;
    try {
      await sendFeedback(childId, result.next_exercise, improved);
    } catch {
      // non-critical, fail silently
    }
  }

  return (
    <div>
      <div className="card">
        <div className="field">
          <label htmlFor="target">Passage to read</label>
          <textarea
            id="target"
            rows={2}
            value={targetText}
            onChange={(e) => setTargetText(e.target.value)}
          />
        </div>

        <div className="row">
          {!recording ? (
            <button className="btn btn-record" onClick={startRecording}>
              ● Start recording
            </button>
          ) : (
            <button className="btn btn-record" onClick={stopRecording}>
              ■ Stop recording
            </button>
          )}
          <label className="btn btn-outline" style={{ margin: 0 }}>
            Upload audio file
            <input type="file" accept="audio/*" onChange={handleFileUpload} hidden />
          </label>
        </div>

        {audioUrl && (
          <div style={{ marginTop: 16 }}>
            <audio controls src={audioUrl} style={{ width: "100%" }} />
          </div>
        )}

        <div style={{ marginTop: 16 }}>
          <button className="btn" onClick={handleAnalyze} disabled={!audioBlob || loading}>
            {loading ? "Analyzing..." : "Analyze reading"}
          </button>
        </div>

        {error && <p className="error-msg">{error}</p>}
      </div>

      {result && (
        <div className="card">
          <div className="stat-grid">
            <div className="stat">
              <div className="value">{result.wpm.toFixed(0)}</div>
              <div className="label">words per minute</div>
            </div>
            <div className="stat">
              <div className="value">{(result.accuracy * 100).toFixed(0)}%</div>
              <div className="label">accuracy</div>
            </div>
            <div className="stat">
              <span className="badge" data-band={result.risk_band}>
                {result.risk_band.replace(/_/g, " ")}
              </span>
              <div className="label" style={{ marginTop: 6 }}>screening indicator</div>
            </div>
          </div>

          <label>Word-by-word result</label>
          <div className="result-line">
            {result.word_errors.map((w) => (
              <span
                key={w.position}
                className="word"
                data-status={w.label === "correct" ? "correct" : "error"}
                title={w.label}
              >
                {w.spoken || w.target || "—"}
              </span>
            ))}
          </div>

          <div className="card" style={{ background: "var(--bg)", marginTop: 16, marginBottom: 0 }}>
            <label>Suggested next exercise</label>
            <p style={{ margin: "4px 0 12px", fontWeight: 600 }}>
              {result.next_exercise.replace(/_/g, " ")}
            </p>
            <div className="row">
              <button className="btn btn-outline" onClick={() => handleFeedback(true)}>
                Helped
              </button>
              <button className="btn btn-outline" onClick={() => handleFeedback(false)}>
                Didn't help
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}