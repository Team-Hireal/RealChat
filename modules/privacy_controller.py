"""
Privacy Controller - Manages user authorization and privacy settings

This module ensures all privacy-sensitive actions require explicit user consent
and maintains an audit log of all privacy-related operations.
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from core.storage import UnifiedStorage


class PrivacyFeature(Enum):
    """Privacy-sensitive features that require authorization"""
    AUTO_REPLY = "auto_reply"
    READ_MESSAGES = "read_messages"
    BROWSE_MOMENTS = "browse_moments"
    PIN_MESSAGES = "pin_messages"
    ANALYZE_RELATIONSHIPS = "analyze_relationships"
    SEND_MESSAGES = "send_messages"
    ACCESS_CONTACTS = "access_contacts"
    READ_CHAT_HISTORY = "read_chat_history"


class AuthorizationLevel(Enum):
    """Authorization levels for features"""
    DENIED = "denied"
    AUTHORIZED = "authorized"
    AUTHORIZED_WITH_CONTACTS = "authorized_with_contacts"  # Only for specific contacts


class PrivacyController:
    """
    Manages privacy authorization and audit logging

    Ensures all privacy-sensitive actions require explicit user consent
    """

    def __init__(self):
        self.storage = UnifiedStorage()
        self.authorizations: Dict[PrivacyFeature, Dict[str, Any]] = {}
        self._load_authorizations()

    def _load_authorizations(self):
        """Load authorization settings from storage"""
        try:
            auth_data = self.storage.load_authorization()
            if auth_data:
                for feature_str, auth_info in auth_data.items():
                    try:
                        feature = PrivacyFeature(feature_str)
                        self.authorizations[feature] = auth_info
                    except ValueError:
                        print(f"Warning: Unknown privacy feature: {feature_str}")
        except Exception as e:
            print(f"Warning: Could not load authorizations: {e}")

    def _save_authorizations(self):
        """Save authorization settings to storage"""
        auth_data = {
            feature.value: auth_info
            for feature, auth_info in self.authorizations.items()
        }
        self.storage.save_authorization(auth_data)

    def check_authorization(
        self,
        feature: PrivacyFeature,
        contact_id: Optional[str] = None
    ) -> bool:
        """
        Check if a feature is authorized

        Args:
            feature: The privacy feature to check
            contact_id: Optional contact ID for contact-specific authorization

        Returns:
            True if authorized, False otherwise
        """
        if feature not in self.authorizations:
            return False

        auth_info = self.authorizations[feature]
        level = AuthorizationLevel(auth_info.get("level", "denied"))

        if level == AuthorizationLevel.DENIED:
            return False

        if level == AuthorizationLevel.AUTHORIZED:
            return True

        if level == AuthorizationLevel.AUTHORIZED_WITH_CONTACTS:
            if contact_id is None:
                return False
            authorized_contacts = auth_info.get("contacts", [])
            return contact_id in authorized_contacts

        return False

    def request_authorization(
        self,
        feature: PrivacyFeature,
        level: AuthorizationLevel = AuthorizationLevel.AUTHORIZED,
        contacts: Optional[List[str]] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Request authorization for a feature

        Args:
            feature: The privacy feature to authorize
            level: Authorization level
            contacts: List of contact IDs (for AUTHORIZED_WITH_CONTACTS level)
            reason: Optional reason for the authorization request

        Returns:
            True if authorization granted
        """
        # Validate contact-specific authorization
        if level == AuthorizationLevel.AUTHORIZED_WITH_CONTACTS and not contacts:
            raise ValueError("Contacts list required for AUTHORIZED_WITH_CONTACTS level")

        # Create authorization record
        auth_info = {
            "level": level.value,
            "authorized_at": datetime.now().isoformat(),
            "reason": reason
        }

        if contacts:
            auth_info["contacts"] = contacts

        self.authorizations[feature] = auth_info
        self._save_authorizations()

        # Log the authorization
        self.log_privacy_action(
            feature=feature,
            action="authorize",
            details={"level": level.value, "reason": reason}
        )

        return True

    def revoke_authorization(
        self,
        feature: PrivacyFeature,
        contact_id: Optional[str] = None
    ) -> bool:
        """
        Revoke authorization for a feature

        Args:
            feature: The privacy feature to revoke
            contact_id: Optional contact ID to revoke for specific contact

        Returns:
            True if revocation successful
        """
        if feature not in self.authorizations:
            return True  # Already not authorized

        if contact_id:
            # Revoke for specific contact
            auth_info = self.authorizations[feature]
            if "contacts" in auth_info:
                contacts = auth_info["contacts"]
                if contact_id in contacts:
                    contacts.remove(contact_id)
                    if not contacts:
                        # No contacts left, revoke entirely
                        del self.authorizations[feature]
                    else:
                        auth_info["contacts"] = contacts
                        self.authorizations[feature] = auth_info
        else:
            # Revoke entirely
            del self.authorizations[feature]

        self._save_authorizations()

        # Log the revocation
        self.log_privacy_action(
            feature=feature,
            action="revoke",
            details={"contact_id": contact_id}
        )

        return True

    def get_authorization_status(
        self,
        feature: Optional[PrivacyFeature] = None
    ) -> Dict[str, Any]:
        """
        Get authorization status

        Args:
            feature: Optional specific feature to check

        Returns:
            Authorization status information
        """
        if feature:
            if feature not in self.authorizations:
                return {
                    "feature": feature.value,
                    "authorized": False,
                    "level": AuthorizationLevel.DENIED.value
                }

            auth_info = self.authorizations[feature]
            return {
                "feature": feature.value,
                "authorized": True,
                "level": auth_info.get("level"),
                "authorized_at": auth_info.get("authorized_at"),
                "contacts": auth_info.get("contacts", []),
                "reason": auth_info.get("reason")
            }
        else:
            # Return all authorizations
            return {
                "authorizations": {
                    feature.value: {
                        "level": auth_info.get("level"),
                        "authorized_at": auth_info.get("authorized_at"),
                        "contacts": auth_info.get("contacts", [])
                    }
                    for feature, auth_info in self.authorizations.items()
                },
                "timestamp": datetime.now().isoformat()
            }

    def add_authorized_contact(
        self,
        feature: PrivacyFeature,
        contact_id: str
    ) -> bool:
        """
        Add a contact to the authorized list for a feature

        Args:
            feature: The privacy feature
            contact_id: Contact ID to add

        Returns:
            True if successful
        """
        if feature not in self.authorizations:
            # Create new authorization with contact
            self.request_authorization(
                feature=feature,
                level=AuthorizationLevel.AUTHORIZED_WITH_CONTACTS,
                contacts=[contact_id]
            )
        else:
            auth_info = self.authorizations[feature]
            level = AuthorizationLevel(auth_info.get("level"))

            if level == AuthorizationLevel.AUTHORIZED:
                # Already fully authorized, no need to add contact
                return True

            if level == AuthorizationLevel.AUTHORIZED_WITH_CONTACTS:
                contacts = auth_info.get("contacts", [])
                if contact_id not in contacts:
                    contacts.append(contact_id)
                    auth_info["contacts"] = contacts
                    self.authorizations[feature] = auth_info
                    self._save_authorizations()

        self.log_privacy_action(
            feature=feature,
            action="add_contact",
            details={"contact_id": contact_id}
        )

        return True

    def remove_authorized_contact(
        self,
        feature: PrivacyFeature,
        contact_id: str
    ) -> bool:
        """
        Remove a contact from the authorized list for a feature

        Args:
            feature: The privacy feature
            contact_id: Contact ID to remove

        Returns:
            True if successful
        """
        return self.revoke_authorization(feature, contact_id)

    def log_privacy_action(
        self,
        feature: PrivacyFeature,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        contact_id: Optional[str] = None
    ):
        """
        Log a privacy-sensitive action

        Args:
            feature: The privacy feature involved
            action: The action performed (authorize, revoke, access, etc.)
            details: Optional additional details
            contact_id: Optional contact ID involved
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "feature": feature.value,
            "action": action,
            "contact_id": contact_id,
            "details": details or {}
        }

        # Save to audit log
        try:
            self.storage.append_privacy_log(log_entry)
        except Exception as e:
            print(f"Warning: Could not save privacy log: {e}")

    def get_privacy_log(
        self,
        feature: Optional[PrivacyFeature] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get privacy audit log

        Args:
            feature: Optional filter by feature
            limit: Maximum number of entries to return

        Returns:
            List of log entries
        """
        try:
            logs = self.storage.load_privacy_log()
            if feature:
                logs = [log for log in logs if log.get("feature") == feature.value]
            return logs[-limit:]
        except Exception as e:
            print(f"Warning: Could not load privacy log: {e}")
            return []

    def require_authorization(self, feature: PrivacyFeature, contact_id: Optional[str] = None):
        """
        Decorator to require authorization for a function

        Usage:
            @privacy_controller.require_authorization(PrivacyFeature.READ_MESSAGES)
            def read_message(message_id):
                ...
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.check_authorization(feature, contact_id):
                    raise PermissionError(
                        f"Authorization required for {feature.value}"
                    )
                return func(*args, **kwargs)
            return wrapper
        return decorator


# Singleton instance
privacy_controller = PrivacyController()
