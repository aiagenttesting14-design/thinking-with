# Research Synthesis MVP - Technical Architecture Document

## Executive Summary

Based on the existing research and implementation guide, this document outlines a simplified MVP architecture focused on delivering core value with minimal complexity. The MVP will enable users to upload research documents (PDFs, web pages, text), process them through an AI pipeline, and receive synthesized insights through a simple web interface.

## 1. MVP Scope & Core Value Proposition

### Core Features (MVP)
1. **Document Upload**: Support for PDF, web URLs, and plain text
2. **AI Processing**: Automatic summarization and key point extraction
3. **Multi-Document Synthesis**: Find connections between uploaded documents
4. **Simple Web Interface**: Basic dashboard to view documents and insights
5. **API Access**: REST API for programmatic document submission

### Out of Scope (Post-MVP)
- Advanced collaboration features
- Complex visualizations
- Mobile apps
- Enterprise SSO
- Advanced document types (Word, Excel, PowerPoint)
- Citation generation
- Advanced search capabilities

## 2. Simplified Technical Architecture

### High-Level Architecture Diagram
```
┌─────────────────────────────────────────────┐
│               User Interface                 │
│  ┌─────────────────────────────────────┐    │
│  │        Simple React Frontend        │    │
│  │  • Document Upload                  │    │
│  │  • Document List                    │    │
│  │  • Synthesis Results                │    │
│  └─────────────────────────────────────┘    │
└───────────────────┬─────────────────────────┘
                    │ HTTP/REST
┌───────────────────▼─────────────────────────┐
│              FastAPI Backend                 │
│  • Document Ingestion API                   │
│  • AI Processing Service                    │
│  • Synthesis Engine                         │
│  • PostgreSQL Database                      │
└───────────────────┬─────────────────────────┘
                    │
    ┌───────────────▼───────────────┐
    │        External Services       │
    │  • OpenAI API (GPT-3.5)       │
    │  • Anthropic API (Claude Haiku)│
    └───────────────────────────────┘
```

### Component Breakdown

#### 2.1 Document Ingestion Layer
**Purpose**: Handle document uploads and text extraction
**Components**:
- File upload endpoint (multipart/form-data)
- PDF text extraction (PyPDF2/pdfplumber)
- Web content fetching (requests + BeautifulSoup)
- Text preprocessing and chunking

**Simplifications for MVP**:
- Store files locally (no S3/MinIO)
- Basic metadata extraction only
- Skip OCR support initially
- Simple text chunking (fixed size)

#### 2.2 AI Processing Pipeline
**Purpose**: Analyze documents and extract insights
**Components**:
- Summarization service (GPT-3.5/Claude Haiku)
- Key point extraction
- Entity extraction (people, organizations, concepts)
- Embedding generation (OpenAI text-embedding-3-small)

**Cost Optimization Strategy**:
1. Use GPT-3.5-turbo for most operations ($0.0015/1K tokens input)
2. Fallback to Claude Haiku for cheaper operations ($0.25/1M tokens)
3. Cache AI responses for identical content
4. Implement token limits per document (max 4000 tokens)

#### 2.3 Synthesis Engine
**Purpose**: Find connections between multiple documents
**Components**:
- Entity overlap detection
- Topic similarity using embeddings
- Basic timeline generation
- Insight generation from combined key points

**Simplified Approach**:
- Compare documents pairwise (n² complexity acceptable for small sets)
- Use simple cosine similarity on embeddings
- Generate insights from combined summaries (not full documents)

#### 2.4 User Interface
**Purpose**: Provide simple web interface for users
**Components**:
- Document upload page (drag & drop)
- Document list with processing status
- Synthesis results page
- Basic authentication (optional for MVP)

**Technology Stack**:
- React + Vite (simpler than Next.js for MVP)
- Tailwind CSS for styling
- Axios for API calls
- React Dropzone for file uploads

#### 2.5 Database Schema
**Minimal Schema for MVP**:
```sql
-- Users (optional for MVP)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(500),
    source_type VARCHAR(20), -- 'pdf', 'web', 'text'
    original_filename VARCHAR(500),
    file_path TEXT,
    content_hash VARCHAR(64),
    raw_text TEXT,
    metadata JSONB,
    processing_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Document Processing Results
CREATE TABLE document_processing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    summary TEXT,
    key_points TEXT[], -- Array of key points
    entities JSONB, -- {people: [], organizations: [], concepts: []}
    embedding VECTOR(1536), -- OpenAI embedding dimension
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Syntheses (collections of documents)
CREATE TABLE syntheses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(500),
    description TEXT,
    insights TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Synthesis Documents (many-to-many)
CREATE TABLE synthesis_documents (
    synthesis_id UUID REFERENCES syntheses(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    PRIMARY KEY (synthesis_id, document_id)
);

-- Document Connections (pre-computed)
CREATE TABLE document_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_a_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    document_b_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    similarity_score FLOAT,
    common_entities TEXT[],
    connection_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 3. Key Technical Components

### 3.1 Document Ingestion Service
```python
# Simplified ingestion service for MVP
class DocumentIngestor:
    def __init__(self):
        self.supported_types = ['.pdf', '.txt', '.md', '.html']
    
    async def ingest(self, file_content: bytes, filename: str) -> Dict:
        """Extract text from uploaded file"""
        file_type = self._detect_type(filename)
        
        if file_type == 'pdf':
            return await self._process_pdf(file_content)
        elif file_type == 'web':
            # For MVP, web content is submitted as text
            return await self._process_text(file_content)
        else:
            return await self._process_text(file_content)
    
    async def _process_pdf(self, content: bytes) -> Dict:
        """Simple PDF text extraction"""
        import PyPDF2
        import io
        
        text = ""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n\n"
        
        return {
            "content": text,
            "type": "pdf",
            "pages": len(pdf_reader.pages)
        }
```

### 3.2 AI Processing Service
```python
# Cost-effective AI processing
class AIProcessor:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    async def process_document(self, text: str) -> Dict:
        """Process document with cost controls"""
        # Limit text length for cost control
        truncated_text = text[:4000]
        
        # Generate summary (cheapest operation first)
        summary = await self._summarize(truncated_text)
        
        # Extract key points
        key_points = await self._extract_key_points(truncated_text)
        
        # Generate embedding for similarity search
        embedding = await self._generate_embedding(truncated_text)
        
        return {
            "summary": summary,
            "key_points": key_points,
            "embedding": embedding
        }
    
    async def _summarize(self, text: str) -> str:
        """Use cheapest model for summarization"""
        try:
            # Try Claude Haiku first (cheapest)
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                temperature=0.3,
                messages=[{
                    "role": "user", 
                    "content": f"Summarize this text in 150 words or less:\n\n{text}"
                }]
            )
            return response.content[0].text
        except:
            # Fallback to GPT-3.5
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant."},
                    {"role": "user", "content": f"Summarize this text in 150 words or less:\n\n{text}"}
                ],
                max_tokens=200,
                temperature=0.3
            )
            return response.choices[0].message.content
```

### 3.3 Synthesis Engine
```python
# Simple synthesis engine for MVP
class SynthesisEngine:
    def __init__(self):
        pass
    
    async def synthesize_documents(self, documents: List[Dict]) -> Dict:
        """Find connections between documents"""
        connections = []
        
        # Pairwise comparison
        for i in range(len(documents)):
            for j in range(i + 1, len(documents)):
                doc1 = documents[i]
                doc2 = documents[j]
                
                # Calculate similarity using embeddings
                similarity = self._cosine_similarity(
                    doc1["embedding"], 
                    doc2["embedding"]
                )
                
                # Find overlapping key points
                common_points = self._find_common_key_points(
                    doc1["key_points"], 
                    doc2["key_points"]
                )
                
                if similarity > 0.3 or common_points:
                    connections.append({
                        "documents": [doc1["id"], doc2["id"]],
                        "similarity": similarity,
                        "common_points": common_points
                    })
        
        # Generate overall insights
        insights = await self._generate_insights(documents)
        
        return {
            "connections": connections[:10],  # Limit to top 10
            "insights": insights,
            "document_count": len(documents)
        }
```

### 3.4 API Design (MVP)
```
# Core endpoints for MVP
POST   /api/v1/documents          # Upload document
GET    /api/v1/documents          # List user's documents
GET    /api/v1/documents/{id}     # Get document with processing results
DELETE /api/v1/documents/{id}     # Delete document

POST   /api/v1/syntheses          # Create new synthesis
GET    /api/v1/syntheses          # List user's syntheses
GET    /api/v1/syntheses/{id}     # Get synthesis with insights
POST   /api/v1/syntheses/{id}/documents  # Add document to synthesis
POST   /api/v1/syntheses/{id}/generate   # Generate/re-generate insights

GET    /health                    # Health check
```

## 4. Development Effort Estimation (3-Day Phases)

### Phase 1: Foundation & Core Infrastructure (3 days)
**Day 1: Project Setup**
- Initialize project structure
- Set up Docker with PostgreSQL + Redis
- Create basic FastAPI application
- Implement health check endpoint
- Set up environment configuration

**Day 2: Database & Models**
- Design and implement database schema
- Create SQLAlchemy models
- Set up Alembic for migrations
- Implement basic CRUD operations
- Add document storage (local filesystem)

**Day 3: Document Ingestion**
- Implement file upload endpoint
- Add PDF text extraction
- Add web content fetching (simple)
- Implement text preprocessing
- Add basic error handling

### Phase 2: AI Processing Pipeline (3 days)
**Day 4: AI Service Integration**
- Set up OpenAI and Anthropic clients
- Implement cost-controlled summarization
- Add key point extraction
- Implement embedding generation
- Add response caching with Redis

**Day 5: Document Processing Service**
- Create async document processing pipeline
- Implement processing status tracking
- Add retry logic for API failures
- Implement token counting and limits
- Add basic monitoring/logging

**Day 6: Synthesis Engine**
- Implement embedding similarity calculation
- Add document connection detection
- Create insight generation from multiple documents
- Implement basic timeline extraction
- Add synthesis result storage

### Phase 3: User Interface & Polish (3 days)
**Day 7: Frontend Foundation**
- Set up React + Vite project
- Create basic layout and navigation
- Implement document upload component
- Add document list view
- Set up API client with error handling

**Day 8: Synthesis Interface**
- Create synthesis creation workflow
- Implement document selection interface
- Add synthesis results display
- Create connection visualization (basic)
- Add insight display component

**Day 9: Polish & Deployment**
- Add loading states and user feedback
- Implement basic error boundaries
- Add responsive design improvements
- Create Docker production configuration
- Set up basic deployment script
- Write README and documentation

## 5. Biggest Technical Risks & Mitigation Strategies

### Risk 1: AI API Costs Spiral Out of Control
**Impact**: High - Could make service economically unviable
**Mitigation**:
- Implement strict token limits per document (max 4000 tokens)
- Use cheapest models first (Claude Haiku > GPT-3.5 > GPT-4)
- Cache AI responses for identical content
- Add user quotas in MVP (e.g., max 10 documents per day)
- Implement usage monitoring and alerts

### Risk 2: Poor PDF Text Extraction Quality
**Impact**: Medium - Core functionality depends on good text extraction
**Mitigation**:
- Use multiple PDF libraries (PyPDF2 + pdfplumber as fallback)
- Implement OCR as optional enhancement (post-MVP)
- Add user feedback for extraction issues
- Provide manual text input as alternative

### Risk 3: Scalability Issues with Document Comparisons
**Impact**: Low for MVP, Medium for scale
**Mitigation**:
- For MVP: Accept O(n²) complexity for small document sets (≤20)
- Use vector similarity search (pgvector) for efficient comparisons
- Implement batch processing for large document sets
- Add progress indicators for long-running operations

### Risk 4: Web Content Fetching Reliability
**Impact**: Medium - Web ingestion is a key feature
**Mitigation**:
- Use robust HTTP client with timeouts and retries
- Implement fallback to manual text input
- Cache fetched content to avoid repeated failures
- Provide clear error messages for failed fetches

### Risk 5: Database Performance with Embeddings
**Impact**: Low for MVP, High for scale
**Mitigation**:
- Use pgvector extension for efficient vector operations
- Implement indexing on embedding columns
- Consider separate vector database (Qdrant/Weaviate) post-MVP
- Implement pagination for large result sets

## 6. Cost-Effective AI Model Usage Strategy

### Tiered Model Selection
1. **Summarization & Simple Extraction**: Claude 3 Haiku ($0.25/1M tokens)
2. **Complex Analysis**: GPT-3.5 Turbo ($1.50/1M tokens input)
3. **Advanced Reasoning**: GPT-4 Turbo (only if absolutely necessary)

### Cost Control Measures
- **Token Limits**: Max 4000 tokens per document for processing
- **Response Caching**: Cache identical content processing results
- **Batch Processing**: Process multiple documents in single API calls when possible
- **Usage Monitoring**: Track costs per user/document
- **Fallback Strategies**: Implement graceful degradation when APIs fail

### Estimated Costs for MVP
- **Development Phase**: ~$50-100 in API costs for testing
- **Beta Users (10 users)**: ~$20-50/month assuming 100 documents/month
- **Scale (100 users)**: ~$200-500/month with optimizations

## 7. Deployment & Infrastructure

### MVP Deployment Options
1. **Simplest**: Single VPS (DigitalOcean, Linode) - $10-20/month
   - Run everything on one machine
   - Use Docker Compose for services
   - Manual backups

2. **Managed Services**: Railway/Render - $20-50/month
   - Easier deployment and scaling
   - Built-in PostgreSQL and Redis
   - Automatic SSL certificates

3. **Serverless**: Vercel + Supabase - $0-30/month
   - Frontend on Vercel (free tier)
   - Backend as serverless functions
   - Supabase for database (free tier)

### Recommended for MVP: Option 1 (Single VPS)
- **Pros**: Full control, predictable costs, simple architecture
- **Cons**: Manual maintenance, single point of failure
- **Suitable for**: MVP testing with ≤100 users

## 8. Success Metrics & Validation

### Technical Validation Criteria
1. **Document Processing Success Rate**: >90% of PDFs processed correctly
2. **AI Processing Latency**: <30 seconds for average document
3. **API Reliability**: >99% uptime for core endpoints
4. **Cost Efficiency**: <$0.10 per document processed

### User Validation Criteria
1. **Core Workflow Completion**: Users can upload, process, and view insights
2. **Insight Quality**: Synthetic insights are useful and accurate
3. **System Responsiveness**: UI feels responsive (<2s for most operations)
4. **Error Handling**: Clear error messages and recovery paths

## 9. Next Steps & Evolution Path

### Post-MVP Enhancements (Prioritized)
1. **Authentication & User Management** (Week 4)
2. **Advanced Document Types** (Word, Excel, PowerPoint) (Week 5)
3.3. **Collaboration Features** (shared projects, comments) (Week 6)
4. **Advanced Search** (semantic + keyword) (Week 7)
5. **Export & Reporting** (PDF, Word exports) (Week 8)
6. **API Rate Limiting & Usage Analytics** (Week 9)
7. **Mobile App** (React Native) (Week 10+)

### Scaling Considerations
- **Database**: Move to managed PostgreSQL with read replicas
- **File Storage**: Migrate from local files to S3/Cloud Storage
- **Processing**: Implement message queue (RabbitMQ/Celery) for async processing
- **Caching**: Add Redis cluster for distributed caching
- **Monitoring**: Implement comprehensive logging and APM (Datadog/Sentry)

## Conclusion

This MVP architecture focuses on delivering the core value proposition of research synthesis with minimal complexity. By starting with a simplified implementation and carefully controlling costs, we can validate the concept with real users before investing in more complex features.

The 3-phase, 9-day development plan provides a realistic roadmap for building a functional MVP that can be tested with early users. The biggest risks are manageable with the proposed mitigation strategies, particularly around AI API costs and PDF extraction quality.

The architecture is designed to be extensible, allowing for incremental addition of features based on user feedback and validation of the core value proposition.

---

**Appendix A: Technology Stack Summary**

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Backend Framework | FastAPI (Python) | Fast, modern, async support, automatic docs |
| Database | PostgreSQL + pgvector | Relational + vector search in one system |
| Cache | Redis | Simple, fast, battle-tested |
| Frontend | React + Vite + TypeScript | Modern, fast dev experience, type safety |
| Styling | Tailwind CSS | Utility-first, rapid UI development |
| AI APIs | OpenAI + Anthropic | Best available models, cost-effective options |
| PDF Processing | PyPDF2 + pdfplumber | Simple, reliable text extraction |
| Web Scraping | requests + BeautifulSoup | Lightweight, effective for most content |
| Deployment | Docker + Docker Compose | Consistent environments, easy deployment |
| Hosting | VPS (DigitalOcean/Linode) | Simple, predictable costs for MVP |

**Appendix B: Development Team Requirements**

- **1 Backend Developer** (Python/FastAPI): 3 weeks full-time
- **1 Frontend Developer** (React/TypeScript): 2 weeks full-time
- **1 DevOps/Full-stack**: 1 week part-time for deployment

**Total Effort**: ~6 person-weeks for complete MVP

**Appendix C: Cost Breakdown for MVP**

| Item | Monthly Cost | Notes |
|------|-------------|-------|
| VPS Hosting | $20 | 2GB RAM, 1 vCPU, 50GB storage |
| Domain Name | $1 | Custom domain |
| SSL Certificate | $0 | Let's Encrypt (free) |
| AI API Costs | $20-100 | Depends on usage (estimate for 100 docs/day) |
| **Total** | **$41-121/month** | Scalable based on usage |

