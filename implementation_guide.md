# Implementation Guide: Research Synthesis MVP

## Step-by-Step Setup Instructions

### 1. Environment Setup

```bash
# Create project directory
mkdir research-synthesis
cd research-synthesis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install fastapi uvicorn sqlalchemy pydantic
pip install openai anthropic langchain
pip install pypdf2 beautifulsoup4 requests
pip install python-multipart aiofiles
```

### 2. Project Structure

```
research-synthesis/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── api/
│   │   ├── __init__.py
│   │   ├── endpoints.py     # REST endpoints
│   │   └── websocket.py     # WebSocket handlers
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration
│   │   └── security.py      # Auth & security
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py      # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ingestion.py     # Document ingestion
│   │   ├── processing.py    # AI processing
│   │   └── synthesis.py     # Cross-doc synthesis
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_utils.py    # File handling
│   │   └── ai_utils.py      # AI service wrappers
│   └── workers/
│       ├── __init__.py
│       └── tasks.py         # Async task processing
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

### 3. Core Implementation Files

#### 3.1 FastAPI Application (app/main.py)

```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import endpoints, websocket
from app.core.config import settings

app = FastAPI(title="Research Synthesis API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(endpoints.router, prefix="/api/v1")
app.include_router(websocket.router, prefix="/ws")

# Serve static files in production
if settings.ENVIRONMENT == "production":
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

#### 3.2 Document Ingestion Service (app/services/ingestion.py)

```python
import os
import tempfile
from typing import Dict, Any
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io

class DocumentIngestor:
    def __init__(self):
        self.supported_types = ['.pdf', '.txt', '.md', '.html']
    
    async def ingest(self, file_content: bytes, filename: str, source_type: str = None) -> Dict[str, Any]:
        """Ingest document and extract text content."""
        
        if not source_type:
            source_type = self._detect_type(filename)
        
        if source_type == 'pdf':
            return await self._process_pdf(file_content)
        elif source_type == 'web':
            return await self._process_web(file_content)
        elif source_type in ['text', 'markdown']:
            return await self._process_text(file_content)
        else:
            raise ValueError(f"Unsupported document type: {source_type}")
    
    async def _process_pdf(self, content: bytes) -> Dict[str, Any]:
        """Extract text from PDF."""
        text = ""
        metadata = {}
        
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            metadata = {
                "pages": len(pdf_reader.pages),
                "author": pdf_reader.metadata.get('/Author', ''),
                "title": pdf_reader.metadata.get('/Title', ''),
                "subject": pdf_reader.metadata.get('/Subject', '')
            }
            
            for page_num, page in enumerate(pdf_reader.pages):
                text += page.extract_text() + "\n\n"
                
        except Exception as e:
            # Fallback to OCR if needed
            text = f"PDF extraction failed: {str(e)}"
        
        return {
            "content": text,
            "metadata": metadata,
            "type": "pdf"
        }
    
    async def _process_web(self, url: str) -> Dict[str, Any]:
        """Fetch and extract content from web page."""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Extract metadata
            metadata = {
                "title": soup.title.string if soup.title else "",
                "url": url,
                "description": soup.find("meta", attrs={"name": "description"})["content"] 
                            if soup.find("meta", attrs={"name": "description"}) else ""
            }
            
            return {
                "content": text,
                "metadata": metadata,
                "type": "web"
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch web page: {str(e)}")
    
    async def _process_text(self, content: bytes) -> Dict[str, Any]:
        """Process plain text or markdown."""
        text = content.decode('utf-8', errors='ignore')
        return {
            "content": text,
            "metadata": {},
            "type": "text"
        }
    
    def _detect_type(self, filename: str) -> str:
        """Detect document type from filename."""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.txt', '.md']:
            return 'text'
        elif ext == '.html':
            return 'web'
        else:
            return 'text'  # Default
```

#### 3.3 AI Processing Service (app/services/processing.py)

```python
import os
from typing import List, Dict, Any
import openai
from anthropic import Anthropic

class AIProcessor:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    async def summarize(self, text: str, max_length: int = 500) -> str:
        """Generate summary of text using AI."""
        
        prompt = f"""Please provide a concise summary of the following text in {max_length} words or less:

{text[:4000]}  # Limit context for cost control

Summary:"""
        
        try:
            # Try OpenAI first
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            return response.choices[0].message.content
            
        except Exception as e:
            # Fallback to Claude
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
    
    async def extract_key_points(self, text: str, max_points: int = 10) -> List[str]:
        """Extract key points from text."""
        
        prompt = f"""Extract the {max_points} most important key points from the following text. Return each point as a separate bullet item:

{text[:3000]}

Key Points:"""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Extract key points as bullet items."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.2
        )
        
        # Parse bullet points
        content = response.choices[0].message.content
        points = [p.strip() for p in content.split('\n') if p.strip().startswith('-') or p.strip().startswith('•')]
        
        if not points:
            # Fallback: split by newlines
            points = [p.strip() for p in content.split('\n') if p.strip()]
        
        return points[:max_points]
    
    async def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        
        prompt = f"""Extract named entities from the following text. Categorize them as:
        - People
        - Organizations
        - Locations
        - Dates
        - Key Terms

Return as JSON format.

Text: {text[:2000]}

Entities:"""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Extract entities and return as JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=300,
            temperature=0.1
        )
        
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"people": [], "organizations": [], "locations": [], "dates": [], "terms": []}
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate vector embeddings for text."""
        
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000],  # Limit for cost
            encoding_format="float"
        )
        
        return response.data[0].embedding
```

#### 3.4 Synthesis Service (app/services/synthesis.py)

```python
from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SynthesisEngine:
    def __init__(self):
        pass
    
    async def find_connections(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find connections between multiple documents."""
        
        connections = []
        
        # Compare each pair of documents
        for i in range(len(documents)):
            for j in range(i + 1, len(documents)):
                doc1 = documents[i]
                doc2 = documents[j]
                
                # Find overlapping entities
                common_entities = self._find_common_entities(doc1, doc2)
                
                # Find similar topics
                topic_similarity = self._calculate_topic_similarity(doc1, doc2)
                
                # Find contrasting viewpoints
                contrasts = self._find_contrasts(doc1, doc2)
                
                if common_entities or topic_similarity > 0.3:
                    connections.append({
                        "documents": [doc1["id"], doc2["id"]],
                        "common_entities": common_entities,
                        "topic_similarity": topic_similarity,
                        "contrasts": contrasts,
                        "strength": len(common_entities) + topic_similarity
                    })
        
        # Sort by connection strength
        connections.sort(key=lambda x: x["strength"], reverse=True)
        return connections[:10]  # Return top 10 connections
    
    async def generate_timeline(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate chronological timeline from documents."""
        
        timeline_events = []
        
        for doc in documents:
            # Extract dates from metadata or content
            dates = self._extract_dates(doc)
            
            for date in dates:
                timeline_events.append({
                    "date": date,
                    "document_id": doc["id"],
                    "title": doc.get("metadata", {}).get("title", "Untitled"),
                    "description": doc.get("summary", "")[:200]  # Truncate
                })
        
        # Sort by date
        timeline_events.sort(key=lambda x: x["date"])
        return timeline_events
    
    async def generate_insights(self, documents: List[Dict[str, Any]]) -> str:
        """Generate high-level insights from multiple documents."""
        
        # Combine key points from all documents
        all_key_points = []
        for doc in documents:
            all_key_points.extend(doc.get("key_points", []))
        
        # Remove duplicates
        unique_points = list(set(all_key_points))
        
        # Generate insights using AI
        combined_text = "\n".join(unique_points[:50])  # Limit context
        
        prompt = f"""Based on the following key points from multiple research documents, generate 3-5 high-level insights or conclusions:

{combined_text}

Insights:"""
        
        # Use AI to generate insights
        from app.services.processing import AIProcessor
        processor = AIProcessor()
        insights = await processor.summarize(prompt, max_length=300)
        
        return insights
    
    def _find_common_entities(self, doc1: Dict, doc2: Dict) -> List[str]:
        """Find common entities between two documents."""
        entities1 = set(doc1.get("entities", {}).get("people", []) + 
                       doc1.get("entities", {}).get("organizations", []) +
                       doc1.get("entities", {}).get("terms", []))
        
        entities2 = set(doc2.get("entities", {}).get("people", []) + 
                       doc2.get("entities", {}).get("organizations", []) +
                       doc2.get("entities", {}).get("terms", []))
        
        return list(entities1.intersection(entities2))
    
    def _calculate_topic_similarity(self, doc1: Dict, doc2: Dict) -> float:
        """Calculate similarity between document topics using embeddings."""
        emb1 = doc1.get("embedding", [])
        emb2 = doc2.get("embedding", [])
        
        if emb1 and emb2 and len(emb1) == len(emb2):
            # Convert to numpy arrays
            emb1_np = np.array(emb1).reshape(1, -1)
            emb2_np = np.array(emb2).reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(emb1_np, emb2_np)[0][0]
            return float(similarity)
        
        return 0.0
    
    def _find_contrasts(self, doc1: Dict, doc2: Dict) -> List[str]:
        """Find contrasting viewpoints between documents."""
        contrasts = []
        
        # Simple keyword-based contrast detection
        contrast_keywords = ["however", "but", "although", "despite", "contrary", "opposite", "disagree"]
        
        # This is a simplified version - in production, use more sophisticated NLP
        content1 = doc1.get("content", "").lower()
        content2 = doc2.get("content", "").lower()
        
        for keyword in contrast_keywords:
            if keyword in content1 or keyword in content2:
                contrasts.append(f"Contains contrasting language: '{keyword}'")
        
        return contrasts
    
    def _extract_dates(self, doc: Dict) -> List[str]:
        """Extract dates from document metadata and content."""
        dates = []
        
        # Check metadata
        metadata = doc.get("metadata", {})
        if "date" in metadata:
            dates.append(metadata["date"])
        
        # Simple date extraction from content (basic implementation)
        import re
        content = doc.get("content", "")
        
        # Look for common date patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{4}'  # Just year
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            dates.extend(matches)
        
        return list(set(dates))[:5]  # Return unique dates, limit to 5
```

### 4. Frontend Implementation (React)

#### 4.1 Main App Component (frontend/src/App.jsx)

```jsx
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ProjectView from './pages/ProjectView';
import UploadPage from './pages/UploadPage';
import Navbar from './components/Navbar';
import './App.css';

function App() {
  const [projects, setProjects] = useState([]);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard projects={projects} />} />
            <Route path="/project/:id" element={<ProjectView />} />
            <Route path="/upload" element={<UploadPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
```

#### 4.2 Document Upload Component (frontend/src/components/UploadZone.jsx)

```jsx
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

function UploadZone({ projectId, onUploadComplete }) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const onDrop = useCallback(async (acceptedFiles) => {
    setUploading(true);
    
    for (const file of acceptedFiles) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('project_id', projectId || '');

      try {
        const response = await axios.post('/api/v1/documents', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const percent = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percent);
          },
        });

        if (onUploadComplete) {
          onUploadComplete(response.data);
        }
      } catch (error) {
        console.error('Upload failed:', error);
        alert(`Failed to upload ${file.name}: ${error.message}`);
      }
    }
    
    setUploading(false);
    setProgress(0);
  }, [projectId, onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt', '.md'],
      'text/html': ['.html'],
    },
    multiple: true,
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        isDragActive
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-300 hover:border-gray-400'
      }`}
    >
      <input {...getInputProps()} />
      
      {uploading ? (
        <div>
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="mt-2 text-sm text-gray-600">
              Uploading... {progress}%
            </p>
          </div>
          <p className="text-gray-500">Processing document...</p>
        </div>
      ) : (
        <div>
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <p className="mt-2 text-sm text-gray-600">
            {isDragActive
              ? 'Drop the files here...'
              : 'Drag & drop files here, or click to select'}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Supports PDF, TXT, MD, HTML (max 50MB)
          </p>
        </div>
      )}
    </div>
  );
}

export default UploadZone;
```

#### 4.3 Synthesis Results Component (frontend/src/components/SynthesisPanel.jsx)

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function SynthesisPanel({ projectId }) {
  const [synthesis, setSynthesis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connections, setConnections] = useState([]);
  const [timeline, setTimeline] = useState([]);

  useEffect(() => {
    fetchSynthesis();
  }, [projectId]);

  const fetchSynthesis = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/v1/projects/${projectId}/synthesis`);
      setSynthesis(response.data);
      setConnections(response.data.connections || []);
      setTimeline(response.data.timeline || []);
    } catch (error) {
      console.error('Failed to fetch synthesis:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateSynthesis = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`/api/v1/projects/${projectId}/synthesize`);
      setSynthesis(response.data);
      setConnections(response.data.connections || []);
      setTimeline(response.data.timeline || []);
    } catch (error) {
      console.error('Failed to generate synthesis:', error);
      alert('Failed to generate synthesis. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Insights Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Key Insights</h3>
          <button
            onClick={generateSynthesis}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Regenerate Synthesis
          </button>
        </div>
        
        {synthesis?.insights ? (
          <div className="prose max-w-none">
            <p className="text-gray-700 whitespace-pre-line">
              {synthesis.insights}
            </p>
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">No insights generated yet.</p>
            <button
              onClick={generateSynthesis}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Generate Insights
            </button>
          </div>
        )}
      </div>

      {/* Connections Section */}
      {connections.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Document Connections
          </h3>
          <div className="space-y-4">
            {connections.slice(0, 5).map((connection, index) => (
              <div
                key={index}
                className="border-l-4 border-blue-500 pl-4 py-2 bg-blue-50 rounded-r"
              >
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Connection strength:</span>{' '}
                  {connection.strength.toFixed(2)}
                </p>
                {connection.common_entities.length > 0 && (
                  <p className="text-sm text-gray-600 mt-1">
                    <span className="font-medium">Common entities:</span>{' '}
                    {connection.common_entities.join(', ')}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timeline Section */}
      {timeline.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Timeline</h3>
          <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-300"></div>
            <div className="space-y-6">
              {timeline.map((event, index) => (
                <div key={index} className="relative pl-12">
                  <div className="absolute left-3 w-4 h-4 bg-blue-600 rounded-full -translate-x-1/2"></div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <h4 className="font-medium text-gray-900">
                        {event.title}
                      </h4>
                      <span className="text-sm text-gray-500 bg-white px-2 py-1 rounded">
                        {event.date}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">
                      {event.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SynthesisPanel;
```

### 5. Docker Configuration

#### 5.1 Dockerfile

```dockerfile
# Backend Dockerfile
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
COPY app ./app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 5.2 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/research_synthesis
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./uploads:/app/uploads
    depends_on:
      - db
      - redis
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=research_synthesis
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
```

### 6. Deployment Scripts

#### 6.1 deploy.sh (for Vercel/Railway)

```bash
#!/bin/bash

# Deployment script for Research Synthesis MVP

set -e

echo "🚀 Starting deployment..."

# Check environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY is not set"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
python -m alembic upgrade head

# Build frontend
echo "🔨 Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Start services
echo "🚀 Starting services..."
if [ "$ENVIRONMENT" = "production" ]; then
    # Production mode
    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
else
    # Development mode
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
```

#### 6.2 Railway.json (for Railway.app deployment)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && cd frontend && npm install && npm run build"
  },
  "deploy": {
    "startCommand": "gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
```

### 7. Testing

#### 7.1 API Tests (tests/test_api.py)

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_document_upload():
    # Test PDF upload
    with open("test_document.pdf", "rb") as f:
        response = client.post(
            "/api/v1/documents",
            files={"file": ("test.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "uploaded"

def test_synthesis_generation():
    # Create a test project
    project_response = client.post("/api/v1/projects", json={"name": "Test Project"})
    project_id = project_response.json()["id"]
    
    # Generate synthesis
    response = client.post(f"/api/v1/projects/{project_id}/synthesize")
    assert response.status_code == 200
    data = response.json()
    assert "insights" in data
    assert "connections" in data
```

### 8. Monitoring & Logging

#### 8.1 Logging Configuration (app/core/logging.py)

```python
import logging
import sys
from loguru import logger

def setup_logging():
    """Configure application logging."""
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Add file handler
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )
    
    # Add error file handler
    logger.add(
        "logs/error.log",
        rotation="500 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR"
    )
    
    return logger
```

### 9. Environment Configuration

#### 9.1 .env.example

```env
# Application
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here
DEBUG=true

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/research_synthesis

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# File Storage
STORAGE_TYPE=local  # local, s3, gcs
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
S3_BUCKET_NAME=your-bucket-name

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

### 10. Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/yourusername/research-synthesis-mvp.git
cd research-synthesis-mvp

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Start with Docker (recommended)
docker-compose up -d

# Or start manually
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend
npm install
npm start
```

## Next Steps

1. **Set up your AI API keys** in the `.env` file
2. **Test the ingestion pipeline** with sample PDFs3. **Customize the UI** to match your branding
4. **Add authentication** if needed (OAuth, JWT)
5. **Set up monitoring** (Sentry, Prometheus)
6. **Configure backups** for your database
7. **Implement rate limiting** for API endpoints
8. **Add more document types** (Word, Excel, PowerPoint)
9. **Implement advanced features** like citation generation
10. **Set up CI/CD pipeline** for automated deployments

## Troubleshooting

### Common Issues

1. **PDF extraction fails**: Install OCR dependencies or use a different PDF library
2. **AI API rate limits**: Implement exponential backoff and caching
3. **Memory issues with large documents**: Implement chunking and streaming
4. **Database connection issues**: Check connection strings and firewall rules
5. **File upload size limits**: Configure your web server (nginx/apache)

### Performance Tips

1. **Cache AI responses**: Store common queries to reduce API calls
2. **Use async processing**: Process documents in background workers
3. **Implement pagination**: For large result sets
4. **Optimize database queries**: Use indexes and query optimization
5. **Use CDN for static files**: For faster frontend loading

## Support

For issues and questions:
1. Check the documentation
2. Review the error logs
3. Test with sample documents
4. Contact support with error details

This implementation guide provides everything needed to build and deploy a functional research synthesis MVP. The architecture is modular, allowing for easy customization and extension based on specific requirements.
