"""
RealChat Modules Package

Core modules for RealChat WeChat automation system:
- agent_manager: Coordinates multiple agents with mutual exclusion
- privacy_controller: Manages privacy authorization and audit logging
- message_analyzer: Analyzes message importance and pinning priority
- moments_browser: Browses and analyzes WeChat Moments
- relationship_analyzer: AI-powered relationship classification
"""

from .agent_manager import AgentManager, AgentType, AgentState, agent_manager
from .privacy_controller import PrivacyController, PrivacyFeature, AuthorizationLevel, privacy_controller
from .message_analyzer import MessageAnalyzer, message_analyzer
from .moments_browser import MomentsBrowser, moments_browser
from .relationship_analyzer import RelationshipAnalyzer, relationship_analyzer

__all__ = [
    'AgentManager',
    'AgentType',
    'AgentState',
    'agent_manager',
    'PrivacyController',
    'PrivacyFeature',
    'AuthorizationLevel',
    'privacy_controller',
    'MessageAnalyzer',
    'message_analyzer',
    'MomentsBrowser',
    'moments_browser',
    'RelationshipAnalyzer',
    'relationship_analyzer',
]

__version__ = '1.0.0'
