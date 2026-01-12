"""
Context Injection Pattern Template
==================================
Inject relevant context into prompts dynamically.

Use when:
- Historical context needed
- RAG (Retrieval Augmented Generation) wanted
- Personalization required

Placeholders:
- {{MAX_CONTEXT_TOKENS}}: Maximum context size
- {{RETRIEVAL_TOP_K}}: Number of items to retrieve
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class ContextItem:
    """A piece of context."""
    id: str
    content: str
    source: str
    relevance: float = 0.5
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InjectedContext:
    """Context ready for injection."""
    items: List[ContextItem]
    total_tokens: int
    truncated: bool = False


class ContextRetriever(ABC):
    """Abstract retriever for context."""

    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[ContextItem]:
        """Retrieve relevant context items."""
        pass


class KeywordRetriever(ContextRetriever):
    """Simple keyword-based retrieval."""

    def __init__(self):
        self.documents: List[ContextItem] = []

    def add_document(self, item: ContextItem):
        """Add a document to the store."""
        self.documents.append(item)

    def retrieve(self, query: str, top_k: int = 5) -> List[ContextItem]:
        """Retrieve by keyword match."""
        query_terms = set(query.lower().split())
        scored = []

        for doc in self.documents:
            doc_terms = set(doc.content.lower().split())
            overlap = len(query_terms & doc_terms)
            score = overlap / len(query_terms) if query_terms else 0
            if score > 0:
                doc_copy = ContextItem(
                    id=doc.id,
                    content=doc.content,
                    source=doc.source,
                    relevance=score,
                    timestamp=doc.timestamp,
                    metadata=doc.metadata
                )
                scored.append(doc_copy)

        # Sort by relevance and return top_k
        scored.sort(key=lambda x: x.relevance, reverse=True)
        return scored[:top_k]


class VectorRetriever(ContextRetriever):
    """Vector similarity-based retrieval."""

    def __init__(self, embedding_fn: Callable[[str], List[float]]):
        self.embedding_fn = embedding_fn
        self.documents: List[ContextItem] = []
        self.embeddings: List[List[float]] = []

    def add_document(self, item: ContextItem):
        """Add a document with its embedding."""
        self.documents.append(item)
        self.embeddings.append(self.embedding_fn(item.content))

    def retrieve(self, query: str, top_k: int = 5) -> List[ContextItem]:
        """Retrieve by vector similarity."""
        query_embedding = self.embedding_fn(query)
        scored = []

        for i, doc in enumerate(self.documents):
            similarity = self._cosine_similarity(query_embedding, self.embeddings[i])
            doc_copy = ContextItem(
                id=doc.id,
                content=doc.content,
                source=doc.source,
                relevance=similarity,
                timestamp=doc.timestamp,
                metadata=doc.metadata
            )
            scored.append(doc_copy)

        scored.sort(key=lambda x: x.relevance, reverse=True)
        return scored[:top_k]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0


class ContextInjector:
    """
    Inject context into prompts.

    Example:
        injector = ContextInjector(retriever, max_tokens=1000)
        prompt = injector.inject(
            "What's the XAUUSD outlook?",
            template="Context:\n{context}\n\nQuestion: {query}"
        )
    """

    def __init__(
        self,
        retriever: ContextRetriever,
        max_tokens: int = 2000,
        min_relevance: float = 0.1
    ):
        self.retriever = retriever
        self.max_tokens = max_tokens
        self.min_relevance = min_relevance

    def inject(
        self,
        query: str,
        template: str = "{context}\n\n{query}",
        top_k: int = 5
    ) -> str:
        """Inject context into query."""
        context = self.get_context(query, top_k)
        context_str = self._format_context(context)

        return template.format(
            context=context_str,
            query=query
        )

    def get_context(self, query: str, top_k: int = 5) -> InjectedContext:
        """Get relevant context for a query."""
        items = self.retriever.retrieve(query, top_k)

        # Filter by relevance
        items = [i for i in items if i.relevance >= self.min_relevance]

        # Truncate to max tokens
        total_tokens = 0
        truncated = False
        selected = []

        for item in items:
            item_tokens = len(item.content.split())  # Simple token estimate
            if total_tokens + item_tokens <= self.max_tokens:
                selected.append(item)
                total_tokens += item_tokens
            else:
                truncated = True
                break

        return InjectedContext(
            items=selected,
            total_tokens=total_tokens,
            truncated=truncated
        )

    def _format_context(self, context: InjectedContext) -> str:
        """Format context for injection."""
        if not context.items:
            return "[No relevant context found]"

        parts = []
        for item in context.items:
            source_info = f"[{item.source}]" if item.source else ""
            parts.append(f"{source_info} {item.content}")

        return "\n\n".join(parts)


class TradingContextInjector(ContextInjector):
    """Context injector specialized for trading."""

    def __init__(self, retriever: ContextRetriever):
        super().__init__(retriever, max_tokens=1500, min_relevance=0.2)
        self.market_data: Dict[str, Any] = {}
        self.recent_signals: List[Dict] = []

    def set_market_data(self, data: Dict[str, Any]):
        """Update current market data."""
        self.market_data = data

    def add_signal(self, signal: Dict):
        """Add a recent signal."""
        self.recent_signals.append(signal)
        # Keep only last 10
        self.recent_signals = self.recent_signals[-10:]

    def inject(
        self,
        query: str,
        template: str = None,
        top_k: int = 5
    ) -> str:
        """Inject trading context."""
        # Build comprehensive context
        context_parts = []

        # Market data
        if self.market_data:
            context_parts.append(f"Current Market Data:\n{json.dumps(self.market_data, indent=2)}")

        # Recent signals
        if self.recent_signals:
            signals_str = "\n".join([
                f"- {s.get('symbol', 'N/A')}: {s.get('direction', 'N/A')} ({s.get('confidence', 0):.0%})"
                for s in self.recent_signals[-5:]
            ])
            context_parts.append(f"Recent Signals:\n{signals_str}")

        # Retrieved context
        retrieved = self.get_context(query, top_k)
        if retrieved.items:
            retrieved_str = self._format_context(retrieved)
            context_parts.append(f"Relevant Information:\n{retrieved_str}")

        full_context = "\n\n---\n\n".join(context_parts)

        if template:
            return template.format(context=full_context, query=query)
        else:
            return f"""Context:
{full_context}

Query: {query}"""


class ConversationContextManager:
    """Manage conversation context with memory."""

    def __init__(self, max_history: int = 10):
        self.history: List[Dict[str, str]] = []
        self.max_history = max_history
        self.user_preferences: Dict[str, Any] = {}

    def add_turn(self, role: str, content: str):
        """Add a conversation turn."""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Trim if needed
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def set_preference(self, key: str, value: Any):
        """Set a user preference."""
        self.user_preferences[key] = value

    def get_context_string(self) -> str:
        """Get conversation context as string."""
        parts = []

        # User preferences
        if self.user_preferences:
            prefs_str = "\n".join(f"- {k}: {v}" for k, v in self.user_preferences.items())
            parts.append(f"User Preferences:\n{prefs_str}")

        # Recent history
        if self.history:
            history_str = "\n".join([
                f"{turn['role'].upper()}: {turn['content'][:200]}..."
                if len(turn['content']) > 200 else f"{turn['role'].upper()}: {turn['content']}"
                for turn in self.history[-5:]
            ])
            parts.append(f"Recent Conversation:\n{history_str}")

        return "\n\n".join(parts) if parts else "[No context]"


# Example usage
if __name__ == "__main__":
    # Create keyword retriever with documents
    retriever = KeywordRetriever()
    retriever.add_document(ContextItem(
        id="1",
        content="Gold prices tend to rise during economic uncertainty and inflation.",
        source="Market Analysis"
    ))
    retriever.add_document(ContextItem(
        id="2",
        content="XAUUSD is currently trading above its 200-day moving average.",
        source="Technical Report"
    ))
    retriever.add_document(ContextItem(
        id="3",
        content="Federal Reserve interest rate decisions significantly impact gold prices.",
        source="Fundamental Analysis"
    ))

    # Create injector
    injector = TradingContextInjector(retriever)
    injector.set_market_data({
        "XAUUSD": {"price": 2000, "change": 0.5},
        "DXY": {"price": 104.5, "change": -0.2}
    })
    injector.add_signal({"symbol": "XAUUSD", "direction": "BUY", "confidence": 0.75})

    # Generate enriched prompt
    prompt = injector.inject("What's the outlook for gold?")
    print("Generated Prompt:")
    print("-" * 50)
    print(prompt)
