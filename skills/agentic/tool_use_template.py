"""
Tool Use Pattern Template
=========================
Enable AI to call external tools and APIs.

Use when:
- AI needs access to real-time data
- External systems need to be queried
- Actions need to be executed

Placeholders:
- {{TOOL_NAME}}: Name of the tool
- {{API_BASE_URL}}: Base URL for API calls
"""

from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
import json
import re
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ToolParameter:
    """Parameter definition for a tool."""
    name: str
    type: str  # string, number, boolean, array, object
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[str]] = None


@dataclass
class Tool:
    """A tool that can be called by the AI."""
    name: str
    description: str
    parameters: List[ToolParameter]
    handler: Callable[..., Any]
    requires_confirmation: bool = False

    def to_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI-style function schema."""
        properties = {}
        required = []

        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description
            }
            if param.enum:
                prop["enum"] = param.enum
            properties[param.name] = prop
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }


@dataclass
class ToolCall:
    """A request to call a tool."""
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str = ""


@dataclass
class ToolResult:
    """Result of a tool call."""
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: float = 0


class ToolRegistry:
    """Registry of available tools."""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> "ToolRegistry":
        """Register a tool."""
        self.tools[tool.name] = tool
        return self

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """List all tool names."""
        return list(self.tools.keys())

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas for LLM."""
        return [tool.to_schema() for tool in self.tools.values()]

    def execute(
        self,
        tool_call: ToolCall,
        confirm_callback: Optional[Callable[[str, Dict], bool]] = None
    ) -> ToolResult:
        """Execute a tool call."""
        start_time = datetime.now()

        tool = self.get(tool_call.tool_name)
        if not tool:
            return ToolResult(
                success=False,
                result=None,
                error=f"Unknown tool: {tool_call.tool_name}"
            )

        # Check confirmation if required
        if tool.requires_confirmation:
            if confirm_callback:
                if not confirm_callback(tool_call.tool_name, tool_call.arguments):
                    return ToolResult(
                        success=False,
                        result=None,
                        error="User declined confirmation"
                    )
            else:
                logger.warning(f"Tool {tool_call.tool_name} requires confirmation but no callback provided")

        try:
            result = tool.handler(**tool_call.arguments)
            return ToolResult(
                success=True,
                result=result,
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e),
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )


class ToolUseAgent:
    """Agent that can use tools to complete tasks."""

    def __init__(self, registry: ToolRegistry, llm_client: Any):
        self.registry = registry
        self.llm_client = llm_client
        self.max_iterations = 10

    def run(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run the agent on a task."""
        messages = []
        context = context or {}
        iterations = 0

        # System prompt
        tools_desc = "\n".join([
            f"- {name}: {tool.description}"
            for name, tool in self.registry.tools.items()
        ])

        system_prompt = f"""You are an AI assistant with access to tools.

Available tools:
{tools_desc}

To use a tool, respond with:
TOOL_CALL: tool_name(arg1=value1, arg2=value2)

When you have the final answer, respond with:
FINAL_ANSWER: your answer here

Always think step by step and explain your reasoning."""

        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": task})

        while iterations < self.max_iterations:
            iterations += 1

            # Get LLM response
            response = self.llm_client.chat(messages)
            messages.append({"role": "assistant", "content": response})

            # Check for final answer
            if "FINAL_ANSWER:" in response:
                answer = response.split("FINAL_ANSWER:")[1].strip()
                return {
                    "success": True,
                    "answer": answer,
                    "iterations": iterations,
                    "messages": messages
                }

            # Check for tool call
            tool_match = re.search(r"TOOL_CALL:\s*(\w+)\((.*?)\)", response, re.DOTALL)
            if tool_match:
                tool_name = tool_match.group(1)
                args_str = tool_match.group(2)

                # Parse arguments
                args = self._parse_args(args_str)

                # Execute tool
                tool_call = ToolCall(tool_name=tool_name, arguments=args)
                result = self.registry.execute(tool_call)

                # Add result to messages
                result_msg = f"TOOL_RESULT for {tool_name}: "
                if result.success:
                    result_msg += json.dumps(result.result, default=str)
                else:
                    result_msg += f"ERROR: {result.error}"

                messages.append({"role": "user", "content": result_msg})
            else:
                # No tool call or final answer, add a nudge
                messages.append({
                    "role": "user",
                    "content": "Please either use a tool or provide FINAL_ANSWER."
                })

        return {
            "success": False,
            "error": "Max iterations reached",
            "iterations": iterations,
            "messages": messages
        }

    def _parse_args(self, args_str: str) -> Dict[str, Any]:
        """Parse tool arguments from string."""
        args = {}
        # Simple parsing - can be enhanced
        for part in args_str.split(","):
            if "=" in part:
                key, value = part.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                # Try to parse as JSON for complex values
                try:
                    value = json.loads(value)
                except:
                    pass
                args[key] = value
        return args


# Pre-built trading tools
def create_trading_tools(api_base_url: str) -> ToolRegistry:
    """Create a registry with common trading tools."""
    import requests

    registry = ToolRegistry()

    # Get signal tool
    def get_signal(symbol: str, timeframe: str = "H1") -> Dict:
        response = requests.get(
            f"{api_base_url}/predict/signal",
            params={"symbol": symbol, "timeframe": timeframe},
            timeout=30
        )
        return response.json()

    registry.register(Tool(
        name="get_signal",
        description="Get a trading signal for a symbol",
        parameters=[
            ToolParameter("symbol", "string", "Trading symbol (e.g., XAUUSD)", required=True),
            ToolParameter("timeframe", "string", "Timeframe", required=False, default="H1",
                         enum=["M5", "M15", "M30", "H1", "H4", "D1"])
        ],
        handler=get_signal
    ))

    # Get price tool
    def get_price(symbol: str) -> Dict:
        response = requests.get(
            f"{api_base_url}/market/price/{symbol}",
            timeout=10
        )
        return response.json()

    registry.register(Tool(
        name="get_price",
        description="Get current price for a symbol",
        parameters=[
            ToolParameter("symbol", "string", "Trading symbol", required=True)
        ],
        handler=get_price
    ))

    # Get news tool
    def get_news(symbol: str = "") -> Dict:
        response = requests.get(
            f"{api_base_url}/news/calendar",
            params={"symbol": symbol} if symbol else {},
            timeout=30
        )
        return response.json()

    registry.register(Tool(
        name="get_news",
        description="Get economic news and calendar events",
        parameters=[
            ToolParameter("symbol", "string", "Filter by symbol", required=False)
        ],
        handler=get_news
    ))

    # Check blackout tool
    def check_blackout(symbol: str) -> Dict:
        response = requests.get(
            f"{api_base_url}/market/blackout",
            params={"symbol": symbol},
            timeout=10
        )
        return response.json()

    registry.register(Tool(
        name="check_blackout",
        description="Check if symbol is in news blackout period",
        parameters=[
            ToolParameter("symbol", "string", "Trading symbol", required=True)
        ],
        handler=check_blackout
    ))

    return registry


# Example usage
if __name__ == "__main__":
    # Create mock registry for testing
    registry = ToolRegistry()

    registry.register(Tool(
        name="get_weather",
        description="Get current weather for a location",
        parameters=[
            ToolParameter("location", "string", "City name", required=True)
        ],
        handler=lambda location: {"location": location, "temp": 72, "condition": "sunny"}
    ))

    registry.register(Tool(
        name="calculate",
        description="Perform a calculation",
        parameters=[
            ToolParameter("expression", "string", "Math expression", required=True)
        ],
        handler=lambda expression: {"result": eval(expression)}
    ))

    # Test execution
    result = registry.execute(ToolCall(
        tool_name="get_weather",
        arguments={"location": "New York"}
    ))
    print(f"Weather result: {result}")

    result = registry.execute(ToolCall(
        tool_name="calculate",
        arguments={"expression": "2 + 2 * 3"}
    ))
    print(f"Calculate result: {result}")
