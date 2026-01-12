# ═══════════════════════════════════════════════════════════════
# WEBSOCKET SERVER TEMPLATE
# Real-time data streaming with subscription management
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Customize message handlers
# 3. Run: python websocket_server.py
#
# ═══════════════════════════════════════════════════════════════

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set, Optional, Any, Callable
from dataclasses import dataclass, asdict
import websockets
from websockets.server import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


@dataclass
class WebSocketMessage:
    """Standard WebSocket message format."""
    type: str
    channel: str
    data: Any
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_json(self) -> str:
        return json.dumps(asdict(self))


@dataclass
class ClientInfo:
    """Client connection information."""
    client_id: str
    connected_at: datetime
    subscriptions: Set[str]
    metadata: Dict[str, Any]


# ═══════════════════════════════════════════════════════════════
# WEBSOCKET SERVER
# ═══════════════════════════════════════════════════════════════


class WebSocketServer:
    """
    WebSocket server with channel-based subscriptions.

    Features:
    - Channel subscriptions (subscribe/unsubscribe)
    - Broadcast to all clients or specific channels
    - Ping/pong heartbeat
    - Connection lifecycle management
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Dict[WebSocketServerProtocol, ClientInfo] = {}
        self.channels: Dict[str, Set[WebSocketServerProtocol]] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self._client_counter = 0

        # Register default handlers
        self.register_handler("subscribe", self._handle_subscribe)
        self.register_handler("unsubscribe", self._handle_unsubscribe)
        self.register_handler("ping", self._handle_ping)

    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler."""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for: {message_type}")

    async def start(self):
        """Start the WebSocket server."""
        logger.info(f"Starting WebSocket server on ws://{self.host}:{self.port}")

        async with websockets.serve(
            self._handle_connection,
            self.host,
            self.port,
            ping_interval=30,
            ping_timeout=10,
        ):
            await asyncio.Future()  # Run forever

    async def _handle_connection(self, websocket: WebSocketServerProtocol):
        """Handle new WebSocket connection."""
        # Generate client ID
        self._client_counter += 1
        client_id = f"client_{self._client_counter}"

        # Register client
        self.clients[websocket] = ClientInfo(
            client_id=client_id,
            connected_at=datetime.utcnow(),
            subscriptions=set(),
            metadata={},
        )

        logger.info(f"Client connected: {client_id} ({len(self.clients)} total)")

        try:
            # Send welcome message
            await self._send(websocket, WebSocketMessage(
                type="connected",
                channel="system",
                data={"client_id": client_id},
            ))

            # Handle messages
            async for message in websocket:
                await self._handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error with client {client_id}: {e}")
        finally:
            await self._cleanup_client(websocket)

    async def _handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming message."""
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")

            # Get handler
            handler = self.message_handlers.get(message_type)

            if handler:
                await handler(websocket, data)
            else:
                logger.warning(f"No handler for message type: {message_type}")
                await self._send(websocket, WebSocketMessage(
                    type="error",
                    channel="system",
                    data={"error": f"Unknown message type: {message_type}"},
                ))

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {message[:100]}")
        except Exception as e:
            logger.error(f"Message handling error: {e}")

    async def _handle_subscribe(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle channel subscription."""
        channel = data.get("channel")
        if not channel:
            return

        # Add to channel
        if channel not in self.channels:
            self.channels[channel] = set()

        self.channels[channel].add(websocket)
        self.clients[websocket].subscriptions.add(channel)

        logger.info(f"Client subscribed to: {channel}")

        await self._send(websocket, WebSocketMessage(
            type="subscribed",
            channel=channel,
            data={"channel": channel},
        ))

    async def _handle_unsubscribe(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle channel unsubscription."""
        channel = data.get("channel")
        if not channel:
            return

        # Remove from channel
        if channel in self.channels:
            self.channels[channel].discard(websocket)

        self.clients[websocket].subscriptions.discard(channel)

        logger.info(f"Client unsubscribed from: {channel}")

        await self._send(websocket, WebSocketMessage(
            type="unsubscribed",
            channel=channel,
            data={"channel": channel},
        ))

    async def _handle_ping(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle ping message."""
        await self._send(websocket, WebSocketMessage(
            type="pong",
            channel="system",
            data={"timestamp": datetime.utcnow().isoformat()},
        ))

    async def _send(self, websocket: WebSocketServerProtocol, message: WebSocketMessage):
        """Send message to client."""
        try:
            await websocket.send(message.to_json())
        except websockets.exceptions.ConnectionClosed:
            pass

    async def _cleanup_client(self, websocket: WebSocketServerProtocol):
        """Cleanup disconnected client."""
        if websocket in self.clients:
            client_info = self.clients[websocket]

            # Remove from all channels
            for channel in client_info.subscriptions:
                if channel in self.channels:
                    self.channels[channel].discard(websocket)

            # Remove client
            del self.clients[websocket]
            logger.info(f"Cleaned up: {client_info.client_id}")

    # ═══════════════════════════════════════════════════════════
    # BROADCAST METHODS
    # ═══════════════════════════════════════════════════════════

    async def broadcast(self, message: WebSocketMessage):
        """Broadcast to all connected clients."""
        if not self.clients:
            return

        tasks = [self._send(ws, message) for ws in self.clients]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def broadcast_to_channel(self, channel: str, message: WebSocketMessage):
        """Broadcast to all clients subscribed to a channel."""
        if channel not in self.channels:
            return

        subscribers = self.channels[channel]
        if not subscribers:
            return

        tasks = [self._send(ws, message) for ws in subscribers]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def send_to_client(self, client_id: str, message: WebSocketMessage):
        """Send to specific client by ID."""
        for ws, info in self.clients.items():
            if info.client_id == client_id:
                await self._send(ws, message)
                return

    # ═══════════════════════════════════════════════════════════
    # STATUS
    # ═══════════════════════════════════════════════════════════

    def get_stats(self) -> Dict:
        """Get server statistics."""
        return {
            "total_clients": len(self.clients),
            "total_channels": len(self.channels),
            "channels": {
                name: len(subs) for name, subs in self.channels.items()
            },
        }


# ═══════════════════════════════════════════════════════════════
# PRICE STREAMING EXAMPLE
# ═══════════════════════════════════════════════════════════════


class PriceStreamingServer(WebSocketServer):
    """
    Example: Real-time price streaming server.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        super().__init__(host, port)

        # Register custom handlers
        self.register_handler("get_price", self._handle_get_price)

        # Simulated prices
        self.prices = {
            "XAUUSD": 2640.50,
            "US30": 43250.00,
            "BTCUSD": 97500.00,
        }

    async def _handle_get_price(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle price request."""
        symbol = data.get("symbol", "").upper()

        if symbol in self.prices:
            await self._send(websocket, WebSocketMessage(
                type="price",
                channel=f"prices.{symbol}",
                data={
                    "symbol": symbol,
                    "price": self.prices[symbol],
                    "bid": self.prices[symbol] - 0.5,
                    "ask": self.prices[symbol] + 0.5,
                },
            ))
        else:
            await self._send(websocket, WebSocketMessage(
                type="error",
                channel="system",
                data={"error": f"Unknown symbol: {symbol}"},
            ))

    async def simulate_price_updates(self):
        """Simulate price updates for demonstration."""
        import random

        while True:
            await asyncio.sleep(1)

            for symbol in self.prices:
                # Random price change
                change = random.uniform(-0.5, 0.5)
                self.prices[symbol] += change

                # Broadcast to subscribers
                await self.broadcast_to_channel(
                    f"prices.{symbol}",
                    WebSocketMessage(
                        type="price_update",
                        channel=f"prices.{symbol}",
                        data={
                            "symbol": symbol,
                            "price": round(self.prices[symbol], 2),
                            "change": round(change, 2),
                        },
                    )
                )


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════


async def main():
    """Run the WebSocket server."""
    server = PriceStreamingServer(port=8765)

    # Run server and price simulation concurrently
    await asyncio.gather(
        server.start(),
        server.simulate_price_updates(),
    )


if __name__ == "__main__":
    asyncio.run(main())
