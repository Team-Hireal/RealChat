# RealChat Modules Documentation

## Overview

This document describes the new modules added to RealChat for advanced message management, moments browsing, and relationship analysis.

## Module Architecture

### 1. Agent Manager (`modules/agent_manager.py`)

**Purpose**: Coordinates multiple agents and ensures only one is active at a time.

**Key Classes**:
- `AgentType`: Enum of available agents (WECHAT_BRIDGE, MESSAGE_ANALYZER, MOMENTS_BROWSER, RELATIONSHIP_ANALYZER)
- `AgentState`: Lifecycle states (IDLE, ACTIVATING, ACTIVE, DEACTIVATING, ERROR)
- `AgentManager`: Singleton manager for agent coordination

**Usage**:
```python
from modules import agent_manager, AgentType

# Activate an agent
agent_manager.activate_agent(AgentType.MESSAGE_ANALYZER)

# Check active agent
active = agent_manager.get_active_agent()

# Get all agent states
states = agent_manager.get_all_states()

# Deactivate
agent_manager.deactivate_agent(AgentType.MESSAGE_ANALYZER)
```

**Features**:
- Mutual exclusion (only one agent active at a time)
- Graceful state transitions
- Persistent state storage
- Thread-safe operations

---

### 2. Privacy Controller (`modules/privacy_controller.py`)

**Purpose**: Manages privacy authorization and audit logging for all sensitive operations.

**Key Classes**:
- `PrivacyFeature`: Enum of privacy-sensitive features
- `AuthorizationLevel`: DENIED, AUTHORIZED, AUTHORIZED_WITH_CONTACTS
- `PrivacyController`: Authorization manager

**Privacy Features**:
- `AUTO_REPLY`: Auto-reply to messages
- `READ_MESSAGES`: Read message content
- `BROWSE_MOMENTS`: Browse WeChat moments
- `PIN_MESSAGES`: Pin/unpin messages
- `ANALYZE_RELATIONSHIPS`: Analyze contact relationships
- `SEND_MESSAGES`: Send messages
- `ACCESS_CONTACTS`: Access contact information
- `READ_CHAT_HISTORY`: Read chat history

**Usage**:
```python
from modules import privacy_controller, PrivacyFeature, AuthorizationLevel

# Request full authorization
privacy_controller.request_authorization(
    PrivacyFeature.READ_MESSAGES,
    AuthorizationLevel.AUTHORIZED,
    reason="Need to analyze message importance"
)

# Request contact-specific authorization
privacy_controller.request_authorization(
    PrivacyFeature.BROWSE_MOMENTS,
    AuthorizationLevel.AUTHORIZED_WITH_CONTACTS,
    contacts=['contact_1', 'contact_2'],
    reason="Analyze relationships"
)

# Check authorization
if privacy_controller.check_authorization(PrivacyFeature.READ_MESSAGES, 'contact_1'):
    # Perform action
    pass

# Revoke authorization
privacy_controller.revoke_authorization(PrivacyFeature.READ_MESSAGES)

# Get audit log
logs = privacy_controller.get_privacy_log(limit=100)
```

**Features**:
- Explicit consent required for all operations
- Granular per-contact permissions
- Complete audit trail
- Decorator support for function-level authorization

---

### 3. Message Analyzer (`modules/message_analyzer.py`)

**Purpose**: Analyzes message importance and determines pinning priority.

**Scoring Criteria**:
- **Relationship weight**: family (10), professional (8), personal (6), service (3), other (3)
- **Urgency keywords**: urgent, ASAP, emergency, deadline, meeting, etc.
- **Question detection**: Question marks and question words
- **Message length**: Longer messages score higher
- **Name mentions**: Bonus if user's name is mentioned
- **Time sensitivity**: Detects time-specific content

**Score Ranges**:
- 9-10: Critical (always pin)
- 7-8: High priority (pin if unread)
- 5-6: Medium priority (pin if from important contact)
- 1-4: Low priority (don't pin)

**Usage**:
```python
from modules import message_analyzer

message = {
    'content': 'URGENT: Please call me ASAP regarding the meeting today at 3pm',
    'unread': True,
    'timestamp': '2026-02-01T10:00:00'
}

contact = {
    'id': 'contact_123',
    'name': 'John Doe',
    'category': 'professional'
}

# Analyze single message
analysis = message_analyzer.analyze_importance(message, contact)
# Returns: {
#     'authorized': True,
#     'score': 8.5,
#     'should_pin': True,
#     'category': 'high',
#     'factors': {...},
#     'timestamp': '...'
# }

# Batch analysis
messages = [...]
contacts = {'contact_123': contact, ...}
results = message_analyzer.analyze_batch(messages, contacts)

# Get messages to pin
to_pin = message_analyzer.get_messages_to_pin(messages, contacts)
```

**Features**:
- Multi-factor importance scoring
- Automatic pinning recommendations
- Batch processing support
- Persistent score storage

---

### 4. Moments Browser (`modules/moments_browser.py`)

**Purpose**: Browse and analyze WeChat Moments for relationship insights.

**Capabilities**:
- Browse contact's moments from their profile
- Browse general moments feed
- Extract moment data (text, images, likes, comments)
- Analyze content (topics, sentiment, work-related detection)
- Categorize contacts based on moments

**Usage**:
```python
from modules import moments_browser

# Browse contact moments
result = moments_browser.browse_contact_moments(
    contact_id='contact_123',
    contact_name='John Doe',
    limit=10,
    force_refresh=False  # Use cache if available
)
# Returns: {
#     'success': True,
#     'contact_id': 'contact_123',
#     'moments': [...],
#     'cached': False,
#     'timestamp': '...'
# }

# Browse feed
feed = moments_browser.browse_feed_moments(limit=20)

# Analyze moment content
moment = {
    'content': 'Great meeting with the team today!',
    'images': ['img1.jpg'],
    'likes': 10,
    'comments': 3
}
analysis = moments_browser.analyze_moment_content(moment)
# Returns: {
#     'content_type': 'image',
#     'topics': ['work'],
#     'sentiment': 'positive',
#     'is_work_related': True,
#     'has_location': False,
#     'engagement': 13
# }

# Categorize contact from moments
categorization = moments_browser.categorize_contact_from_moments(
    'contact_123',
    moments
)
# Returns: {
#     'category': 'professional',
#     'confidence': 0.75,
#     'work_moments': 8,
#     'family_moments': 1,
#     'personal_moments': 1,
#     'total_moments': 10
# }
```

**Content Analysis**:
- **Topics**: work, family, travel, food, sports, entertainment
- **Sentiment**: positive, negative, neutral
- **Work-related detection**: Keywords like meeting, project, client, etc.

**Features**:
- AppleScript-based automation
- Caching for performance
- Privacy-aware (requires authorization)
- Comprehensive content analysis

---

### 5. Relationship Analyzer (`modules/relationship_analyzer.py`)

**Purpose**: AI-powered contact relationship classification.

**Categories**:
- **family**: Family members (parents, siblings, relatives)
- **professional**: Work-related (colleagues, clients, business partners)
- **personal**: Friends and acquaintances
- **service**: Service providers (delivery, support, etc.)
- **other**: Unclear or mixed relationship

**Analysis Factors**:
- Chat frequency and recency
- Message tone and content
- Moments content (work-related, personal, family)
- Shared interests
- Interaction patterns

**Usage**:
```python
from modules import relationship_analyzer

# Analyze contact
analysis = relationship_analyzer.analyze_contact(
    'contact_123',
    force_refresh=False
)
# Returns: {
#     'success': True,
#     'category': 'professional',
#     'confidence': 0.85,
#     'reasoning': 'Frequent work-related discussions...',
#     'key_indicators': ['work', 'meeting', 'project'],
#     'interests': ['technology', 'business'],
#     'analyzed_at': '...',
#     'cached': False
# }

# Generate summary
summary = relationship_analyzer.generate_relationship_summary('contact_123')
# Returns human-readable text summary
```

**AI Integration**:
- Uses Agent Orchestrator for AI processing
- Supports multiple AI providers (Anthropic, OpenAI, etc.)
- Structured JSON output parsing
- Fallback to text parsing if JSON fails

**Features**:
- Comprehensive data gathering (chat history, moments, stats)
- AI-powered classification
- Confidence scoring
- Caching (7-day validity)
- Privacy-aware

---

## Storage System Updates

The unified storage system (`core/storage.py`) has been extended with new methods:

### Agent State Management
```python
storage.save_agent_state('agent_name', state_data)
state = storage.load_agent_state('agent_name')
```

### Message Importance
```python
storage.save_message_importance('contact_id', 'message_id', score, metadata)
importance = storage.load_message_importance('contact_id', 'message_id')
```

### Pinned Messages
```python
storage.save_pinned_message('contact_id', 'message_id', message_data)
pinned = storage.load_pinned_messages()
storage.remove_pinned_message('contact_id', 'message_id')
```

### Privacy Logs
```python
storage.append_privacy_log(log_entry)
logs = storage.load_privacy_log()
```

### Relationship Analysis
```python
storage.save_relationship_analysis('contact_id', analysis)
analysis = storage.load_relationship_analysis('contact_id')
storage.update_contact_category('contact_id', 'category', confidence)
```

---

## AppleScript Automation

### Message Pinning (`scripts/wechat_pin_message.applescript`)

**Commands**:
```bash
# Pin a chat
osascript scripts/wechat_pin_message.applescript pin "Contact Name"

# Unpin a chat
osascript scripts/wechat_pin_message.applescript unpin "Contact Name"

# List pinned chats
osascript scripts/wechat_pin_message.applescript list

# Check read status
osascript scripts/wechat_pin_message.applescript check_read "Contact Name"
```

### Moments Browsing (`scripts/wechat_moments.applescript`)

**Commands**:
```bash
# Browse contact moments
osascript scripts/wechat_moments.applescript browse_contact "Contact Name" 10

# Browse feed
osascript scripts/wechat_moments.applescript browse_feed 20
```

**Output**: JSON format with moments data

---

## Testing

Run the comprehensive test suite:

```bash
python3 tests/test_realchat_modules.py
```

**Test Coverage**:
- Agent Manager: Singleton, activation, mutual exclusion, deactivation
- Privacy Controller: Authorization, revocation, contact-specific permissions
- Storage System: All new storage methods
- Message Analyzer: Scoring, pinning logic, batch analysis
- Moments Browser: Content analysis, categorization
- Relationship Analyzer: Stats calculation, prompt building

**Test Results**: Saved to `tests/test_results.json`

---

## Integration Guide

### Adding to Flask Backend

```python
# In app.py
from modules import (
    agent_manager, AgentType,
    privacy_controller, PrivacyFeature,
    message_analyzer,
    moments_browser,
    relationship_analyzer
)

@app.route('/api/agent/activate', methods=['POST'])
def activate_agent():
    data = request.json
    agent_type = AgentType(data['agent_type'])
    agent_manager.activate_agent(agent_type)
    return jsonify({'success': True})

@app.route('/api/messages/analyze', methods=['POST'])
def analyze_messages():
    data = request.json
    messages = data['messages']
    contacts = data['contacts']
    results = message_analyzer.analyze_batch(messages, contacts)
    return jsonify({'results': results})
```

### Frontend Integration

```javascript
// Activate agent
const activateAgent = async (agentType) => {
  const response = await fetch('/api/agent/activate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({agent_type: agentType})
  });
  return response.json();
};

// Analyze messages
const analyzeMessages = async (messages, contacts) => {
  const response = await fetch('/api/messages/analyze', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({messages, contacts})
  });
  return response.json();
};
```

---

## Best Practices

### Privacy
1. Always check authorization before sensitive operations
2. Log all privacy-sensitive actions
3. Provide clear reasons for authorization requests
4. Implement granular per-contact permissions where appropriate

### Agent Coordination
1. Activate only one agent at a time
2. Deactivate agents when done
3. Handle AgentActiveError gracefully
4. Monitor agent states regularly

### Message Analysis
1. Batch analyze messages for efficiency
2. Cache analysis results
3. Re-analyze periodically for accuracy
4. Respect privacy authorization

### Moments Browsing
1. Use caching to avoid excessive automation
2. Rate limit to avoid detection
3. Handle AppleScript failures gracefully
4. Respect privacy settings

### Relationship Analysis
1. Cache analysis results (7-day validity)
2. Gather sufficient data before analysis
3. Handle AI API failures
4. Validate AI responses

---

## Troubleshooting

### Agent Manager Issues
- **Error**: "Another agent is active"
  - **Solution**: Deactivate current agent or use `force=True`

### Privacy Controller Issues
- **Error**: "Not authorized"
  - **Solution**: Request authorization first

### Message Analyzer Issues
- **Error**: Empty analysis
  - **Solution**: Ensure privacy authorization is granted

### Moments Browser Issues
- **Error**: "AppleScript timeout"
  - **Solution**: Increase timeout, check WeChat is running

### Relationship Analyzer Issues
- **Error**: "AI analysis failed"
  - **Solution**: Check Agent Orchestrator is running, verify API keys

---

## Future Enhancements

- [ ] Web UI for all new features
- [ ] Real-time message analysis
- [ ] Advanced relationship insights dashboard
- [ ] Multi-language support
- [ ] Mobile app integration
- [ ] Cloud sync (optional)
- [ ] Advanced analytics

---

## Support

For issues or questions:
1. Check this documentation
2. Run tests: `python3 tests/test_realchat_modules.py`
3. Check logs in `~/.realchat/logs/`
4. Open an issue on GitHub
