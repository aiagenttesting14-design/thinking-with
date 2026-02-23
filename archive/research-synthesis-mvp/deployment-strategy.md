# Deployment Strategy

## Overview
This document outlines the deployment strategy for the Research Synthesis Service, focusing on cloud-native, scalable, and cost-effective approaches.

## Target Environments

### 1. Development Environment
- **Purpose**: Local development and testing
- **Location**: Developer machines
- **Tools**: Docker Compose, local databases
- **Cost**: Minimal (free tiers/local resources)

### 2. Staging Environment
- **Purpose**: Integration testing and pre-production validation
- **Location**: Cloud (same region as production)
- **Tools**: Managed services with smaller scale
- **Cost**: Low (10-20% of production)

### 3. Production Environment
- **Purpose**: Live user traffic
- **Location**: Multi-region cloud deployment
- **Tools**: Fully managed, auto-scaling services
- **Cost**: Variable based on usage

## Cloud Provider Options

### Option A: AWS (Comprehensive)
**Pros**: Full feature set, mature ecosystem, global presence
**Cons**: Higher complexity, can be expensive

**Services**:
- **Compute**: ECS/EKS or Lambda
- **Database**: RDS PostgreSQL with pgvector
- **Storage**: S3
- **Queue**: SQS + Lambda
- **CDN**: CloudFront
- **Monitoring**: CloudWatch, X-Ray

### Option B: Railway/Render (Simplified)
**Pros**: Easy deployment, good for startups, simpler pricing
**Cons**: Less control, potential vendor lock-in

**Services**:
- **Compute**: Railway services
- **Database**: Railway PostgreSQL
- **Storage**: Railway volumes or Cloudflare R2
- **Queue**: Redis on Railway
- **CDN**: Built-in

### Option C: Hybrid Approach
**Pros**: Balance of control and simplicity, cost optimization
**Cons**: More complex management

**Services**:
- **Compute**: Railway/Render for web services
- **Database**: Supabase (PostgreSQL + pgvector)
- **Storage**: Cloudflare R2 (cheaper than S3)
- **Queue**: Upstash Redis
- **CDN**: Cloudflare
- **AI**: Direct to OpenAI/Anthropic

## Recommended Deployment: Hybrid Approach

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                     Cloudflare CDN                          │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐   │
│  │   Static    │  │     API     │  │   WebSocket       │   │
│  │   Assets    │  │   Proxy     │  │   Proxy           │   │
│  └─────────────┘  └─────────────┘  └───────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐   │
│  │   Next.js   │  │   FastAPI   │  │   Worker          │   │
│  │   (Vercel)  │  │  (Railway)  │  │   (Railway)       │   │
│  └─────────────┘  └─────────────┘  └───────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐   │
│  │  Supabase   │  │ Cloudflare  │  │    Upstash        │   │
│  │ PostgreSQL  │  │     R2      │  │     Redis         │   │
│  │  +pgvector  │  │             │  │                   │   │
│  └─────────────┘  └─────────────┘  └───────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Service Configuration

#### 1. Frontend (Next.js) - Vercel
```json
// vercel.json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["iad1"],  // Virginia
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.research-synthesis.com",
    "NEXT_PUBLIC_WS_URL": "wss://api.research-synthesis.com/ws"
  }
}
```

#### 2. Backend API (FastAPI) - Railway
```yaml
# railway.toml
[service]
name = "research-synthesis-api"
runtime = "python"
startCommand = "uvicorn main:app --host 0.0.0.0 --port ${PORT}"

[service.healthcheck]
path = "/health"
initialDelay = 30
interval = 30
timeout = 10

[variables]
DATABASE_URL = "${SUPABASE_DB_URL}"
REDIS_URL = "${UPSTASH_REDIS_URL}"
STORAGE_TYPE = "r2"
CLOUDFLARE_R2_ACCESS_KEY_ID = "${R2_ACCESS_KEY_ID}"
CLOUDFLARE_R2_SECRET_ACCESS_KEY = "${R2_SECRET_ACCESS_KEY}"
R2_BUCKET_NAME = "research-synthesis"
OPENAI_API_KEY = "${OPENAI_API_KEY}"

[deploy]
regions = ["us-east"]
```

#### 3. Worker Service - Railway
```yaml
# worker.toml
[service]
name = "research-synthesis-worker"
runtime = "python"
startCommand = "python worker.py"

[variables]
DATABASE_URL = "${SUPABASE_DB_URL}"
REDIS_URL = "${UPSTASH_REDIS_URL}"
OPENAI_API_KEY = "${OPENAI_API_KEY}"
ANTHROPIC_API_KEY = "${ANTHROPIC_API_KEY}"

[deploy]
regions = ["us-east"]
```

#### 4. Database - Supabase
- **Plan**: Pro plan ($25/month)
- **Features**:
  - PostgreSQL 15+
  - pgvector extension enabled
  - 8GB RAM, 2 vCPU
  - 50GB storage
  - Automated backups
  - Point-in-time recovery

#### 5. Object Storage - Cloudflare R2
- **Plan**: Pay-as-you-go
- **Features**:
  - S3-compatible API
  - No egress fees
  - Automatic migration from S3
  - 10GB free tier

#### 6. Redis - Upstash
- **Plan**: Free tier (10,000 commands/day)
- **Features**:
  - Serverless Redis
  - Global replication
  - REST API access
  - Automatic backups

## Deployment Pipeline

### CI/CD with GitHub Actions
```yaml
name: Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --build --exit-code-from test

  deploy-staging:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Staging
        run: |
          # Deploy API to Railway
          railway up --service api --environment staging
          
          # Deploy Worker to Railway
          railway up --service worker --environment staging
          
          # Deploy Frontend to Vercel
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Run production tests
        run: |
          # Run integration tests against staging
          npm run test:integration
      
      - name: Deploy to Production
        run: |
          # Promote staging to production
          railway promote --service api --environment production
          railway promote --service worker --environment production
          
          # Deploy frontend to production
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }} --confirm
```

### Environment Promotion Flow
```
Development → Staging → Production
    ↓           ↓          ↓
   Local     Automated   Manual
   Testing     Tests     Approval
```

## Database Migration Strategy

### 1. Schema Changes
```bash
# Create migration
alembic revision --autogenerate -m "add_user_preferences"

# Review migration file
# Apply to staging
alembic upgrade head

# Test in staging
# Apply to production during maintenance window
alembic upgrade head
```

### 2. Data Migrations
```python
# Use separate migration scripts for data changes
def migrate_user_data():
    # Back up first
    backup_database()
    
    # Run migration in transactions
    with transaction.atomic():
        migrate_users()
        migrate_documents()
    
    # Verify migration
    verify_data_integrity()
```

## Monitoring & Observability

### 1. Application Monitoring
- **Vercel Analytics**: Frontend performance
- **Railway Metrics**: Backend performance
- **Sentry**: Error tracking
- **Logtail**: Centralized logging

### 2. Infrastructure Monitoring
- **Supabase Dashboard**: Database performance
- **Cloudflare Analytics**: CDN and storage metrics
- **Upstash Metrics**: Redis performance

### 3. Business Metrics
- **PostHog**: User analytics
- **Stripe**: Revenue tracking
- **Custom Dashboard**: Key business metrics

## Disaster Recovery

### Backup Strategy
```yaml
backup:
  database:
    frequency: hourly
    retention: 7 days
    location: Supabase backups + S3
  
  storage:
    frequency: daily
    retention: 30 days
    location: R2 versioning + S3
  
  configuration:
    frequency: on-change
    retention: forever
    location: GitHub + 1Password
```

### Recovery Procedures

#### Database Recovery
```bash
# 1. Identify backup point
# 2. Restore from Supabase dashboard or CLI
supabase db restore --backup-id <id>

# 3. Verify data integrity
python verify_database.py
```

#### Application Recovery
```bash
# 1. Redeploy from last known good version
git checkout <last-good-commit>
railway up --service api --environment production

# 2. Roll forward migrations if needed
alembic upgrade head
```

## Scaling Strategy

### Horizontal Scaling
```yaml
scaling:
  api:
    min_instances: 2
    max_instances: 10
    metrics:
      - cpu: 70%
      - memory: 80%
      - requests: 1000/min
  
  worker:
    min_instances: 1
    max_instances: 5
    metrics:
      - queue_length: 100
      - processing_time: 30s
```

### Database Scaling
1. **Vertical Scaling**: Upgrade Supabase plan
2. **Read Replicas**: Add for read-heavy workloads
3. **Sharding**: By user or document type (future)

### Storage Scaling
- R2 automatically scales
- Implement lifecycle policies for old data
- Use CDN for frequently accessed files

## Cost Management

### Monthly Cost Estimate
| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Vercel | Pro | $20 |
| Railway | Standard | $50 |
| Supabase | Pro | $25 |
| Cloudflare R2 | Pay-as-you-go | $5-10 |
| Upstash Redis | Free | $0 |
| OpenAI API | Variable | $50-200 |
| **Total** | | **$150-305** |

### Cost Optimization
1. **Cache aggressively**: Reduce AI API calls
2. **Use smaller models**: GPT-3.5 for simple tasks
3. **Implement usage limits**: Per-user quotas
4. **Monitor spending**: Daily cost alerts
5. **Reserved instances**: If using AWS directly

## Security Considerations

### 1. Network Security
- HTTPS everywhere (automatic with Vercel/Railway)
- API key rotation (90 days)
- IP allowlisting for admin endpoints
- DDoS protection (Cloudflare)

### 2. Data Security
- Encryption at rest (Supabase, R2)
- Encryption in transit (TLS 1.3)
- Secure API keys (environment variables)
- Regular security audits

### 3. Application Security
- Input validation and sanitization
- SQL injection prevention (ORM)
- XSS protection (React/Next.js)
- Rate limiting (Redis)
- JWT token validation

## Compliance

### GDPR Compliance
1. **Data Processing Agreement**: With all providers
2. **Right to Erasure**: Implement user data deletion
3. **Data Portability**: Export user data functionality
4. **Privacy Policy**: Clear and comprehensive

### SOC 2 Readiness
1. **Access Controls**: Role-based access
2. **Audit Logging**: All actions logged
3. **Change Management**: Documented procedures
4. **Incident Response**: Defined process

## Maintenance Schedule

### Daily
- Check system health
- Review error logs
- Monitor costs
- Backup verification

### Weekly
- Security patch updates
- Performance review
- User feedback analysis
- Capacity planning

### Monthly
- Full backup test
- Security audit
- Cost optimization review
- Feature planning

### Quarterly
- Disaster recovery test
- Compliance review
- Architecture review
- Roadmap planning

## Rollback Plan

### Conditions for Rollback
1. Error rate > 5% for 15 minutes
2. Critical feature broken
3. Performance degradation > 50%
4. Security vulnerability discovered

### Rollback Procedure
```bash
# 1. Stop traffic to new version
# 2. Revert to previous version
git revert <bad-commit>
# or
git checkout <previous-tag>

# 3. Redeploy
railway up --service api --environment production --detach

# 4. Verify rollback
curl https://api.research-synthesis.com/health
```

## Success Criteria

### Technical Success
- 99.9% uptime
- < 200ms API response time
- Zero data loss
- Successful disaster recovery tests

### Business Success
- User growth targets met
- Positive user feedback
- Cost within budget
- Feature adoption targets met

### Operational Success
- Automated deployments working
- Monitoring alerts effective
- Team able to maintain system
- Documentation complete and useful
