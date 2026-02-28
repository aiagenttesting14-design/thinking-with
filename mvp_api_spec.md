# Research Synthesis MVP - API Specification

## Base URL
`https://api.research-synthesis.com/api/v1` (production)
`http://localhost:8000/api/v1` (development)

## Authentication
For MVP, authentication is optional. If implemented:
- API Key: `X-API-Key` header
- Session Cookie: For web interface

## Rate Limiting
- 100 requests per hour per IP (for MVP)
- 10 document uploads per day per user (for cost control)

## Endpoints

### Health Check
```
GET /health
```
**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-22T20:34:00Z"
}
```

### Document Management

#### Upload Document
```
POST /documents
Content-Type: multipart/form-data
```
**Parameters**:
- `file` (required): File to upload (PDF, TXT, MD, HTML)
- `title` (optional): Custom title for the document
- `source_type` (optional): 'pdf', 'web', 'text' (auto-detected if not provided)
- `url` (optional): If source_type is 'web', provide URL

**Response** (202 Accepted):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Research Paper Title",
  "source_type": "pdf",
  "processing_status": "pending",
  "created_at": "2026-02-22T20:34:00Z",
  "status_url": "/api/v1/documents/550e8400-e29b-41d4-a716-446655440000/status"
}
```

#### List Documents
```
GET /documents
Query Parameters:
  - limit: 20 (default)
  - offset: 0 (default)
  - status: 'pending', 'processing', 'completed', 'failed' (optional)
```
**Response**:
```json
{
  "documents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Research Paper Title",
      "source_type": "pdf",
      "processing_status": "completed",
      "created_at": "2026-02-22T20:34:00Z",
      "processed_at": "2026-02-22T20:35:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### Get Document Details
```
GET /documents/{document_id}
```
**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Research Paper Title",
  "source_type": "pdf",
  "original_filename": "research_paper.pdf",
  "processing_status": "completed",
  "metadata": {
    "pages": 12,
    "author": "John Doe",
    "extraction_method": "PyPDF2"
  },
  "processing_results": {
    "summary": "This paper discusses...",
    "key_points": [
      "Key point 1",
      "Key point 2"
    ],
    "entities": {
      "people": ["John Doe"],
      "organizations": ["Stanford University"],
      "concepts": ["Machine Learning", "AI"]
    },
    "processing_time_ms": 2450,
    "model_used": "claude-3-haiku-20240307"
  },
  "created_at": "2026-02-22T20:34:00Z",
  "processed_at": "2026-02-22T20:35:00Z"
}
```

#### Get Document Status
```
GET /documents/{document_id}/status
```
**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "processing_status": "processing",
  "progress": 60,
  "estimated_completion": "2026-02-22T20:36:00Z",
  "current_step": "AI summarization"
}
```

#### Delete Document
```
DELETE /documents/{document_id}
```
**Response**: 204 No Content

### Synthesis Management

#### Create Synthesis
```
POST /syntheses
Content-Type: application/json
```
**Request Body**:
```json
{
  "title": "My Research Synthesis",
  "description": "Analysis of AI safety papers",
  "document_ids": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

**Response** (201 Created):
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "My Research Synthesis",
  "description": "Analysis of AI safety papers",
  "document_count": 1,
  "processing_status": "pending",
  "created_at": "2026-02-22T20:34:00Z"
}
```

#### List Syntheses
```
GET /syntheses
Query Parameters:
  - limit: 20 (default)
  - offset: 0 (default)
```
**Response**:
```json
{
  "syntheses": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "My Research Synthesis",
      "description": "Analysis of AI safety papers",
      "document_count": 3,
      "processing_status": "completed",
      "created_at": "2026-02-22T20:34:00Z",
      "updated_at": "2026-02-22T20:35:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### Get Synthesis Details
```
GET /syntheses/{synthesis_id}
```
**Response**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "My Research Synthesis",
  "description": "Analysis of AI safety papers",
  "document_count": 3,
  "processing_status": "completed",
  "insights": "The papers collectively suggest that AI safety requires...",
  "documents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "AI Safety Paper 1",
      "summary": "Summary of paper 1...",
      "key_points": ["Point 1", "Point 2"]
    }
  ],
  "connections": [
    {
      "document_a_id": "550e8400-e29b-41d4-a716-446655440000",
      "document_b_id": "550e8400-e29b-41d4-a716-446655440001",
      "similarity_score": 0.85,
      "common_entities": ["AI Safety", "Alignment"],
      "connection_strength": 0.92
    }
  ],
  "created_at": "2026-02-22T20:34:00Z",
  "updated_at": "2026-02-22T20:35:00Z"
}
```

#### Add Document to Synthesis
```
POST /syntheses/{synthesis_id}/documents
Content-Type: application/json
```
**Request Body**:
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

**Response**: 200 OK
```json
{
  "success": true,
  "message": "Document added to synthesis",
  "synthesis_id": "660e8400-e29b-41d4-a716-446655440001",
  "document_id": "550e8400-e29b-41d4-a716-446655440002",
  "document_count": 4
}
```

#### Generate/Re-generate Synthesis Insights
```
POST /syntheses/{synthesis_id}/generate
```
**Response** (202 Accepted):
```json
{
  "synthesis_id": "660e8400-e29b-41d4-a716-446655440001",
  "processing_status": "processing",
  "estimated_completion": "2026-02-22T20:36:00Z",
  "status_url": "/api/v1/syntheses/660e8400-e29b-41d4-a716-446655440001/status"
}
```

#### Get Synthesis Status
```
GET /syntheses/{synthesis_id}/status
```
**Response**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "processing_status": "processing",
  "progress": 75,
  "current_step": "Generating insights from 4 documents",
  "estimated_completion": "2026-02-22T20:36:00Z"
}
```

#### Delete Synthesis
```
DELETE /syntheses/{synthesis_id}
```
**Response**: 204 No Content

### Search & Discovery

#### Search Documents
```
GET /search
Query Parameters:
  - q: search query (required)
  - limit: 10 (default)
  - type: 'semantic', 'keyword', 'both' (default: 'both')
```
**Response**:
```json
{
  "query": "AI safety",
  "type": "semantic",
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "AI Safety Paper",
      "summary": "Paper about AI safety...",
      "relevance_score": 0.92,
      "matched_terms": ["AI", "safety"]
    }
  ],
  "total": 1,
  "limit": 10
}
```

#### Find Similar Documents
```
GET /documents/{document_id}/similar
Query Parameters:
  - limit: 5 (default)
  - threshold: 0.3 (minimum similarity score)
```
**Response**:
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "similar_documents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Related Paper",
      "similarity_score": 0.88,
      "common_entities": ["AI Safety", "Alignment"]
    }
  ],
  "total": 1,
  "limit": 5
}
```

## WebSocket Endpoints

### Processing Status Updates
```
WS /ws/processing/{document_id}
```
**Messages from Server**:
```json
{
  "type": "status_update",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 60,
  "current_step": "AI summarization"
}
```

```json
{
  "type": "completed",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "results_url": "/api/v1/documents/550e8400-e29b-41d4-a716-446655440000"
}
```

## Error Responses

### Common Error Codes
- `400 Bad Request`: Invalid input parameters
- `401 Unauthorized`: Authentication required or invalid
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "error": {
    "code": "invalid_input",
    "message": "Invalid file type. Supported types: PDF, TXT, MD, HTML",
    "details": {
      "field": "file",
      "received": "image.jpg",
      "expected": ["pdf", "txt", "md", "html"]
    },
    "timestamp": "2026-02-22T20:34:00Z"
  }
}
```

## Cost Tracking Headers

Responses include headers for cost transparency:
- `X-AI-Tokens-Used`: Estimated tokens consumed
- `X-AI-Model-Used`: Which AI model was used
- `X-AI-Estimated-Cost`: Estimated cost in USD

## Pagination

All list endpoints support pagination via `limit` and `offset` parameters.
Responses include `total`, `limit`, and `offset` fields.

## File Size Limits

- Maximum file size: 50MB
- Maximum text length for processing: 4000 tokens (~3000 words)
- Maximum documents per synthesis: 20 (for MVP)

## Supported File Types

1. **PDF** (.pdf): Research papers, reports
2. **Text** (.txt, .md): Plain text, markdown
3. **HTML** (.html): Web pages (also via URL)
4. **Web URLs**: Direct URL submission

## Rate Limits (MVP)

- 100 requests/hour per IP
- 10 document uploads/day per user
- 5 synthesis generations/day per user
- 1000 AI tokens/minute per user

These limits can be adjusted based on usage patterns and cost considerations.
