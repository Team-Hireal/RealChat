#!/usr/bin/env python3
"""
Example: OpenAI GPT Agent using RealChat SDK
Shows how to connect any LLM (OpenAI, Gemini, Llama, etc.) to WeChat.

Run:
    OPENAI_API_KEY=sk-... python examples/openai_agent.py

This creates a GPT-powered WeChat agent in ~20 lines of code.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sdk', 'python'))

import logging
logging.basicConfig(level=logging.INFO)

from realchat_sdk import AgentBridge

bridge = AgentBridge(
    name="gpt",
    port=9001,
    description="OpenAI GPT agent for WeChat",
    capabilities={"conversation_history": True, "length_matching": True},
)


@bridge.on_message
def handle(message: str, context: dict) -> str:
    """Route messages to OpenAI's API."""
    try:
        from openai import OpenAI
        client = OpenAI()  # Uses OPENAI_API_KEY env var

        # Build messages from history
        messages = [{"role": "system", "content": (
            "You are GPT, a WeChat messaging assistant. "
            "Always start with '[Gpt]'. Keep responses SHORT and casual. "
            "Match the user's message length."
        )}]

        for msg in context.get("history", []):
            messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=50,
        )

        return response.choices[0].message.content

    except ImportError:
        return "OpenAI package not installed. Run: pip install openai"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    bridge.start()
