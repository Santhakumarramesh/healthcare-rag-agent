# Render Deployment Guide - AI Healthcare Copilot

## 🚀 Quick Deploy

The application is configured for **automatic deployment** to Render using the `render.yaml` blueprint.

---

## 📋 Prerequisites

1. **Render Account**: Sign up at https://render.com
2. **GitHub Repository**: Code must be pushed to GitHub
3. **OpenAI API Key**: Required for AI functionality

---

## 🔧 Deployment Steps

### Step 1: Connect Repository to Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository: `healthcare-rag-agent`
4. Render will automatically detect `render.yaml`

### Step 2: Configure Environment Variables

**For API Service** (`healthcare-rag-api`):
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- All other variables are pre-configured in `render.yaml`

**For UI Service** (`healthcare-rag-ui`):
- `API_BASE_URL`: Auto-configured to `https://healthcare-rag-api.onrender.com`

### Step 3: Deploy

1. Click **"Apply"** to create both services
2. Render will:
   - Build the API service
   - Build the UI service
   - Deploy both automatically

**Deployment time**: ~5-10 minutes

---

## 🌐 Live URLs

After deployment completes:

- **UI (Healthcare Copilot)**: https://healthcare-rag-ui.onrender.com
- **API**: https://healthcare-rag-api.onrender.com
- **API Docs**: https://healthcare-rag-api.onrender.com/docs

---

## 📦 What Gets Deployed

### API Service
- **Name**: `healthcare-rag-api`
- **Type**: FastAPI backend
- **Build**: `pip install -r requirements.txt && python vectorstore/ingest.py`
- **Start**: `bash start_api.sh`
- **Port**: 8000

### UI Service
- **Name**: `healthcare-rag-ui`
- **Type**: Streamlit app
- **Build**: `pip install -r requirements-ui.txt`
- **Start**: `bash start_healthcare.sh`
- **Port**: 8501

---

## 🎯 Deployed Features

### Complete 7-Page Platform

1. **Home** - Care operating dashboard
2. **Analyze Report** - Medical report analysis
3. **Ask AI** - Structured medical Q&A
4. **Serious Condition Follow-up** - Daily tracking (THE MOAT)
5. **Records Timeline** - Persistent healthcare system
6. **Monitoring** - Operations dashboard
7. **Settings** - Admin controls

### Component Library
- 50+ reusable components
- Clinical Intelligence design system
- Trust-first, evidence-based UI

---

## ⚙️ Configuration

### render.yaml Structure

```yaml
services:
  # API Service
  - type: web
    name: healthcare-rag-api
    env: python
    region: oregon
    plan: free
    buildCommand: "pip install -r requirements.txt && python vectorstore/ingest.py"
    startCommand: "bash start_api.sh"
    
  # UI Service (Healthcare Copilot)
  - type: web
    name: healthcare-rag-ui
    env: python
    region: oregon
    plan: free
    buildCommand: "pip install -r requirements-ui.txt"
    startCommand: "bash start_healthcare.sh"
```

### Startup Scripts

**API**: `start_api.sh`
```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

**UI**: `start_healthcare.sh`
```bash
streamlit run streamlit_app/app_healthcare.py \
  --server.port $PORT \
  --server.headless true \
  --server.enableCORS false \
  --server.address 0.0.0.0
```

---

## 🔍 Troubleshooting

### Issue: Deployment Fails

**Check**:
1. All environment variables are set
2. `OPENAI_API_KEY` is configured
3. Build logs for errors

**Solution**:
- Go to service → "Logs" tab
- Check build and runtime logs
- Fix any missing dependencies

### Issue: UI Shows "API Error"

**Check**:
1. API service is running
2. `API_BASE_URL` is correct
3. API health: https://healthcare-rag-api.onrender.com/health

**Solution**:
- Verify API service is deployed
- Check API logs for errors
- Test API endpoints directly

### Issue: Slow Response Times

**Cause**: Render free tier cold starts

**Solution**:
- First request may take 30-60 seconds
- Subsequent requests are faster
- Consider upgrading to paid tier for always-on

### Issue: Build Timeout

**Cause**: Vector store ingestion takes too long

**Solution**:
- Reduce dataset size in `vectorstore/ingest.py`
- Or pre-build vector store and commit to repo

---

## 🔄 Redeployment

### Automatic Redeployment

Render automatically redeploys when you push to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render will:
1. Detect the push
2. Rebuild both services
3. Deploy new version

### Manual Redeployment

1. Go to Render Dashboard
2. Select service
3. Click **"Manual Deploy"** → **"Clear build cache & deploy"**

---

## 📊 Monitoring

### Check Service Health

**API Health**:
```bash
curl https://healthcare-rag-api.onrender.com/health
```

**UI Health**:
```bash
curl https://healthcare-rag-ui.onrender.com
```

### View Logs

1. Go to Render Dashboard
2. Select service
3. Click **"Logs"** tab
4. View real-time logs

### Metrics

Render provides:
- CPU usage
- Memory usage
- Request count
- Response times

---

## 🔐 Security

### Environment Variables

**Never commit**:
- `OPENAI_API_KEY`
- Any API keys or secrets

**Use Render's environment variables**:
- Set in Dashboard → Service → Environment
- Marked as "secret" (not visible in logs)

### CORS Configuration

UI service is configured to accept requests from API:
- `--server.enableCORS false`
- API allows UI origin

---

## 💰 Cost

### Free Tier Limits

**Render Free Tier**:
- 750 hours/month per service
- Automatic sleep after 15 min inactivity
- Cold start on first request
- 512 MB RAM

**OpenAI Costs**:
- GPT-4o-mini: ~$0.15 per 1M input tokens
- Embeddings: ~$0.02 per 1M tokens
- Estimated: $5-20/month for moderate use

### Upgrade Options

**Render Starter ($7/month per service)**:
- Always-on (no cold starts)
- 1 GB RAM
- Faster builds

**OpenAI Tier 1 ($5 credit)**:
- Higher rate limits
- Better for production

---

## 🎯 Production Checklist

Before going live:

- [ ] Set `OPENAI_API_KEY` in Render
- [ ] Test all 7 pages
- [ ] Verify API connectivity
- [ ] Check monitoring dashboard
- [ ] Test report upload
- [ ] Test AI Q&A
- [ ] Test follow-up workflow
- [ ] Review logs for errors
- [ ] Set up error alerts
- [ ] Document known issues

---

## 📈 Scaling

### When to Scale

**Upgrade API service if**:
- Response times > 5 seconds
- Frequent cold starts
- High concurrent users

**Upgrade UI service if**:
- Page load times > 3 seconds
- Memory errors
- Frequent restarts

### Scaling Strategy

1. **Horizontal**: Add more instances (Render Pro+)
2. **Vertical**: Upgrade to larger plan
3. **Database**: Add PostgreSQL for persistence
4. **Cache**: Add Redis for session storage

---

## 🔗 Useful Links

- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **GitHub Repo**: https://github.com/Santhakumarramesh/healthcare-rag-agent
- **OpenAI API**: https://platform.openai.com

---

## 🆘 Support

### Common Issues

1. **"Service Unavailable"**: Wait 30-60s for cold start
2. **"API Error"**: Check API service logs
3. **"Build Failed"**: Check build logs for missing dependencies
4. **"Timeout"**: Increase timeout in `start_healthcare.sh`

### Get Help

- **Render Support**: https://render.com/support
- **GitHub Issues**: Create issue in repo
- **Documentation**: Check `COMPLETE_IMPLEMENTATION.md`

---

## ✅ Deployment Verification

After deployment, verify:

1. **UI loads**: Visit https://healthcare-rag-ui.onrender.com
2. **API responds**: Visit https://healthcare-rag-api.onrender.com/docs
3. **Navigation works**: Click through all 7 pages
4. **API integration**: Try "Ask AI" or "Analyze Report"
5. **Monitoring**: Check system metrics

---

## 🎉 Success!

Once deployed, you'll have a **complete healthcare workflow platform** live on the web with:

✅ 7 pages (Home, Analyze Report, Ask AI, Follow-up, Timeline, Monitoring, Settings)  
✅ 50+ components  
✅ Clinical Intelligence design  
✅ Trust-first, evidence-based UI  
✅ Longitudinal care tracking  

**The moat is the workflow, not the model.**

---

**Last Updated**: March 18, 2026  
**Version**: 1.0.0  
**Status**: Production Ready
