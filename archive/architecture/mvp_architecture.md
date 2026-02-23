# Research Synthesis Service - MVP Architecture

## Overview
A lightweight, cloud-native service for ingesting research documents (PDFs, web pages), processing them with AI, and providing synthesized insights through a simple web interface.

## Core Architecture Principles
1. **Serverless-first** where possible for cost efficiency
2. **Modular design** for easy replacement of AI providers
3. **Simple data model** focusing on core research synthesis needs
4. **Containerized deployment** for portability
5. **API-first design** for future integrations

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Web App   │  │   Mobile    │  │   API Clients      │  │
│  │  (React)    │  │   (Future)  │  │   (Future)         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                        │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐  │
│  │                 REST API (FastAPI)                    │  │
│  │  • Authentication/Authorization                      │  │
│  │  • Request Routing                                   │  │
│  │  • Rate Limiting                                     │  │
│  │  • Input Validation                                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Processing Layer                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Ingestion  │  │ Processing  │  │  Storage    │        │
│  │   Service   │  │   Pipeline  │  │   Service   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Services Layer                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  OpenAI     │  │ Anthropic   │  │  Google AI  │        │
│  │  (GPT-4)    │  │ (Claude)    │  │  (Gemini)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 1. Data Ingestion System

### Supported Input Types
- **PDF Documents** (research papers, articles, reports)
- **Web Pages** (URLs to blog posts, articles, documentation)
- **Plain Text** (markdown, txt files)
- **Images with OCR** (future enhancement)

### Ingestion Pipeline
```
1. Upload/Submit → 2. Validation → 3. Extraction → 4. Chunking → 5. Storage
```

### Key Components:
- **Upload Service**: Handles file uploads via multipart/form-data
- **URL Fetcher**: Downloads and extracts content from web pages
- **PDF Parser**: Extracts text, metadata, and structure from PDFs
- **Text Normalizer**: Cleans and standardizes extracted text
- **Chunking Service**: Splits documents into manageable chunks (e.g., 1000 tokens)

### Implementation Details:
```python
# Example ingestion service structure
class IngestionService:
    async def ingest_pdf(self, file_path: str) -> Document:
        # Extract text using PyPDF2 or pdfplumber
        # Extract metadata (title, authors, date)
        # Return structured document
    
    async def ingest_url(self, url: str) -> Document:
        # Fetch HTML using httpx
        # Extract main content using readability-lxml
        # Clean and structure content
    
    async def chunk_document(self, document: Document, chunk_size: int = 1000) -> List[DocumentChunk]:
        # Split by semantic boundaries (paragraphs, sections)
        # Maintain context windows
        # Add overlap for continuity
```

## 2. Processing Pipeline

### Pipeline Stages:
```
1. Document Chunks → 2. Embedding Generation → 3. Vector Storage → 4. Summarization → 5. Extraction
```

### Core Processing Components:

#### A. Embedding Service
- **Purpose**: Convert text chunks to vector embeddings
- **Options**: OpenAI embeddings, Cohere, SentenceTransformers (local)
- **Storage**: Pinecone, Qdrant, or PostgreSQL with pgvector

#### B. Summarization Service
- **Multi-level Summarization**:
  1. **Chunk-level**: Summarize individual document chunks
  2. **Document-level**: Combine chunk summaries into document summary
  3. **Cross-document**: Synthesize insights across multiple documents

#### C. Information Extraction Service
- **Entity Extraction**: People, organizations, dates, locations
- **Key Concept Extraction**: Main topics, methodologies, findings
- **Relationship Extraction**: Connections between concepts
- **Citation Extraction**: References and sources

#### D. Question Answering Service
- **RAG Pipeline**: Retrieve relevant chunks → Generate answers
- **Citation Tracking**: Link answers to source documents

### Pipeline Implementation:
```python
class ProcessingPipeline:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.summarization_service = SummarizationService()
        self.extraction_service = ExtractionService()
    
    async def process_document(self, document: Document) -> ProcessedDocument:
        # Generate embeddings for chunks
        embeddings = await self.embedding_service.embed_chunks(document.chunks)
        
        # Create document summary
        summary = await self.summarization_service.summarize_document(document)
        
        # Extract key information
        entities = await self.extraction_service.extract_entities(document)
        concepts = await self.extraction_service.extract_concepts(document)
        
        return ProcessedDocument(
            document=document,
            embeddings=embeddings,
            summary=summary,
            entities=entities,
            concepts=concepts
        )
```

## 3. User Interface (Simple Web App)

### Frontend Stack:
- **Framework**: React with TypeScript
- **UI Library**: Chakra UI or Tailwind CSS
- **State Management**: React Query + Zustand
- **Build Tool**: Vite

### Key Pages/Components:

#### 1. Dashboard
- Overview of all research projects
- Recent activity feed
- Quick upload/import buttons

#### 2. Document Management
- List view of all documents
- Search and filter capabilities
- Bulk operations (delete, tag, export)

#### 3. Document Viewer
- Side-by-side view: original text | AI insights
- Interactive summary with expandable sections
- Entity/concept visualization
- Citation tracking

#### 4. Synthesis Workspace
- Multi-document comparison view
- Topic clustering visualization
- Interactive Q&A interface
- Export options (markdown, PDF, JSON)

#### 5. Settings
- API key management
- Processing preferences
- Export/import settings

### Example Component Structure:
```
src/
├── components/
│   ├── upload/
│   │   ├── FileUpload.tsx
│   │   ├── UrlImport.tsx
│   │   └── UploadProgress.tsx
│   ├── documents/
│   │   ├── DocumentList.tsx
│   │   ├── DocumentCard.tsx
│   │   └── DocumentViewer.tsx
│   ├── synthesis/
│   │   ├── SummaryView.tsx
│   │   ├── EntityGraph.tsx
│   │   └── QAPanel.tsx
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Layout.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── Documents.tsx
│   ├── Synthesis.tsx
│   └── Settings.tsx
└── hooks/
    ├── useDocuments.ts
    ├── useProcessing.ts
    └── useSynthesis.ts
```

## 4. API Design (REST Endpoints)

### Authentication:
- **JWT-based authentication**
- **API key support** for programmatic access

### Core Endpoints:

#### Document Management
```
POST   /api/v1/documents/upload       # Upload document
POST   /api/v1/documents/url          # Import from URL
GET    /api/v1/documents              # List documents
GET    /api/v1/documents/{id}         # Get document details
DELETE /api/v1/documents/{id}         # Delete document
POST   /api/v1/documents/{id}/process # Trigger processing
```

#### Processing & Synthesis
```
GET    /api/v1/documents/{id}/summary     # Get document summary
GET    /api/v1/documents/{id}/entities    # Get extracted entities
GET    /api/v1/documents/{id}/concepts    # Get key concepts
POST   /api/v1/synthesis/compare          # Compare multiple documents
POST   /api/v1/synthesis/qa              # Ask questions about documents
```

#### Projects & Collections
```
POST   /api/v1/projects                  # Create research project
GET    /api/v1/projects                  # List projects
GET    /api/v1/projects/{id}             # Get project details
POST   /api/v1/projects/{id}/documents   # Add documents to project
GET    /api/v1/projects/{id}/synthesis   # Get project synthesis
```

#### Search
```
GET    /api/v1/search?q={query}          # Semantic search
GET    /api/v1/search/similar/{doc_id}   # Find similar documents
```

### API Response Format:
```json
{
  "success": true,
  "data": {
    "id": "doc_123",
    "title": "Research Paper Title",
    "status": "processed",
    "summary": "Document summary...",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "meta": {
    "page": 1,
    "total": 100
  }
}
```

### Error Handling:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid file format",
    "details": {
      "field": "file",
      "issue": "Only PDF and text files are supported"
    }
  }
}
```

## 5. Deployment (Docker + Cloud)

### Docker Configuration:

#### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/research_db
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=research_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  postgres_data:
  qdrant_data:
```

#### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000
```

### Cloud Deployment Options:

#### Option A: AWS ECS/Fargate
- **API Service**: ECS Fargate with Application Load Balancer
- **Database**: Amazon RDS PostgreSQL with pgvector
- **Vector Store**: Pinecone (managed) or self-hosted Qdrant
- **File Storage**: Amazon S3 for document storage
- **Caching**: Amazon ElastiCache Redis
- **CDN**: CloudFront for frontend assets

#### Option B: Google Cloud Run
- **API Service**: Cloud Run containers
- **Database**: Cloud SQL PostgreSQL
- **Vector Store**: Vertex AI Matching Engine
- **File Storage**: Cloud Storage
- **Caching**: Memorystore Redis

#### Option C: Azure Container Apps
- **API Service**: Azure Container Apps
- **Database**: Azure Database for PostgreSQL
- **Vector Store**: Azure AI Search
- **File Storage**: Azure Blob Storage
- **Caching**: Azure Cache for Redis

### Infrastructure as Code (Terraform Example):
```hcl
# main.tf - AWS deployment
resource "aws_ecs_cluster" "research_cluster" {
  name = "research-synthesis-cluster"
}

resource "aws_rds_cluster" "postgres" {
  cluster_identifier = "research-db"
  engine            = "aurora-postgresql"
  engine_version    = "15.3"
  database_name     = "research_db"
  master_username   = var.db_username
  master_password   = var.db_password
}

resource "aws_s3_bucket" "documents" {
  bucket = "research-documents-${var.environment}"
}

resource "aws_cloudfront_distribution" "frontend" {
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "frontend"
  }
  
  enabled = true
  default_root_object = "index.html"
}
```

## 6. Technology Stack

### Backend (Python):
- **Framework**: FastAPI (async, OpenAPI, automatic docs)
- **Database**: PostgreSQL with pgvector extension
- **ORM**: SQLAlchemy + Alembic for migrations
- **Task Queue**: Celery + Redis for async processing
- **Vector Store**: Qdrant (self-hosted) or Pinecone (managed)
- **PDF Processing**: pdfplumber, PyPDF2
- **Web Scraping**: httpx, readability-lxml
- **AI Integration**: OpenAI SDK, Anthropic SDK, Google AI SDK

### Frontend (TypeScript):
- **Framework**: React 18+
- **UI Library**: Chakra UI or shadcn/ui
- **State Management**: TanStack Query + Zustand
- **Forms**: React Hook Form + Zod validation
- **Charts**: Recharts or Visx
- **PDF Viewer**: react-pdf or pdf.js
- **Markdown**: react-markdown

### DevOps & Monitoring:
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions or GitLab CI
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack or Loki
- **Error Tracking**: Sentry
- **APM**: Datadog or New Relic

## 7. Development Roadmap

### Phase 1: MVP (Weeks 1-4)
- [ ] Basic document upload and storage
- [ ] PDF text extraction
- [ ] Simple summarization with OpenAI
- [ ] Basic React frontend
- [ ] Docker setup for local development

### Phase 2: Core Features (Weeks 5-8)
- [ ] Web page ingestion
- [ ] Vector embeddings and semantic search
- [ ] Multi-document comparison
- [ ] Entity extraction
- [ ] Improved UI with document viewer

### Phase 3: Enhancement (Weeks 9-12)
- [ ] Advanced summarization (hierarchical)
- [ ] Question answering system
- [ ] Topic modeling and clustering
- [ ] Export functionality
- [ ] User authentication

### Phase 4: Production Ready (Weeks 13-16)
- [ ] Cloud deployment
- [ ] Performance optimization
- [ ] Monitoring and logging
- [ ] API documentation
- [ ] Security hardening

## 8. Cost Considerations

### AI API Costs (Monthly Estimate):
- **OpenAI GPT-4**: ~$0.03 per 1K tokens (input) + $0.06 (output)
- **Embeddings**: ~$0.0001 per 1K tokens
- **Anthropic Claude**: ~$0.008 per 1K tokens (input) + $0.024 (output)

### Infrastructure Costs (AWS, Small Scale):
- **EC2/RDS**: $50-100/month
- **S3 Storage**: $5-20/month (depending on volume)
- **CloudFront**: $10-30/month