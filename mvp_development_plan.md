# Research Synthesis MVP - Development Plan Summary

## Core Architecture Decisions

### 1. Simplified Stack (MVP Focus)
- **Backend**: FastAPI (Python) - for rapid development and async support
- **Database**: PostgreSQL + pgvector - combines relational data and vector search
- **Frontend**: React + Vite - simpler than Next.js for MVP
- **AI Models**: Claude Haiku (primary) + GPT-3.5 (fallback) - cost optimization
- **Deployment**: Single VPS with Docker Compose - simplest for MVP

### 2. MVP Scope (What's IN vs OUT)
**INCLUDED**:
- PDF, web URL, and text document upload
- AI summarization and key point extraction
- Multi-document connection finding
- Simple web interface for upload/results
- REST API for programmatic access

**EXCLUDED (for now)**:
- Authentication (optional for MVP)
- Advanced document types (Word, Excel, PPT)
- Collaboration features
- Mobile apps
- Complex visualizations
- Enterprise features

## 3-Phase Development Plan (9 Days Total)

### Phase 1: Foundation & Core Infrastructure (Days 1-3)

**Day 1: Project Setup**
- Initialize project structure with Docker
- Set up PostgreSQL + Redis containers
- Create basic FastAPI app with health endpoint
- Configure environment variables

**Day 2: Database & Models**
- Design and implement core database schema
- Create SQLAlchemy models for documents/syntheses
- Set up Alembic migrations
- Implement basic CRUD operations

**Day 3: Document Ingestion**
- Implement file upload endpoint (multipart/form-data)
- Add PDF text extraction (PyPDF2)
- Add web content fetching (requests + BeautifulSoup)
- Implement text preprocessing and chunking

### Phase 2: AI Processing Pipeline (Days 4-6)

**Day 4: AI Service Integration**
- Set up OpenAI and Anthropic API clients
- Implement cost-controlled summarization (Claude Haiku first)
- Add key point extraction
- Implement embedding generation (OpenAI text-embedding-3-small)

**Day 5: Document Processing Service**
- Create async processing pipeline
- Implement processing status tracking
- Add retry logic for API failures
- Implement token counting and limits

**Day 6: Synthesis Engine**
- Implement embedding similarity calculation
- Add document connection detection (pairwise comparison)
- Create insight generation from multiple documents
- Implement basic timeline extraction

### Phase 3: User Interface & Polish (Days 7-9)

**Day 7: Frontend Foundation**
- Set up React + Vite project
- Create basic layout and navigation
- Implement document upload component (drag & drop)
- Add document list view with processing status

**Day 8: Synthesis Interface**
- Create synthesis creation workflow
- Implement document selection interface
- Add synthesis results display (connections + insights)
- Create basic visualization of document relationships

**Day 9: Polish & Deployment**
- Add loading states and user feedback
- Implement error handling and boundaries
- Create Docker production configuration
- Set up deployment scripts
- Write documentation and README

## Biggest Technical Risks & Mitigations

### 1. AI API Cost Control
- **Risk**: Costs could spiral with heavy usage
- **Mitigation**: Token limits (4000/doc), cheapest models first, response caching

### 2. PDF Extraction Quality
- **Risk**: Poor text extraction from complex PDFs
- **Mitigation**: Multiple libraries (PyPDF2 + pdfplumber), manual text fallback

### 3. Scalability of Document Comparisons
- **Risk**: O(n²) complexity becomes problematic
- **Mitigation**: Acceptable for MVP (≤20 docs), pgvector for efficient similarity

### 4. Web Content Fetching Reliability
- **Risk**: Websites block scraping or have complex JS
- **Mitigation**: Robust HTTP client, fallback to manual input, clear errors

## Cost Estimates

### Development Phase
- **AI API Costs**: $50-100 for testing
- **Infrastructure**: $0 (local development)

### MVP Deployment (Monthly)
- **VPS Hosting**: $20 (2GB RAM, 1 vCPU)
- **AI API Costs**: $20-100 (100 documents/day)
- **Total**: $40-120/month

### Team Requirements
- **1 Backend Developer**: 3 weeks full-time
- **1 Frontend Developer**: 2 weeks full-time  
- **1 DevOps/Full-stack**: 1 week part-time
- **Total**: ~6 person-weeks

## Success Metrics for MVP Validation

### Technical Metrics
- Document processing success rate >90%
- AI processing latency <30 seconds
- API reliability >99%
- Cost efficiency <$0.10 per document

### User Metrics
- Core workflow completion (upload → process → view insights)
- Insight quality (users find synthetic insights useful)
- System responsiveness (UI feels fast)
- Clear error handling and recovery

## Evolution Path (Post-MVP)

### Priority 1 (Week 4): Authentication & User Management
### Priority 2 (Week 5): Advanced Document Types (Word, Excel, PPT)
### Priority 3 (Week 6): Collaboration Features
### Priority 4 (Week 7): Advanced Search
### Priority 5 (Week 8): Export & Reporting

## Key Technical Components (Simplified for MVP)

### 1. Document Ingestion Service
- File upload handling
- PDF text extraction (PyPDF2)
- Web content fetching
- Text preprocessing

### 2. AI Processing Service  
- Summarization (Claude Haiku → GPT-3.5)
- Key point extraction
- Entity extraction (basic)
- Embedding generation

### 3. Synthesis Engine
- Pairwise document comparison
- Embedding similarity calculation
- Connection detection
- Insight generation

### 4. Database Schema (Minimal)
- Documents table (with embeddings)
- Document processing results
- Syntheses table
- Document connections

## Deployment Strategy

### MVP: Single VPS with Docker Compose
- **Pros**: Simple, predictable costs, full control
- **Cons**: Manual maintenance, single point of failure
- **Suitable for**: ≤100 users, MVP validation

### Future: Managed Services
- Railway/Render for easier scaling
- Managed PostgreSQL + Redis
- Automatic deployments and scaling

## Conclusion

This MVP development plan provides a realistic 9-day roadmap to build a functional research synthesis service. By focusing on core functionality and implementing strong cost controls, we can validate the concept with real users before investing in more complex features.

The architecture is intentionally simplified for the MVP, with clear extension points for adding features based on user feedback and validation of the core value proposition.
