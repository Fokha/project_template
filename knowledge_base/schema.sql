-- ============================================
-- FOKHA AGENT KNOWLEDGE BASE - SCHEMA
-- For Claude Code Agent Development System
-- ============================================

PRAGMA foreign_keys = ON;

-- ============================================
-- PROJECT CONFIGURATION
-- ============================================

CREATE TABLE IF NOT EXISTS kb_project (
    id INTEGER PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    category TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO kb_project (key, value, category, description) VALUES
    ('project_name', 'Fokha Trading System', 'config', 'Project name'),
    ('project_version', '2.8.8', 'config', 'Current version'),
    ('created_at', datetime('now'), 'config', 'KB creation date');

-- ============================================
-- DOCUMENTS & FILES
-- ============================================

CREATE TABLE IF NOT EXISTS kb_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    doc_type TEXT NOT NULL,
    category TEXT,
    file_path TEXT,
    file_name TEXT,
    file_size INTEGER,
    mime_type TEXT,
    content_text TEXT,
    content_summary TEXT,
    tags TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    is_archived INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS kb_file_storage (
    id INTEGER PRIMARY KEY,
    doc_id TEXT UNIQUE,
    file_data BLOB,
    checksum TEXT,
    FOREIGN KEY (doc_id) REFERENCES kb_documents(doc_id) ON DELETE CASCADE
);

-- ============================================
-- TASKS & TASK MANAGEMENT
-- ============================================

CREATE TABLE IF NOT EXISTS kb_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    full_specification TEXT,
    implementation_plan TEXT,
    acceptance_criteria TEXT,
    code_changes TEXT,

    status TEXT DEFAULT 'backlog',
    priority TEXT DEFAULT 'medium',
    assigned_to TEXT,
    requested_by TEXT,
    reviewed_by TEXT,

    parent_task_id TEXT,
    dependencies TEXT,
    blocks TEXT,
    related_tasks TEXT,
    related_docs TEXT,

    estimated_hours REAL,
    actual_hours REAL,
    tags TEXT,
    labels TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    due_date TIMESTAMP
);

-- ============================================
-- AGENT MESSAGES
-- ============================================

CREATE TABLE IF NOT EXISTS kb_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT UNIQUE,
    task_id TEXT,
    thread_id TEXT,
    from_agent TEXT NOT NULL,
    to_agent TEXT,
    message_type TEXT NOT NULL,
    subject TEXT,
    content TEXT NOT NULL,
    attachments TEXT,
    is_read INTEGER DEFAULT 0,
    is_archived INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES kb_tasks(task_id)
);

-- ============================================
-- DECISIONS LOG
-- ============================================

CREATE TABLE IF NOT EXISTS kb_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id TEXT UNIQUE,
    title TEXT NOT NULL,
    context TEXT,
    decision TEXT NOT NULL,
    alternatives TEXT,
    rationale TEXT,
    consequences TEXT,
    related_tasks TEXT,
    related_docs TEXT,
    supersedes TEXT,
    category TEXT,
    tags TEXT,
    made_by TEXT,
    approved_by TEXT,
    made_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_from TIMESTAMP,
    expires_at TIMESTAMP
);

-- ============================================
-- ARCHITECTURE KNOWLEDGE
-- ============================================

CREATE TABLE IF NOT EXISTS kb_architecture (
    id INTEGER PRIMARY KEY,
    component TEXT UNIQUE NOT NULL,
    display_name TEXT,
    description TEXT,
    file_patterns TEXT,
    key_files TEXT,
    entry_points TEXT,
    internal_deps TEXT,
    external_deps TEXT,
    dependents TEXT,
    coding_conventions TEXT,
    naming_conventions TEXT,
    readme_path TEXT,
    api_docs_path TEXT,
    language TEXT,
    framework TEXT,
    version TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SESSION CONTEXT
-- ============================================

CREATE TABLE IF NOT EXISTS kb_session_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    agent_id TEXT,
    context_type TEXT NOT NULL,
    context_key TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_persistent INTEGER DEFAULT 0
);

-- ============================================
-- ACTIVITY LOG
-- ============================================

CREATE TABLE IF NOT EXISTS kb_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    actor TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- RESEARCH
-- ============================================

CREATE TABLE IF NOT EXISTS kb_research (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    research_id TEXT UNIQUE,
    topic TEXT NOT NULL,
    query TEXT,
    summary TEXT,
    findings TEXT,
    sources TEXT,
    related_task_id TEXT,
    status TEXT DEFAULT 'in_progress',
    tags TEXT,
    researcher TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- CODE SNIPPETS (for reusable patterns)
-- ============================================

CREATE TABLE IF NOT EXISTS kb_code_snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snippet_id TEXT UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    language TEXT,
    code TEXT NOT NULL,
    tags TEXT,
    usage_count INTEGER DEFAULT 0,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- AGENT REGISTRY (Multi-Agent Coordination)
-- ============================================

CREATE TABLE IF NOT EXISTS kb_agents (
    agent_id TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    focus TEXT,
    working_on TEXT,
    working_on_task_id TEXT,
    repo TEXT,
    locked_files TEXT DEFAULT '[]',
    session_start DATETIME DEFAULT (datetime('now')),
    last_heartbeat DATETIME DEFAULT (datetime('now')),
    capabilities TEXT DEFAULT '[]',
    created_at DATETIME DEFAULT (datetime('now'))
);

-- ============================================
-- WORK LOGS (Agent Activity Tracking)
-- ============================================

CREATE TABLE IF NOT EXISTS kb_work_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    task_id TEXT,
    action TEXT NOT NULL,
    summary TEXT,
    files_changed TEXT DEFAULT '[]',
    commit_hash TEXT,
    duration_minutes REAL,
    retrospective TEXT,
    lesson_learned TEXT,
    tags TEXT DEFAULT '[]',
    created_at DATETIME DEFAULT (datetime('now')),
    FOREIGN KEY (agent_id) REFERENCES kb_agents(agent_id)
);

-- ============================================
-- AGENT SKILL MATRIX
-- ============================================

CREATE TABLE IF NOT EXISTS kb_agent_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    skill TEXT NOT NULL,
    score REAL DEFAULT 0.0,
    tasks_completed INTEGER DEFAULT 0,
    last_used DATETIME DEFAULT (datetime('now')),
    UNIQUE(agent_id, skill)
);

-- ============================================
-- AGENT MEMORY (Cross-Session Persistence)
-- ============================================

CREATE TABLE IF NOT EXISTS kb_agent_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    memory_key TEXT NOT NULL,
    content TEXT,
    category TEXT DEFAULT 'general',
    created_at DATETIME DEFAULT (datetime('now')),
    updated_at DATETIME DEFAULT (datetime('now')),
    UNIQUE(agent_id, memory_key)
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_docs_type ON kb_documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_docs_category ON kb_documents(category);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON kb_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON kb_tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_messages_task ON kb_messages(task_id);
CREATE INDEX IF NOT EXISTS idx_activity_created ON kb_activity_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_research_topic ON kb_research(topic);
CREATE INDEX IF NOT EXISTS idx_research_status ON kb_research(status);
CREATE INDEX IF NOT EXISTS idx_agents_status ON kb_agents(status);
CREATE INDEX IF NOT EXISTS idx_work_logs_agent ON kb_work_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_work_logs_created ON kb_work_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_skills_agent ON kb_agent_skills(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_memory_agent ON kb_agent_memory(agent_id);

-- ============================================
-- VIEWS
-- ============================================

CREATE VIEW IF NOT EXISTS v_team_workload AS
SELECT a.agent_id, a.role, a.status, a.focus, a.working_on,
       COUNT(t.task_id) as active_tasks
FROM kb_agents a
LEFT JOIN kb_tasks t ON t.assigned_to = a.agent_id AND t.status = 'in_progress'
WHERE a.status != 'inactive'
GROUP BY a.agent_id;

CREATE VIEW IF NOT EXISTS v_active_tasks AS
SELECT task_id, title, status, priority, assigned_to, created_at
FROM kb_tasks
WHERE status NOT IN ('done', 'cancelled')
ORDER BY
    CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END;

CREATE VIEW IF NOT EXISTS v_recent_activity AS
SELECT action, entity_type, entity_id, actor, created_at
FROM kb_activity_log
ORDER BY created_at DESC
LIMIT 50;

-- ============================================
-- TRIGGERS
-- ============================================

CREATE TRIGGER IF NOT EXISTS update_task_timestamp
AFTER UPDATE ON kb_tasks
BEGIN
    UPDATE kb_tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
