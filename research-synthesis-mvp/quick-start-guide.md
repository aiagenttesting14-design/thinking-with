# Quick Start Guide

## Prerequisites

### Required Software
- **Python 3.11+**: [Download](https://www.python.org/downloads/)
- **Node.js 18+**: [Download](https://nodejs.org/)
- **Docker & Docker Compose**: [Download](https://www.docker.com/products/docker-desktop)
- **Git**: [Download](https://git-scm.com/downloads)

### Required Accounts
- **OpenAI API Key**: [Get here](https://platform.openai.com/api-keys)
- **Anthropic API Key** (optional): [Get here](https://console.anthropic.com/)
- **Cloudflare R2** (optional for storage): [Get here](https://dash.cloudflare.com/)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/research-synthesis.git
cd research-synthesis
```

### 2. Set Up Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Set Up Frontend
```bash
cd ../frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API URL
```

### 4. Start Services with Docker
```bash
cd ..

# Start all services
docker-compose up -d

# Check services are running
docker-compose ps
```

### 5. Initialize Database
```bash
# Run migrations
cd backend
alembic upgrade head

# Or using Docker
docker-compose exec api alembic upgrade head
```

### 6. Start Development Servers
```bash
# Terminal 1: Backend API
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

## Basic Usage

### 1. Access the Application
- Open your browser to: http://localhost:3000
- Register a new account or use test credentials

### 2. Upload Your First Document
1. Click "Upload Document" button
2. Drag & drop a PDF file or select from your computer
3. Add metadata (title, author, etc.)
4. Click "Process Document"

### 3. View Processing Results
1. Go to "Documents" page
2. Click on your uploaded document
3. View:
   - Extracted text
   - Generated summary
   - Key points
   - Extracted entities

### 4. Create Your First Synthesis
1. Go to "Synthesis" page
2. Click "Create New Synthesis"
3. Select 2-3 related documents
4. Enter a research question
5. Click "Generate Synthesis"
6. View the synthesized analysis

## API Usage Examples

### Using cURL
```bash
# Upload a document
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@research_paper.pdf" \
  -F "title=AI Ethics Paper" \
  -F "source_type=pdf"

# Get document summary
curl -X GET http://localhost:8000/api/v1/documents/{document_id}/summary \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create synthesis
curl -X POST http://localhost:8000/api/v1/synthesis \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Literature Review",
    "research_question": "What are ethical concerns in AI?",
    "document_ids": ["doc1", "doc2", "doc3"]
  }'
```

### Using Python
```python
import requests

# Configure API client
BASE_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# Upload document
with open("research.pdf", "rb") as f:
    files = {"file": f}
    data = {"title": "Research Paper", "source_type": "pdf"}
    response = requests.post(
        f"{BASE_URL}/documents",
        headers=headers,
        files=files,
        data=data
    )
    document_id = response.json()["id"]

# Get summary
summary_response = requests.get(
    f"{BASE_URL}/documents/{document_id}/summary",
    headers=headers
)
print(summary_response.json())
```

## Configuration Options

### AI Model Selection
Edit `backend/config/ai_models.py`:
```python
# Choose which models to use for different tasks
MODEL_CONFIG = {
    "summarization": "gpt-4",  # or "claude-3-opus", "mixtral"
    "embedding": "text-embedding-3-small",
    "synthesis": "gpt-4",
    "entity_extraction": "gpt-3.5-turbo"
}
```

### Storage Configuration
Edit `.env` file:
```bash
# Use local storage (default)
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./storage

# Or use S3/R2
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=your-bucket

# Or use Cloudflare R2
STORAGE_TYPE=r2
CLOUDFLARE_ACCOUNT_ID=your_account
CLOUDFLARE_R2_ACCESS_KEY_ID=your_key
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_secret
R2_BUCKET_NAME=your-bucket
```

### Vector Database Options
```bash
# Use Qdrant (default with Docker)
VECTOR_DB_TYPE=qdrant
QDRANT_URL=http://localhost:6333

# Or use Pinecone (cloud)
VECTOR_DB_TYPE=pinecone
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=us-east-1

# Or use pgvector (PostgreSQL extension)
VECTOR_DB_TYPE=pgvector
# No additional config needed if using PostgreSQL with pgvector
```

## Common Tasks

### Processing Multiple Documents
```bash
# Using the API
curl -X POST http://localhost:8000/api/v1/process/batch \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_ids": ["doc1", "doc2", "doc3"],
    "options": {
      "generate_summaries": true,
      "extract_entities": true,
      "generate_embeddings": true
    }
  }'
```

### Searching Documents
```python
# Semantic search
search_response = requests.post(
    f"{BASE_URL}/search",
    headers=headers,
    json={
        "query": "machine learning ethics",
        "limit": 10,
        "filters": {
            "min_date": "2020-01-01",
            "max_date": "2024-01-01"
        }
    }
)
```

### Exporting Results
```bash
# Export synthesis as PDF
curl -X GET http://localhost:8000/api/v1/export/{synthesis_id}/pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output synthesis.pdf

# Export as Markdown
curl -X GET http://localhost:8000/api/v1/export/{synthesis_id}/markdown \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output synthesis.md
```

## Troubleshooting

### Common Issues

#### 1. Docker Services Not Starting
```bash
# Check Docker logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d

# Check resource usage
docker stats
```

#### 2. Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose exec postgres psql -U postgres -c "\\l"

# Reset database (development only)
docker-compose down -v
docker-compose up -d
```

#### 3. API Key Errors
- Verify API keys in `.env` file
- Check API quota and billing
- Test API keys directly:
  ```bash
  curl https://api.openai.com/v1/models \
    -H "Authorization: Bearer YOUR_OPENAI_KEY"
  ```

#### 4. File Upload Issues
- Check file size limits (default: 100MB)
- Verify file permissions
- Check storage configuration
- Ensure CORS is properly configured

### Debug Mode
Enable debug logging by setting in `.env`:
```bash
LOG_LEVEL=DEBUG
DEBUG=true
```

View logs:
```bash
# Backend logs
docker-compose logs api -f

# Worker logs
docker-compose logs worker -f

# Frontend logs
cd frontend && npm run dev  # View in terminal
```

## Performance Tips

### For Development
1. **Use smaller models**: Configure GPT-3.5 instead of GPT-4 for faster iteration
2. **Enable caching**: Set `CACHE_ENABLED=true` in `.env`
3. **Limit document size**: Process smaller documents during development
4. **Use mock AI responses**: Set `USE_MOCK_AI=true` for testing

### For Production
1. **Enable CDN**: Configure Cloudflare or similar for static assets
2. **Implement caching**: Use Redis for frequent queries
3. **Optimize database**: Add indexes and optimize queries
4. **Monitor costs**: Set up billing alerts for AI API usage

## Next Steps

### Learn More
- Read the [API Documentation](http://localhost:8000/docs)
- Explore the [Admin Dashboard](http://localhost:3000/admin)
- Check [Example Projects](./examples/)

### Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Get Help
- [Documentation](https://docs.research-synthesis.com)
- [GitHub Issues](https://github.com/your-org/research-synthesis/issues)
- [Community Discord](https://discord.gg/research-synthesis)

## License
This project is licensed under the MIT License - see the LICENSE file for details.
