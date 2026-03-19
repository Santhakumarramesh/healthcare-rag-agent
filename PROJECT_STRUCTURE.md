# 📁 Project Structure

Clean, organized structure for the Healthcare AI Platform.

---

## 🗂️ Directory Layout

```
healthcare-rag-agent/
│
├── 📄 README.md                    # Main project documentation
├── 📄 USER_GUIDE.md                # User manual
├── 📄 ARCHITECTURE.md              # System architecture
├── 📄 SECURITY.md                  # Security features
├── 📄 IMPLEMENTATION_ROADMAP.md    # Development roadmap
│
├── 🔧 requirements.txt             # Production dependencies
├── 🔧 requirements-ui.txt          # UI-only dependencies
├── 🔧 requirements-local.txt       # Local development dependencies
├── 🔧 docker-compose.yml           # Docker configuration
├── 🔧 render.yaml                  # Render deployment config
├── 🔧 .env.example                 # Environment variables template
│
├── api/                            # 🌐 FastAPI Backend
│   ├── main.py                    # Main API application
│   ├── auth.py                    # Authentication endpoints
│   ├── admin.py                   # Admin endpoints
│   └── records.py                 # Medical records endpoints
│
├── agents/                         # 🤖 AI Agents
│   ├── rag_pipeline.py            # Main RAG pipeline
│   ├── router_agent.py            # Query routing
│   ├── reasoning_agent.py         # Multi-step reasoning
│   └── records_agent.py           # Report analysis
│
├── services/                       # 🛠️ Business Logic
│   ├── auth_service.py            # Authentication
│   ├── memory_service.py          # Conversation memory
│   ├── citation_service.py        # Source formatting
│   ├── monitoring_service.py      # Real-time metrics
│   ├── alert_service.py           # Clinical alerts
│   ├── audit_service.py           # Audit logging
│   ├── api_key_service.py         # API key management
│   ├── knowledge_graph.py         # Medical relationships
│   └── feedback_service.py        # User feedback
│
├── database/                       # 💾 Database Layer
│   ├── models.py                  # SQLAlchemy models
│   ├── database.py                # Connection management
│   └── seed.py                    # Database seeding
│
├── multimodal/                     # 👁️ Image Processing
│   └── image_analyzer.py          # GPT-4o vision
│
├── vectorstore/                    # 🔍 Vector Storage
│   ├── ingest.py                  # Document ingestion
│   └── personal_store.py          # Session-scoped storage
│
├── streamlit_app/                  # 🎨 Frontend
│   ├── app.py                     # Advanced UI (full features)
│   └── app_v2.py                  # Simple UI (user-friendly)
│
├── utils/                          # 🔧 Utilities
│   ├── config.py                  # Configuration
│   ├── cache.py                   # Response caching
│   ├── rate_limiter.py            # Rate limiting
│   └── hallucination_detector.py  # Quality checks
│
├── data/                           # 📊 Data Storage
│   ├── healthcare_rag.db          # SQLite database
│   ├── faiss_index/               # Vector index
│   └── processed/                 # Processed documents
│
├── docs/                           # 📚 Documentation
│   ├── README.md                  # Documentation index
│   ├── screenshots/               # UI screenshots
│   ├── archive/                   # Historical docs
│   └── development/               # Development notes
│
└── tests/                          # 🧪 Tests
    └── (test files)
```

---

## 📦 Key Files

### Configuration
- `.env` - Environment variables (not in git)
- `.env.example` - Template for environment variables
- `config.py` - Application configuration
- `render.yaml` - Render deployment configuration
- `docker-compose.yml` - Docker setup

### Entry Points
- `api/main.py` - API server entry point
- `streamlit_app/app.py` - Advanced UI entry point
- `streamlit_app/app_v2.py` - Simple UI entry point
- `run.py` - Unified run script

### Database
- `data/healthcare_rag.db` - SQLite database file
- `database/models.py` - Database schema
- `database/seed.py` - Seed demo data

---

## 🎯 File Naming Conventions

### Python Files
- `*_service.py` - Business logic services
- `*_agent.py` - AI agents
- `*_router.py` - API routers
- `models.py` - Data models

### Documentation
- `README.md` - Main documentation
- `*_COMPLETE.md` - Feature completion docs
- `*_GUIDE.md` - User guides
- `ARCHITECTURE.md` - Technical architecture

### Configuration
- `requirements*.txt` - Python dependencies
- `.env*` - Environment configuration
- `*.yaml` / `*.yml` - Deployment configuration

---

## 🗑️ What Was Removed

### Archived (moved to `docs/archive/`)
- Old UI redesign documentation
- Bug fix logs
- Deployment logs
- Reviewer feedback responses
- Historical feature documentation

### Deleted
- `streamlit_app/app_old.py` - Old UI backup (no longer needed)
- Duplicate markdown files
- Temporary files

---

## 📊 Code Statistics

- **Total Files**: 60+
- **Python Files**: 45+
- **Lines of Code**: 8,500+
- **Documentation**: 15+ files
- **Services**: 11
- **API Endpoints**: 25+
- **Database Tables**: 7

---

## 🔍 Finding Things

### "Where is the authentication code?"
→ `services/auth_service.py` + `api/auth.py`

### "Where is the RAG pipeline?"
→ `agents/rag_pipeline.py`

### "Where are the database models?"
→ `database/models.py`

### "Where is the UI?"
→ `streamlit_app/app.py` (advanced) or `app_v2.py` (simple)

### "Where is the monitoring?"
→ `services/monitoring_service.py` + `GET /monitoring/stats`

### "Where are the clinical alerts?"
→ `services/alert_service.py`

---

## 🚀 Quick Commands

### Development
```bash
# Run API
uvicorn api.main:app --reload

# Run Simple UI
streamlit run streamlit_app/app_v2.py

# Run Advanced UI
streamlit run streamlit_app/app.py

# Run tests
pytest tests/

# Seed database
python database/seed.py
```

### Docker
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

### Deployment
```bash
# Deploy to Render (automatic from GitHub push)
git push origin main
```

---

## 📝 Notes

- **Two UIs**: Use `app_v2.py` for demos (simple), `app.py` for technical depth
- **Database**: SQLite by default, PostgreSQL-ready (change `DATABASE_URL`)
- **Environment**: Copy `.env.example` to `.env` and add your API keys
- **Documentation**: All docs in root or `docs/` folder

---

This structure is **clean, organized, and professional** - ready for production use and job interviews! 🎉
