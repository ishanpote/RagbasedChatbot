# Free Deployment Guide

Follow this step-by-step to deploy your chatbot for free.

## Step 1: Get Hugging Face Token (5 min)

1. Go to https://huggingface.co/join (create account if needed)
2. Click your profile > Settings > Access Tokens
3. Click "New token"
4. Name: `chatbot-api`
5. Role: Read (or fine-grained token with Inference Providers permission)
6. Copy the token and save it somewhere safe
7. You'll use this as `HF_API_TOKEN` in deployment

## Step 2: Deploy Backend on Render (10 min)

### 2.1) Connect your GitHub repo to Render

1. Push your repo to GitHub
2. Go to https://render.com (sign up with GitHub)
3. Click "New" > "Web Service"
4. Connect your GitHub repo (authorize Render)
5. Select your chatbot repo

### 2.2) Configure backend service

On the Render form, fill:

- **Name**: `chatbot-backend`
- **Region**: Choose closest to you
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment**: Python 3.11
- **Plan**: Free

### 2.3) Add environment variables

Click "Advanced" > "Add Environment Variable":

1. Key: `LLM_PROVIDER` → Value: `huggingface`
2. Key: `HF_API_TOKEN` → Value: `<paste your token from Step 1>`
3. Key: `HF_MODEL` → Value: `google/flan-t5-base`
4. (Optional) Key: `HF_API_BASE` → Value: `https://router.huggingface.co/hf-inference`
5. (Optional) Key: `HF_FALLBACK_MODEL` → Value: `openai/gpt-oss-120b:fastest`

### 2.4) Deploy

Click "Create Web Service". Wait ~5 minutes for build.

Once done, you'll see a URL like: `https://chatbot-backend-xxxx.onrender.com`

**Save this URL—you'll need it next.**

## Step 3: Deploy Frontend on Vercel (5 min)

### 3.1) Connect to Vercel

1. Go to https://vercel.com (sign up with GitHub)
2. Click "Add New" > "Project"
3. Import your chatbot repo from GitHub

### 3.2) Configure project

In "Import Project":

- **Root Directory**: `frontend`
- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### 3.3) Add environment variables

Click "Environment Variables":

- Key: `VITE_API_BASE_URL`
- Value: `https://chatbot-backend-xxxx.onrender.com/api/v1` (use your Render URL from Step 2.4)
- Environments: Production, Preview, Development

### 3.4) Deploy

Click "Deploy". Wait ~2 minutes.

Once done, Vercel will show your frontend URL like: `https://chatbot-app-xxx.vercel.app`

## Step 4: Test Your Deployment (5 min)

1. Open your frontend URL in browser
2. In the sidebar, enter vector name: `test-resume`
3. Upload one of your `.txt` resume files from the repo root
4. Wait for upload confirmation
5. Ask a question about the resume (e.g., "What is their email?")
6. You should see an AI response based on the resume

## Troubleshooting

### Frontend shows "Connection failed"

- Check that `VITE_API_BASE_URL` in Vercel matches your Render backend URL
- Frontend env vars are baked at build time, so you may need to redeploy after updating

### Backend shows 500 error

- Check Render logs: Dashboard > Your Service > Logs
- Common issue: `HF_API_TOKEN` is wrong or expired
- Create a new token and update Render environment variable
- If error says `Hugging Face API error 404`, your `HF_MODEL` may not be available on router. Set `HF_FALLBACK_MODEL=openai/gpt-oss-120b:fastest`.

### Upload says "Vector database not found"

- This is expected on first upload—it creates the database
- If it persists, backend cannot write to `/app/faiss_indexes`
- On Render free tier, data does not persist between redeployments
- Solution: Use a paid tier or add persistent storage

## Next Steps

### Upgrade free deployments (optional):

**Render Backend** (to keep data):
- Upgrade from free to Starter ($7/month)
- Add PostgreSQL database for index persistence

**Vercel Frontend**:
- Free tier is unlimited—no action needed

### Custom domain (optional):

- Render: Settings > Custom Domain
- Vercel: Settings > Domains

### Monitor usage:

- Render Dashboard: View logs, metrics
- Vercel Insights: See build times, web vitals
