# ═══════════════════════════════════════════════════════════════
# MEMORY MANAGEMENT PATTERN TEMPLATE
# Persistent context for AI agents across sessions
# ═══════════════════════════════════════════════════════════════
#
# Pattern: Store and retrieve context across conversations
# Use Case: Personal assistants, multi-session agents, learning systems
#
# ═══════════════════════════════════════════════════════════════

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


class MemoryType(Enum):
    """Types of memory storage."""
    SHORT_TERM = "short_term"     # Current session (hours)
    LONG_TERM = "long_term"       # Persistent (days/weeks)
    EPISODIC = "episodic"         # Specific events
    SEMANTIC = "semantic"         # Facts and knowledge
    PROCEDURAL = "procedural"     # How to do things


class MemoryPriority(Enum):
    """Memory importance levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Memory:
    """Single memory entry."""
    id: Optional[str]
    agent_id: str
    memory_type: MemoryType
    content: str
    context: Dict[str, Any]
    priority: MemoryPriority
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.id is None:
            self.id = self._generate_id()

    def _generate_id(self) -> str:
        content_hash = hashlib.md5(
            f"{self.agent_id}{self.content}{self.created_at}".encode()
        ).hexdigest()[:12]
        return f"mem_{content_hash}"


@dataclass
class MemoryQuery:
    """Query parameters for memory retrieval."""
    agent_id: str
    memory_types: Optional[List[MemoryType]] = None
    tags: Optional[List[str]] = None
    min_priority: MemoryPriority = MemoryPriority.LOW
    limit: int = 10
    include_expired: bool = False
    search_text: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# MEMORY STORE
# ═══════════════════════════════════════════════════════════════


class MemoryStore:
    """
    SQLite-based memory storage for agents.

    Features:
    - Multiple memory types (short-term, long-term, episodic, etc.)
    - Priority-based retrieval
    - Tag-based organization
    - Automatic expiration
    - Access tracking
    """

    def __init__(self, db_path: str = "data/agent_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    context TEXT,
                    priority INTEGER DEFAULT 2,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    tags TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_agent
                ON memories(agent_id, memory_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_expires
                ON memories(expires_at)
            """)
            conn.commit()
            logger.info(f"Memory store initialized: {self.db_path}")

    # ═══════════════════════════════════════════════════════════
    # WRITE OPERATIONS
    # ═══════════════════════════════════════════════════════════

    def store(self, memory: Memory) -> str:
        """Store a memory."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO memories
                (id, agent_id, memory_type, content, context, priority,
                 created_at, expires_at, access_count, last_accessed, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id,
                memory.agent_id,
                memory.memory_type.value,
                memory.content,
                json.dumps(memory.context),
                memory.priority.value,
                memory.created_at.isoformat(),
                memory.expires_at.isoformat() if memory.expires_at else None,
                memory.access_count,
                memory.last_accessed.isoformat() if memory.last_accessed else None,
                json.dumps(memory.tags),
            ))
            conn.commit()
            logger.debug(f"Stored memory: {memory.id}")
            return memory.id

    def store_short_term(
        self,
        agent_id: str,
        content: str,
        context: Dict = None,
        hours: int = 4
    ) -> str:
        """Store short-term memory (expires in hours)."""
        memory = Memory(
            id=None,
            agent_id=agent_id,
            memory_type=MemoryType.SHORT_TERM,
            content=content,
            context=context or {},
            priority=MemoryPriority.MEDIUM,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=hours),
        )
        return self.store(memory)

    def store_long_term(
        self,
        agent_id: str,
        content: str,
        context: Dict = None,
        priority: MemoryPriority = MemoryPriority.HIGH,
        days: int = 30
    ) -> str:
        """Store long-term memory (expires in days)."""
        memory = Memory(
            id=None,
            agent_id=agent_id,
            memory_type=MemoryType.LONG_TERM,
            content=content,
            context=context or {},
            priority=priority,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=days),
        )
        return self.store(memory)

    def store_fact(
        self,
        agent_id: str,
        fact: str,
        tags: List[str] = None
    ) -> str:
        """Store a semantic fact (no expiration)."""
        memory = Memory(
            id=None,
            agent_id=agent_id,
            memory_type=MemoryType.SEMANTIC,
            content=fact,
            context={},
            priority=MemoryPriority.HIGH,
            created_at=datetime.utcnow(),
            expires_at=None,  # Never expires
            tags=tags or [],
        )
        return self.store(memory)

    # ═══════════════════════════════════════════════════════════
    # READ OPERATIONS
    # ═══════════════════════════════════════════════════════════

    def retrieve(self, query: MemoryQuery) -> List[Memory]:
        """Retrieve memories matching query."""
        sql = """
            SELECT * FROM memories
            WHERE agent_id = ?
            AND priority >= ?
        """
        params = [query.agent_id, query.min_priority.value]

        if query.memory_types:
            types = [t.value for t in query.memory_types]
            placeholders = ",".join("?" * len(types))
            sql += f" AND memory_type IN ({placeholders})"
            params.extend(types)

        if not query.include_expired:
            sql += " AND (expires_at IS NULL OR expires_at > ?)"
            params.append(datetime.utcnow().isoformat())

        if query.search_text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.search_text}%")

        sql += " ORDER BY priority DESC, created_at DESC LIMIT ?"
        params.append(query.limit)

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()

            memories = []
            for row in rows:
                memory = self._row_to_memory(row)
                memories.append(memory)

                # Update access tracking
                self._update_access(conn, memory.id)

            return memories

    def get_recent(
        self,
        agent_id: str,
        limit: int = 5,
        memory_types: List[MemoryType] = None
    ) -> List[Memory]:
        """Get most recent memories for agent."""
        return self.retrieve(MemoryQuery(
            agent_id=agent_id,
            memory_types=memory_types,
            limit=limit,
        ))

    def get_by_tags(
        self,
        agent_id: str,
        tags: List[str],
        limit: int = 10
    ) -> List[Memory]:
        """Get memories matching any of the given tags."""
        all_memories = self.retrieve(MemoryQuery(
            agent_id=agent_id,
            limit=100,  # Get more, filter client-side
        ))

        matching = []
        for memory in all_memories:
            if any(tag in memory.tags for tag in tags):
                matching.append(memory)
                if len(matching) >= limit:
                    break

        return matching

    def get_context_summary(
        self,
        agent_id: str,
        max_tokens: int = 1000
    ) -> str:
        """
        Build a context summary from relevant memories.

        Useful for injecting into prompts.
        """
        memories = self.retrieve(MemoryQuery(
            agent_id=agent_id,
            min_priority=MemoryPriority.MEDIUM,
            limit=20,
        ))

        if not memories:
            return "No relevant context available."

        # Build summary
        lines = ["## Relevant Context\n"]
        total_chars = 0
        max_chars = max_tokens * 4  # Rough token estimate

        for memory in memories:
            line = f"- [{memory.memory_type.value}] {memory.content}\n"
            if total_chars + len(line) > max_chars:
                break
            lines.append(line)
            total_chars += len(line)

        return "".join(lines)

    # ═══════════════════════════════════════════════════════════
    # MAINTENANCE
    # ═══════════════════════════════════════════════════════════

    def cleanup_expired(self) -> int:
        """Remove expired memories."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "DELETE FROM memories WHERE expires_at < ?",
                (datetime.utcnow().isoformat(),)
            )
            conn.commit()
            count = cursor.rowcount
            if count > 0:
                logger.info(f"Cleaned up {count} expired memories")
            return count

    def forget(self, memory_id: str):
        """Delete a specific memory."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()

    def forget_all(self, agent_id: str, memory_type: MemoryType = None):
        """Delete all memories for an agent (optionally by type)."""
        with sqlite3.connect(str(self.db_path)) as conn:
            if memory_type:
                conn.execute(
                    "DELETE FROM memories WHERE agent_id = ? AND memory_type = ?",
                    (agent_id, memory_type.value)
                )
            else:
                conn.execute(
                    "DELETE FROM memories WHERE agent_id = ?",
                    (agent_id,)
                )
            conn.commit()

    def get_stats(self, agent_id: str = None) -> Dict:
        """Get memory statistics."""
        with sqlite3.connect(str(self.db_path)) as conn:
            if agent_id:
                total = conn.execute(
                    "SELECT COUNT(*) FROM memories WHERE agent_id = ?",
                    (agent_id,)
                ).fetchone()[0]
                by_type = conn.execute("""
                    SELECT memory_type, COUNT(*) FROM memories
                    WHERE agent_id = ? GROUP BY memory_type
                """, (agent_id,)).fetchall()
            else:
                total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
                by_type = conn.execute("""
                    SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type
                """).fetchall()

            return {
                "total_memories": total,
                "by_type": {row[0]: row[1] for row in by_type},
            }

    # ═══════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════

    def _row_to_memory(self, row) -> Memory:
        """Convert database row to Memory object."""
        return Memory(
            id=row["id"],
            agent_id=row["agent_id"],
            memory_type=MemoryType(row["memory_type"]),
            content=row["content"],
            context=json.loads(row["context"]) if row["context"] else {},
            priority=MemoryPriority(row["priority"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None,
            access_count=row["access_count"],
            last_accessed=datetime.fromisoformat(row["last_accessed"]) if row["last_accessed"] else None,
            tags=json.loads(row["tags"]) if row["tags"] else [],
        )

    def _update_access(self, conn, memory_id: str):
        """Update access tracking for a memory."""
        conn.execute("""
            UPDATE memories
            SET access_count = access_count + 1, last_accessed = ?
            WHERE id = ?
        """, (datetime.utcnow().isoformat(), memory_id))


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    # Initialize store
    store = MemoryStore("data/test_memory.db")

    agent_id = "trading_assistant"

    # Store different types of memories
    print("\n=== Storing Memories ===")

    # Short-term: Current session context
    store.store_short_term(
        agent_id=agent_id,
        content="User is interested in XAUUSD today",
        context={"symbol": "XAUUSD"},
        hours=4
    )

    # Long-term: User preferences
    store.store_long_term(
        agent_id=agent_id,
        content="User prefers conservative risk (1% per trade)",
        context={"risk_pct": 1.0},
        priority=MemoryPriority.HIGH,
        days=90
    )

    # Semantic: Facts
    store.store_fact(
        agent_id=agent_id,
        fact="User's account currency is USD",
        tags=["user", "account"]
    )

    store.store_fact(
        agent_id=agent_id,
        fact="User trades during London and NY sessions only",
        tags=["user", "schedule"]
    )

    # Retrieve memories
    print("\n=== Retrieving Memories ===")
    memories = store.get_recent(agent_id, limit=10)
    for mem in memories:
        print(f"  [{mem.memory_type.value}] {mem.content}")

    # Get context summary for prompt
    print("\n=== Context Summary ===")
    summary = store.get_context_summary(agent_id, max_tokens=500)
    print(summary)

    # Get stats
    print("\n=== Stats ===")
    stats = store.get_stats(agent_id)
    print(f"Total memories: {stats['total_memories']}")
    print(f"By type: {stats['by_type']}")
