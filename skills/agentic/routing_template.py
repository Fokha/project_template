"""
Routing Pattern Template
========================
Classify input and route to specialized handlers.

Use when:
- Different types of requests need different handling
- You want modular, maintainable code
- Tasks fall into distinct categories

Placeholders:
- {{ROUTER_NAME}}: Name of this router
- {{ROUTE_COUNT}}: Number of routes
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class Route:
    """A single route definition."""
    name: str
    description: str
    handler: Callable[[Dict[str, Any]], Any]
    patterns: List[str] = field(default_factory=list)  # Regex patterns
    keywords: List[str] = field(default_factory=list)  # Keyword triggers
    priority: int = 0  # Higher = checked first


@dataclass
class RoutingResult:
    """Result of routing decision."""
    route_name: str
    confidence: float
    reasoning: str
    handler_result: Optional[Any] = None


class BaseRouter(ABC):
    """Abstract base for routing implementations."""

    @abstractmethod
    def classify(self, input_data: Dict[str, Any]) -> Tuple[str, float, str]:
        """
        Classify input and return (route_name, confidence, reasoning).
        """
        pass


class RuleBasedRouter(BaseRouter):
    """Route based on patterns and keywords."""

    def __init__(self, name: str):
        self.name = name
        self.routes: Dict[str, Route] = {}
        self.default_route: Optional[str] = None

    def add_route(self, route: Route) -> "RuleBasedRouter":
        """Add a route."""
        self.routes[route.name] = route
        return self

    def set_default(self, route_name: str) -> "RuleBasedRouter":
        """Set default route for unmatched inputs."""
        self.default_route = route_name
        return self

    def classify(self, input_data: Dict[str, Any]) -> Tuple[str, float, str]:
        """Classify based on patterns and keywords."""
        text = str(input_data.get("text", input_data.get("query", "")))
        text_lower = text.lower()

        # Sort by priority (descending)
        sorted_routes = sorted(
            self.routes.values(),
            key=lambda r: r.priority,
            reverse=True
        )

        for route in sorted_routes:
            # Check patterns
            for pattern in route.patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return (route.name, 0.9, f"Pattern match: {pattern}")

            # Check keywords
            for keyword in route.keywords:
                if keyword.lower() in text_lower:
                    return (route.name, 0.8, f"Keyword match: {keyword}")

        # Default route
        if self.default_route:
            return (self.default_route, 0.5, "Default route (no match)")

        return ("unknown", 0.0, "No matching route")

    def route(self, input_data: Dict[str, Any]) -> RoutingResult:
        """Classify and execute handler."""
        route_name, confidence, reasoning = self.classify(input_data)

        result = RoutingResult(
            route_name=route_name,
            confidence=confidence,
            reasoning=reasoning
        )

        if route_name in self.routes:
            handler = self.routes[route_name].handler
            result.handler_result = handler(input_data)

        return result


class LLMRouter(BaseRouter):
    """Route using LLM classification."""

    def __init__(self, name: str, llm_client: Any):
        self.name = name
        self.llm_client = llm_client
        self.routes: Dict[str, Route] = {}

    def add_route(self, route: Route) -> "LLMRouter":
        """Add a route."""
        self.routes[route.name] = route
        return self

    def classify(self, input_data: Dict[str, Any]) -> Tuple[str, float, str]:
        """Classify using LLM."""
        text = str(input_data.get("text", input_data.get("query", "")))

        # Build classification prompt
        route_descriptions = "\n".join([
            f"- {name}: {route.description}"
            for name, route in self.routes.items()
        ])

        prompt = f"""Classify this input into one of the following categories:

{route_descriptions}

Input: {text}

Respond with JSON:
{{"category": "category_name", "confidence": 0.0-1.0, "reasoning": "..."}}"""

        response = self.llm_client.generate(prompt)

        try:
            import json
            result = json.loads(response)
            return (
                result.get("category", "unknown"),
                result.get("confidence", 0.5),
                result.get("reasoning", "LLM classification")
            )
        except:
            return ("unknown", 0.0, "Failed to parse LLM response")


class TradingRouter(RuleBasedRouter):
    """Pre-built router for trading tasks."""

    def __init__(self):
        super().__init__("trading_router")

        # Signal requests
        self.add_route(Route(
            name="signal",
            description="Trading signal generation",
            handler=self._handle_signal,
            patterns=[r"signal\s+for", r"get\s+signal", r"trade\s+recommendation"],
            keywords=["signal", "entry", "buy or sell"],
            priority=10
        ))

        # Analysis requests
        self.add_route(Route(
            name="analysis",
            description="Market analysis",
            handler=self._handle_analysis,
            patterns=[r"analyz[e|is]", r"what.*(think|see)", r"market\s+view"],
            keywords=["analysis", "analyze", "outlook", "view"],
            priority=8
        ))

        # Price queries
        self.add_route(Route(
            name="price",
            description="Price information",
            handler=self._handle_price,
            patterns=[r"(what|current|latest).*price", r"price\s+of"],
            keywords=["price", "quote", "rate"],
            priority=5
        ))

        # Risk queries
        self.add_route(Route(
            name="risk",
            description="Risk assessment",
            handler=self._handle_risk,
            patterns=[r"risk\s+(of|for)", r"position\s+size"],
            keywords=["risk", "exposure", "position size"],
            priority=7
        ))

        # News queries
        self.add_route(Route(
            name="news",
            description="News and events",
            handler=self._handle_news,
            patterns=[r"(news|events|calendar)", r"what.*happening"],
            keywords=["news", "events", "calendar", "blackout"],
            priority=6
        ))

        # Default
        self.set_default("general")
        self.add_route(Route(
            name="general",
            description="General queries",
            handler=self._handle_general,
            priority=0
        ))

    def _handle_signal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "signal", "status": "pending", "data": input_data}

    def _handle_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "analysis", "status": "pending", "data": input_data}

    def _handle_price(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "price", "status": "pending", "data": input_data}

    def _handle_risk(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "risk", "status": "pending", "data": input_data}

    def _handle_news(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "news", "status": "pending", "data": input_data}

    def _handle_general(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "general", "status": "pending", "data": input_data}


# Example usage
if __name__ == "__main__":
    router = TradingRouter()

    # Test various inputs
    test_inputs = [
        {"text": "Get me a signal for XAUUSD"},
        {"text": "What's the current price of gold?"},
        {"text": "Analyze the EUR/USD pair"},
        {"text": "What's my risk exposure?"},
        {"text": "Any news events today?"},
        {"text": "Hello, how are you?"},
    ]

    for input_data in test_inputs:
        result = router.route(input_data)
        print(f"Input: {input_data['text']}")
        print(f"  Route: {result.route_name} ({result.confidence:.0%})")
        print(f"  Reason: {result.reasoning}")
        print()
