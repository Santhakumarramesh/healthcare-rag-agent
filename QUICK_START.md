# ⚡ Quick Start Guide

Get the Healthcare AI Platform running in 5 minutes.

---

## 🚀 Fastest Way to Run

### Option 1: Simple UI (Recommended for Demo)

```bash
# 1. Clone
git clone https://github.com/Santhakumarramesh/healthcare-rag-agent.git
cd healthcare-rag-agent

# 2. Install
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Run
streamlit run streamlit_app/app_v2.py
```

**Done!** Open http://localhost:8501

---

### Option 2: Full Stack (API + Advanced UI)

```bash
# Terminal 1 - API
uvicorn api.main:app --reload

# Terminal 2 - UI
streamlit run streamlit_app/app.py
```

---

### Option 3: Docker (Complete Stack)

```bash
docker-compose up --build
```

**Access:**
- API: http://localhost:8000
- UI: http://localhost:8501
- API Docs: http://localhost:8000/docs

---

## 🔑 Required Environment Variables

**Minimum (Required):**
```env
OPENAI_API_KEY=sk-your-key-here
```

**Optional (Enhanced Features):**
```env
PINECONE_API_KEY=your-pinecone-key
TAVILY_API_KEY=your-tavily-key
```

---

## 🎯 First Steps After Running

### 1. Login (Optional)
Use demo credentials:
```
Email: patient@healthcare.ai
Password: patient123
```

### 2. Try the Chat
Ask questions like:
- "What are the symptoms of diabetes?"
- "Can I take ibuprofen with aspirin?"
- "What does high blood pressure mean?"

### 3. Upload a Report
- Go to "Upload Report" page
- Upload a lab report PDF or image
- Click "Analyze Report"
- Get instant analysis with AI recommendations

### 4. Check Monitoring
- Go to "Monitoring Dashboard"
- See real-time metrics
- View query patterns

---

## 🐛 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "OpenAI API key error"
Check your `.env` file has a valid key:
```env
OPENAI_API_KEY=sk-proj-...
```

### "Port already in use"
Change the port:
```bash
streamlit run streamlit_app/app_v2.py --server.port 8502
```

### "Database error"
Reset the database:
```bash
rm data/healthcare_rag.db
python database/seed.py
```

---

## 📚 Next Steps

### Learn More
- **[User Guide](USER_GUIDE.md)** - Complete usage guide
- **[Architecture](ARCHITECTURE.md)** - How it works
- **[Documentation](DOCUMENTATION.md)** - All docs

### Customize
- **[Configuration](PROJECT_STRUCTURE.md)** - File structure
- **[Contributing](CONTRIBUTING.md)** - How to contribute

### Deploy
- **[Render](render.yaml)** - Cloud deployment
- **[Docker](docker-compose.yml)** - Container deployment

---

## 🎓 Demo Accounts

### Patient
```
Email: patient@healthcare.ai
Password: patient123
Role: Patient (basic access)
```

### Clinician
```
Email: doctor@healthcare.ai
Password: doctor123
Role: Clinician (advanced access)
```

### Admin
```
Email: admin@healthcare.ai
Password: admin123
Role: Admin (full access)
```

---

## 💡 Quick Tips

### Best for Demos
Use `app_v2.py` - clean, simple, fast

### Best for Development
Use `app.py` - all features, advanced UI

### Best for Production
Use Docker - complete stack, isolated

---

## 🔗 Useful Links

- **Live Demo**: https://healthcare-rag-api.onrender.com
- **API Docs**: https://healthcare-rag-api.onrender.com/docs
- **GitHub**: https://github.com/Santhakumarramesh/healthcare-rag-agent
- **Issues**: https://github.com/Santhakumarramesh/healthcare-rag-agent/issues

---

## ⏱️ Expected Startup Time

- **Simple UI**: 5-10 seconds
- **Full Stack**: 15-20 seconds
- **Docker**: 30-60 seconds (first build)

---

## 📊 System Requirements

### Minimum
- Python 3.11+
- 2GB RAM
- 1GB disk space

### Recommended
- Python 3.11+
- 4GB RAM
- 2GB disk space
- OpenAI API key

---

**You're ready to go!** 🎉

For detailed instructions, see [USER_GUIDE.md](USER_GUIDE.md)
