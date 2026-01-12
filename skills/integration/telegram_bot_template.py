"""
Telegram Bot Integration Template
=================================
Patterns for Telegram bot integration.

Use when:
- Trading notifications needed
- Command-based interaction
- Alert broadcasting
- User authentication

Placeholders:
- {{BOT_TOKEN}}: Telegram bot token
- {{CHAT_ID}}: Default chat ID
"""

from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)


class ParseMode(Enum):
    HTML = "HTML"
    MARKDOWN = "MarkdownV2"
    PLAIN = None


@dataclass
class TelegramUser:
    """Telegram user data."""
    user_id: int
    username: Optional[str] = None
    first_name: str = ""
    last_name: str = ""
    is_bot: bool = False
    language_code: str = "en"


@dataclass
class TelegramMessage:
    """Telegram message data."""
    message_id: int
    chat_id: int
    user: TelegramUser
    text: str
    date: datetime
    reply_to_message_id: Optional[int] = None
    entities: List[Dict] = field(default_factory=list)


@dataclass
class CommandContext:
    """Context for command execution."""
    message: TelegramMessage
    command: str
    args: List[str]
    raw_args: str


class CommandHandler:
    """Command handler definition."""

    def __init__(
        self,
        command: str,
        handler: Callable[[CommandContext], str],
        description: str = "",
        admin_only: bool = False
    ):
        self.command = command
        self.handler = handler
        self.description = description
        self.admin_only = admin_only


class TelegramClient(ABC):
    """Abstract Telegram client."""

    @abstractmethod
    def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: ParseMode = ParseMode.HTML,
        reply_to: Optional[int] = None
    ) -> bool:
        """Send a message."""
        pass

    @abstractmethod
    def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: ParseMode = ParseMode.HTML
    ) -> bool:
        """Edit a message."""
        pass

    @abstractmethod
    def delete_message(self, chat_id: int, message_id: int) -> bool:
        """Delete a message."""
        pass


class MockTelegramClient(TelegramClient):
    """Mock Telegram client for testing."""

    def __init__(self):
        self.messages: List[Dict] = []

    def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: ParseMode = ParseMode.HTML,
        reply_to: Optional[int] = None
    ) -> bool:
        self.messages.append({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode.value if parse_mode else None,
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"[TELEGRAM] {text[:100]}...")
        return True

    def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: ParseMode = ParseMode.HTML
    ) -> bool:
        logger.info(f"[TELEGRAM EDIT] {text[:100]}...")
        return True

    def delete_message(self, chat_id: int, message_id: int) -> bool:
        logger.info(f"[TELEGRAM DELETE] {message_id}")
        return True


class HTTPTelegramClient(TelegramClient):
    """HTTP-based Telegram client."""

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: ParseMode = ParseMode.HTML,
        reply_to: Optional[int] = None
    ) -> bool:
        """Send message via API."""
        try:
            # Placeholder - implement with requests
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text
            }
            if parse_mode and parse_mode.value:
                data["parse_mode"] = parse_mode.value
            if reply_to:
                data["reply_to_message_id"] = reply_to

            # response = requests.post(url, json=data)
            # return response.json().get("ok", False)
            logger.info(f"Would send to {chat_id}: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Send message failed: {e}")
            return False

    def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: ParseMode = ParseMode.HTML
    ) -> bool:
        """Edit message via API."""
        return True

    def delete_message(self, chat_id: int, message_id: int) -> bool:
        """Delete message via API."""
        return True


class TelegramBot:
    """
    Telegram bot with command handling.

    Example:
        bot = TelegramBot(client, admin_ids=[123456])

        @bot.command("start", "Start the bot")
        def start_command(ctx):
            return f"Hello, {ctx.message.user.first_name}!"

        @bot.command("signal", "Get latest signal", admin_only=True)
        def signal_command(ctx):
            return "XAUUSD BUY @ 2000"

        bot.handle_update(update_data)
    """

    def __init__(
        self,
        client: TelegramClient,
        admin_ids: List[int] = None,
        command_prefix: str = "/"
    ):
        self.client = client
        self.admin_ids = admin_ids or []
        self.command_prefix = command_prefix
        self.handlers: Dict[str, CommandHandler] = {}
        self.default_handler: Optional[Callable] = None

    def command(
        self,
        name: str,
        description: str = "",
        admin_only: bool = False
    ):
        """Decorator to register a command handler."""
        def decorator(func: Callable[[CommandContext], str]):
            self.handlers[name] = CommandHandler(
                command=name,
                handler=func,
                description=description,
                admin_only=admin_only
            )
            return func
        return decorator

    def set_default_handler(self, handler: Callable[[TelegramMessage], str]):
        """Set default handler for non-command messages."""
        self.default_handler = handler

    def handle_update(self, update: Dict[str, Any]) -> Optional[str]:
        """Handle incoming update."""
        try:
            if "message" not in update:
                return None

            msg_data = update["message"]
            message = TelegramMessage(
                message_id=msg_data["message_id"],
                chat_id=msg_data["chat"]["id"],
                user=TelegramUser(
                    user_id=msg_data["from"]["id"],
                    username=msg_data["from"].get("username"),
                    first_name=msg_data["from"].get("first_name", ""),
                    last_name=msg_data["from"].get("last_name", "")
                ),
                text=msg_data.get("text", ""),
                date=datetime.fromtimestamp(msg_data["date"]),
                entities=msg_data.get("entities", [])
            )

            # Check for command
            if message.text.startswith(self.command_prefix):
                return self._handle_command(message)
            elif self.default_handler:
                response = self.default_handler(message)
                if response:
                    self.client.send_message(message.chat_id, response)
                return response

        except Exception as e:
            logger.error(f"Handle update error: {e}")

        return None

    def _handle_command(self, message: TelegramMessage) -> Optional[str]:
        """Handle a command message."""
        # Parse command
        parts = message.text[len(self.command_prefix):].split(maxsplit=1)
        command = parts[0].lower().split("@")[0]  # Remove bot username
        raw_args = parts[1] if len(parts) > 1 else ""
        args = raw_args.split() if raw_args else []

        handler = self.handlers.get(command)
        if not handler:
            return None

        # Check admin permission
        if handler.admin_only and message.user.user_id not in self.admin_ids:
            response = "This command is admin-only."
            self.client.send_message(message.chat_id, response)
            return response

        # Create context and execute
        context = CommandContext(
            message=message,
            command=command,
            args=args,
            raw_args=raw_args
        )

        try:
            response = handler.handler(context)
            if response:
                self.client.send_message(message.chat_id, response)
            return response
        except Exception as e:
            logger.error(f"Command handler error: {e}")
            return f"Error: {e}"

    def send_notification(
        self,
        chat_id: int,
        title: str,
        body: str,
        parse_mode: ParseMode = ParseMode.HTML
    ) -> bool:
        """Send a formatted notification."""
        message = f"<b>{title}</b>\n\n{body}"
        return self.client.send_message(chat_id, message, parse_mode)

    def get_commands_list(self) -> List[Dict[str, str]]:
        """Get list of commands for BotFather."""
        return [
            {"command": h.command, "description": h.description}
            for h in self.handlers.values()
            if h.description and not h.admin_only
        ]


class TradingNotifier:
    """Send trading notifications via Telegram."""

    def __init__(self, client: TelegramClient, chat_id: int):
        self.client = client
        self.chat_id = chat_id

    def notify_signal(
        self,
        symbol: str,
        direction: str,
        confidence: float,
        entry: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None
    ) -> bool:
        """Notify about a trading signal."""
        emoji = "📈" if direction == "BUY" else "📉" if direction == "SELL" else "⏸"

        message = f"""
{emoji} <b>TRADING SIGNAL</b>

<b>Symbol:</b> {symbol}
<b>Direction:</b> {direction}
<b>Confidence:</b> {confidence:.0%}
"""
        if entry:
            message += f"<b>Entry:</b> {entry}\n"
        if sl:
            message += f"<b>Stop Loss:</b> {sl}\n"
        if tp:
            message += f"<b>Take Profit:</b> {tp}\n"

        return self.client.send_message(self.chat_id, message.strip())

    def notify_trade_opened(
        self,
        symbol: str,
        direction: str,
        volume: float,
        entry: float,
        ticket: int
    ) -> bool:
        """Notify about trade opened."""
        emoji = "🟢" if direction == "BUY" else "🔴"

        message = f"""
{emoji} <b>TRADE OPENED</b>

<b>Symbol:</b> {symbol}
<b>Direction:</b> {direction}
<b>Volume:</b> {volume} lots
<b>Entry:</b> {entry}
<b>Ticket:</b> {ticket}
"""
        return self.client.send_message(self.chat_id, message.strip())

    def notify_trade_closed(
        self,
        symbol: str,
        direction: str,
        profit: float,
        pips: float,
        ticket: int
    ) -> bool:
        """Notify about trade closed."""
        emoji = "✅" if profit > 0 else "❌"
        profit_sign = "+" if profit > 0 else ""

        message = f"""
{emoji} <b>TRADE CLOSED</b>

<b>Symbol:</b> {symbol}
<b>Direction:</b> {direction}
<b>Profit:</b> {profit_sign}${profit:.2f}
<b>Pips:</b> {profit_sign}{pips:.1f}
<b>Ticket:</b> {ticket}
"""
        return self.client.send_message(self.chat_id, message.strip())

    def notify_alert(
        self,
        title: str,
        message: str,
        severity: str = "info"
    ) -> bool:
        """Send alert notification."""
        emojis = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "🚨",
            "success": "✅"
        }
        emoji = emojis.get(severity, "📢")

        text = f"{emoji} <b>{title}</b>\n\n{message}"
        return self.client.send_message(self.chat_id, text)


def create_trading_bot(
    bot_token: str,
    chat_id: int,
    admin_ids: List[int]
) -> tuple:
    """Create trading Telegram bot."""
    client = HTTPTelegramClient(bot_token)
    bot = TelegramBot(client, admin_ids)
    notifier = TradingNotifier(client, chat_id)

    # Register default commands
    @bot.command("start", "Start the bot")
    def start_cmd(ctx: CommandContext) -> str:
        return f"Welcome, {ctx.message.user.first_name}! Use /help for commands."

    @bot.command("help", "Show available commands")
    def help_cmd(ctx: CommandContext) -> str:
        commands = bot.get_commands_list()
        lines = ["<b>Available Commands:</b>\n"]
        for cmd in commands:
            lines.append(f"/{cmd['command']} - {cmd['description']}")
        return "\n".join(lines)

    @bot.command("status", "Get system status")
    def status_cmd(ctx: CommandContext) -> str:
        return "✅ System is operational"

    @bot.command("ping", "Check bot response")
    def ping_cmd(ctx: CommandContext) -> str:
        return "🏓 Pong!"

    return bot, notifier


# Example usage
if __name__ == "__main__":
    # Create mock bot for testing
    client = MockTelegramClient()
    bot = TelegramBot(client, admin_ids=[123456])
    notifier = TradingNotifier(client, chat_id=123456)

    # Register commands
    @bot.command("signal", "Get latest signal")
    def signal_cmd(ctx: CommandContext) -> str:
        symbol = ctx.args[0] if ctx.args else "XAUUSD"
        return f"📊 {symbol}: BUY @ 2000, SL: 1990, TP: 2020"

    # Simulate update
    update = {
        "message": {
            "message_id": 1,
            "chat": {"id": 123456},
            "from": {"id": 123456, "first_name": "Trader"},
            "text": "/signal XAUUSD",
            "date": int(datetime.now().timestamp())
        }
    }

    print("Handling update...")
    response = bot.handle_update(update)
    print(f"Response: {response}")

    # Send notifications
    print("\nSending notifications...")
    notifier.notify_signal("XAUUSD", "BUY", 0.85, 2000, 1990, 2020)
    notifier.notify_trade_opened("XAUUSD", "BUY", 0.1, 2000, 12345)
    notifier.notify_trade_closed("XAUUSD", "BUY", 150.50, 20, 12345)

    print("\nSent messages:")
    for msg in client.messages:
        print(f"  - {msg['text'][:50]}...")
