import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";

const API_BASE = import.meta.env.VITE_API_BASE;
if (API_BASE) {
  const realFetch = window.fetch.bind(window);
  window.fetch = (input, init = {}) => {
    const url = typeof input === "string" ? input : input.url;
    if (url.startsWith(API_BASE)) {
      init = { ...init, headers: { ...(init.headers || {}), "ngrok-skip-browser-warning": "true" } };
    }
    return realFetch(input, init);
  };
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);