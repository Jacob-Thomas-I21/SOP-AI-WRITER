# Pharmaceutical SOP Author - Complete System

A comprehensive pharmaceutical Standard Operating Procedure (SOP) authoring system with AI-powered generation, regulatory compliance validation, and complete audit trails.

## 🏥 System Overview

This is a full-stack pharmaceutical SOP authoring platform consisting of:

### Backend (FastAPI)
- **Location**: `backend/`
- **Technology**: Python FastAPI with pharmaceutical compliance features
- **Features**:
  - AI-powered SOP generation using Ollama
  - Complete audit trails for regulatory compliance
  - FDA 21 CFR Part 11 compliance
  - Pharmaceutical terminology validation
  - PDF generation with regulatory formatting

### Frontend (React TypeScript)
- **Location**: `frontend/`
- **Technology**: React 18 + TypeScript + Vite
- **Features**:
  - Multi-step SOP creation wizard
  - Real-time AI generation status
  - Regulatory framework selection
  - Professional UI with Tailwind CSS

### AI Model Training (Google Colab)
- **Location**: `ai_model/`
- **Technology**: Python with Ollama, Jupyter notebooks
- **Features**:
  - FDA dataset integration
  - Model fine-tuning for pharmaceutical content
  - Regulatory compliance training
  - Local model deployment scripts

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jacob-Thomas-I21/sop-ai-writer.git
   cd sop-ai-writer
   ```

2. **Start all services with Docker**
   ```bash
   cd local-deployment/docker
   docker-compose -f docker-compose.production.yml up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:9000
   - API Documentation: http://localhost:9000/docs

### Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python -c "from app.core.database import init_db; init_db()"
uvicorn app.main:app --reload --port 9000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

#### AI Model Setup
```bash
# See ai_model/README.md for detailed setup instructions
# Requires Google Colab or local Ollama installation
```

## 📁 Project Structure

```
sop-author-pharmaceutical/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── core/                     # Core configuration and security
│   │   ├── models/                   # Pharmaceutical data models
│   │   ├── routers/                  # API endpoints
│   │   ├── services/                 # Business logic services
│   │   └── utils/                    # Utilities and helpers
│   ├── tests/                        # Backend tests
│   └── requirements.txt
├── frontend/                         # React Frontend
│   ├── src/
│   │   ├── components/               # UI components
│   │   ├── services/                 # API services
│   │   ├── types/                    # TypeScript types
│   │   └── hooks/                    # React hooks
│   └── package.json
├── ai_model/                         # Google Colab Training
│   ├── notebooks/                    # Jupyter notebooks
│   └── src/                         # Training utilities
├── local-deployment/                 # Deployment Scripts
│   └── docker/                       # Docker configurations
└── README.md
```

## 🏥 Pharmaceutical Compliance Features

### FDA 21 CFR Part 11 Compliance
- ✅ Electronic records with complete audit trails
- ✅ Electronic signatures ready infrastructure
- ✅ User authentication and authorization
- ✅ Data integrity validation (ALCOA+)
- ✅ System validation documentation

### GMP Compliance Integration
- ✅ WHO GMP guidelines validation
- ✅ ICH Q7, Q9, Q10 compliance checking
- ✅ EMA GMP requirements
- ✅ Pharmaceutical terminology validation
- ✅ Change control procedures

### Regulatory Validation
- ✅ SOP section completeness validation
- ✅ Pharmaceutical terminology accuracy
- ✅ Regulatory framework adherence
- ✅ Manufacturing process compliance
- ✅ Equipment qualification requirements

## 🔧 Configuration

### Environment Variables

**Backend Configuration:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sop_author
REDIS_URL=redis://localhost:6379/0

# Ollama AI
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral:7b-instruct

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Pharmaceutical Settings
MAX_SOP_LENGTH=50000
MIN_SOP_SECTIONS=8
LOG_LEVEL=INFO
```

**Frontend Configuration:**
```bash
VITE_API_URL=http://localhost:9000
VITE_WS_URL=ws://localhost:9000
VITE_PHARMACEUTICAL_MODE=enabled
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## 📊 API Documentation

### Core Endpoints

#### SOP Management
- `POST /api/v1/sops` - Create SOP generation job
- `GET /api/v1/sops/{job_id}` - Get SOP status and content
- `GET /api/v1/sops/{job_id}/pdf` - Download SOP as PDF
- `GET /api/v1/sops` - Search and filter SOPs

#### Template Management
- `GET /api/v1/templates` - Get available templates
- `POST /api/v1/templates` - Create new template

#### Audit and Compliance
- `GET /api/v1/audit/summary` - Get audit summary
- `GET /api/v1/audit/compliance-report` - Generate compliance report

#### Health and Monitoring
- `GET /health` - System health check
- `GET /health/detailed` - Detailed system status

## 🔒 Security Features

- **JWT Authentication** with role-based access control
- **Multi-factor Authentication** ready
- **Rate Limiting** and request validation
- **Input Sanitization** and validation
- **SQL Injection Protection** via SQLModel
- **CORS Configuration** for secure API access
- **Audit Logging** for all user actions
- **Data Encryption** at rest and in transit

## 📄 License

This project is All Rights Reserved with no license for use, modification, or distribution.

✅ **Permitted:**
- Viewing the code for learning and reference purposes

❌ **Restricted:**
- Any use, copying, modification, distribution, or commercial exploitation

© 2025 Jacob Joshy — All rights reserved.

**Note:** This code is provided for educational viewing only. No permission is granted to use, copy, modify, merge, publish, distribute, sublicense, or sell any part of this software without explicit written permission from the author.