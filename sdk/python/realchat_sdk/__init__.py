"""
RealChat Agent SDK for Python
Connect any LLM/agent to WeChat through the RealChat universal bridge.

Usage:
    from realchat_sdk import AgentBridge

    bridge = AgentBridge(name="MyAgent", port=9000)

    @bridge.on_message
    def handle(message, context):
        return f"[MyAgent] {my_llm.respond(message)}"

    bridge.start()
"""

from .bridge import AgentBridge

__version__ = "1.0.0"
__all__ = ["AgentBridge"]
