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

This project now supports a free LLM option through Hugging Face Inference API so you can deploy without running Ollama.

### 1) Create a free Hugging Face token

- Sign in at Hugging Face
- Create an access token
- Keep it for deployment environment variable `HF_API_TOKEN`

### 2) Deploy backend (free tier)

Use a free backend host like Render/Railway and set environment variables:

- `LLM_PROVIDER=huggingface`
- `HF_API_TOKEN=<your_token>`
- `HF_MODEL=google/flan-t5-base`
- `HF_API_BASE=https://router.huggingface.co/hf-inference` (optional)
- `HF_FALLBACK_MODEL=openai/gpt-oss-120b:fastest` (optional, used when HF_MODEL returns 404)

### 3) Deploy frontend (free tier)

Deploy `frontend` on Vercel/Netlify and set:

- `VITE_API_BASE_URL=https://<your-backend-domain>/api/v1`

### 4) Upload resume and chat

After deploy:

- Upload `.txt` resume from UI
- Connect using the same vector database name
- Start querying

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
