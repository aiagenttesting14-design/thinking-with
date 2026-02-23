-- Hybrid Memory System Schema
-- SQLite database for structured memory storage

-- Tasks: What I've worked on
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT CHECK(status IN ('active', 'complete', 'blocked')),
    outcome TEXT,
    metadata TEXT
);

-- Questions: Open questions and answers
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answer TEXT,
    answered_at TIMESTAMP,
    status TEXT CHECK(status IN ('open', 'answered', 'superseded'))
);

-- Decisions: Key choices and rationale
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision TEXT NOT NULL,
    made_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rationale TEXT,
    outcome TEXT
);

-- Index for fast queries
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_questions_status ON questions(status);
