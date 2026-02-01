"""
Message Analyzer - Analyzes message importance and determines pinning priority

This module scores messages based on various criteria including sender relationship,
content keywords, urgency, and context to determine which messages should be pinned.
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from core.storage import UnifiedStorage
from modules.privacy_controller import PrivacyController, PrivacyFeature


class MessageAnalyzer:
    """
    Analyzes message importance and determines pinning priority

    Scoring criteria:
    - Sender relationship (family: 10, professional: 8, personal: 6, other: 3)
    - Keywords (urgent, important, meeting, deadline, etc.)
    - Message length and complexity
    - Time sensitivity
    - Question detection
    - Mention of user's name
    """

    # Urgency keywords and their weights
    URGENCY_KEYWORDS = {
        'urgent': 3.0,
        'asap': 3.0,
        'emergency': 4.0,
        'immediately': 3.0,
        'critical': 3.0,
        'important': 2.0,
        'deadline': 2.5,
        'meeting': 2.0,
        'call me': 2.5,
        'need': 1.5,
        'help': 1.5,
        'please': 1.0,
        'today': 1.5,
        'now': 2.0,
        'quick': 1.0,
        'soon': 1.5,
    }

    # Relationship category weights
    RELATIONSHIP_WEIGHTS = {
        'family': 10.0,
        'professional': 8.0,
        'personal': 6.0,
        'service': 3.0,
        'other': 3.0,
    }

    # Pin thresholds
    PIN_THRESHOLD_CRITICAL = 9.0  # Always pin
    PIN_THRESHOLD_HIGH = 7.0      # Pin if unread
    PIN_THRESHOLD_MEDIUM = 5.0    # Pin if from important contact

    def __init__(self):
        self.storage = UnifiedStorage()
        self.privacy = PrivacyController()

    def analyze_importance(
        self,
        message: Dict[str, Any],
        contact: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze message importance

        Args:
            message: Message data (content, timestamp, etc.)
            contact: Contact information
            context: Optional context (chat history, user profile, etc.)

        Returns:
            Analysis result with score and reasoning
        """
        # Check authorization
        if not self.privacy.check_authorization(PrivacyFeature.READ_MESSAGES, contact.get('id')):
            return {
                'authorized': False,
                'score': 0,
                'reason': 'Not authorized to read messages from this contact'
            }

        # Calculate score
        score, factors = self.score_message(
            content=message.get('content', ''),
            sender_relationship=contact.get('category', 'other'),
            contact_id=contact.get('id'),
            context=context
        )

        # Determine if should pin
        should_pin = self.should_pin(score, message, contact)

        # Categorize message
        category = self.categorize_message(message, score)

        return {
            'authorized': True,
            'score': score,
            'should_pin': should_pin,
            'category': category,
            'factors': factors,
            'timestamp': datetime.now().isoformat()
        }

    def score_message(
        self,
        content: str,
        sender_relationship: str,
        contact_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate message importance score

        Returns:
            Tuple of (score, factors_dict)
        """
        factors = {}
        total_score = 0.0

        # 1. Relationship weight (base score)
        relationship_score = self.RELATIONSHIP_WEIGHTS.get(sender_relationship.lower(), 3.0)
        factors['relationship'] = relationship_score
        total_score += relationship_score

        # 2. Urgency keywords
        urgency_score = self._calculate_urgency_score(content)
        factors['urgency'] = urgency_score
        total_score += urgency_score

        # 3. Question detection
        question_score = self._detect_questions(content)
        factors['question'] = question_score
        total_score += question_score

        # 4. Message length (longer messages may be more important)
        length_score = self._calculate_length_score(content)
        factors['length'] = length_score
        total_score += length_score

        # 5. Name mention (if user's name is mentioned)
        if context and context.get('user_name'):
            name_score = self._detect_name_mention(content, context['user_name'])
            factors['name_mention'] = name_score
            total_score += name_score

        # 6. Time sensitivity
        time_score = self._detect_time_sensitivity(content)
        factors['time_sensitivity'] = time_score
        total_score += time_score

        # 7. Contact interaction frequency (bonus for frequent contacts)
        if context and context.get('interaction_frequency'):
            frequency_score = min(context['interaction_frequency'] / 10, 1.0)
            factors['interaction_frequency'] = frequency_score
            total_score += frequency_score

        # Normalize score to 0-10 range
        normalized_score = min(total_score, 10.0)

        return normalized_score, factors

    def _calculate_urgency_score(self, content: str) -> float:
        """Calculate urgency score based on keywords"""
        content_lower = content.lower()
        urgency_score = 0.0

        for keyword, weight in self.URGENCY_KEYWORDS.items():
            if keyword in content_lower:
                urgency_score += weight

        # Cap at 4.0
        return min(urgency_score, 4.0)

    def _detect_questions(self, content: str) -> float:
        """Detect if message contains questions"""
        # Count question marks
        question_marks = content.count('?')

        # Detect question words
        question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'can you', 'could you', 'would you']
        content_lower = content.lower()
        question_word_count = sum(1 for word in question_words if word in content_lower)

        # Score based on questions
        if question_marks > 0 or question_word_count > 0:
            return min(1.0 + (question_marks * 0.5) + (question_word_count * 0.3), 2.0)

        return 0.0

    def _calculate_length_score(self, content: str) -> float:
        """Calculate score based on message length"""
        length = len(content)

        if length < 10:
            return 0.0  # Very short messages
        elif length < 50:
            return 0.3  # Short messages
        elif length < 150:
            return 0.6  # Medium messages
        elif length < 300:
            return 0.9  # Long messages
        else:
            return 1.0  # Very long messages

    def _detect_name_mention(self, content: str, user_name: str) -> float:
        """Detect if user's name is mentioned"""
        content_lower = content.lower()
        name_lower = user_name.lower()

        if name_lower in content_lower:
            return 1.5  # Bonus for name mention

        return 0.0

    def _detect_time_sensitivity(self, content: str) -> float:
        """Detect time-sensitive content"""
        time_patterns = [
            r'\d{1,2}:\d{2}',  # Time (e.g., 3:30)
            r'\d{1,2}(am|pm)',  # Time (e.g., 3pm)
            r'(today|tomorrow|tonight)',
            r'(this|next) (morning|afternoon|evening|week|month)',
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        ]

        content_lower = content.lower()
        for pattern in time_patterns:
            if re.search(pattern, content_lower):
                return 1.0

        return 0.0

    def should_pin(
        self,
        score: float,
        message: Dict[str, Any],
        contact: Dict[str, Any]
    ) -> bool:
        """
        Determine if message should be pinned

        Args:
            score: Importance score
            message: Message data
            contact: Contact information

        Returns:
            True if message should be pinned
        """
        # Check authorization
        if not self.privacy.check_authorization(PrivacyFeature.PIN_MESSAGES, contact.get('id')):
            return False

        # Critical messages always pin
        if score >= self.PIN_THRESHOLD_CRITICAL:
            return True

        # High priority messages pin if unread
        if score >= self.PIN_THRESHOLD_HIGH:
            if message.get('unread', True):
                return True

        # Medium priority messages pin if from important contact
        if score >= self.PIN_THRESHOLD_MEDIUM:
            relationship = contact.get('category', 'other').lower()
            if relationship in ['family', 'professional']:
                return True

        return False

    def categorize_message(self, message: Dict[str, Any], score: float) -> str:
        """
        Categorize message based on score

        Returns:
            Category string: 'critical', 'high', 'medium', 'low'
        """
        if score >= self.PIN_THRESHOLD_CRITICAL:
            return 'critical'
        elif score >= self.PIN_THRESHOLD_HIGH:
            return 'high'
        elif score >= self.PIN_THRESHOLD_MEDIUM:
            return 'medium'
        else:
            return 'low'

    def analyze_batch(
        self,
        messages: List[Dict[str, Any]],
        contacts: Dict[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze a batch of messages

        Args:
            messages: List of messages to analyze
            contacts: Dictionary of contact data (keyed by contact_id)
            context: Optional context

        Returns:
            List of analysis results
        """
        results = []

        for message in messages:
            contact_id = message.get('contact_id')
            contact = contacts.get(contact_id, {})

            analysis = self.analyze_importance(message, contact, context)
            analysis['message_id'] = message.get('id')
            analysis['contact_id'] = contact_id

            results.append(analysis)

        # Sort by score (highest first)
        results.sort(key=lambda x: x.get('score', 0), reverse=True)

        return results

    def get_messages_to_pin(
        self,
        messages: List[Dict[str, Any]],
        contacts: Dict[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of messages that should be pinned

        Args:
            messages: List of messages to analyze
            contacts: Dictionary of contact data
            context: Optional context

        Returns:
            List of messages that should be pinned
        """
        analyses = self.analyze_batch(messages, contacts, context)

        # Filter messages that should be pinned
        to_pin = [
            analysis for analysis in analyses
            if analysis.get('should_pin', False)
        ]

        return to_pin

    def save_analysis(
        self,
        contact_id: str,
        message_id: str,
        analysis: Dict[str, Any]
    ) -> bool:
        """
        Save message analysis to storage

        Args:
            contact_id: Contact ID
            message_id: Message ID
            analysis: Analysis result

        Returns:
            True if successful
        """
        return self.storage.save_message_importance(
            contact_id=contact_id,
            message_id=message_id,
            score=analysis.get('score', 0),
            metadata={
                'category': analysis.get('category'),
                'factors': analysis.get('factors'),
                'should_pin': analysis.get('should_pin'),
                'timestamp': analysis.get('timestamp')
            }
        )


# Singleton instance
message_analyzer = MessageAnalyzer()
