# Quick Start Guide - Research Synthesis MVP

## Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- OpenAI API key

## Local Development Setup

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_key_here
export DATABASE_URL=sqlite:///./research.db

# Run the backend
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Using Docker (Recommended)
```bash
# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## API Endpoints

### Basic Operations
```
POST   /upload              # Upload document
GET    /documents           # List documents
GET    /documents/{id}      # Get document details
POST   /process/{id}        # Process document
GET    /summaries/{id}      # Get summary
GET    /keypoints/{id}      # Get key points
```

### Advanced Features
```
POST   /synthesize          # Synthesize multiple documents
GET    /search/semantic     # Semantic search
GET    /search/keyword      # Keyword search
POST   /query               # Natural language query
WS     /ws/processing/{id}  # Real-time processing updates
```

## Example Usage

### Upload and Process a Document
```bash
# Upload PDF
curl -X POST http://localhost:8000/upload \
  -F "file=@research_paper.pdf"

# Process document (replace {file_id})
curl -X POST http://localhost:8000/process/{file_id}

# Get summary
curl http://localhost:8000/summaries/{file_id}
```

### Using Python Client
```python
import requests

# Upload document
with open("research.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload",
        files={"file": ("research.pdf", f, "application/pdf")}
    )
file_id = response.json()["file_id"]

# Process document
requests.post(f"http://localhost:8000/process/{file_id}")

# Get results
summary = requests.get(f"http://localhost:8000/summaries/{file_id}").json()
keypoints = requests.get(f"http://localhost:8000/keypoints/{file_id}").json()
```

## Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...          # OpenAI API key

# Optional
DATABASE_URL=postgresql://...  # Database URL
REDIS_URL=redis://...          # Redis URL
PINECONE_API_KEY=...           # Pinecone API key
ANTHROPIC_API_KEY=...          # Anthropic API key
```

### Model Configuration
Edit `backend/config/models.py` to change:
- Default LLM model (gpt-3.5-turbo, gpt-4, claude-3, etc.)
- Embedding model
- Chunk sizes
- Temperature settings

## Testing

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test

# Run integration tests
docker-compose -f docker-compose.test.yml up
```

## Deployment

### Cloud Deployment Options

1. **Vercel + Railway** (Simplest)
   - Frontend: Vercel
   - Backend: Railway
   - Database: Railway PostgreSQL
   - Storage: Cloudflare R2

2. **AWS ECS** (Scalable)
   - Frontend: S3 + CloudFront
   - Backend: ECS Fargate
   - Database: RDS PostgreSQL
   - Cache: ElastiCache Redis

3. **Google Cloud Run** (Serverless)
   - Frontend: Firebase Hosting
   - Backend: Cloud Run
   - Database: Cloud SQL
   - Storage: Cloud Storage

### Deployment Steps
```bash
# Build and push Docker images
docker build -t research-synthesis-backend ./backend
docker build -t research-synthesis-frontend ./frontend

# Deploy to Kubernetes
kubectl apply -f k8s/
```

## Troubleshooting

### Common Issues

1. **PDF extraction fails**
   - Install system dependencies: `apt-get install poppler-utils`
   - Try different PDF libraries: pdfplumber, PyPDF2, pdfminer

2. **LLM API errors**
   - Check API key validity
   - Verify rate limits
   - Check token usage

3. **Database connection issues**
   - Verify connection string
   - Check database permissions
   - Ensure database is running

4. **Frontend not connecting to backend**
   - Check CORS configuration
   - Verify API URL in frontend
   - Check network connectivity

### Getting Help
- Check logs: `docker-compose logs [service]`
- Enable debug mode: `DEBUG=true`
- Check API documentation: `http://localhost:8000/docs`
- File issues on GitHub repository

## Next Steps After Setup

1. **Add authentication** (OAuth, JWT)
2. **Configure vector database** (Pinecone, Qdrant)
3. **Set up monitoring** (Prometheus, Grafana)
4. **Implement billing** (Stripe, LemonSqueezy)
5. **Add more document formats** (DOCX, PPTX, images)
6. **Implement advanced features** (citation extraction, fact-checking)

## Performance Tips

1. **Enable caching** for embeddings and common queries
2. **Use background workers** for document processing
3. **Implement pagination** for large document lists
4. **Compress responses** with gzip
5. **Use CDN** for static assets
6. **Optimize database queries** with indexes
