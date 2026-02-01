"""
Relationship Analyzer - AI-powered contact relationship analysis

This module uses AI to analyze contact relationships based on:
- Chat history and interaction patterns
- WeChat Moments content
- Message frequency and recency
- Shared interests and topics

Classifies relationships into categories:
- Family
- Professional (colleague, client, partner)
- Personal (friend, acquaintance)
- Service (delivery, support)
- Other
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from core.storage import UnifiedStorage
from modules.privacy_controller import PrivacyController, PrivacyFeature


class RelationshipAnalyzer:
    """
    Analyzes contact relationships using AI

    Uses conversation history, moments, and interaction patterns
    to classify and understand relationships.
    """

    # Relationship categories
    CATEGORIES = [
        'family',
        'professional',
        'personal',
        'service',
        'other'
    ]

    def __init__(self, agent_orchestrator_url: str = 'http://localhost:8082'):
        self.storage = UnifiedStorage()
        self.privacy = PrivacyController()
        self.agent_url = agent_orchestrator_url

    def analyze_contact(
        self,
        contact_id: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze a contact's relationship

        Args:
            contact_id: Contact ID
            force_refresh: Force re-analysis even if cached

        Returns:
            Analysis result with category, confidence, and insights
        """
        # Check authorization
        if not self.privacy.check_authorization(PrivacyFeature.ANALYZE_RELATIONSHIPS, contact_id):
            return {
                'success': False,
                'error': 'Not authorized to analyze relationship for this contact',
                'authorized': False
            }

        # Check cache first
        if not force_refresh:
            cached_analysis = self.storage.load_relationship_analysis(contact_id)
            if cached_analysis:
                # Check if analysis is recent (within 7 days)
                last_updated = cached_analysis.get('last_updated')
                if last_updated:
                    try:
                        last_update_date = datetime.fromisoformat(last_updated)
                        if datetime.now() - last_update_date < timedelta(days=7):
                            return {
                                'success': True,
                                'cached': True,
                                **cached_analysis
                            }
                    except:
                        pass

        # Gather data for analysis
        contact_data = self._gather_contact_data(contact_id)

        if not contact_data:
            return {
                'success': False,
                'error': 'Insufficient data to analyze relationship'
            }

        # Perform AI-powered analysis
        analysis = self._classify_relationship(contact_data)

        if analysis['success']:
            # Save analysis
            self.storage.save_relationship_analysis(contact_id, analysis)

            # Update contact category
            self.storage.update_contact_category(
                contact_id,
                analysis['category'],
                analysis['confidence']
            )

            # Log privacy action
            self.privacy.log_privacy_action(
                feature=PrivacyFeature.ANALYZE_RELATIONSHIPS,
                action='analyze',
                contact_id=contact_id,
                details={'category': analysis['category']}
            )

            return {
                'success': True,
                'cached': False,
                **analysis
            }
        else:
            return analysis

    def _gather_contact_data(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """
        Gather all available data about a contact

        Args:
            contact_id: Contact ID

        Returns:
            Dictionary with contact data or None
        """
        # Load contact info
        contact_info = self.storage.load_contact_info(contact_id)
        if not contact_info:
            return None

        # Load chat history
        chat_history = self.storage.load_chat_history(contact_id)

        # Load moments
        moments = self.storage.load_contact_moments(contact_id)

        # Calculate interaction statistics
        interaction_stats = self._calculate_interaction_stats(chat_history)

        return {
            'contact_id': contact_id,
            'name': contact_info.get('name', 'Unknown'),
            'chat_history': chat_history[-20:],  # Last 20 messages
            'moments': moments[:10],  # Last 10 moments
            'interaction_stats': interaction_stats,
            'contact_info': contact_info
        }

    def _calculate_interaction_stats(self, chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate interaction statistics from chat history

        Args:
            chat_history: List of messages

        Returns:
            Statistics dictionary
        """
        if not chat_history:
            return {
                'total_messages': 0,
                'frequency': 0,
                'recency_days': None,
                'avg_response_time': None
            }

        total_messages = len(chat_history)

        # Calculate frequency (messages per day)
        if len(chat_history) >= 2:
            try:
                first_msg_time = datetime.fromisoformat(chat_history[0].get('timestamp', ''))
                last_msg_time = datetime.fromisoformat(chat_history[-1].get('timestamp', ''))
                days_span = (last_msg_time - first_msg_time).days or 1
                frequency = total_messages / days_span
            except:
                frequency = 0
        else:
            frequency = 0

        # Calculate recency
        try:
            last_msg_time = datetime.fromisoformat(chat_history[-1].get('timestamp', ''))
            recency_days = (datetime.now() - last_msg_time).days
        except:
            recency_days = None

        return {
            'total_messages': total_messages,
            'frequency': round(frequency, 2),
            'recency_days': recency_days,
            'message_length_avg': sum(len(msg.get('content', '')) for msg in chat_history) / total_messages if total_messages > 0 else 0
        }

    def _classify_relationship(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to classify relationship

        Args:
            contact_data: Contact data dictionary

        Returns:
            Classification result
        """
        # Build prompt for AI
        prompt = self._build_classification_prompt(contact_data)

        # Call AI agent
        try:
            response = self._call_ai_agent(prompt)

            if response['success']:
                # Parse AI response
                classification = self._parse_ai_response(response['content'])
                return classification
            else:
                return {
                    'success': False,
                    'error': f"AI analysis failed: {response.get('error')}"
                }

        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to classify relationship: {str(e)}"
            }

    def _build_classification_prompt(self, contact_data: Dict[str, Any]) -> str:
        """
        Build prompt for AI classification

        Args:
            contact_data: Contact data

        Returns:
            Prompt string
        """
        name = contact_data['name']
        chat_history = contact_data['chat_history']
        moments = contact_data['moments']
        stats = contact_data['interaction_stats']

        # Format chat history
        chat_summary = ""
        if chat_history:
            recent_messages = chat_history[-5:]
            for msg in recent_messages:
                sender = "Them" if msg.get('from_contact') else "Me"
                content = msg.get('content', '')[:100]  # Truncate long messages
                chat_summary += f"{sender}: {content}\n"

        # Format moments
        moments_summary = ""
        if moments:
            for moment in moments[:3]:
                content = moment.get('content', '')[:100]
                moments_summary += f"- {content}\n"

        prompt = f"""Analyze this WeChat contact and classify their relationship category.

Contact Name: {name}

Interaction Statistics:
- Total messages: {stats['total_messages']}
- Message frequency: {stats['frequency']} messages/day
- Last contact: {stats['recency_days']} days ago
- Average message length: {stats['message_length_avg']} characters

Recent Chat History:
{chat_summary if chat_summary else "No recent messages"}

Recent Moments:
{moments_summary if moments_summary else "No moments available"}

Based on this information, classify the relationship into ONE of these categories:
1. family - Family members (parents, siblings, relatives)
2. professional - Work-related (colleagues, clients, business partners)
3. personal - Friends and acquaintances
4. service - Service providers (delivery, support, etc.)
5. other - Unclear or mixed relationship

Provide your analysis in this JSON format:
{{
    "category": "<category>",
    "confidence": <0.0-1.0>,
    "reasoning": "<brief explanation>",
    "key_indicators": ["<indicator1>", "<indicator2>"],
    "interests": ["<interest1>", "<interest2>"]
}}

Consider:
- Professional relationships often discuss work, projects, meetings, deadlines
- Family relationships are more casual, discuss personal matters, family events
- Personal relationships discuss hobbies, social activities, entertainment
- Service relationships are transactional and brief
- Message frequency and tone are important indicators

Respond ONLY with the JSON object, no additional text."""

        return prompt

    def _call_ai_agent(self, prompt: str, provider: str = 'anthropic') -> Dict[str, Any]:
        """
        Call AI agent orchestrator

        Args:
            prompt: Prompt text
            provider: AI provider to use

        Returns:
            Response dictionary
        """
        try:
            response = requests.post(
                f"{self.agent_url}/api/process",
                json={
                    'message': prompt,
                    'provider': provider,
                    'contact_id': 'relationship_analyzer'
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'content': data.get('response', '')
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Request failed: {str(e)}"
            }

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse AI response into structured data

        Args:
            response_text: AI response text

        Returns:
            Parsed classification
        """
        try:
            # Try to extract JSON from response
            # AI might include extra text, so find JSON block
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                classification = json.loads(json_str)

                # Validate required fields
                if 'category' not in classification:
                    raise ValueError("Missing 'category' field")

                # Ensure category is valid
                if classification['category'] not in self.CATEGORIES:
                    classification['category'] = 'other'

                # Add metadata
                classification['success'] = True
                classification['analyzed_at'] = datetime.now().isoformat()

                return classification
            else:
                raise ValueError("No JSON found in response")

        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: try to extract category from text
            category = 'other'
            for cat in self.CATEGORIES:
                if cat in response_text.lower():
                    category = cat
                    break

            return {
                'success': True,
                'category': category,
                'confidence': 0.5,
                'reasoning': 'Parsed from text (JSON parsing failed)',
                'key_indicators': [],
                'interests': [],
                'analyzed_at': datetime.now().isoformat(),
                'parse_error': str(e)
            }

    def generate_relationship_summary(self, contact_id: str) -> str:
        """
        Generate human-readable relationship summary

        Args:
            contact_id: Contact ID

        Returns:
            Summary text
        """
        analysis = self.storage.load_relationship_analysis(contact_id)
        if not analysis:
            return "No relationship analysis available."

        category = analysis.get('category', 'unknown')
        confidence = analysis.get('confidence', 0)
        reasoning = analysis.get('reasoning', '')
        interests = analysis.get('interests', [])

        summary = f"Relationship: {category.capitalize()} "
        summary += f"(Confidence: {int(confidence * 100)}%)\n\n"
        summary += f"{reasoning}\n\n"

        if interests:
            summary += f"Shared interests: {', '.join(interests)}"

        return summary


# Singleton instance
relationship_analyzer = RelationshipAnalyzer()
