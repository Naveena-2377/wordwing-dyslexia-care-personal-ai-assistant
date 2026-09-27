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
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(name, email, password);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-shell">
            <div className="auth-card blob-bg">
        <div className="mascot-wrap">
          <div className="mascot-bounce"><Mascot size={72} /></div>
        </div>
        <div className="brand" style={{ marginBottom: 24, justifyContent: "center" }}>
          Word<span>Wing</span>
        </div>
        <h1 className="panel-title" style={{ fontSize: "1.3rem" }}>
          {mode === "login" ? "Welcome back" : "Create your account"}
        </h1>
        <p className="panel-sub" style={{ marginBottom: 20 }}>
          {mode === "login"
            ? "Log in to see your reading progress."
            : "Track reading sessions and get personalized exercises."}
        </p>

        <form onSubmit={handleSubmit}>
          {mode === "register" && (
            <div className="field">
              <label htmlFor="name">Name</label>
              <input
                id="name" type="text" value={name}
                onChange={(e) => setName(e.target.value)} required
              />
            </div>
          )}
          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email" type="text" value={email}
              onChange={(e) => setEmail(e.target.value)} required
            />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password" type="password" value={password}
              onChange={(e) => setPassword(e.target.value)} required
            />
          </div>
          {error && <p className="error-msg">{error}</p>}
          <button className="btn" type="submit" disabled={busy} style={{ width: "100%" }}>
            {busy ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}
          </button>
        </form>

        <p className="hint" style={{ marginTop: 18, textAlign: "center" }}>
          {mode === "login" ? "New here?" : "Already have an account?"}{" "}
          <button
            className="link-btn"
            onClick={() => setMode(mode === "login" ? "register" : "login")}
          >
            {mode === "login" ? "Create an account" : "Log in"}
          </button>
        </p>
      </div>
    </div>
  );
}