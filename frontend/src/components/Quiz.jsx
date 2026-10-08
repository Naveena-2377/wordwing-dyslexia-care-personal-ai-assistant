import { useState } from "react";
import { generateQuiz } from "../api";
import Mascot from "./Mascot";

export default function Quiz() {
  const [file, setFile] = useState(null);
  const [numQuestions, setNumQuestions] = useState(5);
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [current, setCurrent] = useState(0);
  const [selected, setSelected] = useState(null);
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);

  async function handleGenerate() {
    if (!file) return;
    setError(null);
    setLoading(true);
    try {
      const res = await generateQuiz(file, numQuestions);
      setQuiz(res);
      setCurrent(0);
      setSelected(null);
      setScore(0);
      setFinished(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function selectAnswer(i) {
    if (selected !== null) return;
    setSelected(i);
    if (i === quiz.questions[current].correct_index) setScore((s) => s + 1);
  }

  function nextQuestion() {
    if (current + 1 >= quiz.questions.length) setFinished(true);
    else { setCurrent((c) => c + 1); setSelected(null); }
  }

  function restart() { setQuiz(null); setFile(null); }

  if (!quiz) {
    return (
      <div className="card">
        <label>Upload a story, rhyme, or worksheet (image, PDF, or text file)</label>
        <input type="file" accept="image/*,.pdf,.txt" onChange={(e) => setFile(e.target.files[0])} />
        <div className="field" style={{ marginTop: 14 }}>
          <label htmlFor="numq">Number of questions</label>
          <input
            id="numq" type="text" value={numQuestions}
            onChange={(e) => setNumQuestions(Number(e.target.value) || 5)}
            style={{ maxWidth: 80 }}
          />
        </div>
        <button className="btn" onClick={handleGenerate} disabled={!file || loading}>
          {loading ? "Building your quiz..." : "Generate Quiz"}
        </button>
        {error && <p className="error-msg">{error}</p>}
      </div>
    );
  }

  if (finished) {
    const pct = Math.round((score / quiz.questions.length) * 100);
    return (
      <div className="card celebrate" style={{ textAlign: "center" }}>
        <Mascot size={72} mood={pct >= 60 ? "happy" : "neutral"} />
        <h2 style={{ fontFamily: "var(--font-display)", margin: "12px 0 4px" }}>
          {pct >= 80 ? "Amazing job! 🎉" : pct >= 50 ? "Nice work! 👍" : "Good try! 💪"}
        </h2>
        <p className="panel-sub">You scored {score} out of {quiz.questions.length} ({pct}%)</p>
        <button className="btn" style={{ marginTop: 16 }} onClick={restart}>Make another quiz</button>
      </div>
    );
  }

  const q = quiz.questions[current];
  return (
    <div>
      <div className="level-bar" style={{ marginBottom: 16 }}>
        <div className="level-bar-fill" style={{ width: `${(current / quiz.questions.length) * 100}%` }} />
      </div>
      <div className="card">
        <div className="hint">Question {current + 1} of {quiz.questions.length}</div>
        <h3 style={{ fontFamily: "var(--font-display)", margin: "8px 0 18px" }}>{q.question}</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {q.options.map((opt, i) => {
            let style = {};
            if (selected !== null) {
              if (i === q.correct_index) style = { background: "var(--ok-bg)", borderColor: "var(--ok)" };
              else if (i === selected) style = { background: "var(--error-bg)", borderColor: "var(--error)" };
            }
            return (
              <button
                key={i}
                className="btn-outline"
                style={{ textAlign: "left", padding: "12px 16px", borderRadius: "var(--radius-sm)", ...style }}
                onClick={() => selectAnswer(i)}
              >
                {opt}
              </button>
            );
          })}
        </div>
        {selected !== null && (
          <div style={{ marginTop: 16 }}>
            <p className="hint">{q.explanation}</p>
            <button className="btn" onClick={nextQuestion} style={{ marginTop: 10 }}>
              {current + 1 >= quiz.questions.length ? "See results" : "Next question"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}