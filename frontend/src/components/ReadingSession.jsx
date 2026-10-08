import { useState, useRef } from "react";
import { useAuth } from "../AuthContext";
import { analyzeSession, sendFeedback, ocrImage } from "../api";

const DEFAULT_TEXT = "The cat sat on the warm mat.";
const EXERCISE_INFO = {
  phoneme_blending: { label: "Sound Blending", desc: "Practice blending individual sounds together to read whole words." },
  bd_pq_discrimination: { label: "Letter Shapes (b/d, p/q)", desc: "Practice telling apart letters that look similar, like b and d." },
  sight_word_drill: { label: "Sight Words", desc: "Practice common words that come up often in reading." },
  syllable_chunking: { label: "Breaking Words Apart", desc: "Practice splitting long words into smaller chunks to read them easier." },
  fluency_repeated_reading: { label: "Reading Practice", desc: "Read the same short passage a few times to build speed and confidence." },
  comprehension_qa: { label: "Understanding Check", desc: "Practice answering simple questions about what was read." },
};

export default function ReadingSession({ childId }) {
  const { token } = useAuth();
  const [targetText, setTargetText] = useState(DEFAULT_TEXT);
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [ocrLoading, setOcrLoading] = useState(false);

  async function handlePassageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setOcrLoading(true);
    try {
      const res = await ocrImage(file);
      setTargetText(res.text);
    } catch (err) {
      setError(err.message);
    } finally {
      setOcrLoading(false);
    }
  }

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
          <div style={{ marginTop: 8 }}>
            <label className="btn-outline" style={{ display: "inline-block", padding: "8px 16px", fontSize: "0.85em" }}>
              {ocrLoading ? "Reading photo..." : "📷 Or upload a photo of the passage"}
              <input type="file" accept="image/*" onChange={handlePassageUpload} hidden disabled={ocrLoading} />
            </label>
            <p className="hint" style={{ marginTop: 6 }}>
              Photos aren't always read perfectly — please check the text above matches the real passage before recording.
            </p>
          </div>
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
            <label>Suggested next activity</label>
            <p style={{ margin: "4px 0 4px", fontWeight: 700, fontFamily: "var(--font-display)" }}>
              {(EXERCISE_INFO[result.next_exercise] || { label: result.next_exercise.replace(/_/g, " ") }).label}
            </p>
            <p className="hint" style={{ marginBottom: 12 }}>
              {(EXERCISE_INFO[result.next_exercise] || {}).desc || ""}
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