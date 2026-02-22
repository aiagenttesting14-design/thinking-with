# Technical Specifications

## 1. Data Models

### Document Model
```python
class Document:
    id: UUID
    user_id: UUID
    title: str
    source_type: str  # "pdf", "web", "text", "docx", etc.
    source_url: str  # Original source URL or path
    content_hash: str  # For deduplication
    raw_text: str  # Extracted text content
    metadata: JSON  # {author, date, publisher, language, etc.}
    file_size: int
    mime_type: str
    processing_status: str  # "pending", "processing", "completed", "failed"
    created_at: datetime
    updated_at: datetime
```

### Chunk Model
```python
class Chunk:
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    token_count: int
    embedding: Vector  # 1536-dim for OpenAI embeddings
    metadata: JSON  # {page_number, section_title, etc.}
    created_at: datetime
```

### Summary Model
```python
class Summary:
    id: UUID
    document_id: UUID
    summary_type: str  # "executive", "detailed", "bullet_points"
    content: str
    key_points: List[str]
    entities: JSON  # {people: [], organizations: [], dates: []}
    confidence_score: float
    model_used: str  # "gpt-4", "claude-3", etc.
    created_at: datetime
```

### Synthesis Model
```python
class Synthesis:
    id: UUID
    project_id: UUID
    title: str
    research_question: str
    documents: List[UUID]  # References to documents
    content: str  # Generated synthesis
    themes: List[str]
    contradictions: List[str]
    gaps: List[str]
    recommendations: List[str]
    knowledge_graph: JSON  # Graph representation
    version: int
    created_at: datetime
    updated_at: datetime
```

## 2. API Specifications

### Base URL: `/api/v1`

### Authentication
- **Method**: JWT Bearer tokens
- **Header**: `Authorization: Bearer <token>`
- **Token Refresh**: `/api/auth/refresh`

### Endpoints

#### Documents
```
GET    /documents           - List documents
POST   /documents           - Upload new document
GET    /documents/{id}      - Get document details
PUT    /documents/{id}      - Update document metadata
DELETE /documents/{id}      - Delete document
POST   /documents/{id}/process - Trigger processing
```

#### Processing
```
POST   /process/batch       - Process multiple documents
GET    /process/status/{job_id} - Check processing status
POST   /process/summarize   - Generate summary for document
POST   /process/extract     - Extract entities/key points
```

#### Synthesis
```
GET    /synthesis           - List synthesis projects
POST   /synthesis           - Create new synthesis
GET    /synthesis/{id}      - Get synthesis details
PUT    /synthesis/{id}      - Update synthesis
POST   /synthesis/{id}/generate - Generate/regenerate synthesis
DELETE /synthesis/{id}      - Delete synthesis
```

#### Search
```
GET    /search              - Semantic search across documents
POST   /search/similar      - Find similar documents
GET    /search/within/{doc_id} - Search within specific document
```

#### Export
```
GET    /export/{synthesis_id}/pdf     - Export as PDF
GET    /export/{synthesis_id}/markdown - Export as Markdown
GET    /export/{synthesis_id}/json    - Export as JSON
```

### Request/Response Examples

#### Upload Document
```json
POST /api/v1/documents
Content-Type: multipart/form-data

{
  "file": <binary file>,
  "title": "Research Paper on AI Ethics",
  "source_type": "pdf",
  "metadata": {
    "author": "Jane Doe",
    "year": 2023
  }
}

Response:
{
  "id": "uuid-123",
  "status": "pending",
  "processing_job_id": "job-456"
}
```

#### Generate Synthesis
```json
POST /api/v1/synthesis
{
  "title": "AI Ethics Literature Review",
  "research_question": "What are the main ethical concerns in AI development?",
  "document_ids": ["doc-1", "doc-2", "doc-3"],
  "options": {
    "depth": "comprehensive",
    "include_contradictions": true,
    "generate_recommendations": true
  }
}

Response:
{
  "id": "synth-789",
  "status": "processing",
  "estimated_completion": "2024-01-15T10:30:00Z"
}
```

## 3. Processing Pipeline Specifications

### Stage 1: Ingestion
```python
def ingest_document(file_path, source_type):
    if source_type == "pdf":
        text = extract_pdf_text(file_path)
        metadata = extract_pdf_metadata(file_path)
    elif source_type == "web":
        text = scrape_web_content(file_path)
        metadata = extract_web_metadata(file_path)
    elif source_type == "text":
        text = read_text_file(file_path)
        metadata = {"source": "text_file"}
    
    return {
        "raw_text": text,
        "metadata": metadata,
        "content_hash": generate_hash(text)
    }
```

### Stage 2: Chunking
```python
def chunk_document(text, chunk_size=1000, overlap=100):
    # Split by paragraphs first
    paragraphs = text.split('\\n\\n')
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para + " "
            else:
                # Single paragraph longer than chunk size
                chunks.extend(split_long_paragraph(para, chunk_size))
        else:
            current_chunk += para + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks
```

### Stage 3: Embedding
```python
def generate_embeddings(chunks):
    # Use OpenAI embeddings API
    response = openai.Embedding.create(
        model="text-embedding-3-small",
        input=chunks
    )
    
    embeddings = [item["embedding"] for item in response["data"]]
    return embeddings
```

### Stage 4: Summarization
```python
def summarize_document(chunks, model="gpt-4"):
    # Combine chunks with context window consideration
    context = "\\n\\n".join(chunks[:5])  # First 5 chunks for context
    
    prompt = f"""
    Summarize the following research document:
    
    {context}
    
    Provide:
    1. Executive summary (2-3 paragraphs)
    2. Key findings (bullet points)
    3. Methodology used
    4. Conclusions and implications
    """
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    return parse_summary(response.choices[0].message.content)
```

### Stage 5: Synthesis
```python
def synthesize_documents(document_summaries, research_question):
    # Prepare context from all documents
    context = "\\n\\n".join([
        f"Document {i+1}:\\n{summary}"
        for i, summary in enumerate(document_summaries)
    ])
    
    prompt = f"""
    Research Question: {research_question}
    
    Documents to synthesize:
    {context}
    
    Create a comprehensive synthesis that:
    1. Identifies common themes across documents
    2. Highlights contradictions or differing viewpoints
    3. Identifies gaps in the literature
    4. Provides recommendations for future research
    5. Answers the research question based on the evidence
    
    Structure your response with clear sections.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2000
    )
    
    return response.choices[0].message.content
```

## 4. Database Schema

### SQL Schema
```sql
-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(500) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_url TEXT,
    content_hash VARCHAR(64) UNIQUE,
    raw_text TEXT,
    metadata JSONB,
    file_size INTEGER,
    mime_type VARCHAR(100),
    processing_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create indexes
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_processing_status ON documents(processing_status);
CREATE INDEX idx_documents_created_at ON documents(created_at);

-- Chunks table
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER,
    embedding vector(1536),  -- For pgvector
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Enable vector similarity search
CREATE INDEX idx_chunks_embedding ON chunks 
USING ivfflat (embedding vector_cosine_ops);

-- Summaries table
CREATE TABLE summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    summary_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    key_points TEXT[],
    entities JSONB,
    confidence_score FLOAT,
    model_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Synthesis table
CREATE TABLE synthesis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL,
    title VARCHAR(500) NOT NULL,
    research_question TEXT,
    content TEXT NOT NULL,
    themes TEXT[],
    contradictions TEXT[],
    gaps TEXT[],
    recommendations TEXT[],
    knowledge_graph JSONB,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Junction table for synthesis documents
CREATE TABLE synthesis_documents (
    synthesis_id UUID NOT NULL,
    document_id UUID NOT NULL,
    PRIMARY KEY (synthesis_id, document_id),
    FOREIGN KEY (synthesis_id) REFERENCES synthesis(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);
```

## 5. Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/research_synthesis
REDIS_URL=redis://localhost:6379

# AI Services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
TOGETHER_API_KEY=...

# Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Storage
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=research-synthesis
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_R2_ACCESS_KEY_ID=
CLOUDFLARE_R2_SECRET_ACCESS_KEY=

# Application
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret
CORS_ORIGINS=http://localhost:3000,https://app.example.com

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600
```

### Docker Compose Configuration
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: research_synthesis
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/research_synthesis
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - postgres
      - redis
      - qdrant

  worker:
    build: ./backend
    command: python worker.py
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/research_synthesis
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - postgres
      - redis
      - qdrant

  web:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

volumes:
  postgres_data:
  qdrant_data:
```

## 6. Performance Targets

### Response Times
- **API Response**: < 200ms for simple requests
- **Document Upload**: < 2 seconds for files up to 10MB
- **Initial Processing**: < 30 seconds per document
- **Synthesis Generation**: < 2 minutes for up to 10 documents
- **Search Queries**: < 100ms

### Throughput
- **Concurrent Users**: 100+ simultaneous users
- **Document Processing**: 10+ documents per minute
- **API Requests**: 1000+ requests per minute

### Availability
- **Uptime**: 99.9%
- **Error Rate**: < 0.1%
- **Data Durability**: 99.999999999% (11 nines)

## 7. Testing Strategy

### Unit Tests
- Document ingestion functions
- Chunking algorithms
- Embedding generation
- API endpoints

### Integration Tests
- Full processing pipeline
- Database operations
- External API calls (OpenAI, etc.)
- File upload and storage

### Load Tests
- Concurrent document uploads
- Multiple synthesis generations
- Search query performance
- API rate limiting

### Security Tests
- Authentication and authorization
- Input validation
- SQL injection prevention
- File upload security

## 8. Deployment Checklist

### Pre-deployment
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Backup strategy in place

### Deployment
- [ ] Container images built and tagged
- [ ] Kubernetes manifests applied (if using K8s)
- [ ] Services started and healthy
- [ ] Load balancer configured
- [ ] DNS records updated

### Post-deployment
- [ ] Health checks passing
- [ ] Monitoring alerts configured
- [ ] Log aggregation working
- [ ] Performance baselines established
- [ ] User acceptance testing completed
