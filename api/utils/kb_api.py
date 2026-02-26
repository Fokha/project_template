"""
Knowledge Base API Endpoints
Enables all agents to read/write to agent_kb.db
"""

import sqlite3
import json
import os
from datetime import datetime
from flask import Blueprint, request, jsonify

# Create Blueprint
kb_bp = Blueprint('kb', __name__, url_prefix='/kb')

# Database path
KB_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knowledge_base', 'agent_kb.db')


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(KB_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def dict_from_row(row):
    """Convert sqlite3.Row to dict."""
    return dict(zip(row.keys(), row)) if row else None


# ============================================
# PROJECT INFO
# ============================================

@kb_bp.route('/project', methods=['GET'])
def get_project():
    """Get project information."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM kb_project")
    rows = cursor.fetchall()
    conn.close()

    project = {row['key']: row['value'] for row in rows}
    return jsonify({'success': True, 'project': project})


# ============================================
# TASKS
# ============================================

@kb_bp.route('/tasks', methods=['GET'])
def list_tasks():
    """List all tasks with optional filters."""
    status = request.args.get('status')
    assigned_to = request.args.get('assigned_to')
    priority = request.args.get('priority')
    limit = request.args.get('limit', 50, type=int)

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM kb_tasks WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if assigned_to:
        query += " AND assigned_to = ?"
        params.append(assigned_to)
    if priority:
        query += " AND priority = ?"
        params.append(priority)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    tasks = [dict_from_row(row) for row in rows]
    return jsonify({'success': True, 'count': len(tasks), 'tasks': tasks})


@kb_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    data = request.get_json()

    if not data.get('title'):
        return jsonify({'success': False, 'error': 'title is required'}), 400

    # Generate task_id
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(CAST(SUBSTR(task_id, 2) AS INTEGER)) FROM kb_tasks WHERE task_id LIKE 'T%'")
    max_id = cursor.fetchone()[0] or 0
    task_id = f"T{max_id + 1}"

    cursor.execute("""
        INSERT INTO kb_tasks (task_id, title, description, full_specification, status, priority, assigned_to, requested_by, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task_id,
        data.get('title'),
        data.get('description'),
        data.get('full_specification'),
        data.get('status', 'backlog'),
        data.get('priority', 'medium'),
        data.get('assigned_to'),
        data.get('requested_by'),
        json.dumps(data.get('tags', []))
    ))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'task_id': task_id, 'message': f'Task {task_id} created'})


@kb_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kb_tasks WHERE task_id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({'success': False, 'error': 'Task not found'}), 404

    return jsonify({'success': True, 'task': dict_from_row(row)})


@kb_bp.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task."""
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    # Build update query dynamically
    updates = []
    params = []

    for field in ['title', 'description', 'full_specification', 'status', 'priority', 'assigned_to']:
        if field in data:
            updates.append(f"{field} = ?")
            params.append(data[field])

    if not updates:
        return jsonify({'success': False, 'error': 'No fields to update'}), 400

    # Handle special timestamp updates
    if data.get('status') == 'in_progress' and 'started_at' not in data:
        updates.append("started_at = datetime('now')")
    if data.get('status') == 'done' and 'completed_at' not in data:
        updates.append("completed_at = datetime('now')")

    params.append(task_id)
    query = f"UPDATE kb_tasks SET {', '.join(updates)} WHERE task_id = ?"

    cursor.execute(query, params)
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'success': False, 'error': 'Task not found'}), 404

    conn.close()
    return jsonify({'success': True, 'message': f'Task {task_id} updated'})


# ============================================
# MESSAGES
# ============================================

@kb_bp.route('/messages', methods=['GET'])
def list_messages():
    """List messages with optional filters."""
    task_id = request.args.get('task_id')
    from_agent = request.args.get('from_agent')
    to_agent = request.args.get('to_agent')
    limit = request.args.get('limit', 50, type=int)

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM kb_messages WHERE 1=1"
    params = []

    if task_id:
        query += " AND task_id = ?"
        params.append(task_id)
    if from_agent:
        query += " AND from_agent = ?"
        params.append(from_agent)
    if to_agent:
        query += " AND (to_agent = ? OR to_agent IS NULL)"
        params.append(to_agent)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    messages = [dict_from_row(row) for row in rows]
    return jsonify({'success': True, 'count': len(messages), 'messages': messages})


@kb_bp.route('/messages', methods=['POST'])
def create_message():
    """Create a new message."""
    data = request.get_json()

    if not data.get('from_agent') or not data.get('content'):
        return jsonify({'success': False, 'error': 'from_agent and content are required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO kb_messages (task_id, from_agent, to_agent, message_type, subject, content, attachments)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('task_id'),
        data.get('from_agent'),
        data.get('to_agent'),
        data.get('message_type', 'update'),
        data.get('subject'),
        data.get('content'),
        json.dumps(data.get('attachments', []))
    ))
    conn.commit()
    message_id = cursor.lastrowid
    conn.close()

    return jsonify({'success': True, 'message_id': message_id, 'message': 'Message created'})


# ============================================
# DECISIONS
# ============================================

@kb_bp.route('/decisions', methods=['GET'])
def list_decisions():
    """List all decisions."""
    limit = request.args.get('limit', 20, type=int)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kb_decisions ORDER BY made_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    decisions = [dict_from_row(row) for row in rows]
    return jsonify({'success': True, 'count': len(decisions), 'decisions': decisions})


@kb_bp.route('/decisions', methods=['POST'])
def create_decision():
    """Record a new decision."""
    data = request.get_json()

    if not data.get('title') or not data.get('decision'):
        return jsonify({'success': False, 'error': 'title and decision are required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Generate decision_id
    cursor.execute("SELECT MAX(CAST(SUBSTR(decision_id, 2) AS INTEGER)) FROM kb_decisions WHERE decision_id LIKE 'D%'")
    max_id = cursor.fetchone()[0] or 0
    decision_id = f"D{max_id + 1:03d}"

    cursor.execute("""
        INSERT INTO kb_decisions (decision_id, title, context, decision, alternatives, rationale, category, made_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        decision_id,
        data.get('title'),
        data.get('context'),
        data.get('decision'),
        json.dumps(data.get('alternatives', [])),
        data.get('rationale'),
        data.get('category'),
        data.get('made_by')
    ))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'decision_id': decision_id, 'message': f'Decision {decision_id} recorded'})


# ============================================
# CONTEXT & SESSION
# ============================================

@kb_bp.route('/context', methods=['GET'])
def get_context():
    """Get session context."""
    context_type = request.args.get('type', 'focus')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT context_key, content, created_at
        FROM kb_session_context
        WHERE context_type = ? AND is_persistent = 1
        ORDER BY created_at DESC
    """, (context_type,))
    rows = cursor.fetchall()
    conn.close()

    context = {row['context_key']: row['content'] for row in rows}
    return jsonify({'success': True, 'context_type': context_type, 'context': context})


@kb_bp.route('/context', methods=['POST'])
def save_context():
    """Save session context."""
    data = request.get_json()

    if not data.get('key') or not data.get('content'):
        return jsonify({'success': False, 'error': 'key and content are required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO kb_session_context (session_id, context_type, context_key, content, is_persistent, created_at)
        VALUES ('global', ?, ?, ?, 1, datetime('now'))
    """, (
        data.get('type', 'focus'),
        data.get('key'),
        data.get('content')
    ))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Context saved'})


# ============================================
# RESUME - Full Session Load
# ============================================

@kb_bp.route('/resume', methods=['GET'])
def resume_session():
    """Load full context for resuming a session."""
    conn = get_db()
    cursor = conn.cursor()

    # Project info
    cursor.execute("SELECT key, value FROM kb_project")
    project = {row['key']: row['value'] for row in cursor.fetchall()}

    # Current focus
    cursor.execute("""
        SELECT context_key, content FROM kb_session_context
        WHERE context_type = 'focus' AND is_persistent = 1
    """)
    focus = {row['context_key']: row['content'] for row in cursor.fetchall()}

    # Active tasks
    cursor.execute("""
        SELECT task_id, title, status, priority, assigned_to
        FROM kb_tasks
        WHERE status NOT IN ('done', 'cancelled')
        ORDER BY CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END
        LIMIT 10
    """)
    tasks = [dict_from_row(row) for row in cursor.fetchall()]

    # Recent decisions
    cursor.execute("""
        SELECT decision_id, title, decision, made_at
        FROM kb_decisions
        ORDER BY made_at DESC LIMIT 5
    """)
    decisions = [dict_from_row(row) for row in cursor.fetchall()]

    # Architecture
    cursor.execute("SELECT component, display_name, language, framework FROM kb_architecture")
    architecture = [dict_from_row(row) for row in cursor.fetchall()]

    # Important conversation context
    cursor.execute("""
        SELECT summary, created_at FROM kb_conversations
        WHERE importance >= 1
        ORDER BY created_at DESC LIMIT 10
    """)
    context_points = [row['summary'] for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        'success': True,
        'project': project,
        'focus': focus,
        'active_tasks': tasks,
        'recent_decisions': decisions,
        'architecture': architecture,
        'important_context': context_points
    })


# ============================================
# ARCHITECTURE
# ============================================

@kb_bp.route('/architecture', methods=['GET'])
def get_architecture():
    """Get architecture components."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kb_architecture")
    rows = cursor.fetchall()
    conn.close()

    components = [dict_from_row(row) for row in rows]
    return jsonify({'success': True, 'components': components})


@kb_bp.route('/architecture', methods=['POST'])
def add_architecture():
    """Add or update architecture component."""
    data = request.get_json()

    if not data.get('component'):
        return jsonify({'success': False, 'error': 'component is required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO kb_architecture
        (component, display_name, description, language, framework, file_patterns, key_files)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('component'),
        data.get('display_name'),
        data.get('description'),
        data.get('language'),
        data.get('framework'),
        json.dumps(data.get('file_patterns', [])),
        json.dumps(data.get('key_files', []))
    ))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f"Component '{data.get('component')}' saved"})


# ============================================
# CONVERSATIONS
# ============================================

@kb_bp.route('/conversations', methods=['POST'])
def save_conversation():
    """Save important conversation point."""
    data = request.get_json()

    if not data.get('content'):
        return jsonify({'success': False, 'error': 'content is required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO kb_conversations (session_id, role, content, summary, importance, tags, related_task_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('session_id', datetime.now().strftime('%Y-%m-%d')),
        data.get('role', 'assistant'),
        data.get('content'),
        data.get('summary'),
        data.get('importance', 1),
        json.dumps(data.get('tags', [])),
        data.get('related_task_id')
    ))
    conn.commit()
    conv_id = cursor.lastrowid
    conn.close()

    return jsonify({'success': True, 'conversation_id': conv_id, 'message': 'Conversation saved'})


# ============================================
# ACTIVITY LOG
# ============================================

@kb_bp.route('/activity', methods=['GET'])
def get_activity():
    """Get recent activity."""
    limit = request.args.get('limit', 50, type=int)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT action, entity_type, entity_id, actor, details, created_at
        FROM kb_activity_log
        ORDER BY created_at DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    activity = [dict_from_row(row) for row in rows]
    return jsonify({'success': True, 'activity': activity})


@kb_bp.route('/activity', methods=['POST'])
def log_activity():
    """Log an activity."""
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO kb_activity_log (action, entity_type, entity_id, actor, details)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data.get('action'),
        data.get('entity_type'),
        data.get('entity_id'),
        data.get('actor', 'unknown'),
        json.dumps(data.get('details', {}))
    ))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Activity logged'})


# ============================================
# RESEARCH
# ============================================

@kb_bp.route('/research', methods=['GET'])
def list_research():
    """List research entries with optional filters."""
    topic = request.args.get('topic')
    status = request.args.get('status')
    task_id = request.args.get('task_id')
    limit = request.args.get('limit', 50, type=int)

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM kb_research WHERE 1=1"
    params = []

    if topic:
        query += " AND topic LIKE ?"
        params.append(f'%{topic}%')
    if status:
        query += " AND status = ?"
        params.append(status)
    if task_id:
        query += " AND related_task_id = ?"
        params.append(task_id)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    research = [dict_from_row(row) for row in rows]
    return jsonify({'success': True, 'count': len(research), 'research': research})


@kb_bp.route('/research', methods=['POST'])
def create_research():
    """Create a new research entry."""
    data = request.get_json()

    if not data.get('topic'):
        return jsonify({'success': False, 'error': 'topic is required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Generate research_id
    cursor.execute("SELECT MAX(CAST(SUBSTR(research_id, 2) AS INTEGER)) FROM kb_research WHERE research_id LIKE 'R%'")
    max_id = cursor.fetchone()[0] or 0
    research_id = f"R{max_id + 1:03d}"

    cursor.execute("""
        INSERT INTO kb_research (research_id, topic, query, summary, findings, sources, related_task_id, status, tags, researcher)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        research_id,
        data.get('topic'),
        data.get('query'),
        data.get('summary'),
        data.get('findings'),
        json.dumps(data.get('sources', [])),
        data.get('related_task_id'),
        data.get('status', 'in_progress'),
        json.dumps(data.get('tags', [])),
        data.get('researcher')
    ))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'research_id': research_id, 'message': f'Research {research_id} created'})


@kb_bp.route('/research/<research_id>', methods=['GET'])
def get_research(research_id):
    """Get a specific research entry."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kb_research WHERE research_id = ?", (research_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({'success': False, 'error': 'Research not found'}), 404

    return jsonify({'success': True, 'research': dict_from_row(row)})


@kb_bp.route('/research/<research_id>', methods=['PUT'])
def update_research(research_id):
    """Update a research entry."""
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    updates = []
    params = []

    for field in ['topic', 'query', 'summary', 'findings', 'status', 'related_task_id', 'researcher']:
        if field in data:
            updates.append(f"{field} = ?")
            params.append(data[field])

    if 'sources' in data:
        updates.append("sources = ?")
        params.append(json.dumps(data['sources']))

    if 'tags' in data:
        updates.append("tags = ?")
        params.append(json.dumps(data['tags']))

    if not updates:
        return jsonify({'success': False, 'error': 'No fields to update'}), 400

    updates.append("updated_at = datetime('now')")
    params.append(research_id)

    query = f"UPDATE kb_research SET {', '.join(updates)} WHERE research_id = ?"
    cursor.execute(query, params)
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'success': False, 'error': 'Research not found'}), 404

    conn.close()
    return jsonify({'success': True, 'message': f'Research {research_id} updated'})


@kb_bp.route('/research/<research_id>/findings', methods=['POST'])
def add_research_finding(research_id):
    """Add a finding to existing research."""
    data = request.get_json()

    if not data.get('finding'):
        return jsonify({'success': False, 'error': 'finding is required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Get current findings
    cursor.execute("SELECT findings FROM kb_research WHERE research_id = ?", (research_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({'success': False, 'error': 'Research not found'}), 404

    current = row['findings'] or ''
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    new_finding = f"\n\n[{timestamp}] {data.get('finding')}"

    cursor.execute("""
        UPDATE kb_research
        SET findings = ?, updated_at = datetime('now')
        WHERE research_id = ?
    """, (current + new_finding, research_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Finding added'})


@kb_bp.route('/research/<research_id>/sources', methods=['POST'])
def add_research_source(research_id):
    """Add a source to existing research."""
    data = request.get_json()

    if not data.get('url') and not data.get('title'):
        return jsonify({'success': False, 'error': 'url or title is required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Get current sources
    cursor.execute("SELECT sources FROM kb_research WHERE research_id = ?", (research_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({'success': False, 'error': 'Research not found'}), 404

    try:
        sources = json.loads(row['sources']) if row['sources'] else []
    except (json.JSONDecodeError, TypeError):
        sources = []

    sources.append({
        'url': data.get('url'),
        'title': data.get('title'),
        'type': data.get('type', 'web'),
        'notes': data.get('notes'),
        'added_at': datetime.now().isoformat()
    })

    cursor.execute("""
        UPDATE kb_research
        SET sources = ?, updated_at = datetime('now')
        WHERE research_id = ?
    """, (json.dumps(sources), research_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Source added', 'source_count': len(sources)})


# ============================================
# AGENT REGISTRY
# ============================================

def _ensure_agent_tables():
    """Create agent coordination tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.executescript("""
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

        CREATE TABLE IF NOT EXISTS kb_work_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            task_id TEXT,
            action TEXT NOT NULL,
            summary TEXT,
            files_changed TEXT DEFAULT '[]',
            commit_hash TEXT,
            duration_minutes REAL,
            created_at DATETIME DEFAULT (datetime('now')),
            FOREIGN KEY (agent_id) REFERENCES kb_agents(agent_id)
        );
    """)
    conn.commit()
    conn.close()


# Run on import to ensure tables exist
_ensure_agent_tables()


@kb_bp.route('/agents', methods=['GET'])
def list_agents():
    """List all registered agents."""
    status = request.args.get('status')
    conn = get_db()
    cursor = conn.cursor()

    if status:
        cursor.execute("SELECT * FROM kb_agents WHERE status = ? ORDER BY last_heartbeat DESC", (status,))
    else:
        cursor.execute("SELECT * FROM kb_agents ORDER BY last_heartbeat DESC")

    rows = cursor.fetchall()
    conn.close()
    agents = [dict_from_row(row) for row in rows]
    return jsonify({'success': True, 'count': len(agents), 'agents': agents})


@kb_bp.route('/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get a specific agent's info."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kb_agents WHERE agent_id = ?", (agent_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({'success': False, 'error': 'Agent not found'}), 404

    # Also get their active tasks
    cursor.execute("""
        SELECT task_id, title, status, priority FROM kb_tasks
        WHERE assigned_to = ? AND status NOT IN ('done', 'cancelled')
        ORDER BY created_at DESC
    """, (agent_id,))
    tasks = [dict_from_row(r) for r in cursor.fetchall()]

    # Recent work logs
    cursor.execute("""
        SELECT * FROM kb_work_logs
        WHERE agent_id = ? ORDER BY created_at DESC LIMIT 10
    """, (agent_id,))
    logs = [dict_from_row(r) for r in cursor.fetchall()]

    conn.close()
    agent = dict_from_row(row)
    agent['active_tasks'] = tasks
    agent['recent_logs'] = logs
    return jsonify({'success': True, 'agent': agent})


@kb_bp.route('/agents/<agent_id>', methods=['POST'])
def register_agent(agent_id):
    """Register or update an agent."""
    data = request.get_json() or {}

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO kb_agents (agent_id, role, status, focus, working_on, repo, capabilities)
        VALUES (?, ?, 'active', ?, ?, ?, ?)
        ON CONFLICT(agent_id) DO UPDATE SET
            role = excluded.role,
            status = 'active',
            focus = excluded.focus,
            working_on = excluded.working_on,
            repo = excluded.repo,
            capabilities = excluded.capabilities,
            last_heartbeat = datetime('now'),
            session_start = datetime('now')
    """, (
        agent_id,
        data.get('role', 'general'),
        data.get('focus'),
        data.get('working_on'),
        data.get('repo'),
        json.dumps(data.get('capabilities', []))
    ))
    conn.commit()
    conn.close()

    # Auto-log the registration
    _log_activity('registered', 'agent', agent_id, agent_id, {'role': data.get('role')})

    return jsonify({'success': True, 'message': f'Agent {agent_id} registered'})


@kb_bp.route('/agents/<agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """Update agent status/focus/working_on."""
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    updates = ["last_heartbeat = datetime('now')"]
    params = []

    for field in ['status', 'focus', 'working_on', 'working_on_task_id', 'repo', 'locked_files']:
        if field in data:
            updates.append(f"{field} = ?")
            if field == 'locked_files':
                params.append(json.dumps(data[field]))
            else:
                params.append(data[field])

    params.append(agent_id)
    cursor.execute(f"UPDATE kb_agents SET {', '.join(updates)} WHERE agent_id = ?", params)
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'success': False, 'error': 'Agent not found'}), 404

    conn.close()
    return jsonify({'success': True, 'message': f'Agent {agent_id} updated'})


@kb_bp.route('/agents/<agent_id>', methods=['DELETE'])
def deregister_agent(agent_id):
    """Deregister an agent (mark inactive)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE kb_agents SET status = 'inactive', locked_files = '[]'
        WHERE agent_id = ?
    """, (agent_id,))
    conn.commit()
    conn.close()

    _log_activity('deregistered', 'agent', agent_id, agent_id, {})
    return jsonify({'success': True, 'message': f'Agent {agent_id} deregistered'})


@kb_bp.route('/agents/<agent_id>/heartbeat', methods=['POST'])
def agent_heartbeat(agent_id):
    """Update agent heartbeat timestamp."""
    data = request.get_json() or {}

    conn = get_db()
    cursor = conn.cursor()

    updates = ["last_heartbeat = datetime('now')"]
    params = []

    if 'working_on' in data:
        updates.append("working_on = ?")
        params.append(data['working_on'])
    if 'status' in data:
        updates.append("status = ?")
        params.append(data['status'])

    params.append(agent_id)
    cursor.execute(f"UPDATE kb_agents SET {', '.join(updates)} WHERE agent_id = ?", params)
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Heartbeat recorded'})


# ============================================
# WORK LOGS
# ============================================

@kb_bp.route('/work-logs', methods=['GET'])
def list_work_logs():
    """List work logs with optional filters."""
    agent_id = request.args.get('agent_id')
    task_id = request.args.get('task_id')
    limit = request.args.get('limit', 50, type=int)

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM kb_work_logs WHERE 1=1"
    params = []

    if agent_id:
        query += " AND agent_id = ?"
        params.append(agent_id)
    if task_id:
        query += " AND task_id = ?"
        params.append(task_id)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    logs = [dict_from_row(row) for row in rows]
    return jsonify({'success': True, 'count': len(logs), 'logs': logs})


    # NOTE: work-logs POST is defined below (v2 with retrospectives)


# ============================================
# TEAM DASHBOARD
# ============================================

@kb_bp.route('/team/status', methods=['GET'])
def team_status():
    """Get full team coordination dashboard."""
    conn = get_db()
    cursor = conn.cursor()

    # Active agents
    cursor.execute("""
        SELECT agent_id, role, status, focus, working_on, working_on_task_id,
               locked_files, last_heartbeat
        FROM kb_agents WHERE status != 'inactive'
        ORDER BY last_heartbeat DESC
    """)
    agents = [dict_from_row(r) for r in cursor.fetchall()]

    # All locked files across agents
    all_locked = {}
    for a in agents:
        try:
            files = json.loads(a.get('locked_files', '[]'))
            for f in files:
                all_locked[f] = a['agent_id']
        except (json.JSONDecodeError, TypeError):
            pass

    # Task summary
    cursor.execute("""
        SELECT status, COUNT(*) as count FROM kb_tasks
        GROUP BY status
    """)
    task_summary = {row['status']: row['count'] for row in cursor.fetchall()}

    # In-progress tasks with assignees
    cursor.execute("""
        SELECT task_id, title, assigned_to, priority, started_at
        FROM kb_tasks WHERE status = 'in_progress'
        ORDER BY started_at DESC
    """)
    active_tasks = [dict_from_row(r) for r in cursor.fetchall()]

    # Pending unassigned tasks
    cursor.execute("""
        SELECT task_id, title, priority
        FROM kb_tasks WHERE status = 'pending' AND (assigned_to IS NULL OR assigned_to = 'unassigned')
        ORDER BY CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END
    """)
    available_tasks = [dict_from_row(r) for r in cursor.fetchall()]

    # Recent work logs (last 20)
    cursor.execute("""
        SELECT agent_id, task_id, action, summary, created_at
        FROM kb_work_logs ORDER BY created_at DESC LIMIT 20
    """)
    recent_work = [dict_from_row(r) for r in cursor.fetchall()]

    # Recent activity (last 10)
    cursor.execute("""
        SELECT action, entity_type, entity_id, actor, details, created_at
        FROM kb_activity_log ORDER BY created_at DESC LIMIT 10
    """)
    recent_activity = [dict_from_row(r) for r in cursor.fetchall()]

    conn.close()

    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'agents': agents,
        'locked_files': all_locked,
        'task_summary': task_summary,
        'active_tasks': active_tasks,
        'available_tasks': available_tasks,
        'recent_work': recent_work,
        'recent_activity': recent_activity
    })


# ============================================
# HELPERS
# ============================================

def _log_activity(action, entity_type, entity_id, actor, details):
    """Internal helper to log activity."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO kb_activity_log (action, entity_type, entity_id, actor, details)
            VALUES (?, ?, ?, ?, ?)
        """, (action, entity_type, entity_id, actor, json.dumps(details)))
        conn.commit()
        conn.close()
    except Exception:
        pass


# ============================================
# ENSURE EXTENDED TABLES
# ============================================

def _ensure_extended_tables():
    """Create extended tables for evolution features."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.executescript("""
        -- Agent skill matrix
        CREATE TABLE IF NOT EXISTS kb_agent_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            skill TEXT NOT NULL,
            score REAL DEFAULT 0.0,
            tasks_completed INTEGER DEFAULT 0,
            last_used DATETIME DEFAULT (datetime('now')),
            UNIQUE(agent_id, skill)
        );

        -- Agent memory (per-agent persistent context)
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

        CREATE INDEX IF NOT EXISTS idx_agent_skills_agent ON kb_agent_skills(agent_id);
        CREATE INDEX IF NOT EXISTS idx_agent_memory_agent ON kb_agent_memory(agent_id);
    """)

    # Add retrospective columns to work_logs if missing
    try:
        cursor.execute("SELECT retrospective FROM kb_work_logs LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE kb_work_logs ADD COLUMN retrospective TEXT")
        cursor.execute("ALTER TABLE kb_work_logs ADD COLUMN lesson_learned TEXT")
        cursor.execute("ALTER TABLE kb_work_logs ADD COLUMN tags TEXT DEFAULT '[]'")

    conn.commit()
    conn.close()


_ensure_extended_tables()


# ============================================
# 1. PREFLIGHT CHECK
# ============================================

@kb_bp.route('/preflight/<task_id>', methods=['GET'])
def preflight_check(task_id):
    """Pre-task check: returns relevant lessons, decisions, conflicts, and warnings."""
    conn = get_db()
    cursor = conn.cursor()

    # Get the task
    cursor.execute("SELECT * FROM kb_tasks WHERE task_id = ?", (task_id,))
    task = cursor.fetchone()
    if not task:
        conn.close()
        return jsonify({'success': False, 'error': 'Task not found'}), 404

    task = dict_from_row(task)
    title = (task.get('title') or '').lower()
    desc = (task.get('description') or '').lower()
    search_text = f"{title} {desc}"

    # Extract keywords (words > 3 chars, skip common words)
    stop_words = {'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'been', 'will', 'should', 'could', 'would'}
    keywords = [w for w in search_text.split() if len(w) > 3 and w not in stop_words]

    # Search lessons (kb_research) for relevant findings
    lessons = []
    search_keywords = keywords[:5]  # Limit to 5 keywords
    if search_keywords:
        keyword_clauses = " OR ".join(["topic LIKE ? OR findings LIKE ?" for _ in search_keywords])
        keyword_params = []
        for kw in search_keywords:
            keyword_params.extend([f'%{kw}%', f'%{kw}%'])
        cursor.execute(f"""
            SELECT research_id, topic, findings, tags FROM kb_research
            WHERE {keyword_clauses}
            ORDER BY created_at DESC LIMIT 5
        """, keyword_params)
        lessons = [dict_from_row(r) for r in cursor.fetchall()]

    # Search decisions for relevant context
    decisions = []
    decision_keywords = keywords[:3]
    if decision_keywords:
        decision_clauses = " OR ".join(["title LIKE ? OR decision LIKE ? OR context LIKE ?" for _ in decision_keywords])
        decision_params = []
        for kw in decision_keywords:
            decision_params.extend([f'%{kw}%', f'%{kw}%', f'%{kw}%'])
        cursor.execute(f"""
            SELECT decision_id, title, decision, rationale, category FROM kb_decisions
            WHERE {decision_clauses}
            ORDER BY made_at DESC LIMIT 5
        """, decision_params)
        decisions = [dict_from_row(r) for r in cursor.fetchall()]

    # Check for file conflicts (locked files)
    cursor.execute("SELECT agent_id, locked_files, working_on FROM kb_agents WHERE status = 'active'")
    agents = cursor.fetchall()
    locked_files = {}
    for a in agents:
        a = dict_from_row(a)
        try:
            files = json.loads(a.get('locked_files', '[]'))
            for f in files:
                locked_files[f] = a['agent_id']
        except (json.JSONDecodeError, TypeError):
            pass

    # Check task dependencies
    blocked_by = []
    deps_str = task.get('dependencies')
    if deps_str:
        try:
            deps = json.loads(deps_str)
            for dep_id in deps:
                cursor.execute("SELECT task_id, title, status FROM kb_tasks WHERE task_id = ?", (dep_id,))
                dep = cursor.fetchone()
                if dep:
                    dep = dict_from_row(dep)
                    if dep['status'] not in ('done', 'cancelled'):
                        blocked_by.append(dep)
        except (json.JSONDecodeError, TypeError):
            pass

    # Warnings
    warnings = []
    if blocked_by:
        warnings.append(f"BLOCKED: {len(blocked_by)} dependency task(s) not completed")
    if locked_files:
        warnings.append(f"CAUTION: {len(locked_files)} file(s) locked by other agents")
    if lessons:
        warnings.append(f"LEARN: {len(lessons)} relevant lesson(s) found — review before starting")

    conn.close()

    return jsonify({
        'success': True,
        'task': {'task_id': task['task_id'], 'title': task['title'], 'status': task['status']},
        'warnings': warnings,
        'relevant_lessons': lessons,
        'relevant_decisions': decisions,
        'locked_files': locked_files,
        'blocked_by': blocked_by,
        'preflight_status': 'CLEAR' if not blocked_by else 'BLOCKED'
    })


# ============================================
# 2. LESSONS LOOKUP
# ============================================

@kb_bp.route('/lessons', methods=['GET'])
def search_lessons():
    """Search lessons learned by topic, tags, or keyword."""
    topic = request.args.get('topic')
    keyword = request.args.get('keyword', request.args.get('q'))
    tags = request.args.get('tags')
    limit = request.args.get('limit', 20, type=int)

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM kb_research WHERE 1=1"
    params = []

    if topic:
        query += " AND topic LIKE ?"
        params.append(f'%{topic}%')
    if keyword:
        query += " AND (topic LIKE ? OR findings LIKE ? OR summary LIKE ?)"
        params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])
    if tags:
        for tag in tags.split(','):
            query += " AND tags LIKE ?"
            params.append(f'%{tag.strip()}%')

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    lessons = [dict_from_row(r) for r in rows]
    return jsonify({'success': True, 'count': len(lessons), 'lessons': lessons})


# ============================================
# 3. TASK CONFLICTS CHECK
# ============================================

@kb_bp.route('/tasks/<task_id>/conflicts', methods=['GET'])
def check_task_conflicts(task_id):
    """Check for conflicts: locked files, blocking dependencies, agent overlap."""
    conn = get_db()
    cursor = conn.cursor()

    # Get the task
    cursor.execute("SELECT * FROM kb_tasks WHERE task_id = ?", (task_id,))
    task = cursor.fetchone()
    if not task:
        conn.close()
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    task = dict_from_row(task)

    conflicts = []

    # Check dependencies not done
    deps_str = task.get('dependencies')
    if deps_str:
        try:
            deps = json.loads(deps_str)
            for dep_id in deps:
                cursor.execute("SELECT task_id, title, status, assigned_to FROM kb_tasks WHERE task_id = ?", (dep_id,))
                dep = cursor.fetchone()
                if dep:
                    dep = dict_from_row(dep)
                    if dep['status'] not in ('done', 'cancelled'):
                        conflicts.append({
                            'type': 'dependency',
                            'severity': 'blocking',
                            'detail': f"Depends on {dep['task_id']} ({dep['title']}) — status: {dep['status']}"
                        })
        except (json.JSONDecodeError, TypeError):
            pass

    # Check if another agent is working on same task
    cursor.execute("""
        SELECT agent_id, working_on_task_id FROM kb_agents
        WHERE status = 'active' AND working_on_task_id = ? AND agent_id != ?
    """, (task_id, task.get('assigned_to', '')))
    for row in cursor.fetchall():
        r = dict_from_row(row)
        conflicts.append({
            'type': 'agent_overlap',
            'severity': 'warning',
            'detail': f"Agent {r['agent_id']} is also working on this task"
        })

    # Check locked files overlap (if task has related files via code_changes)
    code_changes = task.get('code_changes')
    if code_changes:
        try:
            task_files = json.loads(code_changes)
        except (json.JSONDecodeError, TypeError):
            task_files = []

        cursor.execute("SELECT agent_id, locked_files FROM kb_agents WHERE status = 'active'")
        for row in cursor.fetchall():
            r = dict_from_row(row)
            try:
                locked = json.loads(r.get('locked_files', '[]'))
                for f in locked:
                    if f in task_files:
                        conflicts.append({
                            'type': 'file_lock',
                            'severity': 'blocking',
                            'detail': f"File '{f}' is locked by {r['agent_id']}"
                        })
            except (json.JSONDecodeError, TypeError):
                pass

    conn.close()

    blocking = [c for c in conflicts if c['severity'] == 'blocking']
    return jsonify({
        'success': True,
        'task_id': task_id,
        'conflicts': conflicts,
        'blocking_count': len(blocking),
        'can_proceed': len(blocking) == 0
    })


# ============================================
# 4. AGENT SKILL MATRIX
# ============================================

@kb_bp.route('/agents/<agent_id>/skills', methods=['GET'])
def get_agent_skills(agent_id):
    """Get agent's skill scores."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT skill, score, tasks_completed, last_used
        FROM kb_agent_skills WHERE agent_id = ?
        ORDER BY score DESC
    """, (agent_id,))
    skills = [dict_from_row(r) for r in cursor.fetchall()]

    conn.close()
    return jsonify({'success': True, 'agent_id': agent_id, 'skills': skills})


@kb_bp.route('/agents/<agent_id>/skills', methods=['POST'])
def update_agent_skill(agent_id):
    """Update or add an agent skill score."""
    data = request.get_json()
    skill = data.get('skill')
    if not skill:
        return jsonify({'success': False, 'error': 'skill is required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO kb_agent_skills (agent_id, skill, score, tasks_completed, last_used)
        VALUES (?, ?, ?, 1, datetime('now'))
        ON CONFLICT(agent_id, skill) DO UPDATE SET
            score = CASE
                WHEN ? > 0 THEN ?
                ELSE MIN(kb_agent_skills.score + 0.1, 10.0)
            END,
            tasks_completed = kb_agent_skills.tasks_completed + 1,
            last_used = datetime('now')
    """, (agent_id, skill, data.get('score', 0), data.get('score', 0), data.get('score', 0)))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'Skill {skill} updated for {agent_id}'})


@kb_bp.route('/skills/matrix', methods=['GET'])
def skill_matrix():
    """Get full skill matrix across all agents."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.agent_id, a.role, s.skill, s.score, s.tasks_completed
        FROM kb_agent_skills s
        LEFT JOIN kb_agents a ON s.agent_id = a.agent_id
        ORDER BY s.skill, s.score DESC
    """)
    rows = [dict_from_row(r) for r in cursor.fetchall()]

    # Pivot into matrix format
    matrix = {}
    all_skills = set()
    for r in rows:
        agent = r['agent_id']
        if agent not in matrix:
            matrix[agent] = {'role': r.get('role', ''), 'skills': {}}
        matrix[agent]['skills'][r['skill']] = {'score': r['score'], 'tasks': r['tasks_completed']}
        all_skills.add(r['skill'])

    conn.close()
    return jsonify({
        'success': True,
        'matrix': matrix,
        'all_skills': sorted(all_skills),
        'agent_count': len(matrix)
    })


# ============================================
# 5. AGENT MEMORY (Cross-Session)
# ============================================

@kb_bp.route('/memory/<agent_id>', methods=['GET'])
def get_agent_memory(agent_id):
    """Get agent's persistent memory."""
    category = request.args.get('category')

    conn = get_db()
    cursor = conn.cursor()

    if category:
        cursor.execute("""
            SELECT memory_key, content, category, updated_at
            FROM kb_agent_memory WHERE agent_id = ? AND category = ?
            ORDER BY updated_at DESC
        """, (agent_id, category))
    else:
        cursor.execute("""
            SELECT memory_key, content, category, updated_at
            FROM kb_agent_memory WHERE agent_id = ?
            ORDER BY updated_at DESC
        """, (agent_id,))

    memories = [dict_from_row(r) for r in cursor.fetchall()]
    conn.close()

    return jsonify({'success': True, 'agent_id': agent_id, 'count': len(memories), 'memories': memories})


@kb_bp.route('/memory/<agent_id>', methods=['POST'])
def save_agent_memory(agent_id):
    """Save or update agent memory entry."""
    data = request.get_json()

    if not data.get('key') or not data.get('content'):
        return jsonify({'success': False, 'error': 'key and content are required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO kb_agent_memory (agent_id, memory_key, content, category, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        ON CONFLICT(agent_id, memory_key) DO UPDATE SET
            content = excluded.content,
            category = excluded.category,
            updated_at = datetime('now')
    """, (agent_id, data['key'], data['content'], data.get('category', 'general')))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f"Memory '{data['key']}' saved for {agent_id}"})


@kb_bp.route('/memory/<agent_id>/<memory_key>', methods=['DELETE'])
def delete_agent_memory(agent_id, memory_key):
    """Delete a specific memory entry."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kb_agent_memory WHERE agent_id = ? AND memory_key = ?", (agent_id, memory_key))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f"Memory '{memory_key}' deleted for {agent_id}"})


# ============================================
# 6. RETROSPECTIVES (Enhanced Work Logs)
# ============================================

# Override the work-logs POST to support retrospective fields
@kb_bp.route('/work-logs', methods=['POST'])
def create_work_log_v2():
    """Log completed work with optional retrospective and lesson learned."""
    data = request.get_json()

    if not data.get('agent_id') or not data.get('action'):
        return jsonify({'success': False, 'error': 'agent_id and action are required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO kb_work_logs (agent_id, task_id, action, summary, files_changed,
                                   commit_hash, duration_minutes, retrospective, lesson_learned, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('agent_id'),
        data.get('task_id'),
        data.get('action'),
        data.get('summary'),
        json.dumps(data.get('files_changed', [])),
        data.get('commit_hash'),
        data.get('duration_minutes'),
        data.get('retrospective'),
        data.get('lesson_learned'),
        json.dumps(data.get('tags', []))
    ))
    conn.commit()
    log_id = cursor.lastrowid

    # If lesson_learned is provided, auto-create a research entry
    if data.get('lesson_learned'):
        cursor.execute("SELECT MAX(CAST(SUBSTR(research_id, 2) AS INTEGER)) FROM kb_research WHERE research_id LIKE 'R%'")
        max_id = cursor.fetchone()[0] or 0
        research_id = f"R{max_id + 1:03d}"

        cursor.execute("""
            INSERT INTO kb_research (research_id, topic, findings, status, tags, researcher)
            VALUES (?, ?, ?, 'completed', ?, ?)
        """, (
            research_id,
            f"Lesson from {data.get('task_id', 'work')}: {data.get('action', '')}",
            data['lesson_learned'],
            json.dumps(data.get('tags', ['lesson', 'auto-captured'])),
            data.get('agent_id')
        ))
        conn.commit()

    # Auto-update skill matrix based on tags
    if data.get('tags') and data.get('agent_id'):
        tags = data['tags'] if isinstance(data['tags'], list) else []
        for tag in tags:
            cursor.execute("""
                INSERT INTO kb_agent_skills (agent_id, skill, score, tasks_completed, last_used)
                VALUES (?, ?, 1.0, 1, datetime('now'))
                ON CONFLICT(agent_id, skill) DO UPDATE SET
                    score = MIN(kb_agent_skills.score + 0.1, 10.0),
                    tasks_completed = kb_agent_skills.tasks_completed + 1,
                    last_used = datetime('now')
            """, (data['agent_id'], tag))
        conn.commit()

    conn.close()

    return jsonify({'success': True, 'log_id': log_id, 'message': 'Work logged'})


# ============================================
# 7. POST-TASK HEALTH CHECK
# ============================================

@kb_bp.route('/health-check', methods=['POST'])
def post_task_health_check():
    """Run post-task health verification checks."""
    data = request.get_json()
    agent_id = data.get('agent_id')
    task_id = data.get('task_id')
    checks = data.get('checks', [])

    results = []

    conn = get_db()
    cursor = conn.cursor()

    for check in checks:
        check_type = check.get('type')
        result = {'type': check_type, 'status': 'unknown'}

        if check_type == 'task_complete':
            cursor.execute("SELECT status FROM kb_tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            result['status'] = 'pass' if row and row['status'] == 'done' else 'fail'
            result['detail'] = f"Task status: {row['status']}" if row else 'Task not found'

        elif check_type == 'files_unlocked':
            cursor.execute("SELECT locked_files FROM kb_agents WHERE agent_id = ?", (agent_id,))
            row = cursor.fetchone()
            if row:
                locked = json.loads(row['locked_files'] or '[]')
                result['status'] = 'pass' if not locked else 'fail'
                result['detail'] = f"{len(locked)} files still locked" if locked else 'All files released'
            else:
                result['status'] = 'skip'
                result['detail'] = 'Agent not found'

        elif check_type == 'work_logged':
            cursor.execute("""
                SELECT COUNT(*) as cnt FROM kb_work_logs
                WHERE agent_id = ? AND task_id = ?
            """, (agent_id, task_id))
            cnt = cursor.fetchone()['cnt']
            result['status'] = 'pass' if cnt > 0 else 'fail'
            result['detail'] = f"{cnt} work log(s) found"

        elif check_type == 'no_blocking':
            cursor.execute("""
                SELECT COUNT(*) as cnt FROM kb_tasks
                WHERE status NOT IN ('done', 'cancelled') AND dependencies LIKE ?
            """, (f'%{task_id}%',))
            cnt = cursor.fetchone()['cnt']
            result['status'] = 'info'
            result['detail'] = f"{cnt} task(s) were waiting on this task"

        elif check_type == 'retrospective':
            cursor.execute("""
                SELECT retrospective FROM kb_work_logs
                WHERE agent_id = ? AND task_id = ? AND retrospective IS NOT NULL
                ORDER BY created_at DESC LIMIT 1
            """, (agent_id, task_id))
            row = cursor.fetchone()
            result['status'] = 'pass' if row else 'warn'
            result['detail'] = 'Retrospective recorded' if row else 'No retrospective — consider adding one'

        results.append(result)

    conn.close()

    passed = sum(1 for r in results if r['status'] == 'pass')
    total = len(results)

    return jsonify({
        'success': True,
        'agent_id': agent_id,
        'task_id': task_id,
        'results': results,
        'summary': f"{passed}/{total} checks passed",
        'all_clear': all(r['status'] in ('pass', 'info', 'skip') for r in results)
    })
