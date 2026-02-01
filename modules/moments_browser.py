"""
Moments Browser - Browse and analyze WeChat Moments

This module provides functionality to browse WeChat Moments (similar to Facebook feed)
for both specific contacts and the general feed, extracting data for relationship analysis.
"""

import subprocess
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from core.storage import UnifiedStorage
from modules.privacy_controller import PrivacyController, PrivacyFeature


class MomentsBrowser:
    """
    Browse and analyze WeChat Moments

    Features:
    - Browse contact's moments from their profile
    - Browse general moments feed
    - Extract moment data (text, images, likes, comments)
    - Analyze moment content for relationship insights
    - Cache moments data
    """

    def __init__(self):
        self.storage = UnifiedStorage()
        self.privacy = PrivacyController()
        self.applescript_path = "scripts/wechat_moments.applescript"

    def browse_contact_moments(
        self,
        contact_id: str,
        contact_name: str,
        limit: int = 10,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Browse moments from a specific contact's profile

        Args:
            contact_id: Contact ID
            contact_name: Contact display name (for AppleScript)
            limit: Maximum number of moments to retrieve
            force_refresh: Force refresh even if cached data exists

        Returns:
            Dictionary with moments data and metadata
        """
        # Check authorization
        if not self.privacy.check_authorization(PrivacyFeature.BROWSE_MOMENTS, contact_id):
            return {
                'success': False,
                'error': 'Not authorized to browse moments for this contact',
                'authorized': False
            }

        # Check cache first
        if not force_refresh:
            cached_moments = self.storage.load_contact_moments(contact_id)
            if cached_moments:
                return {
                    'success': True,
                    'contact_id': contact_id,
                    'moments': cached_moments[:limit],
                    'cached': True,
                    'timestamp': datetime.now().isoformat()
                }

        # Browse moments using AppleScript
        try:
            result = self._browse_contact_moments_applescript(contact_name, limit)

            if result['success']:
                moments = result['moments']

                # Save to storage
                self.storage.save_contact_moments(contact_id, moments)

                # Log privacy action
                self.privacy.log_privacy_action(
                    feature=PrivacyFeature.BROWSE_MOMENTS,
                    action='browse_contact',
                    contact_id=contact_id,
                    details={'moments_count': len(moments)}
                )

                return {
                    'success': True,
                    'contact_id': contact_id,
                    'moments': moments,
                    'cached': False,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return result

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to browse moments: {str(e)}'
            }

    def browse_feed_moments(
        self,
        limit: int = 20,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Browse general moments feed

        Args:
            limit: Maximum number of moments to retrieve
            force_refresh: Force refresh even if cached data exists

        Returns:
            Dictionary with moments data and metadata
        """
        # Check authorization (general feed browsing)
        if not self.privacy.check_authorization(PrivacyFeature.BROWSE_MOMENTS):
            return {
                'success': False,
                'error': 'Not authorized to browse moments feed',
                'authorized': False
            }

        # Check cache first
        if not force_refresh:
            cached_feed = self.storage.load_feed_cache()
            if cached_feed:
                return {
                    'success': True,
                    'moments': cached_feed[:limit],
                    'cached': True,
                    'timestamp': datetime.now().isoformat()
                }

        # Browse feed using AppleScript
        try:
            result = self._browse_feed_moments_applescript(limit)

            if result['success']:
                moments = result['moments']

                # Save to cache
                self.storage.save_feed_cache(moments)

                # Log privacy action
                self.privacy.log_privacy_action(
                    feature=PrivacyFeature.BROWSE_MOMENTS,
                    action='browse_feed',
                    details={'moments_count': len(moments)}
                )

                return {
                    'success': True,
                    'moments': moments,
                    'cached': False,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return result

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to browse feed: {str(e)}'
            }

    def _browse_contact_moments_applescript(
        self,
        contact_name: str,
        limit: int
    ) -> Dict[str, Any]:
        """
        Use AppleScript to browse contact moments

        Args:
            contact_name: Contact display name
            limit: Maximum number of moments

        Returns:
            Result dictionary
        """
        try:
            # Call AppleScript
            cmd = [
                'osascript',
                self.applescript_path,
                'browse_contact',
                contact_name,
                str(limit)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Parse output
                output = result.stdout.strip()

                # Try to parse as JSON
                try:
                    data = json.loads(output)
                    return data
                except json.JSONDecodeError:
                    # If not JSON, treat as error message
                    if output.startswith('Error:'):
                        return {'success': False, 'error': output}
                    else:
                        # Parse plain text output
                        moments = self._parse_moments_text(output)
                        return {'success': True, 'moments': moments}
            else:
                return {
                    'success': False,
                    'error': f'AppleScript error: {result.stderr}'
                }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Timeout while browsing moments'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to execute AppleScript: {str(e)}'
            }

    def _browse_feed_moments_applescript(self, limit: int) -> Dict[str, Any]:
        """
        Use AppleScript to browse feed moments

        Args:
            limit: Maximum number of moments

        Returns:
            Result dictionary
        """
        try:
            cmd = [
                'osascript',
                self.applescript_path,
                'browse_feed',
                str(limit)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=90
            )

            if result.returncode == 0:
                output = result.stdout.strip()

                try:
                    data = json.loads(output)
                    return data
                except json.JSONDecodeError:
                    if output.startswith('Error:'):
                        return {'success': False, 'error': output}
                    else:
                        moments = self._parse_moments_text(output)
                        return {'success': True, 'moments': moments}
            else:
                return {
                    'success': False,
                    'error': f'AppleScript error: {result.stderr}'
                }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Timeout while browsing feed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to execute AppleScript: {str(e)}'
            }

    def _parse_moments_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse moments from plain text output

        Args:
            text: Plain text output from AppleScript

        Returns:
            List of moment dictionaries
        """
        moments = []

        # Split by moment separator (assuming each moment is separated by "---")
        moment_texts = text.split('---')

        for i, moment_text in enumerate(moment_texts):
            if not moment_text.strip():
                continue

            moment = {
                'id': f'moment_{i}',
                'content': moment_text.strip(),
                'timestamp': datetime.now().isoformat(),
                'images': [],
                'likes': 0,
                'comments': 0
            }

            moments.append(moment)

        return moments

    def extract_moment_data(self, moment_raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and structure moment data

        Args:
            moment_raw: Raw moment data from AppleScript

        Returns:
            Structured moment data
        """
        return {
            'id': moment_raw.get('id', ''),
            'content': moment_raw.get('content', ''),
            'timestamp': moment_raw.get('timestamp', datetime.now().isoformat()),
            'images': moment_raw.get('images', []),
            'likes': moment_raw.get('likes', 0),
            'comments': moment_raw.get('comments', 0),
            'location': moment_raw.get('location'),
            'mentioned_contacts': moment_raw.get('mentioned_contacts', [])
        }

    def analyze_moment_content(self, moment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze moment content for insights

        Args:
            moment: Moment data

        Returns:
            Analysis result
        """
        content = moment.get('content', '')

        # Detect content type
        content_type = 'text'
        if moment.get('images'):
            content_type = 'image' if len(moment['images']) == 1 else 'album'

        # Detect topics
        topics = self._detect_topics(content)

        # Detect sentiment (basic)
        sentiment = self._detect_sentiment(content)

        # Detect work-related content
        is_work_related = self._is_work_related(content)

        return {
            'content_type': content_type,
            'topics': topics,
            'sentiment': sentiment,
            'is_work_related': is_work_related,
            'has_location': bool(moment.get('location')),
            'engagement': moment.get('likes', 0) + moment.get('comments', 0)
        }

    def _detect_topics(self, content: str) -> List[str]:
        """Detect topics in moment content"""
        topics = []
        content_lower = content.lower()

        topic_keywords = {
            'work': ['work', 'office', 'meeting', 'project', 'client', 'business'],
            'family': ['family', 'kids', 'children', 'parents', 'home'],
            'travel': ['travel', 'trip', 'vacation', 'holiday', 'visit'],
            'food': ['food', 'restaurant', 'dinner', 'lunch', 'breakfast', 'cooking'],
            'sports': ['sports', 'gym', 'exercise', 'running', 'fitness'],
            'entertainment': ['movie', 'music', 'concert', 'show', 'game'],
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def _detect_sentiment(self, content: str) -> str:
        """Detect sentiment (basic)"""
        content_lower = content.lower()

        positive_words = ['happy', 'great', 'awesome', 'love', 'excited', 'wonderful', 'amazing']
        negative_words = ['sad', 'bad', 'terrible', 'hate', 'angry', 'disappointed']

        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def _is_work_related(self, content: str) -> bool:
        """Check if content is work-related"""
        work_keywords = [
            'work', 'office', 'meeting', 'project', 'client', 'business',
            'conference', 'presentation', 'deadline', 'team', 'colleague'
        ]

        content_lower = content.lower()
        return any(keyword in content_lower for keyword in work_keywords)

    def categorize_contact_from_moments(
        self,
        contact_id: str,
        moments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Categorize contact based on their moments

        Args:
            contact_id: Contact ID
            moments: List of moments

        Returns:
            Categorization result
        """
        if not moments:
            return {
                'category': 'unknown',
                'confidence': 0.0,
                'reason': 'No moments available'
            }

        # Analyze all moments
        work_count = 0
        family_count = 0
        personal_count = 0

        for moment in moments:
            analysis = self.analyze_moment_content(moment)

            if analysis['is_work_related']:
                work_count += 1

            topics = analysis['topics']
            if 'family' in topics:
                family_count += 1
            if 'travel' in topics or 'food' in topics or 'entertainment' in topics:
                personal_count += 1

        total = len(moments)

        # Determine category
        if work_count / total > 0.5:
            category = 'professional'
            confidence = work_count / total
        elif family_count / total > 0.3:
            category = 'family'
            confidence = family_count / total
        else:
            category = 'personal'
            confidence = personal_count / total if personal_count > 0 else 0.5

        return {
            'category': category,
            'confidence': confidence,
            'work_moments': work_count,
            'family_moments': family_count,
            'personal_moments': personal_count,
            'total_moments': total
        }


# Singleton instance
moments_browser = MomentsBrowser()
