# Deployment Strategy

## Overview
This document outlines the deployment strategy for the Research Synthesis Service MVP, focusing on simplicity, reliability, and cost-effectiveness.

## Target Architecture

### Production Environment
```
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare (CDN/DNS)                     │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                    Vercel (Frontend)                        │
│  • Next.js Application                                      │
│  • Automatic deployments from main branch                   │
│  • Edge Functions for API routes                            │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                    Railway/Render (Backend)                 │
│  • FastAPI Application                                      │
│  • PostgreSQL Database                                      │
│  • Redis Cache                                              │
│  • Worker processes                                         │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                    Cloud Storage                            │
│  • Cloudflare R2 (S3-compatible)                           │
│  • Document storage                                         │
│  • Embedding cache                                          │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                    Vector Database                          │
│  • Pinecone (managed) or Qdrant (self-hosted)              │
│  • Vector embeddings storage                                │
│  • Semantic search index                                    │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Options

### Option 1: Fully Managed (Recommended for MVP)
**Platform**: Railway.app or Render.com
**Pros**:
- Simple setup and configuration
- Automatic scaling
- Built-in databases and Redis
- Free tier available
- Easy CI/CD integration

**Configuration**:
```yaml
# railway.toml
[service]
name = "research-synthesis-api"
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"

[service.env]
DATABASE_URL = "postgresql://..."
REDIS_URL = "redis://..."
OPENAI_API_KEY = "{{OPENAI_API_KEY}}"

[deploy]
triggers = [{ ref = "main" }]
```

### Option 2: AWS Serverless
**Services**:
- **API Gateway + Lambda** for API endpoints
- **RDS PostgreSQL** for metadata
- **ElastiCache Redis** for caching
- **S3** for document storage
- **ECS Fargate** for background workers

**Pros**:
- High scalability
- Pay-per-use pricing
- Enterprise features

**Cons**:
- More complex setup
- Higher operational overhead

### Option 3: Kubernetes (Self-Hosted)
**Platform**: DigitalOcean, AWS EKS, or GKE
**Pros**:
- Full control over infrastructure
- Can be cost-effective at scale
- Portable across clouds

**Cons**:
- Significant DevOps overhead
- Steeper learning curve

## Step-by-Step Deployment Guide

### Phase 1: Pre-deployment Setup

#### 1.1 Domain & DNS
```bash
# Purchase domain (e.g., research-synthesis.com)
# Configure DNS records:
#   A     @      → Vercel IP
#   CNAME www    → cname.vercel-dns.com
#   CNAME api    → railway.app
```

#### 1.2 Environment Variables
Create `.env.production`:
```bash
# Backend
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_KEY=...
S3_ENDPOINT=https://r2.cloudflarestorage.com
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET=research-documents
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west1-gcp

# Frontend
NEXT_PUBLIC_API_URL=https://api.research-synthesis.com
NEXT_PUBLIC_APP_URL=https://research-synthesis.com
```

#### 1.3 Database Setup
```sql
-- Initial schema
CREATE TABLE documents (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    original_filename VARCHAR(500),
    file_type VARCHAR(50),
    storage_path TEXT,
    metadata JSONB,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_status ON documents(status);
```

### Phase 2: Backend Deployment

#### 2.1 Railway Deployment
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and initialize
railway login
railway init

# Link to existing project or create new
railway link --project research-synthesis

# Set environment variables
railway variables set DATABASE_URL=$DATABASE_URL
railway variables set OPENAI_API_KEY=$OPENAI_API_KEY
# ... set all other variables

# Deploy
railway up
```

#### 2.2 Database Migration
```python
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:pass@host:5432/db

# Run migrations
alembic upgrade head
```

#### 2.3 Vector Database Setup
```python
# Initialize Pinecone
import pinecone

pinecone.init(api_key="your-api-key", environment="us-west1-gcp")

# Create index if it doesn't exist
if "research-index" not in pinecone.list_indexes():
    pinecone.create_index(
        name="research-index",
        dimension=1536,  # OpenAI embedding dimension
        metric="cosine"
    )

index = pinecone.Index("research-index")
```

### Phase 3: Frontend Deployment

#### 3.1 Vercel Deployment
```bash
# Install Vercel CLI
npm i -g vercel

# Login and initialize
vercel login
vercel

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_APP_URL production

# Deploy to production
vercel --prod
```

#### 3.2 Configure Custom Domain
```bash
# Add domain in Vercel dashboard
vercel domains add research-synthesis.com

# Or via CLI
vercel domains add research-synthesis.com
```

### Phase 4: Storage Setup

#### 4.1 Cloudflare R2 Configuration
```bash
# Create R2 bucket
r2 bucket create research-documents

# Configure CORS
r2 bucket cors put research-documents --cors-config cors.json
```

```json
// cors.json
{
  "AllowedOrigins": ["https://research-synthesis.com"],
  "AllowedMethods": ["GET", "PUT", "POST"],
  "MaxAgeSeconds": 3000
}
```

#### 4.2 S3 Client Configuration
```python
import boto3
from botocore.config import Config

s3_client = boto3.client(
    's3',
    endpoint_url='https://r2.cloudflarestorage.com',
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    config=Config(signature_version='s3v4')
)
```

### Phase 5: Monitoring & Analytics

#### 5.1 Application Monitoring
```python
# Sentry setup
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)
```

#### 5.2 Logging Configuration
```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

#### 5.3 Metrics Collection
```python
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
DOCUMENTS_PROCESSED = Counter('documents_processed', 'Total documents processed')
PROCESSING_TIME = Histogram('processing_seconds', 'Document processing time')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Phase 6: CI/CD Pipeline

#### 6.1 GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: railway/action@v1
        with:
          service: research-synthesis-api
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID}}
          vercel-project-id: ${{ secrets.PROJECT_ID}}
```

#### 6.2 Database Migration Automation
```yaml
# .github/workflows/migrate.yml
name: Database Migrations

on:
  workflow_run:
    workflows: ["Deploy"]
    types:
      - completed

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: |
          pip install -r backend/requirements.txt
          cd backend
          alembic upgrade head
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### Phase 7: Security & Compliance

#### 7.1 SSL/TLS Configuration
```bash
# Automatic with Vercel and Railway
# Ensure HTTPS redirect
```

#### 7.2 API Security
```python
# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# CORS configuration
origins = [
    "https://research-synthesis.com",
    "https://www.research-synthesis.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 7.3 Data Encryption
```python
# Encrypt sensitive data at rest
from cryptography.fernet import Fernet

cipher = Fernet(settings.ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(encrypted: str) -> str:
    return cipher.decrypt(encrypted.encode()).decode()
```

### Phase 8: Backup & Disaster Recovery

#### 8.1 Database Backups
```bash
# Automated backups with Railway/Render
# Or manual backup script:
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Upload to S3/R2
aws s3 cp backup.sql s3://backups/research-db/
```

#### 8.2 Document Storage Redundancy
```python
# Cross-region replication for R2
# Or implement backup to secondary storage
```

#### 8.3 Recovery Procedures
```bash
# Database restore
psql $DATABASE_URL < backup.sql

# Vector index rebuild
python scripts/rebuild_index.py
```

## Cost Optimization

### Monthly Cost Estimates
| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Vercel | Pro | $20 |
| Railway | Standard | $50 |
| PostgreSQL | 1GB RAM | $7 |
| Redis | 256MB | $5 |
| Cloudflare R2 | 10GB storage | $0.50 |
| Pinecone | Starter | $0 |
| OpenAI API | ~100k tokens/day | $100 |
| **Total** | | **~$182.50** |

### Cost Saving Tips
1. **Cache aggressively**: Redis cache for embeddings and common queries
2. **Batch processing**: Process documents in batches during off-peak hours
3. **Use smaller models**: Use GPT-3.5-turbo for simple tasks, GPT-4 for complex synthesis
4. **Implement usage limits**: Per-user rate limiting
5. **Monitor and alert**: Set up cost alerts for API usage

## Scaling Strategy

### Horizontal Scaling
```yaml
# railway.toml scaling configuration
[service]
scale = {
  min = 1,
  max = 10,
  concurrency = 100,
  cpu = 512,
  memory = 1024
}
```

### Database Scaling
1. **Read replicas** for heavy read workloads
2. **Connection pooling** with PgBouncer
3. **Query optimization** and indexing

### Cache Strategy
1. **Multi-level caching**:
   - Redis for frequent queries
   - CDN for static assets
   - Browser cache for UI assets

## Monitoring & Alerting

### Key Metrics to Monitor
1. **Application Health**
   - Response time (p95 < 2s)
   - Error rate (< 1%)
   - Uptime (> 99.5%)

2. **Resource Usage**
   - CPU/Memory utilization
   - Database connections
   - Cache hit rate

3. **Business Metrics**
   - Documents processed per day
   - Active users
   - API usage per user

### Alert Configuration
```python
# Alert thresholds
ALERT_THRESHOLDS = {
    "error_rate": 0.05,  # 5% errors
    "response_time": 5000,  # 5 seconds
    "cpu_usage": 0.8,  # 80% CPU
    "memory_usage": 0.9,  # 90% memory
}
```

## Rollback Procedures

### Frontend Rollback
```bash
# Vercel rollback to previous deployment
vercel rollback <deployment-id>
```

### Backend Rollback
```bash
# Railway rollback
railway logs --deployment <previous-deployment-id>
railway rollback <deployment-id>
```

### Database Rollback
```bash
# Revert last migration
alembic downgrade -1

# Or restore from backup
psql $DATABASE_URL < backup.sql
```

## Conclusion

This deployment strategy provides a robust, scalable, and cost-effective foundation for the Research Synthesis Service MVP. By leveraging managed services and following best practices, we can achieve:

1. **Quick deployment** (1-2 days for initial setup)
2. **Reliable operation** with monitoring and alerting
3. **Cost control** through optimization and monitoring
4. **Easy scaling** as user base grows

The modular architecture allows for incremental improvements and technology swaps as needed, ensuring the platform can evolve with user needs.
