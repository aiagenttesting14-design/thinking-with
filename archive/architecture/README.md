# Research Synthesis Service - MVP Architecture

## Overview

This repository contains the complete architecture design for a Research Synthesis Service MVP. The service ingests research documents (PDFs, web pages), processes them with AI, and provides synthesized insights through a simple web interface.

## Architecture Documents

1. **`mvp_architecture.md`** - Comprehensive architecture overview covering all five requested areas
2. **`technical_spec.md`** - Detailed technical specifications with code examples
3. **`summary.md`** - Executive summary and implementation roadmap
4. **`project_structure.md`** - Complete project structure and development workflow

## Key Features

### 1. Data Ingestion
- PDF document parsing with metadata extraction
- Web page content extraction
- Intelligent document chunking
- Multiple file format support

### 2. Processing Pipeline
- Vector embeddings for semantic search
- Multi-level document summarization
- Entity and concept extraction
- Question answering with citations

### 3. User Interface
- React-based web application
- Document management and viewing
- Interactive synthesis workspace
- Visual analytics and graphs

### 4. API Design
- RESTful API with OpenAPI documentation
- JWT authentication and API keys
- Comprehensive error handling
- Rate limiting and security

### 5. Deployment
- Docker containerization
- PostgreSQL with pgvector
- Qdrant vector database
- Redis caching and task queue
- Cloud-ready configurations

## Technology Stack

### Backend
- **Python 3.11** with FastAPI framework
- **PostgreSQL** with pgvector extension
- **SQLAlchemy** ORM with Alembic migrations
- **Celery** for async task processing
- **Qdrant** for vector similarity search

### Frontend
- **React 18** with TypeScript
- **Chakra UI** component library
- **TanStack Query** for data fetching
- **Vite** build tool

### Infrastructure
- **Docker** and Docker Compose
- **Nginx** reverse proxy
- **Prometheus** and **Grafana** for monitoring
- **GitHub Actions** CI/CD

## Getting Started

### Prerequisites
- Docker and Docker Compose
- OpenAI API key (or other AI provider)
- PostgreSQL (via Docker)
- Node.js 18+ (for frontend development)

### Quick Start
```bash
# Clone and setup
git clone <repository>
cd research-synthesis

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head

# Access the application:
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
kubectl apply -f infrastructure/kubernetes/
```

### Cloud Providers
- **AWS**: ECS/Fargate, RDS, S3, ElastiCache
- **GCP**: Cloud Run, Cloud SQL, Cloud Storage, Memorystore
- **Azure**: Container Apps, Azure SQL, Blob Storage, Redis Cache

## Cost Estimates

### Development Phase (3 months)
- AI API: $200-500/month
- Infrastructure: $50-100/month
- **Total**: $750-1,800

### Production (Small Scale)
- AI API: $500-2,000/month (usage-based)
- Infrastructure: $100-300/month
- **Total**: $600-2,300/month

## Roadmap

### Phase 1 (Weeks 1-4): MVP Foundation
- Basic document upload and processing
- Simple summarization
- React frontend with document list
- Docker development setup

### Phase 2 (Weeks 5-8): Core Features
- Web page ingestion
- Vector embeddings and search
- Multi-document comparison
- Improved UI with viewer

### Phase 3 (Weeks 9-12): Enhancement
- Advanced summarization
- Question answering
- Topic modeling
- Export functionality

### Phase 4 (Weeks 13-16): Production
- Cloud deployment
- Performance optimization
- Monitoring and security
- Load testing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Specify license - e.g., MIT, Apache 2.0]

## Support

For questions and support:
- Create an issue in the repository
- Check the documentation in `/docs`
- Review API documentation at `/docs` when running locally

## Acknowledgments

- Built with FastAPI, React, and modern AI APIs
- Inspired by research synthesis tools like Elicit, SciSpace, and Consensus
- Designed for practicality and ease of implementation
