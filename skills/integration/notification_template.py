"""
Multi-Channel Notification Template
====================================
Patterns for sending notifications across multiple channels.

Use when:
- Multi-channel notifications needed
- Priority-based routing
- Rate limiting per channel
- Template-based messages

Placeholders:
- {{DEFAULT_CHANNEL}}: Default notification channel
- {{RATE_LIMIT}}: Notifications per minute
"""

from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging
from datetime import datetime, timedelta
import time
import threading
from collections import deque

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class NotificationChannel(Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"
    DISCORD = "discord"
    SLACK = "slack"
    PUSH = "push"
    SMS = "sms"
    WEBHOOK = "webhook"


@dataclass
class Notification:
    """Notification message."""
    id: str
    title: str
    body: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: List[NotificationChannel] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    template: Optional[str] = None
    recipients: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None


@dataclass
class DeliveryResult:
    """Result of notification delivery."""
    notification_id: str
    channel: NotificationChannel
    success: bool
    recipient: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class ChannelProvider(ABC):
    """Abstract notification channel provider."""

    def __init__(self, channel: NotificationChannel):
        self.channel = channel
        self.enabled = True

    @abstractmethod
    def send(
        self,
        notification: Notification,
        recipient: Optional[str] = None
    ) -> DeliveryResult:
        """Send notification through this channel."""
        pass


class TelegramProvider(ChannelProvider):
    """Telegram notification provider."""

    def __init__(self, bot_token: str, default_chat_id: str):
        super().__init__(NotificationChannel.TELEGRAM)
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id

    def send(
        self,
        notification: Notification,
        recipient: Optional[str] = None
    ) -> DeliveryResult:
        """Send Telegram notification."""
        chat_id = recipient or self.default_chat_id

        try:
            # Format message
            message = f"<b>{notification.title}</b>\n\n{notification.body}"

            # Placeholder - implement with requests
            logger.info(f"[TELEGRAM] {chat_id}: {message[:50]}...")

            return DeliveryResult(
                notification_id=notification.id,
                channel=self.channel,
                success=True,
                recipient=chat_id
            )

        except Exception as e:
            return DeliveryResult(
                notification_id=notification.id,
                channel=self.channel,
                success=False,
                recipient=chat_id,
                error=str(e)
            )


class EmailProvider(ChannelProvider):
    """Email notification provider."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        from_address: str
    ):
        super().__init__(NotificationChannel.EMAIL)
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_address = from_address

    def send(
        self,
        notification: Notification,
        recipient: Optional[str] = None
    ) -> DeliveryResult:
        """Send email notification."""
        if not recipient:
            return DeliveryResult(
                notification_id=notification.id,
                channel=self.channel,
                success=False,
                error="No recipient specified"
            )

        try:
            # Placeholder - implement with smtplib
            logger.info(f"[EMAIL] {recipient}: {notification.title}")

            return DeliveryResult(
                notification_id=notification.id,
                channel=self.channel,
                success=True,
                recipient=recipient
            )

        except Exception as e:
            return DeliveryResult(
                notification_id=notification.id,
                channel=self.channel,
                success=False,
                recipient=recipient,
                error=str(e)
            )


class DiscordProvider(ChannelProvider):
    """Discord webhook notification provider."""

    def __init__(self, webhook_url: str):
        super().__init__(NotificationChannel.DISCORD)
        self.webhook_url = webhook_url

    def send(
        self,
        notification: Notification,
        recipient: Optional[str] = None
    ) -> DeliveryResult:
        """Send Discord notification."""
        try:
            # Format as Discord embed
            payload = {
                "embeds": [{
                    "title": notification.title,
                    "description": notification.body,
                    "color": self._priority_color(notification.priority)
                }]
            }

            # Placeholder - implement with requests
            logger.info(f"[DISCORD] {notification.title}")

            return DeliveryResult(
                notification_id=notification.id,
                channel=self.channel,
                success=True
            )

        except Exception as e:
            return DeliveryResult(
                notification_id=notification.id,
                channel=self.channel,
                success=False,
                error=str(e)
            )

    def _priority_color(self, priority: NotificationPriority) -> int:
        """Get Discord color for priority."""
        colors = {
            NotificationPriority.LOW: 0x808080,     # Gray
            NotificationPriority.NORMAL: 0x0099FF,  # Blue
            NotificationPriority.HIGH: 0xFFAA00,    # Orange
            NotificationPriority.URGENT: 0xFF0000   # Red
        }
        return colors.get(priority, 0x0099FF)


class RateLimiter:
    """Rate limiter for notifications."""

    def __init__(self, max_per_minute: int = 60):
        self.max_per_minute = max_per_minute
        self.timestamps: deque = deque()
        self._lock = threading.Lock()

    def can_send(self) -> bool:
        """Check if can send notification."""
        with self._lock:
            now = time.time()
            cutoff = now - 60

            # Remove old timestamps
            while self.timestamps and self.timestamps[0] < cutoff:
                self.timestamps.popleft()

            if len(self.timestamps) < self.max_per_minute:
                self.timestamps.append(now)
                return True

            return False

    def wait_time(self) -> float:
        """Get time to wait before can send."""
        with self._lock:
            if len(self.timestamps) < self.max_per_minute:
                return 0

            oldest = self.timestamps[0]
            wait = 60 - (time.time() - oldest)
            return max(0, wait)


class NotificationService:
    """
    Multi-channel notification service.

    Example:
        service = NotificationService()
        service.add_provider(TelegramProvider(token, chat_id))
        service.add_provider(DiscordProvider(webhook_url))

        notification = Notification(
            id="1",
            title="Trading Alert",
            body="XAUUSD BUY signal generated",
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.TELEGRAM, NotificationChannel.DISCORD]
        )

        results = service.send(notification)
    """

    def __init__(
        self,
        default_channel: NotificationChannel = NotificationChannel.TELEGRAM,
        rate_limit: int = 60
    ):
        self.default_channel = default_channel
        self.providers: Dict[NotificationChannel, ChannelProvider] = {}
        self.rate_limiters: Dict[NotificationChannel, RateLimiter] = {}
        self.rate_limit = rate_limit
        self.templates: Dict[str, str] = {}
        self.delivery_history: deque = deque(maxlen=1000)

    def add_provider(self, provider: ChannelProvider):
        """Add a notification provider."""
        self.providers[provider.channel] = provider
        self.rate_limiters[provider.channel] = RateLimiter(self.rate_limit)

    def add_template(self, name: str, template: str):
        """Add a message template."""
        self.templates[name] = template

    def send(self, notification: Notification) -> List[DeliveryResult]:
        """Send notification through all specified channels."""
        results = []
        channels = notification.channels or [self.default_channel]

        for channel in channels:
            provider = self.providers.get(channel)
            if not provider or not provider.enabled:
                results.append(DeliveryResult(
                    notification_id=notification.id,
                    channel=channel,
                    success=False,
                    error="Provider not available"
                ))
                continue

            # Check rate limit
            rate_limiter = self.rate_limiters.get(channel)
            if rate_limiter and not rate_limiter.can_send():
                results.append(DeliveryResult(
                    notification_id=notification.id,
                    channel=channel,
                    success=False,
                    error="Rate limited"
                ))
                continue

            # Apply template if specified
            notif = self._apply_template(notification)

            # Send to recipients
            recipients = notification.recipients or [None]
            for recipient in recipients:
                result = provider.send(notif, recipient)
                results.append(result)
                self.delivery_history.append(result)

        return results

    def _apply_template(self, notification: Notification) -> Notification:
        """Apply template to notification."""
        if not notification.template:
            return notification

        template = self.templates.get(notification.template)
        if not template:
            return notification

        # Simple template substitution
        body = template.format(**notification.data)

        return Notification(
            id=notification.id,
            title=notification.title,
            body=body,
            priority=notification.priority,
            channels=notification.channels,
            data=notification.data,
            recipients=notification.recipients
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics."""
        history = list(self.delivery_history)
        if not history:
            return {"total": 0}

        successful = [r for r in history if r.success]

        by_channel = {}
        for channel in NotificationChannel:
            channel_results = [r for r in history if r.channel == channel]
            if channel_results:
                by_channel[channel.value] = {
                    "total": len(channel_results),
                    "successful": len([r for r in channel_results if r.success]),
                    "rate_limit_remaining": self.rate_limiters.get(channel, RateLimiter(1000)).max_per_minute - len([
                        r for r in channel_results
                        if r.success and (datetime.now() - r.timestamp).total_seconds() < 60
                    ])
                }

        return {
            "total": len(history),
            "successful": len(successful),
            "failed": len(history) - len(successful),
            "success_rate": len(successful) / len(history) * 100 if history else 0,
            "by_channel": by_channel
        }


class TradingNotificationService(NotificationService):
    """Notification service specialized for trading."""

    def __init__(
        self,
        telegram_token: str,
        telegram_chat_id: str
    ):
        super().__init__(
            default_channel=NotificationChannel.TELEGRAM,
            rate_limit=30  # 30 per minute for trading
        )

        # Add Telegram provider
        self.add_provider(TelegramProvider(telegram_token, telegram_chat_id))

        # Add trading templates
        self._setup_templates()

    def _setup_templates(self):
        """Setup trading notification templates."""
        self.add_template("signal", """
📊 <b>Trading Signal</b>

Symbol: {symbol}
Direction: {direction}
Confidence: {confidence:.0%}
Entry: {entry}
Stop Loss: {sl}
Take Profit: {tp}
""")

        self.add_template("trade_opened", """
🟢 <b>Trade Opened</b>

Symbol: {symbol}
Direction: {direction}
Volume: {volume} lots
Entry: {entry}
Ticket: {ticket}
""")

        self.add_template("trade_closed", """
{emoji} <b>Trade Closed</b>

Symbol: {symbol}
Profit: {profit_sign}${profit:.2f}
Pips: {pips:.1f}
Ticket: {ticket}
""")

        self.add_template("alert", """
{emoji} <b>{title}</b>

{message}
""")

    def notify_signal(
        self,
        symbol: str,
        direction: str,
        confidence: float,
        entry: float,
        sl: float,
        tp: float
    ) -> List[DeliveryResult]:
        """Send signal notification."""
        return self.send(Notification(
            id=f"signal_{int(time.time())}",
            title="Trading Signal",
            body="",
            priority=NotificationPriority.HIGH,
            template="signal",
            data={
                "symbol": symbol,
                "direction": direction,
                "confidence": confidence,
                "entry": entry,
                "sl": sl,
                "tp": tp
            }
        ))

    def notify_trade_opened(
        self,
        symbol: str,
        direction: str,
        volume: float,
        entry: float,
        ticket: int
    ) -> List[DeliveryResult]:
        """Send trade opened notification."""
        return self.send(Notification(
            id=f"trade_{ticket}",
            title="Trade Opened",
            body="",
            priority=NotificationPriority.NORMAL,
            template="trade_opened",
            data={
                "symbol": symbol,
                "direction": direction,
                "volume": volume,
                "entry": entry,
                "ticket": ticket
            }
        ))

    def notify_trade_closed(
        self,
        symbol: str,
        profit: float,
        pips: float,
        ticket: int
    ) -> List[DeliveryResult]:
        """Send trade closed notification."""
        return self.send(Notification(
            id=f"close_{ticket}",
            title="Trade Closed",
            body="",
            priority=NotificationPriority.HIGH if profit > 100 else NotificationPriority.NORMAL,
            template="trade_closed",
            data={
                "symbol": symbol,
                "profit": abs(profit),
                "profit_sign": "+" if profit > 0 else "-",
                "pips": pips,
                "ticket": ticket,
                "emoji": "✅" if profit > 0 else "❌"
            }
        ))


# Example usage
if __name__ == "__main__":
    # Create service
    service = TradingNotificationService(
        telegram_token="test-token",
        telegram_chat_id="123456"
    )

    # Send notifications
    print("Sending notifications...")

    results = service.notify_signal(
        symbol="XAUUSD",
        direction="BUY",
        confidence=0.85,
        entry=2000.50,
        sl=1990.00,
        tp=2020.00
    )
    print(f"Signal: {results[0].success}")

    results = service.notify_trade_opened(
        symbol="XAUUSD",
        direction="BUY",
        volume=0.1,
        entry=2000.50,
        ticket=12345
    )
    print(f"Trade opened: {results[0].success}")

    results = service.notify_trade_closed(
        symbol="XAUUSD",
        profit=150.50,
        pips=20,
        ticket=12345
    )
    print(f"Trade closed: {results[0].success}")

    # Get stats
    print(f"\nStats: {service.get_stats()}")
