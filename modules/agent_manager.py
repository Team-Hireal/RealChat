"""
Agent Manager - Coordinates multiple agents and ensures mutual exclusion

This module manages the lifecycle of different agents (WeChat Bridge, Message Analyzer,
Moments Browser) and ensures only one agent is active at a time.
"""

import json
import time
import threading
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from core.storage import UnifiedStorage


class AgentType(Enum):
    """Available agent types in the system"""
    WECHAT_BRIDGE = "wechat_bridge"
    MESSAGE_ANALYZER = "message_analyzer"
    MOMENTS_BROWSER = "moments_browser"
    RELATIONSHIP_ANALYZER = "relationship_analyzer"


class AgentState(Enum):
    """Agent lifecycle states"""
    IDLE = "idle"
    ACTIVATING = "activating"
    ACTIVE = "active"
    DEACTIVATING = "deactivating"
    ERROR = "error"


class AgentActiveError(Exception):
    """Raised when attempting to activate an agent while another is active"""
    pass


class AgentManager:
    """
    Singleton manager for coordinating agent lifecycle and mutual exclusion

    Ensures only one agent is active at a time and manages state transitions.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.storage = UnifiedStorage()
            self.active_agent: Optional[AgentType] = None
            self.agent_states: Dict[AgentType, AgentState] = {
                agent: AgentState.IDLE for agent in AgentType
            }
            self.agent_metadata: Dict[AgentType, Dict[str, Any]] = {}
            self._load_state()
            self.initialized = True

    def _load_state(self):
        """Load agent state from storage"""
        try:
            state_data = self.storage.load_agent_state("manager")
            if state_data:
                if state_data.get("active_agent"):
                    self.active_agent = AgentType(state_data["active_agent"])

                for agent_type_str, state_str in state_data.get("agent_states", {}).items():
                    agent_type = AgentType(agent_type_str)
                    self.agent_states[agent_type] = AgentState(state_str)

                self.agent_metadata = state_data.get("agent_metadata", {})
        except Exception as e:
            print(f"Warning: Could not load agent state: {e}")

    def _save_state(self):
        """Save agent state to storage"""
        # Convert agent metadata keys to strings
        serializable_metadata = {}
        for agent, metadata in self.agent_metadata.items():
            agent_key = agent.value if isinstance(agent, AgentType) else str(agent)
            serializable_metadata[agent_key] = metadata

        state_data = {
            "active_agent": self.active_agent.value if self.active_agent else None,
            "agent_states": {
                agent.value: state.value
                for agent, state in self.agent_states.items()
            },
            "agent_metadata": serializable_metadata,
            "last_updated": datetime.now().isoformat()
        }
        self.storage.save_agent_state("manager", state_data)

    def get_active_agent(self) -> Optional[AgentType]:
        """Get the currently active agent"""
        return self.active_agent

    def get_agent_state(self, agent_type: AgentType) -> AgentState:
        """Get the state of a specific agent"""
        return self.agent_states.get(agent_type, AgentState.IDLE)

    def get_all_states(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "active_agent": self.active_agent.value if self.active_agent else None,
            "agents": {
                agent.value: {
                    "state": state.value,
                    "metadata": self.agent_metadata.get(agent, {})
                }
                for agent, state in self.agent_states.items()
            },
            "timestamp": datetime.now().isoformat()
        }

    def activate_agent(self, agent_type: AgentType, force: bool = False, metadata: Dict[str, Any] = None) -> bool:
        """
        Activate an agent

        Args:
            agent_type: The agent to activate
            force: If True, deactivate current agent first
            metadata: Optional metadata about the agent activation

        Returns:
            True if activation successful

        Raises:
            AgentActiveError: If another agent is active and force=False
        """
        with self._lock:
            # Check if another agent is active
            if self.active_agent and self.active_agent != agent_type:
                if not force:
                    raise AgentActiveError(
                        f"Cannot activate {agent_type.value}: "
                        f"{self.active_agent.value} is currently active"
                    )
                else:
                    # Force deactivation of current agent
                    self.deactivate_agent(self.active_agent)

            # Check if agent is already active
            if self.active_agent == agent_type:
                return True

            # Activate the agent
            self.agent_states[agent_type] = AgentState.ACTIVATING
            self._save_state()

            try:
                # Perform activation (can be extended for specific agent logic)
                self._perform_activation(agent_type, metadata)

                # Update state
                self.active_agent = agent_type
                self.agent_states[agent_type] = AgentState.ACTIVE
                self.agent_metadata[agent_type] = metadata or {}
                self.agent_metadata[agent_type]["activated_at"] = datetime.now().isoformat()

                self._save_state()
                return True

            except Exception as e:
                self.agent_states[agent_type] = AgentState.ERROR
                self.agent_metadata[agent_type] = {"error": str(e)}
                self._save_state()
                raise

    def deactivate_agent(self, agent_type: AgentType) -> bool:
        """
        Deactivate an agent

        Args:
            agent_type: The agent to deactivate

        Returns:
            True if deactivation successful
        """
        with self._lock:
            if self.active_agent != agent_type:
                return True  # Already deactivated

            self.agent_states[agent_type] = AgentState.DEACTIVATING
            self._save_state()

            try:
                # Perform deactivation
                self._perform_deactivation(agent_type)

                # Update state
                self.active_agent = None
                self.agent_states[agent_type] = AgentState.IDLE
                if agent_type in self.agent_metadata:
                    self.agent_metadata[agent_type]["deactivated_at"] = datetime.now().isoformat()

                self._save_state()
                return True

            except Exception as e:
                self.agent_states[agent_type] = AgentState.ERROR
                self.agent_metadata[agent_type] = {"error": str(e)}
                self._save_state()
                raise

    def _perform_activation(self, agent_type: AgentType, metadata: Dict[str, Any] = None):
        """
        Perform agent-specific activation logic

        This can be extended to start specific processes or services
        """
        # Log activation
        print(f"Activating agent: {agent_type.value}")

        # Agent-specific activation logic can be added here
        # For example:
        # - Start background threads
        # - Initialize connections
        # - Load agent-specific configuration

    def _perform_deactivation(self, agent_type: AgentType):
        """
        Perform agent-specific deactivation logic

        This can be extended to stop specific processes or services
        """
        # Log deactivation
        print(f"Deactivating agent: {agent_type.value}")

        # Agent-specific deactivation logic can be added here
        # For example:
        # - Stop background threads
        # - Close connections
        # - Save agent state

    def set_agent_metadata(self, agent_type: AgentType, metadata: Dict[str, Any]):
        """Update metadata for an agent"""
        with self._lock:
            if agent_type not in self.agent_metadata:
                self.agent_metadata[agent_type] = {}
            self.agent_metadata[agent_type].update(metadata)
            self._save_state()

    def get_agent_metadata(self, agent_type: AgentType) -> Dict[str, Any]:
        """Get metadata for an agent"""
        return self.agent_metadata.get(agent_type, {})

    def reset_all(self):
        """Reset all agents to idle state (emergency use only)"""
        with self._lock:
            self.active_agent = None
            self.agent_states = {agent: AgentState.IDLE for agent in AgentType}
            self.agent_metadata = {}
            self._save_state()


# Singleton instance
agent_manager = AgentManager()
