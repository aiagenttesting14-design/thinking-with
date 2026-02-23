# Technical Specification - Research Synthesis Service

## Data Models

### Document Model
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"

class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    authors: List[str] = []
    publication_date: Optional[datetime] = None
    source_url: Optional[str] = None
    file_type: str
    file_size: int
    page_count: Optional[int] = None
    language: str = "en"
    keywords: List[str] = []

class DocumentChunk(BaseModel):
    id: str
    document_id: str
    content: str
    chunk_index: int
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = {}

class Document(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    status: DocumentStatus
    metadata: DocumentMetadata
    chunks: List[DocumentChunk] = []
    summary: Optional[str] = None
    entities: List[Dict] = []
    concepts: List[Dict] = []
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
```

### Project Model
```python
class Project(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    documents: List[str] = []  # Document IDs
    synthesis: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
```

## Database Schema

### PostgreSQL Tables

```sql
-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'uploaded',
    metadata JSONB NOT NULL DEFAULT '{}',
    summary TEXT,
    entities JSONB DEFAULT '[]',
    concepts JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Document chunks table with pgvector support
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding VECTOR(1536),  -- OpenAI embedding dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    synthesis JSONB,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Project documents junction table
CREATE TABLE project_documents (
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (project_id, document_id)
);

-- Users table (simplified)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    api_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_projects_user_id ON projects(user_id);
```

## API Implementation Examples

### FastAPI Application Structure

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import uuid

from models import Document, DocumentCreate, DocumentUpdate, Project, ProjectCreate
from services import DocumentService, ProcessingService, SynthesisService
from auth import get_current_user

app = FastAPI(
    title="Research Synthesis API",
    description="API for research document processing and synthesis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
document_service = DocumentService()
processing_service = ProcessingService()
synthesis_service = SynthesisService()

# Authentication
security = HTTPBearer()

@app.post("/api/v1/documents/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload a document for processing"""
    user = await get_current_user(credentials.credentials)
    
    # Save file temporarily
    file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create document
    document = await document_service.create_document(
        user_id=user.id,
        file_path=file_path,
        title=title or file.filename,
        file_type=file.content_type
    )
    
    # Trigger async processing
    await processing_service.process_document(document.id)
    
    return document

@app.get("/api/v1/documents/{document_id}/summary")
async def get_document_summary(
    document_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get the summary of a processed document"""
    user = await get_current_user(credentials.credentials)
    
    document = await document_service.get_document(document_id, user.id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != "processed":
        raise HTTPException(status_code=400, detail="Document not yet processed")
    
    return {
        "summary": document.summary,
        "entities": document.entities,
        "concepts": document.concepts
    }

@app.post("/api/v1/synthesis/compare")
async def compare_documents(
    document_ids: List[str],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Compare multiple documents and generate synthesis"""
    user = await get_current_user(credentials.credentials)
    
    # Verify user has access to all documents
    documents = []
    for doc_id in document_ids:
        doc = await document_service.get_document(doc_id, user.id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        if doc.status != "processed":
            raise HTTPException(status_code=400, detail=f"Document {doc_id} not processed")
        documents.append(doc)
    
    # Generate synthesis
    synthesis = await synthesis_service.compare_documents(documents)
    
    return synthesis

@app.post("/api/v1/synthesis/qa")
async def ask_question(
    document_ids: List[str],
    question: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Ask a question about one or more documents"""
    user = await get_current_user(credentials.credentials)
    
    # Verify access and get documents
    documents = []
    for doc_id in document_ids:
        doc = await document_service.get_document(doc_id, user.id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        documents.append(doc)
    
    # Get answer using RAG
    answer = await synthesis_service.answer_question(documents, question)
    
    return answer
```

## Processing Service Implementation

```python
# services/processing.py
import asyncio
from typing import List, Optional
import logging
from models import Document, DocumentChunk
from ai_providers import OpenAIService, EmbeddingService

logger = logging.getLogger(__name__)

class ProcessingService:
    def __init__(self):
        self.openai = OpenAIService()
        self.embedding_service = EmbeddingService()
        self.chunk_size = 1000  # tokens
        self.chunk_overlap = 100  # tokens
    
    async def process_document(self, document_id: str):
        """Process a document through the full pipeline"""
        try:
            # 1. Get document from database
            document = await self._get_document(document_id)
            
            # 2. Update status to processing
            await self._update_document_status(document_id, "processing")
            
            # 3. Chunk the document
            chunks = await self._chunk_document(document)
            
            # 4. Generate embeddings for chunks
            chunks_with_embeddings = await self._generate_embeddings(chunks)
            
            # 5. Store chunks in vector database
            await self._store_chunks(document_id, chunks_with_embeddings)
            
            # 6. Generate document summary
            summary = await self._generate_summary(document, chunks)
            
            # 7. Extract entities and concepts
            entities = await self._extract_entities(document, chunks)
            concepts = await self._extract_concepts(document, chunks)
            
            # 8. Update document with results
            await self._update_document_results(
                document_id, summary, entities, concepts, "processed"
            )
            
            logger.info(f"Successfully processed document {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {e}")
            await self._update_document_status(document_id, "failed")
            raise
    
    async def _chunk_document(self, document: Document) -> List[DocumentChunk]:
        """Split document into manageable chunks"""
        chunks = []
        content = document.content
        
        # Simple chunking by paragraphs first
        paragraphs = content.split('\n\n')
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > self.chunk_size:
                # Save current chunk
                if current_chunk:
                    chunks.append(DocumentChunk(
                        document_id=document.id,
                        content=current_chunk.strip(),
                        chunk_index=chunk_index
                    ))
                    chunk_index += 1
                    current_chunk = para + "\n\n"
                else:
                    # Single paragraph is too long, split by sentences
                    sentences = para.split('. ')
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) > self.chunk_size:
                            if current_chunk:
                                chunks.append(DocumentChunk(
                                    document_id=document.id,
                                    content=current_chunk.strip(),
                                    chunk_index=chunk_index
                                ))
                                chunk_index += 1
                            current_chunk = sentence + ". "
                        else:
                            current_chunk += sentence + ". "
            else:
                current_chunk += para + "\n\n"
        
        # Add the last chunk
        if current_chunk:
            chunks.append(DocumentChunk(
                document_id=document.id,
                content=current_chunk.strip(),
                chunk_index=chunk_index
            ))
        
        return chunks
    
    async def _generate_embeddings(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Generate embeddings for document chunks"""
        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = await self.embedding_service.embed_batch(chunk_texts)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
        
        return chunks
    
    async def _generate_summary(self, document: Document, chunks: List[DocumentChunk]) -> str:
        """Generate a summary of the document"""
        # First, generate summaries for each chunk
        chunk_summaries = []
        for chunk in chunks:
            summary = await self.openai.summarize_text(chunk.content)
            chunk_summaries.append(summary)
        
        # Combine chunk summaries into document summary
        combined_summaries = "\n\n".join(chunk_summaries)
        document_summary = await self.openai.summarize_text(
            combined_summaries,
            instruction="Create a comprehensive summary of this research document"
        )
        
        return document_summary
    
    async def _extract_entities(self, document: Document, chunks: List[DocumentChunk]) -> List[Dict]:
        """Extract entities from document"""
        entities = []
        
        for chunk in chunks:
            chunk_entities = await self.openai.extract_entities(chunk.content)
            entities.extend(chunk_entities)
        
        # Deduplicate and consolidate entities
        unique_entities = {}
        for entity in entities:
            key = f"{entity['type']}:{entity['text'].lower()}"
            if key not in unique_entities:
                unique_entities[key] = entity
            else:
                # Merge occurrences
                unique_entities[key]['count'] = unique_entities[key].get('count', 1) + 1
        
        return list(unique_entities.values())
    
    async def _extract_concepts(self, document: Document, chunks: List[DocumentChunk]) -> List[Dict]:
        """Extract key concepts from document"""
        concepts = []
        
        for chunk in chunks:
            chunk_concepts = await self.openai.extract_concepts(chunk.content)
            concepts.extend(chunk_concepts)
        
        # Rank concepts by frequency and relevance
        concept_scores = {}
        for concept in concepts:
            text = concept['text'].lower()
            if text not in concept_scores:
                concept_scores[text] = {
                    'text': concept['text'],
                    'score': concept.get('score', 1),
                    'count': 1
                }
            else:
                concept_scores[text]['count'] += 1
                concept_scores[text]['score'] += concept.get('score', 1)
        
        # Sort by score and return top concepts
        sorted_concepts = sorted(
            concept_scores.values(),
            key=lambda x: x['score'] * x['count'],
            reverse=True
        )
        
        return sorted_concepts[:20]  # Return top 20 concepts
```

## Frontend Implementation Examples

### React Component for Document Upload

```tsx
// components/upload/FileUpload.tsx
import React, { useState } from 'react';
import {
  Box,
  Button,
  VStack,
  Text,
  Progress,
  useToast,
} from '@chakra-ui/react';
import { useDropzone } from 'react-dropzone';
import { uploadDocument } from '../../api/documents';

interface FileUploadProps {
  onUploadComplete?: (documentId: string) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const toast = useToast();

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    multiple: false,
    onDrop: async (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        await handleUpload(acceptedFiles[0]);
      }
    },
  });

  const handleUpload = async (file: File) => {
    setUploading(true);
    setProgress(0);
    
    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 300);

      const formData = new FormData();
      formData.append('file', file);
      
      const response = await uploadDocument(formData, (progressEvent) => {
        if (progressEvent.total) {
          const percent = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setProgress(percent);
        }
      });

      clearInterval(progressInterval);
      setProgress(100);

      toast({
        title: 'Upload successful',
        description: 'Document is being processed',
        status: 'success',
        duration: 5000,
      });

      if (onUploadComplete) {
        onUploadComplete(response.data.id);
      }
    } catch (error) {
      toast({
        title: 'Upload failed',
        description: error.message,
        status: 'error',
        duration: 5000,
      });
    } finally {
      setUploading(false);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  return (
    <Box
      {...getRootProps()}
      border="2px dashed"
      borderColor={isDragActive ? 'blue.500' : 'gray.300'}
      borderRadius="lg"
      p={8}
      textAlign="center"
      cursor="pointer"
      transition="all 0.2s"
      _hover={{ borderColor: 'blue.400', bg: 'gray.50' }}
    >
      <input {...getInputProps()} />
      
      <VStack spacing={4}>
        {uploading ? (
          <>
            <Text>Uploading document...</Text>
            <Progress
              value={progress}
              width="100%"
              colorScheme="blue"
              borderRadius="full"
            />
            <Text fontSize="sm">{progress}%</Text>
          </>
        ) : (
          <>
            <Text fontSize="lg" fontWeight="medium">
              {isDragActive
                ? 'Drop the file here'
                : 'Drag & drop a document here'}
            </            <Text>
              or
            </Text>
            <Button colorScheme="blue">
              Browse files
            </Button>
          </>
        )}
        
        <Text fontSize="sm" color="gray.600">
          Supported formats: PDF, TXT, MD (Max 50MB)
        </Text>
      </VStack>
    </Box>
  );
};

export default FileUpload;
```

### Document Viewer Component

```tsx
// components/documents/DocumentViewer.tsx
import React, { useState } from 'react';
import {
  Box,
  Grid,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  VStack,
  Text,
  Badge,
  Heading,
} from '@chakra-ui/react';
import { Document } from '../../types';
import EntityGraph from '../synthesis/EntityGraph';
import QAPanel from '../synthesis/QAPanel';

interface DocumentViewerProps {
  document: Document;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ document }) => {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <Box height="100vh" p={4}>
      <VStack spacing={4} align="stretch">
        <Heading size="lg">{document.title}</Heading>
        
        <Box>
          <Badge colorScheme="green" mr={2}>
            {document.status}
          </Badge>
          <Badge colorScheme="blue" mr={2}>
            {document.metadata.file_type}
          </Badge>
          {document.metadata.page_count && (
            <Badge colorScheme="purple">
              {document.metadata.page_count} pages
            </Badge>
          )}
        </Box>

        <Tabs
          variant="enclosed"
          onChange={(index) => setActiveTab(index)}
          colorScheme="blue"
        >
          <TabList>
            <Tab>Summary</Tab>
            <Tab>Original Text</Tab>
            <Tab>Entities</Tab>
            <Tab>Concepts</Tab>
            <Tab>Q&A</Tab>
          </TabList>

          <TabPanels>
            <TabPanel>
              <Box
                p={4}
                borderWidth="1px"
                borderRadius="lg"
                bg="white"
                maxHeight="70vh"
                overflowY="auto"
              >
                <Text whiteSpace="pre-wrap">{document.summary}</Text>
              </Box>
            </TabPanel>

            <TabPanel>
              <Grid templateColumns="1fr 1fr" gap={6}>
                <Box
                  p={4}
                  borderWidth="1px"
                  borderRadius="lg"
                  bg="gray.50"
                  maxHeight="70vh"
                  overflowY="auto"
                >
                  <Text whiteSpace="pre-wrap" fontFamily="mono" fontSize="sm">
                    {document.content}
                  </Text>
                </Box>
                <Box
                  p={4}
                  borderWidth="1px"
                  borderRadius="lg"
                  bg="blue.50"
                  maxHeight="70vh"
                  overflowY="auto"
                >
                  <Text fontWeight="bold" mb={2}>AI Insights</Text>
                  <Text fontSize="sm">
                    Key insights and annotations will appear here as you read
                  </Text>
                </Box>
              </Grid>
            </TabPanel>

            <TabPanel>
              <EntityGraph entities={document.entities} />
            </TabPanel>

            <TabPanel>
              <Box
                p={4}
                borderWidth="1px"
                borderRadius="lg"
                bg="white"
                maxHeight="70vh"
                overflowY="auto"
              >
                <VStack align="stretch" spacing={3}>
                  {document.concepts.map((concept, index) => (
                    <Box
                      key={index}
                      p={3}
                      borderWidth="1px"
                      borderRadius="md"
                      bg="purple.50"
                    >
                      <Text fontWeight="bold">{concept.text}</Text>
                      <Text fontSize="sm" color="gray.600">
                        Relevance: {concept.score.toFixed(2)}
                      </Text>
                    </Box>
                  ))}
                </VStack>
              </Box>
            </TabPanel>

            <TabPanel>
              <QAPanel documentId={document.id} />
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>
    </Box>
  );
};

export default DocumentViewer;
```

## Deployment Configuration

### Docker Compose for Development

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: research_dev
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dev_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/readyz"]
      interval: 30s
      timeout: 10s
      retries: 3

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://dev_user:dev_password@postgres:5432/research_dev
      REDIS_URL: redis://redis:6379/0
      QDRANT_URL: http://qdrant:6333
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ENVIRONMENT: development
      CORS_ORIGINS: http://localhost:3000
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_healthy
    command: >
      sh -c "alembic upgrade head &&
             uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000/api/v1
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - api

  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    environment:
      DATABASE_URL: postgresql://dev_user:dev_password@postgres:5432/research_dev
      REDIS_URL: redis://redis:6379/0
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
    depends_on:
      - api
      - redis
    command: celery -A worker.celery_app worker --loglevel=info

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    environment:
      DATABASE_URL: postgresql://dev_user:dev_password@postgres:5432/research_dev
      REDIS_URL: redis://redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      - api
      - redis
    command: celery -A worker.celery_app beat --loglevel=info

volumes:
  postgres_data:
  qdrant_data:
```

### Production Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p uploads logs

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: research-api
  namespace: research
spec:
  replicas: 3
  selector:
    matchLabels:
      app: research-api
  template:
    metadata:
      labels:
        app: research-api
    spec:
      containers:
      - name: api
        image: research-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: research-secrets
              key: database-url
        - name: REDIS_URL
          value: redis://research-redis:6379/0
        - name: QDRANT_URL
          value: http://research-qdrant:6333
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: research-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: uploads
          mountPath: /app/uploads
      volumes:
      - name: uploads
        persistentVolumeClaim:
          claimName: uploads-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: research-api
  namespace: research
spec:
  selector:
    app: research-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

## Environment Configuration

```bash
# .env.example
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/research_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=20

# Vector Store
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=research_documents
EMBEDDING_DIMENSION=1536

# AI Providers
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-opus-20240229

GOOGLE_AI_API_KEY=...
GOOGLE_AI_MODEL=gemini-pro

# Application
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=52428800  # 50MB

# Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
MAX_CONCURRENT_PROCESSING=5

# Monitoring
SENTRY_DSN=...
LOGGING_LEVEL=INFO
```

## Testing Strategy

### Unit Tests
```python
# tests/test_processing.py
import pytest
from unittest.mock import AsyncMock, patch
from services.processing import ProcessingService
from models import Document

@pytest.mark.asyncio
async def test_chunk_document():
    service = ProcessingService()
    
    document = Document(
        id="test-id",
        user_id="user-1",
        title="Test Document",
        content="This is a test document. " * 100,  # 2000+ chars
        status="uploaded",
        metadata={}
    )
    
    chunks = await service._chunk_document(document)
    
    assert len(chunks) > 1
    assert all(len(chunk.content) <= 1500 for chunk in chunks)
    assert chunks[0].chunk_index == 0

@pytest.mark.asyncio
async def test_generate_summary():
    service = ProcessingService()
    
    with patch.object(service.openai, 'summarize_text') as mock_summarize:
        mock_summarize.return_value = "Test summary"
        
        document = Document(id="test", user_id="user", title="Test", content="Content", status="uploaded", metadata={})
        chunks = [DocumentChunk(document_id="test", content="Chunk 1", chunk_index=0)]
        
        summary = await service._generate_summary(document, chunks)
        
        assert summary == "Test summary"
        assert mock_summarize.call_count == 2  # Once per chunk, once for combined
```

### Integration Tests
```python
# tests/integration/test_api.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_upload_document():
    async with AsyncClient(app=app, base_url="http://test") as client:
        files = {'file': ('test.pdf', b'PDF content', 'application/pdf')}
        headers = {'Authorization': 'Bearer test-token'}
        
        response = await client.post("/api/v1/documents/upload", files=files, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert data['title'] == 'test.pdf'
```

### Performance Tests
```python
# tests/performance/test_processing_performance.py
import pytest
import asyncio
from datetime import datetime
from services.processing import ProcessingService

@pytest.mark.performance
@pytest.mark.asyncio
async def test_processing_large_document():
    """Test processing performance with a large document"""
    service = ProcessingService()
    
    # Create a large document (approx 50 pages)
    content = "This is a test paragraph. " * 10000
    
    document = Document(
        id="perf-test",
        user_id="user-1",
        title="Performance Test Document",
        content=content,
        status="uploaded",
        metadata={}
    )
    
    start_time = datetime.now()
    
    # Run processing
    await service.process_document(document.id)
    
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    # Should complete within 2 minutes
    assert processing_time < 120
    
    print(f"Processing time: {processing_time:.2f} seconds")
```

## Security Considerations

### 1. Authentication & Authorization
- JWT tokens with short expiration (1 hour)
- Refresh token mechanism
- Role-based access control (RBAC)
- API key authentication for programmatic access

### 2. Input Validation
- File type validation (whitelist approach)
- File size limits
- Content sanitization
- SQL injection prevention (ORM parameterized queries)

### 3. Data Protection
- Encryption at rest for sensitive data
- Secure file upload handling
- Regular security audits
- Vulnerability scanning in CI/CD

### 4. API Security
- Rate limiting per user/IP
- CORS configuration
- HTTPS enforcement
- Security headers (HSTS, CSP)

## Monitoring & Observability

### Logging Configuration
```python
# logging_config.py
import logging
import json
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # JSON formatter for structured logging
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler for errors
    file_handler = logging.FileHandler('logs/error.log')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
```

### Metrics Collection
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
DOCUMENTS_PROCESSED = Counter(
    'documents_processed_total',
    'Total number of documents processed',
    ['status']
)

PROCESSING_DURATION = Histogram(
