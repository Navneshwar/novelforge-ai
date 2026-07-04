# Deploying NovelForge publicly (no Ollama)

What changed to make this possible:
- `backend/main.py` now serves the built frontend directly (one process, one
  URL — see the static mount + SPA catch-all near the bottom of the file).
  The old `/` JSON welcome message moved to `/api/status`.
- `backend/requirements.txt` installs `cognee[groq,fastembed]` instead of
  relying on a local Ollama server.
- `backend/.env.production.example` — Groq (LLM) + fastembed (embeddings).
  fastembed runs in-process, so there's nothing extra to host for embeddings.
- Root `Dockerfile` — multi-stage build: builds the frontend, then runs the
  backend which serves it.

None of `memory_service.py`'s remember/recall/improve/forget code changed —
those calls are provider-agnostic. Only the env vars that pick the provider
changed.

## 1. Get a Groq API key (2 minutes)
https://console.groq.com/keys → create key. Free tier is generous enough for
a demo. As of this writing `openai/gpt-oss-20b` is Groq's current
fast/cheap model (they deprecated llama-3.1-8b-instant and
llama-3.3-70b-versatile in June 2026) — double check
https://console.groq.com/docs/models if you're reading this much later.

## 2. Deploy — Railway (recommended, fastest with a Dockerfile + volume)
1. Push this repo to GitHub if it isn't already.
2. https://railway.app → New Project → Deploy from GitHub repo → pick this repo.
   Railway auto-detects the root `Dockerfile`.
3. Add a **Volume**: Settings → Volumes → mount path `/app/backend/data`.
   This is where SQLite + Cognee's local vector/graph stores persist —
   without this, every redeploy wipes memory.
4. Add environment variables (Variables tab) — copy everything from
   `backend/.env.production.example`, filling in your real `LLM_API_KEY`
   and a real `SECRET_KEY` (any long random string).
5. Deploy. Railway gives you a public `*.up.railway.app` URL — that's it,
   share that with judges.

## Alternative: Render
Same idea — New → Web Service → Docker → this repo → add a **Persistent
Disk** mounted at `/app/backend/data` → same env vars → deploy. Render's
free tier spins down on idle (~30–60s cold start on the first request after
inactivity), which matters if judges try it cold — worth knowing before
your live demo, not just after.

## 3. Verify before you present
- Open the public URL, not localhost.
- Run the full remember → recall → improve → forget → generate → graph loop
  once against the live deployment, the same way you tested it locally.
  Groq's output will differ from Ollama's — same shape, different phrasing —
  so re-check nothing downstream (consistency checker, graph visualizer)
  assumed something Ollama-specific about response format.
- Still record the local/Ollama backup video too. A public URL adds a new
  failure mode (cold starts, Groq rate limits, host outages) on top of the
  old ones — it doesn't remove the need for a backup.

## What NOT to do tonight
Don't also try to wire up Cognee Cloud for the second prize track on top of
this. That's a genuinely different integration path (`cognee.serve()`, not
env vars) and mixing it in tonight risks breaking the thing that already
works. If the Groq+fastembed deploy is solid with time to spare, treat
Cognee Cloud as a stretch goal, not a checklist item.
