# Frontend

Vite + React. Build the pages in this order - each maps to one backend endpoint.

| Page | Endpoint | Purpose |
| --- | --- | --- |
| `pages/Reader.tsx` | `POST /read/ocr`, `POST /read/speak` | upload page, read aloud, word highlighting |
| `pages/ReadAloudSession.tsx` | `POST /session/analyze` | child reads, mic records, errors returned |
| `pages/Simplify.tsx` | `POST /simplify` | side-by-side original vs simplified |
| `pages/Coach.tsx` | `GET /coach/next/{id}`, `POST /coach/feedback` | targeted exercises |
| `pages/Dashboard.tsx` | session history | WPM trend, error mix, risk band |

## Accessibility rules (non-negotiable for this project)

- Font: OpenDyslexic or Lexend, minimum 18px
- Letter spacing >= 0.12em, word spacing >= 0.16em, line height >= 1.6
- Background: cream `#FAF3E0` or soft grey - never pure white on black
- Max 65 characters per line
- Current word highlighted with a background block, not just colour change
- Every colour cue paired with a shape/weight cue (colour-blind safety)
- No autoplay audio, no timers visible to the child
