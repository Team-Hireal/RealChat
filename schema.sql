-- RealChat Database Schema
-- SQLite database for storing WeChat message history and moments

-- Contacts table: stores information about WeChat contacts
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    wechat_id TEXT UNIQUE,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE(name)
);

-- Messages table: stores message history
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    is_from_me BOOLEAN NOT NULL DEFAULT 0,
    chat_type TEXT DEFAULT 'individual', -- 'individual' or 'group'
    retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

-- Moments table: stores contact moments/stories
CREATE TABLE IF NOT EXISTS moments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    content TEXT,
    images TEXT, -- JSON array of image paths/URLs
    timestamp TIMESTAMP NOT NULL,
    retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    likes_count INTEGER DEFAULT 0,
    comments TEXT, -- JSON array of comments
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_messages_contact_id ON messages(contact_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_moments_contact_id ON moments(contact_id);
CREATE INDEX IF NOT EXISTS idx_moments_timestamp ON moments(timestamp);
CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name);

-- Retrieval progress tracking
CREATE TABLE IF NOT EXISTS retrieval_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL, -- 'messages' or 'moments'
    last_contact_processed TEXT,
    total_contacts INTEGER DEFAULT 0,
    processed_contacts INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'in_progress' -- 'in_progress', 'completed', 'failed'
);
