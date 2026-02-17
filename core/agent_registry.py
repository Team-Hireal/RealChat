"""
Universal Agent Registry for RealChat
Manages agent registration, discovery, health checking, and routing.
Any LLM/agent can register itself and communicate with WeChat through this protocol.
"""

import time
import logging
import threading
import requests
from dataclasses import dataclass, field, asdict
from typing import Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"


@dataclass
class AgentCapabilities:
    """What an agent can do."""
    streaming: bool = False
    conversation_history: bool = True
    length_matching: bool = False
    multi_language: bool = False
    custom_capabilities: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class AgentInfo:
    """Registered agent metadata."""
    name: str
    url: str
    port: int
    description: str = ""
    prefix: str = ""  # e.g. "[Zypher]", "[Claude]"
    capabilities: AgentCapabilities = field(default_factory=AgentCapabilities)
    status: AgentStatus = AgentStatus.OFFLINE
    registered_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    health_endpoint: str = "/health"
    chat_endpoint: str = "/api/chat"
    webhook_url: Optional[str] = None  # Optional callback URL for push-based messaging

    def to_dict(self):
        d = asdict(self)
        d['status'] = self.status.value
        return d


# Standard protocol request/response schemas
PROTOCOL_VERSION = "1.0"

CHAT_REQUEST_SCHEMA = {
    "message": "string (required)",
    "history": "[{role: 'user'|'assistant', content: string}] (optional)",
    "context": "{sender: string, chat: string} (optional)",
    "model": "string (optional - agent's preferred model)",
    "max_tokens": "int (optional)",
}

CHAT_RESPONSE_SCHEMA = {
    "success": "bool",
    "response": "string",
    "model": "string",
    "agent": "string (agent name)",
}

HEALTH_RESPONSE_SCHEMA = {
    "status": "string (ok|degraded|error)",
    "service": "string (agent name)",
    "version": "string (optional)",
    "uptime": "float (optional, seconds)",
}

CAPABILITIES_RESPONSE_SCHEMA = {
    "name": "string",
    "version": "string",
    "protocol_version": "string",
    "capabilities": "AgentCapabilities",
    "endpoints": "[string]",
}


class AgentRegistry:
    """Central registry for all connected agents."""

    def __init__(self, health_check_interval: int = 30):
        self._agents: dict[str, AgentInfo] = {}
        self._lock = threading.Lock()
        self._health_check_interval = health_check_interval
        self._health_thread: Optional[threading.Thread] = None
        self._running = False

        # Built-in agents (Claude is always available)
        self._builtin_agents = {"claude"}

    def start_health_checks(self):
        """Start background health checking thread."""
        if self._running:
            return
        self._running = True
        self._health_thread = threading.Thread(
            target=self._health_check_loop, daemon=True
        )
        self._health_thread.start()
        logger.info("Agent health checker started")

    def stop_health_checks(self):
        self._running = False

    def _health_check_loop(self):
        while self._running:
            time.sleep(self._health_check_interval)
            self._check_all_agents()

    def _check_all_agents(self):
        with self._lock:
            agents = list(self._agents.values())

        for agent in agents:
            try:
                url = f"{agent.url}{agent.health_endpoint}"
                resp = requests.get(url, timeout=5)
                with self._lock:
                    if agent.name in self._agents:
                        if resp.status_code == 200:
                            self._agents[agent.name].status = AgentStatus.ONLINE
                            self._agents[agent.name].last_heartbeat = time.time()
                        else:
                            self._agents[agent.name].status = AgentStatus.DEGRADED
            except requests.exceptions.ConnectionError:
                with self._lock:
                    if agent.name in self._agents:
                        self._agents[agent.name].status = AgentStatus.OFFLINE
                        logger.warning(f"Agent '{agent.name}' is offline")
            except Exception as e:
                logger.error(f"Health check failed for '{agent.name}': {e}")

    def register(self, agent_data: dict) -> AgentInfo:
        """Register a new agent or update existing one."""
        name = agent_data.get("name", "").lower().strip()
        if not name:
            raise ValueError("Agent name is required")
        if name in self._builtin_agents:
            raise ValueError(f"Cannot register built-in agent '{name}'")

        url = agent_data.get("url", "")
        port = agent_data.get("port", 0)
        if not url:
            if port:
                url = f"http://localhost:{port}"
            else:
                raise ValueError("Agent URL or port is required")

        caps_data = agent_data.get("capabilities", {})
        capabilities = AgentCapabilities(
            streaming=caps_data.get("streaming", False),
            conversation_history=caps_data.get("conversation_history", True),
            length_matching=caps_data.get("length_matching", False),
            multi_language=caps_data.get("multi_language", False),
            custom_capabilities=caps_data.get("custom_capabilities", []),
        )

        agent = AgentInfo(
            name=name,
            url=url,
            port=port,
            description=agent_data.get("description", ""),
            prefix=agent_data.get("prefix", f"[{name.capitalize()}]"),
            capabilities=capabilities,
            status=AgentStatus.ONLINE,
            health_endpoint=agent_data.get("health_endpoint", "/health"),
            chat_endpoint=agent_data.get("chat_endpoint", "/api/chat"),
            webhook_url=agent_data.get("webhook_url"),
        )

        with self._lock:
            is_update = name in self._agents
            self._agents[name] = agent

        action = "updated" if is_update else "registered"
        logger.info(f"Agent '{name}' {action} at {url}")
        return agent

    def unregister(self, name: str) -> bool:
        name = name.lower().strip()
        with self._lock:
            if name in self._agents:
                del self._agents[name]
                logger.info(f"Agent '{name}' unregistered")
                return True
        return False

    def get_agent(self, name: str) -> Optional[AgentInfo]:
        name = name.lower().strip()
        with self._lock:
            return self._agents.get(name)

    def list_agents(self, include_offline: bool = True) -> list[AgentInfo]:
        with self._lock:
            agents = list(self._agents.values())
        if not include_offline:
            agents = [a for a in agents if a.status != AgentStatus.OFFLINE]
        return agents

    def route_message(self, agent_name: str, message: str, history: list = None, context: dict = None, timeout: int = 10) -> dict:
        """Route a message to a registered agent and return the response."""
        agent = self.get_agent(agent_name)
        if not agent:
            return {"success": False, "error": f"Agent '{agent_name}' not found"}

        if agent.status == AgentStatus.OFFLINE:
            return {"success": False, "error": f"Agent '{agent_name}' is offline"}

        try:
            payload = {"message": message}
            if history:
                payload["history"] = history
            if context:
                payload["context"] = context

            url = f"{agent.url}{agent.chat_endpoint}"
            resp = requests.post(url, json=payload, timeout=timeout)

            if resp.status_code == 200:
                data = resp.json()
                data["agent"] = agent_name
                # Update heartbeat on successful communication
                with self._lock:
                    if agent_name in self._agents:
                        self._agents[agent_name].last_heartbeat = time.time()
                return data
            else:
                return {
                    "success": False,
                    "error": f"Agent returned status {resp.status_code}",
                    "agent": agent_name,
                }
        except requests.exceptions.ConnectionError:
            with self._lock:
                if agent_name in self._agents:
                    self._agents[agent_name].status = AgentStatus.OFFLINE
            return {"success": False, "error": f"Agent '{agent_name}' is unreachable"}
        except requests.exceptions.Timeout:
            return {"success": False, "error": f"Agent '{agent_name}' timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_agent_health(self, name: str) -> dict:
        """Check health of a specific agent."""
        agent = self.get_agent(name)
        if not agent:
            return {"status": "not_found", "agent": name}

        try:
            url = f"{agent.url}{agent.health_endpoint}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                with self._lock:
                    self._agents[name].status = AgentStatus.ONLINE
                    self._agents[name].last_heartbeat = time.time()
                health_data = resp.json()
                health_data["registered"] = True
                return health_data
            else:
                with self._lock:
                    self._agents[name].status = AgentStatus.DEGRADED
                return {"status": "degraded", "agent": name, "http_status": resp.status_code}
        except requests.exceptions.ConnectionError:
            with self._lock:
                self._agents[name].status = AgentStatus.OFFLINE
            return {"status": "offline", "agent": name}
        except Exception as e:
            return {"status": "error", "agent": name, "error": str(e)}
