-- Research Synthesis MVP - Database Schema
-- Simplified for MVP, extensible for future features

-- Users table (optional for MVP - can be anonymous)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    -- For MVP, authentication is optional
    -- hashed_password VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(500),
    source_type VARCHAR(20) NOT NULL, -- 'pdf', 'web', 'text'
    original_filename VARCHAR(500),
    file_path TEXT, -- Local filesystem path for MVP
    content_hash VARCHAR(64), -- SHA256 of original content
    raw_text TEXT, -- Extracted text content
    metadata JSONB DEFAULT '{}', -- Extracted metadata
    processing_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes for common queries
    INDEX idx_documents_user_id (user_id),
    INDEX idx_documents_status (processing_status),
    INDEX idx_documents_created (created_at DESC)
);

-- Document processing results
CREATE TABLE document_processing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE UNIQUE,
    summary TEXT,
    key_points TEXT[], -- Array of key points (max 10)
    entities JSONB DEFAULT '{}', -- {people: [], organizations: [], concepts: [], dates: []}
    embedding VECTOR(1536), -- OpenAI text-embedding-3-small dimension
    token_count INTEGER,
    model_used VARCHAR(50), -- Which AI model was used
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Index for similarity search
    INDEX idx_document_processing_embedding USING ivfflat (embedding vector_cosine_ops)
);

-- Syntheses (collections of documents)
CREATE TABLE syntheses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    insights TEXT, -- Generated insights from all documents
    document_count INTEGER DEFAULT 0,
    processing_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_syntheses_user_id (user_id),
    INDEX idx_syntheses_created (created_at DESC)
);

-- Many-to-many relationship between syntheses and documents
CREATE TABLE synthesis_documents (
    synthesis_id UUID REFERENCES syntheses(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (synthesis_id, document_id),
    
    INDEX idx_synthesis_documents_synthesis (synthesis_id),
    INDEX idx_synthesis_documents_document (document_id)
);

-- Pre-computed document connections (for performance)
CREATE TABLE document_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_a_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    document_b_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    similarity_score FLOAT CHECK (similarity_score >= 0 AND similarity_score <= 1),
    common_entities TEXT[], -- Overlapping entities
    connection_strength FLOAT, -- Combined score
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure we don't duplicate connections
    UNIQUE (document_a_id, document_b_id),
    
    -- Indexes for efficient querying
    INDEX idx_document_connections_a (document_a_id),
    INDEX idx_document_connections_b (document_b_id),
    INDEX idx_document_connections_strength (connection_strength DESC)
);

-- API usage tracking (for cost control)
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    endpoint VARCHAR(100),
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    token_count INTEGER,
    model_used VARCHAR(50),
    estimated_cost DECIMAL(10, 6), -- Estimated cost in USD
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_api_usage_user (user_id),
    INDEX idx_api_usage_created (created_at),
    INDEX idx_api_usage_document (document_id)
);

-- Simple cache for AI responses (to avoid duplicate API calls)
CREATE TABLE ai_response_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_hash VARCHAR(64) UNIQUE, -- Hash of input text + prompt
    model_used VARCHAR(50),
    response_text TEXT,
    token_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_ai_cache_hash (content_hash),
    INDEX idx_ai_cache_created (created_at)
);

-- Functions and triggers

-- Update document count in syntheses
CREATE OR REPLACE FUNCTION update_synthesis_document_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE syntheses 
        SET document_count = document_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.synthesis_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE syntheses 
        SET document_count = document_count - 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = OLD.synthesis_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER synthesis_document_count_trigger
AFTER INSERT OR DELETE ON synthesis_documents
FOR EACH ROW
EXECUTE FUNCTION update_synthesis_document_count();

-- Update document processed_at timestamp
CREATE OR REPLACE FUNCTION update_document_processed_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.processing_status = 'completed' AND OLD.processing_status != 'completed' THEN
        NEW.processed_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER document_processed_at_trigger
BEFORE UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION update_document_processed_at();

-- Update AI cache accessed_at
CREATE OR REPLACE FUNCTION update_ai_cache_accessed_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.accessed_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ai_cache_accessed_at_trigger
BEFORE UPDATE ON ai_response_cache
FOR EACH ROW
EXECUTE FUNCTION update_ai_cache_accessed_at();

-- View for document connections with titles
CREATE VIEW document_connections_view AS
SELECT 
    dc.id,
    dc.document_a_id,
    da.title AS document_a_title,
    dc.document_b_id,
    db.title AS document_b_title,
    dc.similarity_score,
    dc.common_entities,
    dc.connection_strength,
    dc.created_at
FROM document_connections dc
JOIN documents da ON dc.document_a_id = da.id
JOIN documents db ON dc.document_b_id = db.id;

-- View for synthesis details
CREATE VIEW synthesis_details AS
SELECT 
    s.id,
    s.title,
    s.description,
    s.insights,
    s.document_count,
    s.processing_status,
    s.created_at,
    s.updated_at,
    u.email AS user_email,
    COUNT(DISTINCT sd.document_id) AS actual_document_count
FROM syntheses s
LEFT JOIN users u ON s.user_id = u.id
LEFT JOIN synthesis_documents sd ON s.id = sd.synthesis_id
GROUP BY s.id, u.email;
