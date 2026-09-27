import { useState } from "react";
import { ocrImage, getSyllables } from "../api";

export default function ReadAloud() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [loadingOcr, setLoadingOcr] = useState(false);
  const [error, setError] = useState(null);
  const [speaking, setSpeaking] = useState(false);

  const [word, setWord] = useState("");
  const [syllables, setSyllables] = useState(null);

  async function handleUpload(e) {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setError(null);
    setLoadingOcr(true);
    try {
      const res = await ocrImage(f);
      setText(res.text);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingOcr(false);
    }
  }

  function speak(str) {
    if (!str.trim() || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(str);
    utter.rate = 0.85;
    utter.onstart = () => setSpeaking(true);
    utter.onend = () => setSpeaking(false);
    window.speechSynthesis.speak(utter);
  }

  async function handleSyllables() {
    if (!word.trim()) return;
    setError(null);
    try {
      const res = await getSyllables(word.trim());
      setSyllables(res.syllables);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <div className="card">
        <label>Upload a page or worksheet photo</label>
        <input type="file" accept="image/*" onChange={handleUpload} />
        {loadingOcr && <p className="hint">Reading the page...</p>}
        {error && <p className="error-msg">{error}</p>}
      </div>

      {text && (
        <div className="card">
          <label htmlFor="extracted">Extracted text</label>
          <textarea
            id="extracted"
            rows={4}
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <div className="row" style={{ marginTop: 14 }}>
            <button className="btn" onClick={() => speak(text)} disabled={speaking}>
              {speaking ? "Reading..." : "🔊 Read aloud"}
            </button>
            {speaking && (
              <button className="btn btn-outline" onClick={() => window.speechSynthesis.cancel()}>
                Stop
              </button>
            )}
          </div>
        </div>
      )}

      <div className="card">
        <label htmlFor="syl-word">Break a tricky word into syllables</label>
        <div className="row">
          <input
            id="syl-word" type="text" value={word}
            onChange={(e) => setWord(e.target.value)}
            style={{ flex: 1 }}
            placeholder="e.g. elephant"
          />
          <button className="btn btn-outline" onClick={handleSyllables}>Break it down</button>
        </div>
        {syllables && (
          <div style={{ marginTop: 16 }}>
            <div className="result-line">
              {syllables.map((s, i) => (
                <span className="word" key={i}>{s}</span>
              ))}
            </div>
            <button className="btn btn-outline" onClick={() => speak(syllables.join(" "))}>
              🔊 Say it slowly
            </button>
          </div>
        )}
      </div>
    </div>
  );
}