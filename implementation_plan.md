# Implementation Plan - Week by Week

## Week 1: Project Setup & Foundation

### Day 1-2: Environment Setup
```bash
# Create project structure
mkdir research-synthesis
cd research-synthesis
mkdir -p frontend backend worker scripts docker

# Initialize repositories
git init
echo "# Research Synthesis Service" > README.md

# Create Docker setup
cat > docker-compose.yml << 'DOCKER'
version: '3.8'
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: research
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

volumes:
  postgres_data:
  minio_data:
DOCKER
```

### Day 3-4: Backend Foundation
```python
# backend/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
python-multipart==0.0.6
redis==5.0.1
boto3==1.34.0
openai==1.3.0
langchain==0.0.340
pdfplumber==0.10.3
beautifulsoup4==4.12.2
requests==2.31.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

### Day 5: Database Schema
```sql
-- backend/alembic/versions/initial_schema.sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    source_type VARCHAR(50), -- 'pdf', 'webpage', 'text'
    source_url TEXT,
    file_path TEXT,
    content_hash VARCHAR(64),
    metadata JSONB,
    processing_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    content TEXT,
    embedding vector(1536), -- OpenAI embedding dimension
    metadata JSONB
);

CREATE INDEX idx_document_chunks_embedding ON document_chunks 
USING ivfflat (embedding vector_cosine_ops);
```

## Week 2: Core Processing Pipeline

### Day 1-2: Document Processing Service
```python
# backend/services/document_processor.py
import pdfplumber
from bs4 import BeautifulSoup
import requests
from typing import Optional, Dict, Any
import hashlib

class DocumentProcessor:
    def __init__(self, storage_service, ai_service):
        self.storage = storage_service
        self.ai = ai_service
    
    async def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text and metadata from PDF"""
        text = ""
        metadata = {}
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            
            if pdf.metadata:
                metadata = dict(pdf.metadata)
        
        return {
            "content": text,
            "metadata": metadata,
            "page_count": len(pdf.pages)
        }
    
    async def process_webpage(self, url: str) -> Dict[str, Any]:
        """Fetch and extract content from webpage"""
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get title
        title = soup.title.string if soup.title else ""
        
        # Try to get main content
        article = soup.find('article') or soup.find('main') or soup.body
        
        return {
            "content": article.get_text(separator='\n', strip=True),
            "metadata": {
                "title": title,
                "url": url,
                "content_type": response.headers.get('content-type', '')
            }
        }
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content for deduplication"""
        return hashlib.sha256(content.encode()).hexdigest()
```

### Day 3-4: AI Integration Service
```python
# backend/services/ai_service.py
from openai import OpenAI
from typing import List, Dict, Any
import os

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def generate_summary(self, text: str, max_length: int = 500) -> str:
        """Generate concise summary of text"""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a research assistant. Provide a concise summary highlighting key points."},
                {"role": "user", "content": f"Summarize this text in {max_length} words or less:\n\n{text}"}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content
    
    async def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text"""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Extract entities from the text. Return as JSON with keys: people, organizations, concepts, dates."},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
```

### Day 5: Worker Service Setup
```python
# worker/main.py
import redis
import json
from rq import Queue
from services.document_processor import DocumentProcessor
from services.ai_service import AIService

# Setup Redis queue
redis_conn = redis.Redis(host='localhost', port=6379, db=0)
queue = Queue('default', connection=redis_conn)

def process_document_task(document_id: str):
    """Background task to process a document"""
    # Initialize services
    ai_service = AIService()
    processor = DocumentProcessor(ai_service)
    
    # Fetch document from database
    # Process document
    # Store results
    # Update status
    
    return {"status": "completed", "document_id": document_id}
```

## Week 3: API Development

### Day 1-2: FastAPI Application Structure
```python
# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid

app = FastAPI(title="Research Synthesis API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/documents")
async def upload_document(
    file: UploadFile = File(...),
    source_type: str = "pdf"
):
    """Upload a document for processing"""
    document_id = str(uuid.uuid4())
    
    # Save file temporarily
    file_path = f"/tmp/{document_id}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Queue processing task
    from worker.main import queue
    queue.enqueue('worker.main.process_document_task', document_id)
    
    return {
        "id": document_id,
        "status": "queued",
        "message": "Document uploaded and queued for processing"
    }

@app.get("/api/v1/documents/{document_id}")
async def get_document(document_id: str):
    """Get document details and processing status"""
    # Fetch from database
    return {
        "id": document_id,
        "status": "processing",
        "summary": "Document summary will appear here..."
    }

@app.post("/api/v1/syntheses")
async def create_synthesis(
    title: str,
    description: str,
    document_ids: List[str]
):
    """Create a new synthesis from multiple documents"""
    synthesis_id = str(uuid.uuid4())
    
    # Start synthesis process
    return {
        "id": synthesis_id,
        "title": title,
        "status": "processing"
    }
```

### Day 3-4: Authentication & Authorization
```python
# backend/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Fetch user from database
    return {"id": user_id, "email": "user@example.com"}
```

### Day 5: Search Endpoints
```python
# backend/search.py
from fastapi import APIRouter, Depends
from typing import List
import numpy as np

router = APIRouter(prefix="/api/v1/search", tags=["search"])

@router.post("/semantic")
async def semantic_search(
    query: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Semantic search across documents"""
    # Generate embedding for query
    from services.ai_service import AIService
    ai_service = AIService()
    query_embedding = await ai_service.generate_embedding(query)
    
    # Search in database using vector similarity
    # This would use pgvector's cosine similarity search
    
    return {
        "query": query,
        "results": [
            {
                "document_id": "doc_123",
                "title": "Sample Document",
                "similarity": 0.85,
                "excerpt": "Relevant text excerpt..."
            }
        ]
    }
```

## Week 4: Frontend Development

### Day 1-2: Next.js Setup
```bash
# Create Next.js app
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend

# Install dependencies
npm install @tanstack/react-query axios react-hook-form @hookform/resolvers zod
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install lucide-react date-fns
```

### Day 3-4: Document Upload Component
```tsx
// frontend/components/DocumentUpload.tsx
'use client';

import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Globe, Loader2 } from 'lucide-react';

export function DocumentUpload() {
  const [uploading, setUploading] = useState(false);
  const [uploadType, setUploadType] = useState<'file' | 'url'>('file');
  
  const onDrop = async (acceptedFiles: File[]) => {
    setUploading(true);
    const formData = new FormData();
    
    acceptedFiles.forEach(file => {
      formData.append('files', file);
    });
    
    try {
      const response = await fetch('/api/v1/documents', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        // Handle success
        console.log('Upload successful');
      }
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc', '.docx'],
    },
    multiple: true,
  });
  
  return (
    <div className="space-y-6">
      {/* Upload Type Selector */}
      <div className="flex space-x-4">
        <button
          onClick={() => setUploadType('file')}
          className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
            uploadType === 'file'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-700'
          }`}
        >
          <FileText size={20} />
          <span>Upload Files</span>
        </button>
        
        <button
          onClick={() => setUploadType('url')}
          className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
            uploadType === 'url'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-700'
          }`}
        >
          <Globe size={20} />
          <span>Add URL</span>
        </button>
      </div>
      
      {/* Upload Area */}
      {uploadType === 'file' ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          
          <p className="mt-4 text-lg font-medium">
            {isDragActive
              ? 'Drop files here...'
              : 'Drag & drop files or click to browse'}
          </p>
          
          <p className="mt-2 text-sm text-gray-500">
            Supports PDF, DOCX, TXT files
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <input
            type="url"
            placeholder="https://example.com/research-paper"
            className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
            Add URL
          </button>
        </div>
      )}
      
      {/* Uploading State */}
      {uploading && (
        <div className="flex items-center justify-center space-x-2 text-blue-500">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Processing documents...</span>
        </div>
      )}
    </div>
  );
}
```

### Day 5: Document List Component
```tsx
// frontend/components/DocumentList.tsx
'use client';

import { useQuery } from '@tanstack/react-query';
import { FileText, CheckCircle, Clock, AlertCircle } from 'lucide-react';

async function fetchDocuments() {
  const response = await fetch('/api/v1/documents');
  if (!response.ok) throw new Error('Failed to fetch documents');
  return response.json();
}

export function DocumentList() {
  const { data: documents, isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: fetchDocuments,
  });
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'processing':
        return <Clock className="h-5 w-5 text-yellow-500 animate-pulse" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-700">Error loading documents: {error.message}</p>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Your Documents</h2>
      
      <div className="grid gap-4">
        {documents?.map((doc: any) => (
          <div
            key={doc.id}
            className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                <FileText className="h-6 w-6 text-gray-400 mt-1" />
                <div>
                  <h3 className="font-medium">{doc.title || 'Untitled Document'}</h3>
                  <p className="text-sm text-gray-500">
                    Uploaded {new Date(doc.created_at).toLocaleDateString()}
                  </p>
                  {doc.summary && (
                    <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                      {doc.summary}
                    </p>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {getStatusIcon(doc.status)}
                <span className="text-sm capitalize">{doc.status}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
