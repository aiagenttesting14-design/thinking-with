# Research Synthesis Service MVP

A lightweight research synthesis service that ingests various document formats (PDFs, web pages, articles), processes them through AI-powered pipelines, and provides synthesized insights through a simple web interface.

## Features

### Core Capabilities
- **Multi-format ingestion**: PDFs, web pages, DOCX, PPTX, plain text
- **AI-powered processing**: Summarization, key point extraction, entity recognition
- **Multi-document synthesis**: Combine insights across multiple research documents
- **Semantic search**: Find relevant content using vector embeddings
- **Knowledge graph**: Visualize relationships between concepts and entities

### User Experience
- **Clean web interface**: Built with Next.js and Tailwind CSS
- **Drag & drop upload**: Easy document management
- **Real-time processing**: Track progress of document analysis
- **Export options**: PDF, Markdown, JSON exports
- **Collaboration**: Share projects with team members

## Architecture

### High-Level Overview
```
Frontend (Next.js) → API Gateway (FastAPI) → Processing Pipeline → AI Services → Data Storage
```

### Key Components
1. **Ingestion Service**: Handles document parsing and text extraction
2. **Processing Pipeline**: Chunking, embedding, summarization, entity extraction
3. **Synthesis Engine**: Multi-document analysis and insight generation
4. **Vector Database**: Semantic search and document similarity
5. **Web Interface**: User-friendly dashboard for research management

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- OpenAI API key (or other LLM provider)

### Installation
```bash
# Clone the repository
git clone https://github.com/your-org/research-synthesis.git
cd research-synthesis

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# Access the application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Basic Usage
1. **Upload documents** via drag & drop or file selection
2. **Process documents** to extract text, generate summaries, and create embeddings
3. **Create synthesis projects** by selecting related documents
4. **Generate insights** by asking research questions
5. **Export results** as PDF, Markdown, or JSON

## Documentation

- [Architecture Overview](./architecture.md) - System design and components
- [Technical Specifications](./technical-spec.md) - API specs, data models, configuration
- [Implementation Plan](./implementation-plan.md) - Phased development roadmap
- [Deployment Strategy](./deployment-strategy.md) - Cloud deployment and scaling
- [Quick Start Guide](./quick-start-guide.md) - Detailed setup and usage instructions

## Technology Stack

### Backend
- **Python 3.11+** with FastAPI
- **PostgreSQL** with pgvector extension
- **Redis** for caching and job queues
- **Qdrant** for vector search (optional)
- **Docker** for containerization

### Frontend
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Shadcn/ui** for components
- **React Query** for data fetching

### AI/ML
- **OpenAI GPT-4/3.5** for summarization and synthesis
- **OpenAI Embeddings** for vector generation
- **Anthropic Claude** (optional alternative)
- **Local models** via Ollama (optional)

### Deployment
- **Vercel** for frontend hosting
- **Railway** for backend services
- **Supabase** for database
- **Cloudflare R2** for storage
- **GitHub Actions** for CI/CD

## Development

### Project Structure
```
research-synthesis/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Configuration and middleware
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   └── workers/  # Background job handlers
│   ├── alembic/      # Database migrations
│   └── tests/        # Backend tests
├── frontend/         # Next.js application
│   ├── app/          # App router pages
│   ├── components/   # React components
│   ├── lib/          # Utilities and hooks
│   └── public/       # Static assets
├── docker/           # Docker configurations
├── docs/             # Documentation
└── scripts/          # Development scripts
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# End-to-end tests
npm run test:e2e
```

### Code Style
```bash
# Backend formatting
cd backend
black .
isort .
flake8 .

# Frontend formatting
cd frontend
npm run lint
npm run format
```

## API Reference

### Authentication
All API endpoints require JWT authentication. Obtain a token via `/api/auth/login`.

### Key Endpoints
- `POST /api/v1/documents` - Upload and process documents
- `GET /api/v1/documents/{id}` - Get document details and analysis
- `POST /api/v1/synthesis` - Create synthesis from multiple documents
- `GET /api/v1/search` - Semantic search across documents
- `GET /api/v1/export/{id}/pdf` - Export synthesis as PDF

### Example Usage
```python
import requests

# Upload a document
response = requests.post(
    "http://localhost:8000/api/v1/documents",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    files={"file": open("research.pdf", "rb")},
    data={"title": "AI Ethics Paper", "source_type": "pdf"}
)

# Get synthesis
response = requests.post(
    "http://localhost:8000/api/v1/synthesis",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "title": "Literature Review",
        "research_question": "What are ethical concerns in AI?",
        "document_ids": ["doc1", "doc2", "doc3"]
    }
)
```

## Deployment

### Production Deployment
See [Deployment Strategy](./deployment-strategy.md) for detailed instructions.

### Environment Variables
Required environment variables:
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# AI Services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...  # Optional

# Storage
CLOUDFLARE_R2_ACCESS_KEY_ID=...
CLOUDFLARE_R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=research-synthesis

# Application
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
```

### Scaling
The architecture supports horizontal scaling:
- Multiple API instances behind load balancer
- Worker pool for background processing
- Read replicas for database
- CDN for static assets

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Write tests for new features
- Update documentation as needed
- Follow existing code style
- Use descriptive commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Documentation](https://docs.research-synthesis.com)
- [GitHub Issues](https://github.com/your-org/research-synthesis/issues)
- [Community Discord](https://discord.gg/research-synthesis)

## Acknowledgments

- Built with FastAPI, Next.js, and OpenAI APIs
- Inspired by research tools like Zotero, Mendeley, and Elicit
- Thanks to all contributors and early testers

---

Built with ❤️ for researchers, students, and knowledge workers.
