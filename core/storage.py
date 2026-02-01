"""
RealChat Unified Storage System
Centralized data storage accessible by all components
"""

import os
import json
import tarfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class UnifiedStorage:
    """Unified file storage system for RealChat"""

    def __init__(self, base_path: str = '~/.realchat'):
        self.base_path = Path(os.path.expanduser(base_path))
        self.ensure_directories()

    def ensure_directories(self):
        """Create necessary directory structure"""
        directories = [
            'config',
            'data/chat_history',
            'data/contacts',
            'data/moments',
            'backups',
            'logs'
        ]

        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Storage initialized at: {self.base_path}")

    # ========================================================================
    # User Profile Management
    # ========================================================================

    def save_user_profile(self, profile_data: Dict[str, Any]) -> bool:
        """Save user profile"""
        try:
            path = self.base_path / 'config' / 'user_profile.json'
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            logger.info("User profile saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save user profile: {e}")
            return False

    def load_user_profile(self) -> Dict[str, Any]:
        """Load user profile"""
        try:
            path = self.base_path / 'config' / 'user_profile.json'
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load user profile: {e}")
        return {}

    # ========================================================================
    # Response Templates
    # ========================================================================

    def save_templates(self, templates: List[Dict[str, Any]]) -> bool:
        """Save response templates"""
        try:
            path = self.base_path / 'config' / 'response_templates.json'
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(templates, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(templates)} templates")
            return True
        except Exception as e:
            logger.error(f"Failed to save templates: {e}")
            return False

    def load_templates(self) -> List[Dict[str, Any]]:
        """Load response templates"""
        try:
            path = self.base_path / 'config' / 'response_templates.json'
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
        return []

    # ========================================================================
    # Authorization Management
    # ========================================================================

    def save_authorization(self, auth_data: Dict[str, bool]) -> bool:
        """Save authorization settings"""
        try:
            path = self.base_path / 'config' / 'authorization.json'
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(auth_data, f, indent=2)
            logger.info("Authorization settings saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save authorization: {e}")
            return False

    def load_authorization(self) -> Dict[str, bool]:
        """Load authorization settings"""
        try:
            path = self.base_path / 'config' / 'authorization.json'
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load authorization: {e}")

        # Default authorization (all disabled)
        return {
            'read_chats': False,
            'send_messages': False,
            'auto_reply': False,
            'pin_messages': False,
            'browse_moments': False,
            'categorize_contacts': False,
            'access_profile': False,
        }

    # ========================================================================
    # Agent State Management
    # ========================================================================

    def save_agent_state(self, state_data: Dict[str, Any]) -> bool:
        """Save agent state"""
        try:
            path = self.base_path / 'config' / 'agent_state.json'
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save agent state: {e}")
            return False

    def load_agent_state(self) -> Dict[str, Any]:
        """Load agent state"""
        try:
            path = self.base_path / 'config' / 'agent_state.json'
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load agent state: {e}")

        # Default state
        return {
            'active_agent': None,
            'agents': {
                'anthropic': {'state': 'DORMANT'},
                'zypher': {'state': 'DORMANT'},
                'openclaw': {'state': 'DORMANT'}
            }
        }

    # ========================================================================
    # Chat History Management
    # ========================================================================

    def save_chat_history(self, contact_id: str, messages: List[Dict[str, Any]]) -> bool:
        """Save chat history for a contact"""
        try:
            path = self.base_path / 'data' / 'chat_history' / f'{contact_id}.json'
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({
                    'contact_id': contact_id,
                    'last_updated': datetime.now().isoformat(),
                    'messages': messages
                }, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save chat history for {contact_id}: {e}")
            return False

    def load_chat_history(self, contact_id: str) -> List[Dict[str, Any]]:
        """Load chat history for a contact"""
        try:
            path = self.base_path / 'data' / 'chat_history' / f'{contact_id}.json'
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('messages', [])
        except Exception as e:
            logger.error(f"Failed to load chat history for {contact_id}: {e}")
        return []

    # ========================================================================
    # Contact Management
    # ========================================================================

    def save_contact_info(self, contact_id: str, contact_data: Dict[str, Any]) -> bool:
        """Save contact information"""
        try:
            path = self.base_path / 'data' / 'contacts' / f'{contact_id}.json'
            contact_data['last_updated'] = datetime.now().isoformat()
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(contact_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save contact info for {contact_id}: {e}")
            return False

    def load_contact_info(self, contact_id: str) -> Dict[str, Any]:
        """Load contact information"""
        try:
            path = self.base_path / 'data' / 'contacts' / f'{contact_id}.json'
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load contact info for {contact_id}: {e}")
        return {}

    def save_contact_category(self, contact_id: str, category: str) -> bool:
        """Save contact category"""
        try:
            categories_path = self.base_path / 'data' / 'contacts' / 'categories.json'
            categories = {}

            if categories_path.exists():
                with open(categories_path, 'r', encoding='utf-8') as f:
                    categories = json.load(f)

            categories[contact_id] = {
                'category': category,
                'updated_at': datetime.now().isoformat()
            }

            with open(categories_path, 'w', encoding='utf-8') as f:
                json.dump(categories, f, indent=2, ensure_ascii=False)

            logger.info(f"Contact {contact_id} categorized as: {category}")
            return True
        except Exception as e:
            logger.error(f"Failed to save contact category: {e}")
            return False

    def load_contact_categories(self) -> Dict[str, Dict[str, Any]]:
        """Load all contact categories"""
        try:
            categories_path = self.base_path / 'data' / 'contacts' / 'categories.json'
            if categories_path.exists():
                with open(categories_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load contact categories: {e}")
        return {}

    # ========================================================================
    # Moments Management
    # ========================================================================

    def save_contact_moments(self, contact_id: str, moments: List[Dict[str, Any]]) -> bool:
        """Save contact's moments"""
        try:
            path = self.base_path / 'data' / 'moments' / f'{contact_id}_moments.json'
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({
                    'contact_id': contact_id,
                    'last_updated': datetime.now().isoformat(),
                    'moments': moments
                }, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save moments for {contact_id}: {e}")
            return False

    def load_contact_moments(self, contact_id: str) -> List[Dict[str, Any]]:
        """Load contact's moments"""
        try:
            path = self.base_path / 'data' / 'moments' / f'{contact_id}_moments.json'
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('moments', [])
        except Exception as e:
            logger.error(f"Failed to load moments for {contact_id}: {e}")
        return []

    def save_feed_cache(self, feed_data: List[Dict[str, Any]]) -> bool:
        """Save moments feed cache"""
        try:
            path = self.base_path / 'data' / 'moments' / 'feed_cache.json'
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({
                    'last_updated': datetime.now().isoformat(),
                    'feed': feed_data
                }, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save feed cache: {e}")
            return False

    def load_feed_cache(self) -> List[Dict[str, Any]]:
        """Load moments feed cache"""
        try:
            path = self.base_path / 'data' / 'moments' / 'feed_cache.json'
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('feed', [])
        except Exception as e:
            logger.error(f"Failed to load feed cache: {e}")
        return []

    # ========================================================================
    # Backup & Restore
    # ========================================================================

    def create_backup(self) -> Optional[str]:
        """Create backup of all data"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'{timestamp}_backup.tar.gz'
            backup_path = self.base_path / 'backups' / backup_filename

            # Create tar.gz of data and config directories
            with tarfile.open(backup_path, 'w:gz') as tar:
                tar.add(self.base_path / 'data', arcname='data')
                tar.add(self.base_path / 'config', arcname='config')

            logger.info(f"Backup created: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None

    def restore_backup(self, backup_path: str) -> bool:
        """Restore from backup"""
        try:
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(self.base_path)

            logger.info(f"Backup restored from: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False

    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        try:
            backups_dir = self.base_path / 'backups'
            backups = []

            for backup_file in backups_dir.glob('*_backup.tar.gz'):
                stat = backup_file.stat()
                backups.append({
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat()
                })

            return sorted(backups, key=lambda x: x['created_at'], reverse=True)
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def clear_all_data(self) -> bool:
        """Clear all data (use with caution!)"""
        try:
            # Create backup first
            self.create_backup()

            # Clear data directories
            for directory in ['data/chat_history', 'data/contacts', 'data/moments']:
                dir_path = self.base_path / directory
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    dir_path.mkdir(parents=True, exist_ok=True)

            logger.warning("All data cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear data: {e}")
            return False

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            def get_dir_size(path):
                total = 0
                for entry in path.rglob('*'):
                    if entry.is_file():
                        total += entry.stat().st_size
                return total

            stats = {
                'total_size': get_dir_size(self.base_path),
                'config_size': get_dir_size(self.base_path / 'config'),
                'data_size': get_dir_size(self.base_path / 'data'),
                'backups_size': get_dir_size(self.base_path / 'backups'),
                'chat_history_count': len(list((self.base_path / 'data' / 'chat_history').glob('*.json'))),
                'contacts_count': len(list((self.base_path / 'data' / 'contacts').glob('*.json'))) - 1,  # Exclude categories.json
                'backups_count': len(list((self.base_path / 'backups').glob('*.tar.gz')))
            }

            return stats
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {}


# Global storage instance
storage = UnifiedStorage()
