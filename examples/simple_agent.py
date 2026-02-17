#!/usr/bin/env python3
"""
Example: Simple Echo Agent using RealChat SDK
Demonstrates the minimal code needed to connect any agent to WeChat.

Run:
    python examples/simple_agent.py

This agent will:
1. Start on port 9000
2. Register itself with the RealChat gateway
3. Echo back any message it receives with a twist
"""

import sys
import os

# Add SDK to path (in production, you'd pip install realchat-sdk)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sdk', 'python'))

import logging
logging.basicConfig(level=logging.INFO)

from realchat_sdk import AgentBridge

# Create the bridge — that's it for setup
bridge = AgentBridge(
    name="echo",
    port=9000,
    description="Simple echo agent for testing",
    capabilities={"conversation_history": True, "length_matching": True},
)


@bridge.on_message
def handle(message: str, context: dict) -> str:
    """Handle incoming messages. Return a string response."""
    # Access conversation history if needed
    history = context.get("history", [])
    turn_count = len(history) // 2 + 1

    # Simple echo with personality
    word_count = len(message.split())
    if word_count <= 3:
        return f"Got it: {message}"
    elif word_count <= 10:
        return f"You said '{message}' — interesting! (turn {turn_count})"
    else:
        return f"That's a lot to unpack! Let me think about '{message[:50]}...'"


if __name__ == "__main__":
    bridge.start()
