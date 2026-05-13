# Deploy AstraRAG (step by step)

This project has **two parts**: a **FastAPI backend** (RAG + agents) and a **Streamlit frontend** (chat UI). The simplest production-style setup is **API on Render** + **UI on Streamlit Community Cloud**.

---

## Part A — Push code to GitHub

1. Commit and push this repository to GitHub (if it is not already there).
2. Keep **`.env` out of git** (it is in `.gitignore`). You will set secrets on each platform.

---

## Part B — Deploy the backend (Render)

1. Go to [https://render.com](https://render.com) and sign in (GitHub login is fine).
2. **New** → **Web Service** → connect your GitHub repo → select **AstraRAG-Agentic-RAG-Chatbot**.
3. Configure the service:
   - **Name**: e.g. `astrarag-api`
   - **Region**: choose closest to you
   - **Branch**: `main`
   - **Runtime**: **Python 3**
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `uvicorn src.backend_src.main:app --host 0.0.0.0 --port $PORT`
   - **Instance type**: Free is OK for testing (cold starts are slow; ML deps may need a paid plan for stability).
4. Open **Environment** and add:
   - `OPENAI_API_KEY` — required for OpenAI models (e.g. `gpt-4o-mini`)
   - Or for **Gemini**: `GOOGLE_API_KEY` and `MODEL_NAME` (e.g. `gemini/gemini-2.0-flash`) instead of relying on `OPENAI_API_KEY`
   - Optional: `MODEL_NAME`, `MODEL_TEMPERATURE`, `VECTOR_STORE_DIR`, `COLLECTION_NAME`
   - Optional: `CORS_ORIGINS` = `*` for quick demos, or your Streamlit URL once you know it (comma-separated list)
5. **Create Web Service** and wait for the first deploy to finish.
6. Copy your public URL, e.g. `https://astrarag-api.onrender.com`
7. **Smoke test** in a browser:
   - `https://YOUR_URL/health` → should return JSON `{"status":"healthy",...}`

**Note:** On free tiers the filesystem is **ephemeral**. After a restart, **`doc_vector_store`** is empty until users upload PDFs again. For a permanent index, use a paid disk add-on or a different vector store.

---

## Part C — Deploy the frontend (Streamlit Community Cloud)

1. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud) and sign in with GitHub.
2. **New app** → pick the same repo → **Main file path**: `src/frontend_src/app.py`
3. **Advanced settings** → **Python version**: 3.11 (match `runtime.txt` if possible).
4. Open **Secrets** (gear icon → Secrets) and paste (replace with your real API URL, no trailing slash):

   ```toml
   API_BASE_URL = "https://YOUR_RENDER_URL"
   CHAT_ENDPOINT_URL = "https://YOUR_RENDER_URL/chat/answer"
   ```

5. **Deploy**. When the app loads, open the sidebar and try **Upload** and chat.

A copy of the secret template lives at `deploy/streamlit-secrets.example.toml`.

---

## Part D — Verify end-to-end

1. Backend: `GET https://YOUR_RENDER_URL/health`
2. Frontend: upload a small PDF, wait for indexing, ask one question.
3. If the UI says backend offline, recheck **Secrets** URLs (must be `https`, exact host, no typo).

---

## Alternative: Docker (any host)

From the repo root:

```bash
docker build -t astrarag-api .
docker run -p 8001:8001 -e OPENAI_API_KEY=sk-... -e PORT=8001 astrarag-api
```

Render can also deploy from the **Dockerfile** instead of the Python build; switch the service type to Docker in the Render dashboard if you prefer.

---

## Alternative: Railway

1. [https://railway.app](https://railway.app) → New Project → Deploy from GitHub → select repo.
2. Add variables: `OPENAI_API_KEY`, optionally `API_HOST=0.0.0.0`.
3. **Start command** (or use the included `Procfile`):  
   `uvicorn src.backend_src.main:app --host 0.0.0.0 --port $PORT`  
   Railway sets `PORT` automatically.
4. Copy the generated public URL and put it into Streamlit Secrets as in Part C.

---

## Troubleshooting

| Symptom | What to check |
|--------|----------------|
| Render build fails (memory / timeout) | Use a paid instance or slim dependencies; first install is heavy. |
| 502 / app crashes on first chat | Logs on Render; confirm `OPENAI_API_KEY` and enough RAM. |
| Streamlit “Backend offline” | `API_BASE_URL` / `CHAT_ENDPOINT_URL` in Streamlit Secrets; Render service must be running. |
| CORS errors in browser | Set `CORS_ORIGINS` on the API to your Streamlit app URL (comma-separated). |

---

## Local parity

Your machine:

- Backend: `python -m src.backend_src.main` (uses `.env` → `API_PORT`, `API_HOST`)
- Frontend: `streamlit run src/frontend_src/app.py`

Production Streamlit never reads your laptop `.env`; it only reads **Streamlit Cloud Secrets** for `API_BASE_URL` and `CHAT_ENDPOINT_URL`.
