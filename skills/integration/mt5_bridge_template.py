"""
MT5 Bridge Integration Template
===============================
Patterns for MetaTrader 5 integration.

Use when:
- Trading signals to MT5 needed
- Market data from MT5 required
- Position management via MT5
- EA communication

Placeholders:
- {{MT5_DATA_PATH}}: MT5 Files directory path
- {{SIGNAL_FILE}}: Signal file name
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from pathlib import Path
import logging
import json
import time
import threading

logger = logging.getLogger(__name__)


class SignalDirection(Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"
    CLOSE_BUY = "CLOSE_BUY"
    CLOSE_SELL = "CLOSE_SELL"


class OrderType(Enum):
    MARKET = 0
    LIMIT = 1
    STOP = 2
    STOP_LIMIT = 3


class PositionType(Enum):
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class TradingSignal:
    """Trading signal for MT5."""
    symbol: str
    direction: SignalDirection
    confidence: float
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    volume: float = 0.01
    comment: str = ""
    magic_number: int = 12345
    timestamp: datetime = field(default_factory=datetime.now)
    expiry_minutes: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Position:
    """MT5 position data."""
    ticket: int
    symbol: str
    position_type: PositionType
    volume: float
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    profit: float
    magic_number: int
    comment: str
    open_time: datetime
    swap: float = 0
    commission: float = 0


@dataclass
class AccountInfo:
    """MT5 account information."""
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    profit: float
    currency: str = "USD"


class MT5Bridge(ABC):
    """Abstract MT5 bridge."""

    @abstractmethod
    def send_signal(self, signal: TradingSignal) -> bool:
        """Send trading signal to MT5."""
        pass

    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Get current positions."""
        pass

    @abstractmethod
    def get_account_info(self) -> Optional[AccountInfo]:
        """Get account information."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if MT5 is connected."""
        pass


class FileBridge(MT5Bridge):
    """File-based MT5 bridge (for EA communication)."""

    def __init__(
        self,
        data_path: str,
        signal_file: str = "signals.json",
        positions_file: str = "positions.json",
        account_file: str = "account.json"
    ):
        self.data_path = Path(data_path)
        self.signal_file = self.data_path / signal_file
        self.positions_file = self.data_path / positions_file
        self.account_file = self.data_path / account_file
        self._lock = threading.Lock()

        # Ensure directory exists
        self.data_path.mkdir(parents=True, exist_ok=True)

    def send_signal(self, signal: TradingSignal) -> bool:
        """Send signal by writing to file."""
        try:
            signal_data = {
                "symbol": signal.symbol,
                "direction": signal.direction.value,
                "confidence": signal.confidence,
                "entry_price": signal.entry_price,
                "stop_loss": signal.stop_loss,
                "take_profit": signal.take_profit,
                "volume": signal.volume,
                "comment": signal.comment,
                "magic_number": signal.magic_number,
                "timestamp": signal.timestamp.isoformat(),
                "expiry": (signal.timestamp.timestamp() + signal.expiry_minutes * 60),
                "metadata": signal.metadata
            }

            with self._lock:
                # Read existing signals
                signals = self._read_signals()

                # Add new signal
                signals.append(signal_data)

                # Write back
                with open(self.signal_file, 'w') as f:
                    json.dump(signals, f, indent=2)

            logger.info(f"Signal sent: {signal.symbol} {signal.direction.value}")
            return True

        except Exception as e:
            logger.error(f"Failed to send signal: {e}")
            return False

    def get_positions(self) -> List[Position]:
        """Read positions from file."""
        try:
            if not self.positions_file.exists():
                return []

            with open(self.positions_file, 'r') as f:
                data = json.load(f)

            positions = []
            for pos in data:
                positions.append(Position(
                    ticket=pos["ticket"],
                    symbol=pos["symbol"],
                    position_type=PositionType(pos["type"]),
                    volume=pos["volume"],
                    entry_price=pos["entry_price"],
                    current_price=pos["current_price"],
                    stop_loss=pos["stop_loss"],
                    take_profit=pos["take_profit"],
                    profit=pos["profit"],
                    magic_number=pos["magic_number"],
                    comment=pos.get("comment", ""),
                    open_time=datetime.fromisoformat(pos["open_time"]),
                    swap=pos.get("swap", 0),
                    commission=pos.get("commission", 0)
                ))

            return positions

        except Exception as e:
            logger.error(f"Failed to read positions: {e}")
            return []

    def get_account_info(self) -> Optional[AccountInfo]:
        """Read account info from file."""
        try:
            if not self.account_file.exists():
                return None

            with open(self.account_file, 'r') as f:
                data = json.load(f)

            return AccountInfo(
                balance=data["balance"],
                equity=data["equity"],
                margin=data["margin"],
                free_margin=data["free_margin"],
                margin_level=data.get("margin_level", 0),
                profit=data.get("profit", 0),
                currency=data.get("currency", "USD")
            )

        except Exception as e:
            logger.error(f"Failed to read account info: {e}")
            return None

    def is_connected(self) -> bool:
        """Check if MT5 is updating files."""
        try:
            if not self.account_file.exists():
                return False

            # Check if file was updated recently (within 1 minute)
            mtime = self.account_file.stat().st_mtime
            age = time.time() - mtime
            return age < 60

        except Exception:
            return False

    def _read_signals(self) -> List[Dict]:
        """Read existing signals."""
        try:
            if self.signal_file.exists():
                with open(self.signal_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []

    def clear_processed_signals(self, max_age_minutes: int = 60):
        """Clear old processed signals."""
        try:
            signals = self._read_signals()
            cutoff = time.time() - (max_age_minutes * 60)

            # Keep only recent signals
            signals = [s for s in signals if s.get("timestamp", 0) > cutoff]

            with self._lock:
                with open(self.signal_file, 'w') as f:
                    json.dump(signals, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to clear signals: {e}")


class HTTPBridge(MT5Bridge):
    """HTTP-based MT5 bridge (for WebSocket/REST API)."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def send_signal(self, signal: TradingSignal) -> bool:
        """Send signal via HTTP."""
        try:
            # Placeholder - implement with requests/httpx
            url = f"{self.base_url}/signal"
            data = {
                "symbol": signal.symbol,
                "direction": signal.direction.value,
                "confidence": signal.confidence,
                "entry_price": signal.entry_price,
                "stop_loss": signal.stop_loss,
                "take_profit": signal.take_profit,
                "volume": signal.volume
            }
            # response = requests.post(url, json=data, headers=self._get_headers())
            # return response.status_code == 200
            logger.info(f"HTTP signal: {data}")
            return True
        except Exception as e:
            logger.error(f"HTTP signal failed: {e}")
            return False

    def get_positions(self) -> List[Position]:
        """Get positions via HTTP."""
        # Placeholder implementation
        return []

    def get_account_info(self) -> Optional[AccountInfo]:
        """Get account info via HTTP."""
        # Placeholder implementation
        return None

    def is_connected(self) -> bool:
        """Check HTTP connection."""
        try:
            # response = requests.get(f"{self.base_url}/health")
            # return response.status_code == 200
            return True
        except:
            return False


class SignalManager:
    """
    Manage trading signals with validation.

    Example:
        bridge = FileBridge("/path/to/mt5/files")
        manager = SignalManager(bridge)

        signal = TradingSignal(
            symbol="XAUUSD",
            direction=SignalDirection.BUY,
            confidence=0.85,
            stop_loss=1950,
            take_profit=2050
        )

        if manager.send_signal(signal):
            print("Signal sent successfully")
    """

    def __init__(
        self,
        bridge: MT5Bridge,
        min_confidence: float = 0.6,
        max_positions_per_symbol: int = 1
    ):
        self.bridge = bridge
        self.min_confidence = min_confidence
        self.max_positions_per_symbol = max_positions_per_symbol
        self.signal_history: List[TradingSignal] = []

    def send_signal(self, signal: TradingSignal) -> bool:
        """Send signal with validation."""
        # Validate confidence
        if signal.confidence < self.min_confidence:
            logger.warning(f"Signal confidence {signal.confidence} below minimum {self.min_confidence}")
            return False

        # Check existing positions
        positions = self.bridge.get_positions()
        symbol_positions = [p for p in positions if p.symbol == signal.symbol]

        if len(symbol_positions) >= self.max_positions_per_symbol:
            logger.warning(f"Max positions reached for {signal.symbol}")
            return False

        # Send signal
        if self.bridge.send_signal(signal):
            self.signal_history.append(signal)
            return True

        return False

    def get_position_summary(self) -> Dict[str, Any]:
        """Get position summary."""
        positions = self.bridge.get_positions()
        account = self.bridge.get_account_info()

        if not positions:
            return {"total_positions": 0, "total_profit": 0}

        return {
            "total_positions": len(positions),
            "total_profit": sum(p.profit for p in positions),
            "total_volume": sum(p.volume for p in positions),
            "by_symbol": {
                symbol: {
                    "count": len([p for p in positions if p.symbol == symbol]),
                    "profit": sum(p.profit for p in positions if p.symbol == symbol)
                }
                for symbol in set(p.symbol for p in positions)
            },
            "account": {
                "balance": account.balance if account else 0,
                "equity": account.equity if account else 0,
                "profit": account.profit if account else 0
            }
        }


def create_trading_bridge(mt5_path: str) -> SignalManager:
    """Create trading bridge for MT5."""
    bridge = FileBridge(
        data_path=mt5_path,
        signal_file="signals.json",
        positions_file="positions.json",
        account_file="account.json"
    )

    return SignalManager(
        bridge=bridge,
        min_confidence=0.6,
        max_positions_per_symbol=2
    )


# Example usage
if __name__ == "__main__":
    import tempfile

    # Create temp directory for demo
    with tempfile.TemporaryDirectory() as mt5_path:
        manager = create_trading_bridge(mt5_path)

        # Create and send signal
        signal = TradingSignal(
            symbol="XAUUSD",
            direction=SignalDirection.BUY,
            confidence=0.85,
            entry_price=2000.50,
            stop_loss=1990.00,
            take_profit=2020.00,
            volume=0.1,
            comment="ML Signal",
            magic_number=12345
        )

        print("Sending signal...")
        result = manager.send_signal(signal)
        print(f"Signal sent: {result}")

        # Check connection
        print(f"\nMT5 Connected: {manager.bridge.is_connected()}")

        # Get summary
        print("\nPosition Summary:")
        summary = manager.get_position_summary()
        print(json.dumps(summary, indent=2))
