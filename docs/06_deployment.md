# Deployment

## Local

```bash
docker compose -f deployment/docker/docker-compose.yml up --build
# api       -> http://localhost:8000/docs
# frontend  -> http://localhost:3000
```

Three services: FastAPI, Postgres, nginx-served React build.

## Design decisions

**Weights are mounted, not baked.** `VOLUME ["/app/models"]`. Keeps the image
small, lets you swap a retrained model without a rebuild, and keeps model
artefacts out of your git history.

**Models load at startup, not per request.** Loading Whisper per request costs
~8 seconds and will kill your demo. The `lifespan` handler in `api/main.py` loads
once; heavy predictors load lazily on first use.

**Whisper on CPU is the bottleneck.** `small` takes roughly 1× realtime on CPU —
a 30-second recording takes ~30 seconds. Options in order of preference:
1. GPU host (10–20× faster)
2. drop to `base` (worse on child speech — measure the WER cost before committing)
3. `faster-whisper` (CTranslate2 backend, ~4× faster on CPU, same weights)
4. chunk the audio and process segments in parallel

The nginx `proxy_read_timeout` is set to 120s for this reason.

**The handwriting CNN exports to ONNX** (`scripts/export_onnx.py`) so letter
checking can run in the browser with onnxruntime-web — no round trip, works offline,
and no child's handwriting leaves the device.

## Production checklist

- [ ] `.env` is not committed, secrets come from the platform's secret store
- [ ] CORS restricted to your actual frontend origin (currently `*` for dev)
- [ ] Audio uploads capped (nginx `client_max_body_size 25M`) and validated by MIME type
- [ ] Rate limiting on `/session/analyze` — it is the expensive endpoint
- [ ] Temp audio files deleted after processing (currently they are not — fix before any real use)
- [ ] Postgres backups + migrations via alembic
- [ ] Structured logging with a request id; never log transcript text
- [ ] Health check wired to the orchestrator

## Hosting options for a student project

| Option | Cost | Notes |
| --- | --- | --- |
| Render / Railway | free–low | easiest; CPU only, so use `faster-whisper` |
| HuggingFace Spaces | free | great for the demo; Gradio wrapper around the same pipeline |
| Oracle Cloud free tier | free | 4 ARM cores — genuinely usable |
| Local + ngrok | free | fine for a hackathon demo, not for a submission link |

Ship a 2-minute demo video alongside any hosted link. Judges' wifi fails; your
video does not.
