"""
AgentBridge - The core SDK class for connecting agents to RealChat.
Handles registration, health endpoints, message routing, and WeChat formatting.
"""

import json
import time
import signal
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Callable, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

logger = logging.getLogger(__name__)


class AgentBridge:
    """Universal bridge for connecting any agent to RealChat's WeChat gateway."""

    def __init__(
        self,
        name: str,
        port: int = 9000,
        gateway_url: str = "http://localhost:5001",
        description: str = "",
        capabilities: Optional[dict] = None,
    ):
        self.name = name.lower().strip()
        self.port = port
        self.gateway_url = gateway_url
        self.description = description or f"{name} agent"
        self.prefix = f"[{name.capitalize()}]"
        self.capabilities = capabilities or {}
        self._message_handler: Optional[Callable] = None
        self._server: Optional[HTTPServer] = None
        self._start_time = time.time()

    def on_message(self, func: Callable):
        """Decorator to register a message handler.

        The handler receives (message: str, context: dict) and should return a string.
        The SDK automatically adds the agent prefix if missing.
        """
        self._message_handler = func
        return func

    def _format_response(self, text: str) -> str:
        """Ensure response has the agent prefix and is single-line."""
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = ' '.join(text.split())
        if not text.startswith(self.prefix):
            text = f"{self.prefix} {text}"
        return text

    def _register_with_gateway(self):
        """Register this agent with the RealChat gateway."""
        payload = json.dumps({
            "name": self.name,
            "url": f"http://localhost:{self.port}",
            "port": self.port,
            "description": self.description,
            "prefix": self.prefix,
            "capabilities": self.capabilities,
            "health_endpoint": "/health",
            "chat_endpoint": "/api/chat",
        }).encode()

        try:
            req = Request(
                f"{self.gateway_url}/api/agents/register",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            resp = urlopen(req, timeout=5)
            data = json.loads(resp.read())
            if data.get("success"):
                logger.info(f"Registered with gateway at {self.gateway_url}")
            else:
                logger.warning(f"Registration response: {data}")
        except URLError as e:
            logger.warning(f"Could not register with gateway (is it running?): {e}")
        except Exception as e:
            logger.error(f"Registration failed: {e}")

    def _deregister_from_gateway(self):
        """Deregister this agent from the gateway on shutdown."""
        try:
            req = Request(
                f"{self.gateway_url}/api/agents/{self.name}",
                method="DELETE",
            )
            urlopen(req, timeout=3)
            logger.info("Deregistered from gateway")
        except Exception:
            pass  # Best effort on shutdown

    def _create_handler(bridge_self):
        """Create the HTTP request handler with access to the bridge instance."""

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Suppress default logging

            def _send_json(self, status, data):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())

            def do_OPTIONS(self):
                self._send_json(200, {})

            def do_GET(self):
                if self.path == "/health":
                    self._send_json(200, {
                        "status": "ok",
                        "service": bridge_self.name,
                        "version": "1.0.0",
                        "uptime": time.time() - bridge_self._start_time,
                    })
                else:
                    self._send_json(404, {"error": "Not found"})

            def do_POST(self):
                if self.path == "/api/chat":
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = json.loads(self.rfile.read(content_length))

                    message = body.get("message", "")
                    if not message:
                        self._send_json(400, {"success": False, "error": "Message required"})
                        return

                    if not bridge_self._message_handler:
                        self._send_json(500, {"success": False, "error": "No handler registered"})
                        return

                    try:
                        context = {
                            "history": body.get("history", []),
                            "context": body.get("context", {}),
                            "model": body.get("model"),
                        }
                        response = bridge_self._message_handler(message, context)
                        response = bridge_self._format_response(response)

                        self._send_json(200, {
                            "success": True,
                            "response": response,
                            "model": bridge_self.name,
                            "agent": bridge_self.name,
                        })
                    except Exception as e:
                        logger.error(f"Handler error: {e}")
                        self._send_json(500, {"success": False, "error": str(e)})
                else:
                    self._send_json(404, {"error": "Not found"})

        return Handler

    def start(self):
        """Start the agent server and register with the gateway."""
        if not self._message_handler:
            raise RuntimeError("No message handler registered. Use @bridge.on_message")

        Handler = self._create_handler()
        self._server = HTTPServer(("0.0.0.0", self.port), Handler)

        # Register with gateway
        self._register_with_gateway()

        # Handle graceful shutdown
        def shutdown_handler(sig, frame):
            logger.info(f"Shutting down {self.name}...")
            self._deregister_from_gateway()
            self._server.shutdown()

        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        logger.info(f"{self.name} agent listening on port {self.port}")
        print(f"🤖 {self.name.capitalize()} agent running on http://localhost:{self.port}")
        print(f"   Health: http://localhost:{self.port}/health")
        print(f"   Chat:   http://localhost:{self.port}/api/chat")

        self._server.serve_forever()
