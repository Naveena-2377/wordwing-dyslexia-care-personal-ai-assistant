const BASE = "http://localhost:8000";

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function simplifyText(text, targetGrade = 3) {
  const res = await fetch(`${BASE}/simplify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, target_grade: targetGrade }),
  });
  if (!res.ok) throw new Error(`Simplify failed (${res.status})`);
  return res.json();
}

export async function analyzeSession(audioBlob, targetText, childId, token) {
  const form = new FormData();
  form.append("audio", audioBlob, "recording.webm");
  form.append("target_text", targetText);
  form.append("child_id", childId || "guest");

  const res = await fetch(`${BASE}/session/analyze`, {
    method: "POST",
    headers: authHeaders(token),
    body: form,
  });
  if (!res.ok) throw new Error(`Analysis failed (${res.status})`);
  return res.json();
}

export async function nextExercise(childId) {
  const res = await fetch(`${BASE}/coach/next/${encodeURIComponent(childId)}`);
  if (!res.ok) throw new Error(`Coach request failed (${res.status})`);
  return res.json();
}

export async function sendFeedback(childId, exercise, improved) {
  const res = await fetch(`${BASE}/coach/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ child_id: childId, exercise, improved }),
  });
  if (!res.ok) throw new Error(`Feedback failed (${res.status})`);
  return res.json();
}

export async function getDashboard(token) {
  const res = await fetch(`${BASE}/dashboard/me`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error(`Dashboard request failed (${res.status})`);
  return res.json();
}
export async function ocrImage(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/read/ocr`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`OCR failed (${res.status})`);
  return res.json();
}

export async function getSyllables(word) {
  const res = await fetch(`${BASE}/read/syllables`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ word }),
  });
  if (!res.ok) throw new Error(`Syllable split failed (${res.status})`);
  return res.json();
}

export async function checkHandwriting(file) {
  const form = new FormData();
  form.append("image", file);
  const res = await fetch(`${BASE}/handwriting/check`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Handwriting check failed (${res.status})`);
  return res.json();
}