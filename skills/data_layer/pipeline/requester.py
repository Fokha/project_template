# fokha_data/pipeline/requester.py
# =============================================================================
# TEMPLATE: Data Requester
# =============================================================================
# Handles data requests from various sources (APIs, files, databases).
# First stage in the data pipeline.
# =============================================================================

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable, List
from enum import Enum
import json


class RequestMethod(Enum):
    """HTTP request methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class SourceType(Enum):
    """Types of data sources."""
    HTTP = "http"
    FILE = "file"
    DATABASE = "database"
    MEMORY = "memory"
    CUSTOM = "custom"


@dataclass
class RequestConfig:
    """
    Configuration for a data request.

    Attributes:
        source_type: Type of data source
        url: URL or path for the source
        method: HTTP method (for HTTP sources)
        headers: HTTP headers
        params: Query parameters
        body: Request body
        timeout_ms: Request timeout
        retry_count: Number of retries
    """
    source_type: SourceType = SourceType.HTTP
    url: Optional[str] = None
    method: RequestMethod = RequestMethod.GET
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    body: Optional[Any] = None
    timeout_ms: int = 30000
    retry_count: int = 3
    retry_delay_ms: int = 1000


@dataclass
class RequestResult:
    """
    Result of a data request.

    Attributes:
        success: Whether request succeeded
        data: Response data
        status_code: HTTP status code (for HTTP requests)
        error: Error message if failed
        metadata: Additional response metadata
    """
    success: bool
    data: Any = None
    status_code: Optional[int] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Requester:
    """
    Data requester for fetching data from various sources.

    Usage:
        requester = Requester()

        # HTTP request
        result = requester.get("https://api.example.com/data")

        # With configuration
        config = RequestConfig(
            source_type=SourceType.HTTP,
            url="https://api.example.com/data",
            headers={"Authorization": "Bearer token"},
        )
        result = requester.request(config)

        # File request
        result = requester.from_file("/path/to/data.json")

        # Custom source
        requester.register_source("my_source", my_fetch_function)
        result = requester.from_source("my_source", {"key": "value"})
    """

    def __init__(self):
        self._custom_sources: Dict[str, Callable] = {}
        self._default_headers: Dict[str, str] = {}
        self._interceptors: List[Callable] = []

    # =========================================================================
    # CONFIGURATION
    # =========================================================================

    def set_default_header(self, key: str, value: str) -> "Requester":
        """Set a default header for all requests."""
        self._default_headers[key] = value
        return self

    def set_default_headers(self, headers: Dict[str, str]) -> "Requester":
        """Set multiple default headers."""
        self._default_headers.update(headers)
        return self

    def add_interceptor(self, interceptor: Callable[[RequestConfig], RequestConfig]) -> "Requester":
        """Add a request interceptor."""
        self._interceptors.append(interceptor)
        return self

    def register_source(self, name: str, handler: Callable[[Dict], Any]) -> "Requester":
        """
        Register a custom data source.

        Args:
            name: Source name
            handler: Function(params) -> data
        """
        self._custom_sources[name] = handler
        return self

    # =========================================================================
    # REQUEST METHODS
    # =========================================================================

    def request(self, config: RequestConfig) -> RequestResult:
        """
        Execute a data request with configuration.

        Args:
            config: Request configuration

        Returns:
            RequestResult with data or error
        """
        # Apply interceptors
        for interceptor in self._interceptors:
            config = interceptor(config)

        # Merge default headers
        config.headers = {**self._default_headers, **config.headers}

        # Route to appropriate handler
        if config.source_type == SourceType.HTTP:
            return self._http_request(config)
        elif config.source_type == SourceType.FILE:
            return self._file_request(config)
        elif config.source_type == SourceType.MEMORY:
            return self._memory_request(config)
        elif config.source_type == SourceType.CUSTOM:
            return self._custom_request(config)
        else:
            return RequestResult(
                success=False,
                error=f"Unsupported source type: {config.source_type}",
            )

    def get(self, url: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None) -> RequestResult:
        """Make a GET request."""
        config = RequestConfig(
            source_type=SourceType.HTTP,
            url=url,
            method=RequestMethod.GET,
            params=params or {},
            headers=headers or {},
        )
        return self.request(config)

    def post(self, url: str, body: Any = None, headers: Dict[str, str] = None) -> RequestResult:
        """Make a POST request."""
        config = RequestConfig(
            source_type=SourceType.HTTP,
            url=url,
            method=RequestMethod.POST,
            body=body,
            headers=headers or {},
        )
        return self.request(config)

    def from_file(self, path: str, format: str = "auto") -> RequestResult:
        """Load data from a file."""
        config = RequestConfig(
            source_type=SourceType.FILE,
            url=path,
            params={"format": format},
        )
        return self.request(config)

    def from_source(self, source_name: str, params: Dict[str, Any] = None) -> RequestResult:
        """Load data from a custom source."""
        config = RequestConfig(
            source_type=SourceType.CUSTOM,
            params={"source_name": source_name, **(params or {})},
        )
        return self.request(config)

    # =========================================================================
    # INTERNAL HANDLERS
    # =========================================================================

    def _http_request(self, config: RequestConfig) -> RequestResult:
        """
        Handle HTTP requests.

        Note: This is a template implementation.
        In production, use proper HTTP library (requests, httpx, aiohttp).
        """
        try:
            # Template implementation - replace with actual HTTP client
            import urllib.request
            import urllib.parse

            url = config.url
            if config.params:
                url += "?" + urllib.parse.urlencode(config.params)

            req = urllib.request.Request(
                url,
                method=config.method.value,
                headers=config.headers,
            )

            if config.body:
                req.data = json.dumps(config.body).encode('utf-8')
                if 'Content-Type' not in config.headers:
                    req.add_header('Content-Type', 'application/json')

            with urllib.request.urlopen(req, timeout=config.timeout_ms / 1000) as response:
                data = response.read().decode('utf-8')

                # Try to parse as JSON
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass

                return RequestResult(
                    success=True,
                    data=data,
                    status_code=response.status,
                    metadata={
                        "headers": dict(response.headers),
                        "url": response.url,
                    },
                )

        except Exception as e:
            return RequestResult(
                success=False,
                error=str(e),
            )

    def _file_request(self, config: RequestConfig) -> RequestResult:
        """Handle file requests."""
        try:
            path = config.url
            format = config.params.get("format", "auto")

            # Auto-detect format
            if format == "auto":
                if path.endswith(".json"):
                    format = "json"
                elif path.endswith(".csv"):
                    format = "csv"
                else:
                    format = "text"

            with open(path, 'r') as f:
                if format == "json":
                    data = json.load(f)
                elif format == "csv":
                    import csv
                    reader = csv.DictReader(f)
                    data = list(reader)
                else:
                    data = f.read()

            return RequestResult(
                success=True,
                data=data,
                metadata={"path": path, "format": format},
            )

        except FileNotFoundError:
            return RequestResult(
                success=False,
                error=f"File not found: {config.url}",
            )
        except Exception as e:
            return RequestResult(
                success=False,
                error=str(e),
            )

    def _memory_request(self, config: RequestConfig) -> RequestResult:
        """Handle in-memory data (passthrough)."""
        return RequestResult(
            success=True,
            data=config.body,
        )

    def _custom_request(self, config: RequestConfig) -> RequestResult:
        """Handle custom source requests."""
        source_name = config.params.get("source_name")

        if source_name not in self._custom_sources:
            return RequestResult(
                success=False,
                error=f"Unknown custom source: {source_name}",
            )

        try:
            handler = self._custom_sources[source_name]
            data = handler(config.params)
            return RequestResult(
                success=True,
                data=data,
                metadata={"source": source_name},
            )
        except Exception as e:
            return RequestResult(
                success=False,
                error=str(e),
            )
