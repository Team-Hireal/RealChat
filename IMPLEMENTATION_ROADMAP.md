# RealChat - Complete Implementation Roadmap

## Overview

This document outlines the complete implementation of RealChat's enhanced user flow with chat selection, privacy controls, multi-agent support, and advanced features.

## Current Status

✅ **Completed**:
- Consolidated Flask monorepo
- Basic WeChat automation (send/receive)
- AI integration (Anthropic Claude)
- Web interface (basic)
- API endpoints (new + legacy)

❌ **Missing**:
- Chat selection interface
- Configuration system
- Privacy authorization
- Message importance analysis
- Moments browsing
- Multi-agent coordination

---

## Phase 1: Enhanced Web Interface with Chat Selection

### 1.1 Chat Selection UI

**Features**:
- Dropdown to select target chat
- "Scan Chats" button to discover available chats
- Display list of found chats
- Save selected chat to configuration
- Show current monitoring target

**Implementation**:
- Update `client.html` with chat selector
- Add `/api/chats/list` endpoint
- Add `/api/chats/select` endpoint
- Store selected chat in session/config

### 1.2 Configuration Panel

**Settings to Add**:
- **Personal Info**:
  - Name
  - Title/Role
  - Introduction template
- **Response Templates**:
  - Introduction template
  - Auto-reply templates
  - Custom responses
- **Agent Behavior**:
  - Auto-reply mode (on/off)
  - Response delay
  - Monitoring interval
- **AI Provider Selection**:
  - Anthropic Claude
  - OpenClaw (file operations)
  - Zypher (task-based)
- **Privacy Controls**:
  - Read messages: Yes/No
  - Send messages: Yes/No
  - Pin messages: Yes/No
  - Browse moments: Yes/No
  - Auto-reply: Yes/No

---

## Phase 2: Privacy & Authorization System

### 2.1 Privacy Controller Enhancement

**Features**:
- Explicit authorization for each feature
- Per-contact authorization
- Authorization history/audit log
- Revoke permissions anytime

**Implementation**:
- Enhance `modules/privacy_controller.py`
- Add authorization UI in web interface
- Store authorizations in unified storage
- Check authorization before every action

### 2.2 Authorization Flow

```
User Action → Check Authorization → Request if Not Authorized → Execute if Authorized
```

**Example**:
1. User clicks "Start Agent"
2. System checks if "read_messages" authorized
3. If not, show authorization dialog
4. User grants permission
5. Agent starts monitoring

---

## Phase 3: Multi-Agent System

### 3.1 Agent Types

1. **Message Monitor Agent**:
   - Monitors selected chat
   - Detects new messages
   - Triggers auto-reply if enabled

2. **Message Analyzer Agent**:
   - Analyzes message importance
   - Pins important messages
   - Categorizes contacts

3. **Moments Browser Agent**:
   - Browses contact moments
   - Profiles contacts
   - Browses feed

4. **Auto-Reply Agent**:
   - Generates responses
   - Uses templates
   - Sends replies

### 3.2 Agent Manager (Mutual Exclusion)

**Rules**:
- Only ONE agent active at a time
- When starting new agent, stop current agent
- Agents can be in states: `idle`, `running`, `paused`
- Unified storage for agent state

**Implementation**:
- Already exists in `modules/agent_manager.py`
- Enhance with agent coordination
- Add agent status API endpoints
- Update UI to show active agent

---

## Phase 4: Message Importance & Pinning

### 4.1 Importance Analysis

**Criteria**:
- Urgency keywords (URGENT, ASAP, etc.)
- Time-sensitive content
- Questions requiring response
- Sender relationship (professional/personal)
- Message length and complexity

**Scoring**: 1-10 scale

### 4.2 Auto-Pinning

**Logic**:
```
if importance_score >= 7:
    pin_message()
if message_is_read():
    unpin_message()
```

**Implementation**:
- Already exists in `modules/message_analyzer.py`
- Add AppleScript for pinning messages
- Add read status detection
- Add auto-unpin on read

---

## Phase 5: Moments Browsing

### 5.1 Contact Profiling

**Process**:
1. Navigate to contact profile
2. Browse their moments
3. Analyze content (work/personal/family)
4. Categorize relationship
5. Store profile data

**Implementation**:
- Add AppleScript for moments navigation
- Add OCR for content extraction
- Use AI to analyze and categorize
- Store in `modules/relationship_analyzer.py`

### 5.2 Feed Browsing

**Process**:
1. Open moments feed
2. Scroll through recent posts
3. Extract content
4. Analyze trends
5. Store insights

**Implementation**:
- Add AppleScript for feed navigation
- Add content extraction
- Store in unified storage

---

## Phase 6: Multi-Provider Support

### 6.1 Provider Interface

**Providers**:
1. **Anthropic Claude** (General chat)
2. **OpenClaw** (File operations)
3. **Zypher** (Task-based)

**Implementation**:
- Abstract AI provider interface
- Provider selection in UI
- Provider-specific capabilities
- Fallback to default provider

### 6.2 Provider Switching

**UI Flow**:
```
Settings → AI Provider → Select Provider → Save → Restart Agent
```

**Backend**:
- Already partially implemented in `services/ai_service.py`
- Add provider factory pattern
- Add provider-specific endpoints

---

## Phase 7: Unified Storage System

### 7.1 Storage Structure

```
data/
├── config/
│   ├── user_profile.json
│   ├── templates.json
│   ├── privacy_settings.json
│   └── agent_config.json
├── chats/
│   ├── {chat_id}/
│   │   ├── messages.json
│   │   ├── importance_scores.json
│   │   └── pinned_messages.json
├── contacts/
│   ├── {contact_id}/
│   │   ├── profile.json
│   │   ├── moments.json
│   │   └── relationship.json
├── agents/
│   ├── agent_state.json
│   └── agent_history.json
└── logs/
    └── activity.log
```

### 7.2 Storage API

**Methods**:
- `save_config(key, value)`
- `load_config(key)`
- `save_chat_data(chat_id, data)`
- `load_chat_data(chat_id)`
- `save_contact_profile(contact_id, profile)`
- `load_contact_profile(contact_id)`

**Implementation**:
- Already exists in `core/storage.py`
- Enhance with new data types
- Add backup/restore functionality

---

## Implementation Priority

### Phase 1: Critical (Week 1)
1. ✅ Chat selection UI
2. ✅ Configuration panel
3. ✅ Save/load settings

### Phase 2: High Priority (Week 2)
1. ✅ Privacy authorization UI
2. ✅ Authorization checks
3. ✅ Agent manager coordination

### Phase 3: Medium Priority (Week 3)
1. ✅ Message importance analysis
2. ✅ Auto-pinning logic
3. ✅ Contact categorization

### Phase 4: Nice to Have (Week 4)
1. ⏳ Moments browsing
2. ⏳ Multi-provider switching
3. ⏳ Advanced analytics

---

## Technical Architecture

### Frontend (client.html)
```
┌─────────────────────────────────────┐
│         Configuration Panel          │
│  - Personal Info                     │
│  - Templates                         │
│  - Privacy Settings                  │
│  - AI Provider Selection             │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         Chat Selection               │
│  - Dropdown: Select Chat             │
│  - Button: Scan Chats                │
│  - Display: Current Target           │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         Agent Control                │
│  - Start Agent (with selected chat)  │
│  - Stop Agent                        │
│  - Agent Status Display              │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         Messages & Logs              │
│  - Real-time message display         │
│  - Importance scores                 │
│  - System logs                       │
└─────────────────────────────────────┘
```

### Backend (Flask API)
```
app_consolidated.py
├── Configuration Endpoints
│   ├── GET  /api/config/profile
│   ├── POST /api/config/profile
│   ├── GET  /api/config/templates
│   ├── POST /api/config/templates
│   └── GET  /api/config/privacy
├── Chat Management
│   ├── GET  /api/chats/list
│   ├── POST /api/chats/select
│   └── GET  /api/chats/current
├── Agent Control
│   ├── POST /api/agent/start
│   ├── POST /api/agent/stop
│   └── GET  /api/agent/status
├── Privacy & Authorization
│   ├── GET  /api/privacy/status
│   ├── POST /api/privacy/authorize
│   └── POST /api/privacy/revoke
└── Advanced Features
    ├── GET  /api/messages/importance
    ├── POST /api/messages/pin
    └── GET  /api/moments/browse
```

---

## Next Steps

1. **Immediate**: Implement chat selection UI
2. **Short-term**: Add configuration panel
3. **Medium-term**: Implement privacy controls
4. **Long-term**: Add moments browsing

---

## Success Criteria

✅ User can select which chat to monitor
✅ User can configure personal info and templates
✅ User must authorize each feature explicitly
✅ Only one agent runs at a time
✅ Important messages are auto-pinned
✅ Messages are auto-unpinned when read
✅ Contacts are categorized automatically
✅ User can switch AI providers
✅ All data stored in unified system
✅ Complete audit trail of actions

---

**Status**: 📋 Planning Complete
**Next**: 🚀 Begin Phase 1 Implementation
**Timeline**: 4 weeks for full implementation
**Priority**: Chat Selection + Configuration (Week 1)
