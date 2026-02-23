# Implementation Plan - Research Synthesis Service MVP

## Phase 1: Foundation (Week 1-2)

### Day 1-2: Project Setup & Basic Backend
```bash
# Create project structure
mkdir research-synthesis
cd research-synthesis
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-multipart pypdf2 pdfplumber beautifulsoup4 requests
```

**File: `backend/main.py`**
```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
import uuid

app = FastAPI(title="Research Synthesis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return {"file_id": file_id, "filename": file.filename, "status": "uploaded"}

@app.get("/")
async def root():
    return {"message": "Research Synthesis API"}
```

### Day 3-4: Document Processing
**File: `backend/processors/pdf_processor.py`**
```python
import pdfplumber
from typing import List, Dict
import re

class PDFProcessor:
    def extract_text(self, file_path: str) -> str:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text
    
    def clean_text(self, text: str) -> str:
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove headers/footers (simple heuristic)
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if len(line.strip()) > 20]
        return '\n'.join(cleaned_lines)
```

**File: `backend/processors/web_processor.py`**
```python
import requests
from bs4 import BeautifulSoup
import readability

class WebProcessor:
    def extract_content(self, url: str) -> Dict:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get title
            title = soup.title.string if soup.title else "No title"
            
            # Get main content (simple heuristic)
            main_content = soup.find('main') or soup.find('article') or soup.body
            text = main_content.get_text(separator='\n', strip=True)
            
            return {
                "title": title,
                "content": text,
                "url": url,
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
```

### Day 5-6: AI Integration
**File: `backend/ai/summarizer.py`**
```python
import openai
from typing import List
import tiktoken

class Summarizer:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))
    
    def chunk_text(self, text: str, max_tokens: int = 3000) -> List[str]:
        tokens = self.encoding.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
    
    def summarize(self, text: str, model: str = "gpt-3.5-turbo") -> str:
        prompt = f"""Please summarize the following text, focusing on:
        1. Main arguments or findings
        2. Key evidence or data points
        3. Conclusions or recommendations
        4. Any limitations mentioned

        Text:
        {text[:4000]}  # Limit input for demo
        
        Summary:"""
        
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a research assistant that creates concise, accurate summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating summary: {str(e)}"
```

### Day 7-10: Frontend Development
**File: `frontend/package.json`**
```json
{
  "name": "research-synthesis-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "tailwindcss": "^3.3.0",
    "@headlessui/react": "^1.7.0",
    "react-dropzone": "^14.2.0"
  },
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

**File: `frontend/pages/index.js`**
```jsx
import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

export default function Home() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [summary, setSummary] = useState('');
  
  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
    onDrop: (acceptedFiles) => {
      setFiles(acceptedFiles.map(file => ({
        ...file,
        preview: URL.createObjectURL(file)
      })));
    }
  });
  
  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', files[0]);
    
    try {
      const uploadRes = await axios.post('http://localhost:8000/upload', formData);
      const processRes = await axios.post(`http://localhost:8000/process/${uploadRes.data.file_id}`);
      setSummary(processRes.data.summary);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Research Synthesis Tool
        </h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div {...getRootProps()} className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition">
            <input {...getInputProps()} />
            <p className="text-gray-600">Drag & drop research documents here, or click to select</p>
            <p className="text-sm text-gray-500 mt-2">Supports PDF, TXT, and web URLs</p>
          </div>
          
          {files.length > 0 && (
            <div className="mt-6">
              <h3 className="font-medium text-gray-900 mb-2">Selected files:</h3>
              <ul className="space-y-2">
                {files.map(file => (
                  <li key={file.name} className="text-sm text-gray-600">
                    {file.name} ({(file.size / 1024).toFixed(1)} KB)
                  </li>
                ))}
              </ul>
              
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? 'Processing...' : 'Process Document'}
              </button>
            </div>
          )}
        </div>
        
        {summary && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Summary</h2>
            <div className="prose max-w-none">
              <p className="text-gray-700 whitespace-pre-line">{summary}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
```

## Phase 2: Core Features (Week 3-4)

### Day 11-12: Database Setup
**File: `backend/database/models.py`**
```python
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./research.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_type = Column(String)
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    summary = Column(Text, nullable=True)
    key_points = Column(Text, nullable=True)
    user_id = Column(String, nullable=True)
    
class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    
    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, index=True)
    status = Column(String)  # pending, processing, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
```

### Day 13-14: Vector Database Integration
**File: `backend/ai/embeddings.py`**
```python
import openai
import numpy as np
from typing import List
import pinecone

class EmbeddingService:
    def __init__(self, openai_key: str, pinecone_key: str = None):
        openai.api_key = openai_key
        self.pinecone_key = pinecone_key
        
        if pinecone_key:
            pinecone.init(api_key=pinecone_key, environment="us-east1-gcp")
    
    def create_embedding(self, text: str) -> List[float]:
        response = openai.Embedding.create(
            model="text-embedding-3-small",
            input=text
        )
        return response['data'][0]['embedding']
    
    def chunk_and_embed(self, text: str, chunk_size: int = 1000) -> List[dict]:
        # Simple chunking by sentences
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    embedding = self.create_embedding(current_chunk)
                    chunks.append({
                        "text": current_chunk,
                        "embedding": embedding
                    })
                current_chunk = sentence + ". "
        
        if current_chunk:
            embedding = self.create_embedding(current_chunk)
            chunks.append({
                "text": current_chunk,
                "embedding": embedding
            })
        
        return chunks
```

### Day 15-16: Key Point Extraction
**File: `backend/ai/keypoints.py`**
```python
import openai
import json
from typing import List, Dict

class KeyPointExtractor:
    def __init__(self, api_key: str):
        openai.api_key = api_key
    
    def extract_key_points(self, text: str) -> Dict:
        prompt = f"""Analyze the following text and extract key points in JSON format:
        
        Text:
        {text[:3000]}
        
        Return a JSON object with:
        1. main_arguments: List of main arguments or findings
        2. supporting_evidence: List of key evidence or data points
        3. conclusions: List of conclusions or recommendations
        4. limitations: List of limitations or caveats mentioned
        5. entities: Dictionary with people, organizations, dates mentioned
        
        JSON:"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You extract structured key points from research texts. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            # Extract JSON from response
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            json_str = result[json_start:json_end]
            
            return json.loads(json_str)
        except Exception as e:
            return {"error": str(e)}
```

### Day 17-20: Enhanced Frontend & Authentication
**File: `frontend/components/DocumentList.js`**
```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

export default function DocumentList() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchDocuments();
  }, []);
  
  const fetchDocuments = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/documents');
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const deleteDocument = async (id) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await axios.delete(`http://localhost:8000/api/documents/${id}`);
        fetchDocuments(); // Refresh list
      } catch (error) {
        console.error('Failed to delete document:', error);
      }
    }
  };
  
  if (loading) {
    return <div className="text-center py-8">Loading documents...</div>;
  }
  
  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <ul className="divide-y divide-gray-200">
        {documents.map((doc) => (
          <li key={doc.id} className="px-6 py-4 hover:bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {doc.filename}
                </p>
                <p className="text-sm text-gray-500">
                  Uploaded: {new Date(doc.upload_date).toLocaleDateString()}
                </p>
                {doc.summary && (
                  <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                    {doc.summary.substring(0, 200)}...
                  </p>
                )}
              </div>
              <div className="ml-4 flex-shrink-0 flex space-x-2">
                <button
                  onClick={() => window.location.href = `/document/${doc.id}`}
                  className="text-blue-600 hover:text-blue-900"
                >
                  View
                </button>
                <button
                  onClick={() => deleteDocument(doc.id)}
                  className="text-red-600 hover:text-red-900"
                >
                  Delete
                </button>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## Phase 3: Synthesis Features (Week 5-6)

### Day 21-22: Cross-Document Analysis
**File: `backend/ai/synthesizer.py`**
```python
import openai
from typing import List, Dict
import json

class DocumentSynthesizer:
    def __init__(self, api_key: str):
        openai.api_key = api_key
    
    def compare_documents(self, documents: List[Dict]) -> Dict:
        # Extract summaries and key points
        document_texts = []
        for doc in documents:
            doc_text = f"Document: {doc.get('title', 'Untitled')}\n"
            doc_text += f"Summary: {doc.get('summary', '')}\n"
            doc_text += f"Key Points: {json.dumps(doc.get('key_points', {}), indent=2)}\n"
            document_texts.append(doc_text)
        
        combined_text = "\n---\n".join(document_texts)
        
        prompt = f"""Compare and synthesize the following research documents:
        
        {combined_text}
        
        Provide a synthesis that includes:
        1. Common themes across documents
        2. Areas of agreement and disagreement
        3. Gaps in the research
        4. Overall conclusions
        5. Recommendations for further research
        
        Format the        response in a structured way."""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a research synthesis expert. Provide clear, structured comparisons of research documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return {
                "synthesis": response.choices[0].message.content,
                "document_count": len(documents)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def create_timeline(self, documents: List[Dict]) -> List[Dict]:
        # Extract dates and events from documents
        timeline_prompt = f"""From these documents, extract important dates and events:
        
        {json.dumps([doc.get('metadata', {}) for doc in documents], indent=2)}
        
        Create a chronological timeline of events mentioned across all documents."""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract dates and create timelines from research documents."},
                    {"role": "user", "content": timeline_prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse the timeline from response
            return self._parse_timeline(response.choices[0].message.content)
        except Exception as e:
            return [{"error": str(e)}]
    
    def _parse_timeline(self, text: str) -> List[Dict]:
        # Simple parsing - in production, use more robust parsing
        lines = text.split('\n')
        timeline = []
        
        for line in lines:
            if ':' in line and any(char.isdigit() for char in line):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    timeline.append({
                        "date": parts[0].strip(),
                        "event": parts[1].strip()
                    })
        
        return timeline
```

### Day 23-24: Search Implementation
**File: `backend/api/search.py`**
```python
from fastapi import APIRouter, Query
from typing import List, Optional
from backend.ai.embeddings import EmbeddingService
import pinecone

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/semantic")
async def semantic_search(
    query: str,
    limit: int = Query(10, ge=1, le=50),
    threshold: float = Query(0.7, ge=0.0, le=1.0)
):
    """Semantic search across document chunks"""
    
    # Initialize embedding service
    embedding_service = EmbeddingService(
        openai_key=os.getenv("OPENAI_API_KEY"),
        pinecone_key=os.getenv("PINECONE_API_KEY")
    )
    
    # Create query embedding
    query_embedding = embedding_service.create_embedding(query)
    
    # Search in vector database
    if os.getenv("PINECONE_API_KEY"):
        index = pinecone.Index("research-documents")
        results = index.query(
            vector=query_embedding,
            top_k=limit,
            include_metadata=True
        )
        
        return {
            "query": query,
            "results": results.get("matches", []),
            "count": len(results.get("matches", []))
        }
    else:
        # Fallback to simple text search
        return {"message": "Vector search not configured", "query": query}

@router.get("/keyword")
async def keyword_search(
    q: str,
    field: Optional[str] = "all"
):
    """Traditional keyword search"""
    # Implement with PostgreSQL full-text search
    # or use Whoosh/Elasticsearch for more advanced features
    pass
```

### Day 25-26: Advanced UI Components
**File: `frontend/components/SynthesisView.js`**
```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export default function SynthesisView({ documentIds }) {
  const [synthesis, setSynthesis] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const analyzeDocuments = async () => {
    setLoading(true);
    try {
      // Get synthesis
      const synthRes = await axios.post('http://localhost:8000/api/synthesize', {
        document_ids: documentIds
      });
      setSynthesis(synthRes.data);
      
      // Get timeline
      const timelineRes = await axios.post('http://localhost:8000/api/timeline', {
        document_ids: documentIds
      });
      setTimeline(timelineRes.data);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    if (documentIds.length > 1) {
      analyzeDocuments();
    }
  }, [documentIds]);
  
  if (loading) {
    return <div className="text-center py-8">Analyzing documents...</div>;
  }
  
  if (!synthesis) {
    return (
      <div className="text-center py-8 text-gray-500">
        Select multiple documents to see synthesis analysis
      </div>
    );
  }
  
  return (
    <div className="space-y-8">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Document Synthesis</h2>
        <div className="prose max-w-none">
          <pre className="whitespace-pre-wrap text-gray-700">
            {synthesis.synthesis}
          </pre>
        </div>
      </div>
      
      {timeline.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Timeline</h2>
          <div className="space-y-4">
            {timeline.map((item, index) => (
              <div key={index} className="flex items-start">
                <div className="flex-shrink-0 w-24">
                  <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    {item.date}
                  </span>
                </div>
                <div className="ml-4">
                  <p className="text-gray-700">{item.event}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Thematic Analysis</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h3 className="font-medium text-gray-900 mb-2">Common Themes</h3>
            <ul className="space-y-2">
              {synthesis.themes?.map((theme, index) => (
                <li key={index} className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-gray-700">{theme}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="font-medium text-gray-900 mb-2">Research Gaps</h3>
            <ul className="space-y-2">
              {synthesis.gaps?.map((gap, index) => (
                <li key={index} className="flex items-center">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
                  <span className="text-gray-700">{gap}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
```

## Phase 4: Polish & Scale (Week 7-8)

### Day 27-28: Performance Optimization
**File: `backend/utils/cache.py`**
```python
import redis
import json
import hashlib
from functools import wraps
from typing import Any, Callable
import os

redis_client = None

def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = redis.from_url(redis_url)
    return redis_client

def cache_result(ttl: int = 3600):
    """Decorator to cache function results"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_parts = [func.__name__] + [str(arg) for arg in args]
            key_parts += [f"{k}:{v}" for k, v in sorted(kwargs.items())]
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            redis_client = get_redis_client()
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

# Usage example
@cache_result(ttl=86400)  # Cache for 24 hours
def get_document_summary(document_id: str):
    # Expensive operation
    pass
```

**File: `backend/utils/rate_limiter.py`**
```python
from fastapi import HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)

def setup_rate_limiting(app):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Apply rate limits
    @app.middleware("http")
    async def rate_limit_middleware(request, call_next):
        # Custom rate limiting logic
        user_id = request.headers.get("X-User-ID")
        if user_id:
            # Check user-specific limits
            pass
        return await call_next(request)
```

### Day 29-30: Monitoring & Analytics
**File: `backend/monitoring/metrics.py`**
```python
from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps

# Define metrics
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'api_request_duration_seconds',
    'API request latency',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users'
)

LLM_TOKEN_USAGE = Counter(
    'llm_tokens_total',
    'Total LLM tokens used',
    ['model', 'operation']
)

def track_metrics(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            status = "success"
            return result
        except Exception as e:
            status = "error"
            raise e
        finally:
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(
                method=kwargs.get('method', 'GET'),
                endpoint=func.__name__
            ).observe(duration)
            
            REQUEST_COUNT.labels(
                method=kwargs.get('method', 'GET'),
                endpoint=func.__name__,
                status=status
            ).inc()
    return wrapper

def track_llm_usage(model: str, operation: str, tokens: int):
    """Track LLM token usage"""
    LLM_TOKEN_USAGE.labels(model=model, operation=operation).inc(tokens)
```

### Day 31-32: Deployment Configuration
**File: `docker-compose.yml`**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: research
      POSTGRES_USER: research_user
      POSTGRES_PASSWORD: research_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://research_user:research_pass@postgres:5432/research
      REDIS_URL: redis://redis:6379
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

**File: `backend/Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**File: `frontend/Dockerfile`**
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Build the application
RUN npm run build

# Run the application
CMD ["npm", "start"]
```

### Day 33-35: Testing & Documentation
**File: `backend/tests/test_api.py`**
```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_upload_pdf():
    # Test PDF upload
    with open("test.pdf", "rb") as f:
        response = client.post("/upload", files={"file": ("test.pdf", f, "application/pdf")})
    
    assert response.status_code == 200
    assert "file_id" in response.json()

def test_process_document():
    # Test document processing
    response = client.post("/process/some-file-id")
    assert response.status_code in [200, 404]  # 404 if file doesn't exist

def test_search():
    # Test search endpoint
    response = client.get("/search/semantic?query=test")
    assert response.status_code == 200
```

**File: `backend/tests/test_ai.py`**
```python
import pytest
from backend.ai.summarizer import Summarizer

def test_summarizer_chunking():
    summarizer = Summarizer(api_key="test-key")
    text = "A " * 5000  # Long text
    
    chunks = summarizer.chunk_text(text, max_tokens=1000)
    assert len(chunks) > 1
    assert all(len(chunk) > 0 for chunk in chunks)

def test_token_count():
    summarizer = Summarizer(api_key="test-key")
    text = "This is a test sentence."
    
    tokens = summarizer.count_tokens(text)
    assert tokens > 0
```

### Day 36-40: Final Polish & Launch
**Tasks**:
1. **Performance Testing**: Load test with 100+ concurrent users
2. **Security Audit**: Check for common vulnerabilities
3. **User Testing**: Get feedback from beta users
4. **Documentation**: Complete API docs, user guide
5. **Deployment**: Deploy to production environment
6. **Monitoring Setup**: Configure alerts and dashboards
7. **Backup Strategy**: Implement data backup procedures
8. **Scaling Plan**: Prepare for user growth

## Deployment Checklist

### Pre-launch
- [ ] All tests passing
- [ ] Security scan completed
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] Backup system tested
- [ ] Monitoring alerts configured
- [ ] SSL certificates installed
- [ ] CDN configured
- [ ] Rate limiting enabled
- [ ] Error tracking setup

### Launch Day
- [ ] Deploy to production
- [ ] Verify all services running
- [ ] Test critical user flows
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Send announcement to users

### Post-launch
- [ ] Monitor usage patterns
- [ ] Gather user feedback
- [ ] Plan feature iterations
- [ ] Optimize based on metrics
- [ ] Scale infrastructure as needed

## Cost Optimization Strategies

1. **LLM Costs**:
   - Cache common queries and embeddings
   - Use smaller models for simple tasks
   - Implement usage quotas
   - Consider local models for some tasks

2. **Infrastructure**:
   - Use spot instances for non-critical workloads
   - Implement auto-scaling
   - Use CDN for static assets
   - Optimize database queries

3. **Storage**:
   - Implement data lifecycle policies
   - Compress stored documents
   - Use cheaper storage tiers for old data

## Success Metrics to Track

1. **User Metrics**:
   - Daily active users
   - Documents processed per user
   - User retention rate
   - Feature adoption rate

2