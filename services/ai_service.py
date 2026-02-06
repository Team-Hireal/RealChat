"""
AI Service
Handles AI provider integration (Anthropic Claude)
Consolidates functionality from agent.py and agent-orchestrator/
"""

import os
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AIService:
    """Unified AI provider service"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.api_key = self.config.get('api_key') or os.getenv('AI_API_KEY')
        self.base_url = self.config.get('base_url') or os.getenv('AI_BASE_URL', 'https://api.anthropic.com')
        self.model = self.config.get('model') or os.getenv('AI_MODEL', 'claude-sonnet-4-5-20250929')
        self.max_tokens = int(self.config.get('max_tokens') or os.getenv('AI_MAX_TOKENS', '1024'))

        if not self.api_key:
            logger.warning("AI_API_KEY not configured")

    def get_response(self, user_message: str, system_prompt: str = None,
                    conversation_history: List[Dict] = None) -> Optional[str]:
        """
        Get AI response from Anthropic Claude

        Args:
            user_message: User's message
            system_prompt: Optional system prompt
            conversation_history: Optional conversation history

        Returns:
            str: AI response or None on error
        """
        if not self.api_key:
            logger.error("AI API key not configured")
            return None

        try:
            # Build messages
            messages = []

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current message
            messages.append({
                "role": "user",
                "content": user_message
            })

            # Prepare request
            payload = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": messages
            }

            # Check if using custom endpoint (non-Anthropic)
            is_custom_endpoint = 'anthropic.com' not in self.base_url.lower()

            # Add system prompt if provided (only for official Anthropic API)
            if system_prompt and not is_custom_endpoint:
                payload["system"] = system_prompt
            elif system_prompt and is_custom_endpoint:
                # For custom endpoints, prepend system prompt to first user message
                if messages and messages[0]["role"] == "user":
                    messages[0]["content"] = f"{system_prompt}\n\nUser: {messages[0]['content']}"

            # Make API request
            # Check if using custom endpoint (non-Anthropic)
            is_custom_endpoint = 'anthropic.com' not in self.base_url.lower()

            headers = {
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }

            # Use appropriate auth header based on endpoint
            if is_custom_endpoint:
                headers["Authorization"] = f"Bearer {self.api_key}"
            else:
                headers["x-api-key"] = self.api_key

            response = requests.post(
                f"{self.base_url}/v1/messages",
                headers=headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            # Extract response text
            if 'content' in data and len(data['content']) > 0:
                response_text = data['content'][0]['text']

                # SAFETY CHECK: Ensure [Agent] prefix is always present
                if not response_text.strip().startswith('[Agent]'):
                    response_text = f"[Agent] {response_text}"
                    logger.info("Added [Agent] prefix to response")

                return response_text
            else:
                logger.error(f"Unexpected API response format: {data}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"AI API request failed: {e}")
            # Log response body for debugging
            try:
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"Response body: {e.response.text}")
            except:
                pass
            return None
        except Exception as e:
            logger.error(f"AI service error: {e}")
            return None

    def get_chat_response(self, user_message: str, context: Dict = None) -> Optional[str]:
        """
        Get conversational response for chat

        Args:
            user_message: User's message
            context: Optional context (contact info, history, conversation_history, etc.)

        Returns:
            str: AI response
        """
        # Build system prompt
        system_prompt = "IMPORTANT: You MUST start EVERY response with '[Agent]' (including the square brackets). "
        system_prompt += "You are a friendly AI assistant helping with WeChat conversations. "
        system_prompt += "Respond naturally and conversationally. Keep responses VERY brief (1-2 sentences max) and helpful. "
        system_prompt += "Be concise and direct. Always start with '[Agent]'."

        # Add context if provided
        if context:
            if 'contact_name' in context:
                system_prompt += f"\n\nYou are chatting with: {context['contact_name']}"
            if 'relationship' in context:
                system_prompt += f"\nRelationship: {context['relationship']}"
            if 'chat_name' in context:
                system_prompt += f"\n\nChat: {context['chat_name']}"
            if 'message_count' in context:
                system_prompt += f"\nTotal messages in conversation: {context['message_count']}"

        # Build conversation history for API
        conversation_history = []
        if context and 'conversation_history' in context:
            history = context['conversation_history']
            if history:
                system_prompt += f"\n\nRecent conversation history ({len(history)} messages):"
                for msg in history[:-1]:  # Exclude the latest message (it's the user_message)
                    text = msg.get('text', '')
                    if text:
                        # Try to determine if it's from user or assistant
                        # Messages with "🤖" or "RealChat" are from assistant
                        if "🤖" in text or "RealChat" in text:
                            conversation_history.append({
                                "role": "assistant",
                                "content": text.replace("🤖", "").strip()
                            })
                        else:
                            conversation_history.append({
                                "role": "user",
                                "content": text
                            })

        # Get response with conversation history
        response = self.get_response(user_message, system_prompt=system_prompt, conversation_history=conversation_history)

        # SAFETY CHECK: Ensure [Agent] prefix is always present
        if response and not response.strip().startswith('[Agent]'):
            response = f"[Agent] {response}"
            logger.info("Added [Agent] prefix to chat response")

        return response

    def analyze_message_importance(self, message: str, contact_info: Dict = None) -> Dict:
        """
        Analyze message importance using AI

        Args:
            message: Message content
            contact_info: Optional contact information

        Returns:
            Dict with score and reasoning
        """
        prompt = f"""Analyze the importance of this message on a scale of 1-10:

Message: "{message}"

Consider:
- Urgency indicators (URGENT, ASAP, etc.)
- Time-sensitive content
- Questions requiring response
- Emotional tone

Respond with JSON format:
{{"score": <1-10>, "reasoning": "<brief explanation>"}}"""

        response = self.get_response(prompt)

        if response:
            try:
                import json
                result = json.loads(response)
                return result
            except:
                # Fallback to basic scoring
                pass

        # Fallback scoring
        score = 5
        if any(word in message.upper() for word in ['URGENT', 'ASAP', 'IMPORTANT', '紧急']):
            score = 9
        elif '?' in message or '？' in message:
            score = 7

        return {"score": score, "reasoning": "Basic keyword analysis"}

    def categorize_contact(self, contact_data: Dict) -> Dict:
        """
        Categorize contact relationship using AI

        Args:
            contact_data: Contact information and interaction history

        Returns:
            Dict with category and confidence
        """
        prompt = f"""Analyze this contact and categorize the relationship:

Contact: {contact_data.get('name', 'Unknown')}
Recent messages: {contact_data.get('message_count', 0)}
Interaction frequency: {contact_data.get('frequency', 'Unknown')}

Sample messages:
{contact_data.get('sample_messages', 'None')}

Categorize as one of:
- professional (work, business)
- personal (friends, family)
- casual (acquaintances)
- service (customer service, delivery)

Respond with JSON:
{{"category": "<category>", "confidence": <0-1>, "reasoning": "<brief explanation>"}}"""

        response = self.get_response(prompt)

        if response:
            try:
                import json
                result = json.loads(response)
                return result
            except:
                pass

        # Fallback
        return {
            "category": "casual",
            "confidence": 0.5,
            "reasoning": "Unable to analyze"
        }

    def generate_auto_reply(self, message: str, reply_style: str = "friendly") -> Optional[str]:
        """
        Generate automatic reply

        Args:
            message: Incoming message
            reply_style: Style of reply (friendly, professional, brief)

        Returns:
            str: Generated reply
        """
        style_prompts = {
            "friendly": "Respond in a warm, friendly manner.",
            "professional": "Respond professionally and courteously.",
            "brief": "Respond very briefly, 1-2 sentences max."
        }

        system_prompt = f"""You are an AI assistant generating automatic replies to WeChat messages.
{style_prompts.get(reply_style, style_prompts['friendly'])}

Keep responses natural and contextually appropriate.
If the message requires specific information you don't have, politely acknowledge and say you'll respond later."""

        return self.get_response(message, system_prompt=system_prompt)

    def health_check(self) -> bool:
        """
        Check if AI service is healthy

        Returns:
            bool: True if service is accessible
        """
        try:
            response = self.get_response("Hello", system_prompt="Respond with just 'Hi'")
            return response is not None
        except:
            return False

    def get_status(self) -> Dict:
        """
        Get service status

        Returns:
            Dict with status information
        """
        return {
            "provider": "Anthropic Claude",
            "model": self.model,
            "base_url": self.base_url,
            "api_key_configured": bool(self.api_key),
            "healthy": self.health_check() if self.api_key else False
        }
