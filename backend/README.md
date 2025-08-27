# Pharmaceutical SOP Author - Backend

FastAPI backend for the Pharmaceutical SOP Author system, providing AI-powered SOP generation with regulatory compliance and audit trails.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional, for caching)
- Ollama (for AI model inference)

### Local Development Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database:**
   ```bash
   python -c "from app.core.database import init_db; init_db()"
   ```

6. **Start the backend:**
   ```bash
   uvicorn app.main:app --reload --port 9000
   ```

### API Documentation

Once running, access:
- API docs: http://localhost:9000/docs
- Alternative docs: http://localhost:9000/redoc
- Health check: http://localhost:9000/health

### Key Dependencies

- **FastAPI**: High-performance async web framework
- **SQLModel**: SQL database ORM and serialization
- **Ollama**: Local AI model inference
- **ReportLab**: PDF generation
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### Environment Configuration

See `.env.example` for all available configuration options including:
- Database connection
- Ollama host/model settings
- Security settings
- Pharmaceutical validation parameters

### Testing

```bash
pytest tests/ -v --cov=app
```

### Pharmaceutical Compliance

This backend implements:
- FDA 21 CFR Part 11 compliance
- Complete audit trails
- Data integrity validation
- Regulatory framework validation
- GMP guideline adherence