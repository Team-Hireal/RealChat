"""
Command Parser Module
Handles user commands sent through File Transfer chat to control the agent
"""

import re
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class CommandParser:
    """Parse and execute user commands for agent control"""

    # Command patterns
    COMMANDS = {
        'monitor': r'^(?:monitor|watch|track)\s+(.+)$',
        'stop_monitor': r'^(?:stop monitoring|stop watching|unmonitor)$',
        'status': r'^(?:status|check status|agent status)$',
        'list_chats': r'^(?:list chats|show chats|available chats)$',
        'help': r'^(?:help|commands|\?)$',
        'switch': r'^(?:switch to|change to)\s+(.+)$',
    }

    def __init__(self):
        self.compiled_patterns = {
            cmd: re.compile(pattern, re.IGNORECASE)
            for cmd, pattern in self.COMMANDS.items()
        }

    def parse(self, message: str) -> Optional[Dict]:
        """
        Parse a message to check if it's a command

        Args:
            message: User message to parse

        Returns:
            Dict with command info or None if not a command
        """
        message = message.strip()

        # Check each command pattern
        for cmd_name, pattern in self.compiled_patterns.items():
            match = pattern.match(message)
            if match:
                result = {
                    'command': cmd_name,
                    'raw_message': message
                }

                # Extract arguments if any
                if match.groups():
                    result['args'] = [g.strip() for g in match.groups()]

                logger.info(f"Parsed command: {cmd_name}")
                return result

        return None

    def is_command(self, message: str) -> bool:
        """Check if message is a command"""
        return self.parse(message) is not None

    def get_help_text(self) -> str:
        """Get help text with available commands"""
        return """🤖 RealChat Agent Commands:

📱 Chat Control:
• monitor <chat name> - Start monitoring a specific chat
• switch to <chat name> - Switch to monitoring a different chat
• stop monitoring - Stop monitoring current chat

📊 Status & Info:
• status - Check agent status and current chat
• list chats - Show available chats
• help - Show this help message

💡 Examples:
• "monitor John Doe" - Start monitoring chat with John Doe
• "switch to Work Group" - Switch to Work Group chat
• "status" - Check what chat is being monitored
• "list chats" - See all available chats

Note: Send these commands in File Transfer chat to control the agent."""


class CommandExecutor:
    """Execute parsed commands"""

    def __init__(self, wechat_service, agent_manager=None):
        self.wechat_service = wechat_service
        self.agent_manager = agent_manager
        self.parser = CommandParser()
        self.current_monitored_chat = None
        self.available_chats = []

    def execute(self, command_dict: Dict) -> str:
        """
        Execute a parsed command

        Args:
            command_dict: Parsed command dictionary

        Returns:
            str: Response message
        """
        cmd = command_dict['command']

        if cmd == 'help':
            return self.parser.get_help_text()

        elif cmd == 'status':
            return self._get_status()

        elif cmd == 'list_chats':
            return self._list_chats()

        elif cmd == 'monitor':
            chat_name = command_dict['args'][0]
            return self._start_monitoring(chat_name)

        elif cmd == 'switch':
            chat_name = command_dict['args'][0]
            return self._switch_chat(chat_name)

        elif cmd == 'stop_monitor':
            return self._stop_monitoring()

        else:
            return "❌ Unknown command. Type 'help' for available commands."

    def _get_status(self) -> str:
        """Get current agent status"""
        if self.current_monitored_chat:
            return f"""📊 Agent Status:
✅ Active
📱 Monitoring: {self.current_monitored_chat}
🤖 AI: Online
⏰ Last check: Just now

Type 'stop monitoring' to stop or 'switch to <chat>' to change."""
        else:
            return """📊 Agent Status:
⏹️ Not monitoring any chat
📱 Default: File Transfer (command mode)
🤖 AI: Online

Type 'monitor <chat name>' to start monitoring a chat."""

    def _list_chats(self) -> str:
        """List available chats"""
        try:
            # Scan for chats
            chats = self.wechat_service.scan_chats(max_chats=20)
            self.available_chats = chats

            if chats:
                chat_list = "\n".join([f"  • {chat}" for chat in chats])
                return f"""📱 Available Chats ({len(chats)}):
{chat_list}

Type 'monitor <chat name>' to start monitoring."""
            else:
                return "❌ No chats found. Make sure WeChat is open."
        except Exception as e:
            logger.error(f"Error listing chats: {e}")
            return f"❌ Error scanning chats: {str(e)}"

    def _start_monitoring(self, chat_name: str) -> str:
        """Start monitoring a specific chat"""
        try:
            # Verify chat exists
            if not self.available_chats:
                self.available_chats = self.wechat_service.scan_chats(max_chats=20)

            # Find matching chat (case-insensitive partial match)
            matched_chat = None
            for chat in self.available_chats:
                if chat_name.lower() in chat.lower() or chat.lower() in chat_name.lower():
                    matched_chat = chat
                    break

            if not matched_chat:
                return f"""❌ Chat '{chat_name}' not found.

Type 'list chats' to see available chats."""

            self.current_monitored_chat = matched_chat

            return f"""✅ Now monitoring: {matched_chat}

🤖 I'll respond to messages in this chat automatically.
📊 Type 'status' to check anytime
🔄 Type 'switch to <chat>' to change
⏹️ Type 'stop monitoring' to stop"""

        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            return f"❌ Error: {str(e)}"

    def _switch_chat(self, chat_name: str) -> str:
        """Switch to monitoring a different chat"""
        old_chat = self.current_monitored_chat
        result = self._start_monitoring(chat_name)

        if "✅" in result and old_chat:
            return f"""🔄 Switched from '{old_chat}' to '{self.current_monitored_chat}'

{result}"""
        return result

    def _stop_monitoring(self) -> str:
        """Stop monitoring current chat"""
        if self.current_monitored_chat:
            old_chat = self.current_monitored_chat
            self.current_monitored_chat = None
            return f"""⏹️ Stopped monitoring: {old_chat}

📱 Back to File Transfer command mode
Type 'monitor <chat>' to start monitoring again."""
        else:
            return "ℹ️ Not currently monitoring any chat."

    def get_current_chat(self) -> Optional[str]:
        """Get currently monitored chat"""
        return self.current_monitored_chat

    def set_current_chat(self, chat_name: Optional[str]):
        """Set currently monitored chat"""
        self.current_monitored_chat = chat_name
