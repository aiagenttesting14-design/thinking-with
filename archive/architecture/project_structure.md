# Project Structure

```
research-synthesis/
├── backend/
│   ├── src/
│   │   ├── main.py                    # FastAPI application
│   │   ├── models/                    # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── document.py
│   │   │   ├── user.py
│   │   │   └── project.py
│   │   ├── api/                       # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── projects.py
│   │   │   │   ├── synthesis.py
│   │   │   │   └── auth.py
│   │   │   └── dependencies.py
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── document_service.py
│   │   │   ├── processing_service.py
│   │   │   ├── synthesis_service.py
│   │   │   └── embedding_service.py
│   │   ├── ingestion/                 # Document ingestion
│   │   │   ├── __init__.py
│   │   │   ├── pdf_parser.py
│   │   │   ├── web_fetcher.py
│   │   │   └── text_normalizer.py
│   │   ├── ai/                        # AI provider integrations
│   │   │   ├── __init__.py
│   │   │   ├── openai_client.py
│   │   │   ├── anthropic_client.py
│   │   │   └── google_ai_client.py
│   │   ├── database/                  # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   ├── models.py              # SQLAlchemy models
│   │   │   └── repositories.py
│   │   ├── worker/                    # Celery worker
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py
│   │   │   └── tasks.py
│   │   └── utils/                     # Utilities
│   │       ├── __init__.py
│   │       ├── logging.py
│   │       ├── security.py
│   │       └── file_handling.py
│   ├── tests/                         # Backend tests
│   │   ├── __init__.py
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   ├── migrations/                    # Alembic migrations
│   │   └── versions/
│   ├── uploads/                       # Uploaded files
│   ├── logs/                          # Application logs
│   ├── requirements.txt               # Python dependencies
│   ├── requirements-dev.txt           # Development dependencies
│   ├── Dockerfile                     # Production Dockerfile
│   ├── Dockerfile.dev                 # Development Dockerfile
│   └── alembic.ini                    # Alembic configuration
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx                   # Application entry point
│   │   ├── App.tsx                    # Main App component
│   │   ├── types/                     # TypeScript types
│   │   │   ├── index.ts
│   │   │   ├── document.ts
│   │   │   └── user.ts
│   │   ├── api/                       # API client
│   │   │   ├── index.ts
│   │   │   ├── client.ts
│   │   │   ├── documents.ts
│   │   │   └── projects.ts
│   │   ├── components/                # React components
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Layout.tsx
│   │   │   ├── upload/
│   │   │   │   ├── FileUpload.tsx
│   │   │   │   ├── UrlImport.tsx
│   │   │   │   └── UploadProgress.tsx
│   │   │   ├── documents/
│   │   │   │   ├── DocumentList.tsx
│   │   │   │   ├── DocumentCard.tsx
│   │   │   │   └── DocumentViewer.tsx
│   │   │   ├── synthesis/
│   │   │   │   ├── SummaryView.tsx
│   │   │   │   ├── EntityGraph.tsx
│   │   │   │   └── QAPanel.tsx
│   │   │   └── common/
│   │   │       ├── Button.tsx
│   │   │       ├── Input.tsx
│   │   │       └── LoadingSpinner.tsx
│   │   ├── pages/                     # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Documents.tsx
│   │   │   ├── Synthesis.tsx
│   │   │   └── Settings.tsx
│   │   ├── hooks/                     # Custom React hooks
│   │   │   ├── useDocuments.ts
│   │   │   ├── useProcessing.ts
│   │   │   └── useSynthesis.ts
│   │   ├── store/                     # State management
│   │   │   ├── index.ts
│   │   │   ├── documentStore.ts
│   │   │   └── userStore.ts
│   │   ├── utils/                     # Frontend utilities
│   │   │   ├── formatters.ts
│   │   │   └── validators.ts
│   │   ├── styles/                    # Global styles
│   │   │   └── globals.css
│   │   └── assets/                    # Static assets
│   │       └── images/
│   ├── public/                        # Public assets
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── package.json                   # NPM dependencies
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── vite.config.ts                 # Vite configuration
│   ├── Dockerfile                     # Production Dockerfile
│   └── Dockerfile.dev                 # Development Dockerfile
│
├── infrastructure/
│   ├── docker-compose.yml             # Local development
│   ├── docker-compose.prod.yml        # Production-like
│   ├── nginx/                         # Nginx configuration
│   │   └── nginx.conf
│   ├── terraform/                     # Infrastructure as Code
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── kubernetes/                    # K8s manifests
│       ├── namespace.yaml
│       ├── deployment.yaml
│       ├── service.yaml
│       └── ingress.yaml
│
├── docs/                              # Documentation
│   ├── api/                           # API documentation
│   ├── architecture/                  # Architecture diagrams
│   ├── deployment/                    # Deployment guides
│   └── development/                   # Development guides
│
├── scripts/                           # Utility scripts
│   ├── setup.sh                       # Development setup
│   ├── deploy.sh                      # Deployment script
│   └── backup.sh                      # Backup script
│
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── README.md                          # Project README
├── LICENSE                            # License file
└── docker-compose.yml                 # Root docker-compose
```

## Quick Start Commands

```bash
# Clone and setup
git clone <repository-url>
cd research-synthesis
cp .env.example .env
# Edit .env with your API keys

# Start development environment
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# Access services:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Database: localhost:5432
# Redis: localhost:6379
# Qdrant: localhost:6333

# Run tests
docker-compose exec api pytest
```

## Development Workflow

1. **Environment Setup**
   ```bash
   ./scripts/setup.sh
   docker-compose up -d
   ```

2. **Database Migrations**
   ```bash
   docker-compose exec api alembic revision --autogenerate -m "Description"
   docker-compose exec api alembic upgrade head
   ```

3. **Running Tests**
   ```bash
   # Unit tests
   docker-compose exec api pytest tests/unit/
   
   # Integration tests
   docker-compose exec api pytest tests/integration/
   
   # All tests with coverage
   docker-compose exec api pytest --cov=src tests/
   ```

4. **Code Quality**
   ```bash
   # Format code
   docker-compose exec api black src/
   docker-compose exec api isort src/
   
   # Lint code
   docker-compose exec api flake8 src/
   docker-compose exec api mypy src/
   ```

5. **Development Server**
   ```bash
   # Backend (auto-reload)
   docker-compose up api
   
   # Frontend (auto-reload)
   docker-compose up frontend
   ```

This structure provides a clean separation of concerns, follows best practices for both Python and TypeScript projects, and supports both development and production workflows.
