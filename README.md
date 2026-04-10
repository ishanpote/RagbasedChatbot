# Chatbot Application

This project is a full-stack resume chatbot built with FastAPI, React (Vite), and FAISS-based retrieval.

## Local Development

### Backend

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Start the API:

```bash
uvicorn main:app --reload
```

Backend docs: `http://127.0.0.1:8000/docs`

### Frontend

1. Install frontend dependencies:

```bash
cd frontend
npm install
```

2. Start Vite dev server:

```bash
npm run dev
```

Frontend: `http://localhost:5173`

## Free Deployment (Recommended)

This project supports a free LLM option via Hugging Face router endpoints, so you can deploy without running Ollama.

For the full guide, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

### 1) Create a Hugging Face token

- Create a token from Hugging Face settings.
- Use `Read` role or a fine-grained token with Inference Providers permission.
- Save it as `HF_API_TOKEN` for backend deployment.

### 2) Deploy backend on Render

Use these backend environment variables:

- `LLM_PROVIDER=huggingface`
- `HF_API_TOKEN=<your_token>`
- `HF_MODEL=google/flan-t5-base`
- `HF_API_BASE=https://router.huggingface.co/hf-inference` (optional)
- `HF_FALLBACK_MODEL=openai/gpt-oss-120b:fastest` (optional; used if `HF_MODEL` returns 404/410)

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 3) Deploy frontend on Vercel

Set frontend environment variable:

- `VITE_API_BASE_URL=https://<your-render-backend>.onrender.com/api/v1`

Important: Vite environment variables are baked at build time, so redeploy after changing them.

### 4) Validate end-to-end

- Open the frontend URL.
- Enter a vector name (for example: `test-resume`).
- Upload a `.txt` resume.
- Ask a question based on uploaded content.

### 5) Troubleshooting quick notes

- `Hugging Face API error 410`: old endpoint was used somewhere. Use router base via `HF_API_BASE`.
- `Hugging Face API error 404`: selected `HF_MODEL` is unavailable on current route/provider. Keep `HF_FALLBACK_MODEL` set.
- Frontend `Connection failed`: verify `VITE_API_BASE_URL` and redeploy frontend.

## Docker Deployment

You can still run full stack in containers:

```bash
docker compose up -d --build
```

By default `docker-compose.yml` uses Hugging Face provider. To use Ollama instead:

- `LLM_PROVIDER=ollama`
- `OLLAMA_HOST=<your_ollama_host:11434>`

## Deployment Artifacts

- `Dockerfile` (FastAPI backend)
- `frontend/Dockerfile` (React build + Nginx)
- `frontend/nginx.conf` (SPA routing + API proxy)
- `docker-compose.yml` (multi-service orchestration)
- `.dockerignore`
