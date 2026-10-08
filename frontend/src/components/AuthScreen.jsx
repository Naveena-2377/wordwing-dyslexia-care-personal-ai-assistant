import { useState } from "react";
import { useAuth } from "../AuthContext";
import Mascot from "./Mascot";

export default function AuthScreen() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (mode === "login") await login(email, password);
      else await register(name, email, password);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-shell-split">
        <div className="auth-illustration">
        <div className="glow-ring" />
        <div className="float-shape s1" style={{ width: 70, height: 70, top: "10%", left: "12%" }} />
        <div className="float-shape s3" style={{ width: 90, height: 90, top: "16%", right: "10%" }} />
        <div className="float-shape s4" style={{ width: 45, height: 45, bottom: "26%", left: "8%" }} />
        <span className="star-twinkle" style={{ top: "18%", left: "28%", fontSize: "1.5rem" }}>✨</span>
        <span className="star-twinkle" style={{ top: "65%", right: "20%", fontSize: "1.3rem", animationDelay: "0.6s" }}>⭐</span>
        <span className="star-twinkle" style={{ top: "38%", right: "32%", fontSize: "1.1rem", animationDelay: "1.1s" }}>✨</span>

        <div className="big-mascot">
          <Mascot size={230} />
        </div>
        <div className="ground-wave" />
        <div className="auth-illustration-text">
          <h2>Welcome to WordWing!</h2>
          <p>Every child reads at their own pace — let's make it fun.</p>
        </div>
      </div>

      <div className="auth-form-side">
        <div className="auth-card">
          <div className="brand" style={{ marginBottom: 10, justifyContent: "center" }}>
            Word<span>Wing</span>
          </div>
          <div style={{ textAlign: "center" }}>
            <span className="auth-tagline">✨ Reading made fun ✨</span>
          </div>

          <h1 className="panel-title" style={{ fontSize: "1.3rem", textAlign: "center", marginTop: 6 }}>
            {mode === "login" ? "Welcome back!" : "Let's get started!"}
          </h1>
          <p className="panel-sub" style={{ marginBottom: 20, textAlign: "center" }}>
            {mode === "login"
              ? "Log in to see your reading progress."
              : "Create an account to start your reading adventure."}
          </p>

          <form onSubmit={handleSubmit}>
            {mode === "register" && (
              <div className="field">
                <label htmlFor="name">Name</label>
                <input id="name" type="text" value={name} onChange={(e) => setName(e.target.value)} required />
              </div>
            )}
            <div className="field">
              <label htmlFor="email">Email</label>
              <input id="email" type="text" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="field">
              <label htmlFor="password">Password</label>
              <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            {error && <p className="error-msg">{error}</p>}
            <button className="btn" type="submit" disabled={busy} style={{ width: "100%" }}>
              {busy ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}
            </button>
          </form>

          <p className="hint" style={{ marginTop: 18, textAlign: "center" }}>
            {mode === "login" ? "New here?" : "Already have an account?"}{" "}
            <button className="link-btn" onClick={() => setMode(mode === "login" ? "register" : "login")}>
              {mode === "login" ? "Create an account" : "Log in"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}