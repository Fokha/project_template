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
    except:
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
