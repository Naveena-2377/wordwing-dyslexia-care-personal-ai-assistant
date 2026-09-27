import { useState ,useEffect} from "react";
import { AuthProvider, useAuth } from "./AuthContext";
import AuthScreen from "./components/AuthScreen";
import ReadingSession from "./components/ReadingSession";
import Simplify from "./components/Simplify";
import Dashboard from "./components/Dashboard";
import ReadAloud from "./components/ReadAloud";
import HandwritingCheck from "./components/HandwritingCheck";
import "./styles/theme.css";
import Mascot from "./components/Mascot";

const TABS = [
  { id: "session", label: "Reading session", icon: "🎙️" },
  { id: "dashboard", label: "Dashboard", icon: "📊" },
  { id: "readaloud", label: "Read a page", icon: "📖" },
  { id: "handwriting", label: "Handwriting check", icon: "✏️" },
  { id: "simplify", label: "Simplify text", icon: "✍️" },
];

const TITLES = {
  session: ["Reading session", "Record a passage and see word-by-word feedback."],
  dashboard: ["Your progress", "Trends across every session you've completed."],
  readaloud: ["Read a page", "Upload a page, hear it read aloud, break tricky words into syllables."],
  handwriting: ["Handwriting check", "Upload a handwritten image"],
  simplify: ["Simplify text", "Rewrite complex sentences in simpler words."],
};

const TINTS = [
  { id: "cream", color: "#FBF3E3" },
  { id: "mint", color: "#EAF5EC" },
  { id: "lavender", color: "#F3EEFA" },
];

function initials(name) {
  return name.split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase();
}

function MainApp() {
  const { user, logout } = useAuth();
  const [tab, setTab] = useState("session");
  const [dyslexiaMode, setDyslexiaMode] = useState(false);
  const [textSize, setTextSize] = useState("standard");
  const [tint, setTint] = useState("cream");
  const [title, sub] = TITLES[tab];


  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute("data-mode", dyslexiaMode ? "dyslexia" : "default");
    root.setAttribute("data-size", textSize);
    root.setAttribute("data-tint", tint);
  }, [dyslexiaMode, textSize, tint]);

  return (
    <div
      className="app-shell">
      <aside className="sidebar">
        <div className="mascot-wrap">
          <div className="mascot-bounce"><Mascot size={54} /></div>
        </div>
        <div className="brand" style={{ justifyContent: "center" }}>Word<span>Wing</span></div>

        {TABS.map((t) => (
          <button
            key={t.id}
            className="nav-item"
            data-active={tab === t.id}
            onClick={() => setTab(t.id)}
          >
            <span className="icon-chip">{t.icon}</span>
            <span>{t.label}</span>
            <span className="dot" style={{ marginLeft: "auto" }} />
          </button>
        ))}

        <div className="sidebar-footer">
          <div className="mode-row">
            <span>Dyslexia mode</span>
            <button
              className="switch"
              data-on={dyslexiaMode}
              onClick={() => setDyslexiaMode((v) => !v)}
              aria-pressed={dyslexiaMode}
              aria-label="Toggle dyslexia-friendly mode"
            />
          </div>

          {dyslexiaMode && (
            <div className="dys-settings">
              <div className="dys-settings-label">Text size</div>
              <div className="dys-chip-row">
                {["standard", "large", "xlarge"].map((s) => (
                  <button
                    key={s}
                    className="dys-chip"
                    data-active={textSize === s}
                    onClick={() => setTextSize(s)}
                  >
                    {s === "standard" ? "A" : s === "large" ? "A+" : "A++"}
                  </button>
                ))}
              </div>

              <div className="dys-settings-label">Background</div>
              <div className="dys-chip-row">
                {TINTS.map((t) => (
                  <button
                    key={t.id}
                    className="tint-swatch"
                    data-active={tint === t.id}
                    style={{ background: t.color }}
                    onClick={() => setTint(t.id)}
                    aria-label={`${t.id} background`}
                  />
                ))}
              </div>
            </div>
          )}

          <div className="sidebar-user">
            <div className="avatar">{initials(user.name)}</div>
            <div>
              <div className="name">{user.name}</div>
              <div className="email">{user.email}</div>
            </div>
          </div>
          <button className="btn btn-outline" style={{ width: "100%" }} onClick={logout}>
            Log out
          </button>
        </div>
      </aside>

      <div className="main-area">
          <div className="page-header blob-bg">
          <h1 className="panel-title">{title}</h1>
          <p className="panel-sub">{sub}</p>
        </div>
        <div className="content">
          {tab === "session" && <ReadingSession childId={user.email} />}
          {tab === "dashboard" && <Dashboard />}
          {tab === "readaloud" && <ReadAloud />}
          {tab === "handwriting" && <HandwritingCheck />}
          {tab === "simplify" && <Simplify />}
        </div>
      </div>
    </div>
  );
}

function Gate() {
  const { user, loading } = useAuth();
  if (loading) return <div className="auth-shell"><p className="empty">Loading...</p></div>;
  return user ? <MainApp /> : <AuthScreen />;
}

export default function App() {
  return (
    <AuthProvider>
      <Gate />
    </AuthProvider>
  );
}