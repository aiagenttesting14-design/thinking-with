# API Specification

## Overview
REST API for the Research Synthesis Service. All endpoints require authentication via Bearer token.

## Base URL
```
https://api.research-synthesis.com/api/v1
```

## Authentication
All endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

Tokens are obtained via the `/auth/login` endpoint.

## Rate Limiting
- 100 requests per minute per user
- 1000 requests per hour per user
- Document uploads: 10 per hour per user

## Error Responses
All errors follow this format:
```json
{
  "error": {
    "code": "error_code",
    "message": "Human readable message",
    "details": {}
  }
}
```

## Common Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

## Endpoints

### Authentication

#### POST /auth/login
Authenticate user and get JWT token.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

#### POST /auth/register
Register new user.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}
```

**Response**: Same as login.

#### POST /auth/refresh
Refresh access token using refresh token.

**Request**:
```json
{
  "refresh_token": "refresh_token_here"
}
```

**Response**: Same as login.

### Documents

#### POST /documents
Upload a new document.

**Content-Type**: `multipart/form-data`

**Parameters**:
- `file` (file): The document file (PDF, TXT, DOCX)
- `title` (string, optional): Custom title
- `tags` (array, optional): Array of tags
- `project_id` (string, optional): Associated project ID

**Alternative**: Submit URL instead of file
- `url` (string): URL to fetch document from
- `title`, `tags`, `project_id` as above

**Response**:
```json
{
  "document": {
    "id": "doc_123",
    "title": "Research Paper Title",
    "original_filename": "paper.pdf",
    "file_type": "pdf",
    "status": "processing",
    "metadata": {
      "page_count": 10,
      "author": "John Smith",
      "language": "en"
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "processing_id": "proc_123"
}
```

#### GET /documents
List all documents for the authenticated user.

**Query Parameters**:
- `page` (number, default: 1): Page number
- `limit` (number, default: 20): Items per page
- `status` (string, optional): Filter by status
- `project_id` (string, optional): Filter by project
- `search` (string, optional): Search in titles and content
- `sort_by` (string, default: "created_at"): Field to sort by
- `sort_order` (string, default: "desc"): "asc" or "desc"

**Response**:
```json
{
  "documents": [
    {
      "id": "doc_123",
      "title": "Research Paper",
      "status": "completed",
      "file_type": "pdf",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "metadata": {
        "page_count": 10,
        "author": "John Smith"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

#### GET /documents/{id}
Get document details.

**Response**:
```json
{
  "document": {
    "id": "doc_123",
    "title": "Research Paper",
    "original_filename": "paper.pdf",
    "file_type": "pdf",
    "status": "completed",
    "storage_path": "s3://bucket/documents/doc_123.pdf",
    "metadata": {
      "page_count": 10,
      "author": "John Smith",
      "language": "en",
      "extracted_text_length": 12500
    },
    "processing_metrics": {
      "processing_time": 15.5,
      "chunks_generated": 25,
      "embeddings_generated": 25
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

#### DELETE /documents/{id}
Delete a document and all associated data.

**Response**:
```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

#### GET /documents/{id}/content
Get extracted text content of document.

**Query Parameters**:
- `format` (string, default: "text"): "text" or "json"
- `include_metadata` (boolean, default: false): Include chunk metadata

**Response (text format)**:
```
This is the extracted text content of the document...
```

**Response (JSON format)**:
```json
{
  "content": {
    "full_text": "Full document text...",
    "chunks": [
      {
        "id": "chunk_1",
        "text": "Chunk text...",
        "metadata": {
          "page_number": 1,
          "section": "Introduction",
          "token_count": 256
        }
      }
    ],
    "metadata": {
      "total_chunks": 25,
      "total_tokens": 6400,
      "language": "en"
    }
  }
}
```

#### POST /documents/{id}/summarize
Generate summary of document.

**Request**:
```json
{
  "length": "medium",  // "short", "medium", "long", "detailed"
  "focus_areas": ["methodology", "results"],  // optional
  "format": "paragraph"  // "paragraph", "bullet_points", "structured"
}
```

**Response**:
```json
{
  "summary": {
    "text": "This paper investigates... The main findings are...",
    "metadata": {
      "length": "medium",
      "token_count": 450,
      "model_used": "gpt-4-turbo",
      "processing_time": 2.3
    },
    "key_points": [
      "Key finding 1",
      "Key finding 2"
    ]
  }
}
```

### Search

#### POST /search
Semantic search across documents.

**Request**:
```json
{
  "query": "machine learning applications in healthcare",
  "filters": {
    "document_ids": ["doc_123", "doc_456"],
    "project_id": "proj_123",
    "date_range": {
      "start": "2023-01-01",
      "end": "2024-01-01"
    },
    "file_types": ["pdf", "article"]
  },
  "options": {
    "top_k": 10,
    "min_similarity": 0.7,
    "include_chunks": true,
    "include_document_context": true
  }
}
```

**Response**:
```json
{
  "results": [
    {
      "document_id": "doc_123",
      "document_title": "AI in Healthcare",
      "chunks": [
        {
          "id": "chunk_45",
          "text": "Machine learning algorithms have shown promising results...",
          "similarity": 0.89,
          "metadata": {
            "page_number": 5,
            "section": "Results"
          }
        }
      ],
      "overall_similarity": 0.85
    }
  ],
  "metadata": {
    "total_documents_searched": 25,
    "total_chunks_considered": 1250,
    "search_time": 0.45
  }
}
```

#### POST /search/similar
Find similar documents to a given document or text.

**Request**:
```json
{
  "document_id": "doc_123",
  // OR
  "text": "Text to find similar content for",
  "top_k": 5
}
```

**Response**: Same format as `/search`.

### Synthesis

#### POST /synthesize
Synthesize information across multiple documents.

**Request**:
```json
{
  "query": "Compare the methodologies used in these papers",
  "document_ids": ["doc_123", "doc_456", "doc_789"],
  "instructions": "Focus on experimental design and statistical methods",
  "format": "comparative_analysis",  // "summary", "comparative_analysis", "timeline", "thematic"
  "options": {
    "include_citations": true,
    "include_contradictions": true,
    "max_length": 1000
  }
}
```

**Response**:
```json
{
  "synthesis": {
    "text": "Based on the provided documents, the methodologies show both similarities and differences...",
    "format": "comparative_analysis",
    "citations": [
      {
        "document_id": "doc_123",
        "document_title": "Paper A",
        "chunk_ids": ["chunk_12", "chunk_15"],
        "text_excerpts": ["Excerpt 1...", "Excerpt 2..."]
      }
    ],
    "contradictions": [
      {
        "point": "Sample size justification",
        "document_a": {
          "id": "doc_123",
          "position": "Uses power analysis"
        },
        "document_b": {
          "id": "doc_456",
          "position": "Based on previous studies"
        }
      }
    ],
    "metadata": {
      "documents_used": 3,
      "chunks_retrieved": 45,
      "model_used": "gpt-4-turbo",
      "processing_time": 8.7,
      "token_count": 850
    }
  }
}
```

#### POST /synthesize/question
Answer specific question using documents.

**Request**:
```json
{
  "question": "What was the average success rate across all studies?",
  "document_ids": ["doc_123", "doc_456"],
  "require_citations": true,
  "confidence_threshold": 0.8
}
```

**Response**:
```json
{
  "answer": {
    "text": "The average success rate across the three studies was 78.5%.",
    "confidence": 0.92,
    "citations": [
      {
        "document_id": "doc_123",
        "text": "Study A reported a success rate of 82%...",
        "page": 7
      }
    ],
    "supporting_evidence": [
      {
        "document_id": "doc_123",
        "metric": "success_rate",
        "value": 0.82
      }
    ]
  }
}
```

### Projects

#### GET /projects
List all projects.

**Response**:
```json
{
  "projects": [
    {
      "id": "proj_123",
      "name": "Healthcare AI Research",
      "description": "Collection of papers on AI in healthcare",
      "document_count": 15,
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-15T14:30:00Z"
    }
  ]
}
```

#### POST /projects
Create new project.

**Request**:
```json
{
  "name": "New Research Project",
  "description": "Description of the project",
  "tags": ["ai", "healthcare"],
  "document_ids": ["doc_123", "doc_456"]  // optional
}
```

**Response**:
```json
{
  "project": {
    "id": "proj_456",
    "name": "New Research Project",
    "description": "Description of the project",
    "tags": ["ai", "healthcare"],
    "document_count": 2,
    "created_at": "2024-01-20T09:00:00Z",
    "updated_at": "2024-01-20T09:00:00Z"
  }
}
```

#### PUT /projects/{id}
Update project.

**Request**: Same as POST, all fields optional.

**Response**: Updated project.

#### DELETE /projects/{id}
Delete project (does not delete documents).

**Response**:
```json
{
  "success": true,
  "message": "Project deleted successfully"
}
```

#### POST /projects/{id}/documents
Add documents to project.

**Request**:
```json
{
  "document_ids": ["doc_123", "doc_456", "doc_789"]
}
```

**Response**:
```json
{
  "success": true,
  "added_count": 3,
  "project": {
    "id": "proj_123",
    "document_count": 18
  }
}
```

#### DELETE /projects/{id}/documents/{document_id}
Remove document from project.

**Response**:
```json
{
  "success": true,
  "message": "Document removed from project"
}
```

### Processing Status

#### GET /processing/{id}
Get status of document processing.

**Response**:
```json
{
  "processing_id": "proc_123",
  "document_id": "doc_123",
  "status": "processing",  // "pending", "processing", "completed", "failed"
  "progress": 0.65,
  "current_step": "generating_embeddings",
  "steps": [
    {
      "name": "text_extraction",
      "status": "completed",
      "duration": 2.1
    },
    {
      "name": "chunking",
      "status": "completed",
      "duration": 0.8
    },
    {
      "name": "generating_embeddings",
      "status": "in_progress",
      "progress": 0.65
    }
  ],
  "estimated_completion": "2024-01-15T10:35:00Z",
  "started_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:32:00Z"
}
```

#### GET /processing/queue
Get processing queue status.

**Response**:
```json
{
  "queue_status": {
    "pending": 3,
    "processing": 2,
    "recently_completed": 15,
    "average_processing_time": 12.5
  },
  "user_queue": [
    {
      "processing_id": "proc_123",
      "document_id": "doc_123",
      "status": "processing",
      "position": 1,
      "estimated_wait_time": 30
    }
  ]
}
```

### Export

#### POST /export
Export documents or synthesis results.

**Request**:
```json
{
  "type": "synthesis",  // "documents", "synthesis", "summary"
  "content_ids": ["synth_123"],  // or document_ids
  "format": "markdown",  // "markdown", "pdf", "json", "html"
  "options": {
    "include_citations": true,
    "include_metadata": true,
    "template": "academic"  // "academic", "business", "simple"
  }
}
```

**Response**:
```json
{
  "export": {
    "id": "export_123",
    "status": "processing",
    "download_url": "https://api.research-synthesis.com/exports/export_123.pdf",
    "expires_at": "2024-01-15T11:30:00Z"
  }
}
```

#### GET /exports/{id}
Get export status and download URL.

**Response**:
```json
{
  "export": {
    "id": "export_123",
    "status": "completed",
    "download_url": "https://api.research-synthesis.com/exports/export_123.pdf",
    "file_size": 125000,
    "expires_at": "2024-01-15T11:30:00Z",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### System

#### GET /system/status
Get system status and health.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 86400,
  "services": {
    "database": {
      "status": "healthy",
      "latency": 12
    },
    "vector_db": {
      "status": "healthy",
      "index_size": 12500
    },
    "storage": {
      "status": "healthy",
      "used_space": "1.2GB"
    },
    "ai_services": {
      "openai": "healthy",
      "anthropic": "healthy"
    }
  },
  "metrics": {
    "documents_processed_today": 45,
    "active_users_today": 23,
    "average_response_time": 0.45
  }
}
```

#### GET /system/metrics
Get Prometheus