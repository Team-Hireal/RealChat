# RealChat Complete System Architecture

## 🎯 System Overview

RealChat is a privacy-first WeChat automation system with AI agent integration, designed to help users manage their WeChat communications intelligently while maintaining full control and consent.

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Layer                               │
│  Web Browser → http://localhost:5001                            │
└─────────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────────┐
│                    Web Application Layer                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Flask Backend (app.py)                                  │  │
│  │  - API endpoints                                         │  │
│  │  - Session management                                    │  │
│  │  - Authorization checks                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  React Frontend                                          │  │
│  │  - Setup wizard                                          │  │
│  │  - Control panel                                         │  │
│  │  - Settings UI                                           │  │
│  │  - Authorization manager                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────────┐
│                   Core Services Layer                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  WeChat Desktop Connector                                │  │
│  │  - Auto-detection (no additional libraries)              │  │
│  │  - AppleScript automation                                │  │
│  │  - UI element access                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Chat Operations Module                                  │  │
│  │  - Chat locator & searcher                               │  │
│  │  - History reader                                        │  │
│  │  - Message sender                                        │  │
│  │  - Self-chat agent selector                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Message Management System                               │  │
│  │  - Unread message scanner                                │  │
│  │  - Importance analyzer                                   │  │
│  │  - Pin/unpin controller                                  │  │
│  │  - Contact categorizer                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  WeChat Moments Browser                                  │  │
│  │  - Contact profile moments reader                        │  │
│  │  - User feed browser                                     │  │
│  │  - Relationship analyzer                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────────┐
│                   AI Agent Layer                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Agent Orchestrator (Mutual Exclusivity)                 │  │
│  │  - Only one agent active at a time                       │  │
│  │  - Others in dormant/quit state                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌────────────┬────────────┬────────────┐                     │
│  │ Anthropic  │  Zypher    │  OpenClaw  │                     │
│  │ (General)  │  (Tasks)   │  (Files)   │                     │
│  └────────────┴────────────┴────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────────┐
│                   Storage Layer                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Unified File Storage System                             │  │
│  │  - User profiles                                         │  │
│  │  - Response templates                                    │  │
│  │  - Chat history cache                                    │  │
│  │  │  Contact categorization                                │  │
│  │  - Authorization records                                 │  │
│  │  - Agent state                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 📋 Component Specifications

### 1. WeChat Desktop Auto-Detection

**Purpose**: Automatically locate and connect to WeChat desktop app without additional libraries

**Implementation**:
```applescript
-- Auto-detect WeChat process
tell application "System Events"
    set wechatRunning to (name of processes) contains "WeChat"
    if wechatRunning then
        tell process "WeChat"
            set frontmost to true
            -- Access UI elements
        end tell
    end if
end tell
```

**Features**:
- Process detection
- Window activation
- UI element access
- Accessibility API usage

### 2. Chat Operations Module

**Purpose**: Comprehensive chat management

**Operations**:

**A. Locate Chat**
```python
def locate_chat(chat_name):
    """Find chat by name in sidebar"""
    # AppleScript to search chat list
    # Return chat reference
```

**B. Search Chat**
```python
def search_chat(query):
    """Search for chats matching query"""
    # Use WeChat search function
    # Return list of matching chats
```

**C. Read Chat History**
```python
def read_chat_history(chat_name, limit=50):
    """Read recent messages from chat"""
    # Scroll through chat
    # Extract message content
    # Return structured data
```

**D. Reply to Chat**
```python
def reply_to_chat(chat_name, message, agent_type=None):
    """Send reply to chat"""
    # If agent_type specified, use that agent
    # Otherwise use default
    # Send message
```

**E. Self-Chat Agent Selector**
```python
def process_self_chat_command(message):
    """
    User chats with themselves to select agent:
    - "use openclaw" → Switch to OpenClaw for file operations
    - "use zypher" → Switch to Zypher for online tasks
    - "use anthropic" → Switch to Anthropic for general chat
    """
    if "use openclaw" in message.lower():
        switch_agent("openclaw")
    elif "use zypher" in message.lower():
        switch_agent("zypher")
    elif "use anthropic" in message.lower():
        switch_agent("anthropic")
```

### 3. Message Management System

**Purpose**: Intelligent message prioritization and organization

**A. Unread Message Scanner**
```python
def scan_unread_messages():
    """
    Scan all chats for unread messages
    Returns: List of (chat_name, message_count, last_message)
    """
    # Iterate through chat list
    # Identify unread indicators
    # Extract message previews
```

**B. Importance Analyzer**
```python
def analyze_importance(chat_name, message_preview, contact_info):
    """
    Use AI to determine message importance
    Factors:
    - Contact relationship (professional/personal/family)
    - Message content urgency
    - Keywords (meeting, urgent, deadline, etc.)
    - Historical interaction frequency
    """
    # Send to AI agent for analysis
    # Return importance score (1-10)
```

**C. Pin/Unpin Controller**
```python
def pin_message(chat_name):
    """Pin chat to top"""
    # Right-click chat
    # Select "Pin to top"

def unpin_message(chat_name):
    """Unpin chat"""
    # Right-click chat
    # Select "Unpin"

def auto_unpin_when_read(chat_name):
    """Monitor chat and unpin when user reads it"""
    # Watch for read status change
    # Auto-unpin when read
```

**D. Contact Categorizer**
```python
def categorize_contact(contact_name):
    """
    Categorize contact based on:
    - Chat history analysis
    - Moments content
    - Interaction patterns

    Categories:
    - Professional
    - Personal
    - Family
    - Acquaintance
    - Business
    - Other
    """
    # Analyze chat history
    # Browse moments if authorized
    # Use AI to categorize
    # Store in database
```

### 4. WeChat Moments Browser

**Purpose**: Understand contacts better through their moments

**A. Contact Profile Moments**
```python
def browse_contact_moments(contact_name, limit=10):
    """
    Browse contact's moments from their profile
    Requires: User authorization

    Returns:
    - Recent moments content
    - Photos/videos
    - Comments
    - Likes
    """
    # Check authorization
    # Navigate to contact profile
    # Open moments
    # Extract content
    # Analyze for relationship insights
```

**B. User Feed Browser**
```python
def browse_user_feed(limit=20):
    """
    Browse user's own moments feed (latest only)
    Requires: User authorization

    Purpose:
    - See what contacts are posting
    - Identify engagement opportunities
    - Stay updated
    """
    # Check authorization
    # Open moments feed
    # Scroll through latest
    # Extract content
```

**C. Relationship Analyzer**
```python
def analyze_relationship(contact_name, moments_data):
    """
    Analyze relationship type based on moments

    Indicators:
    - Professional: Work-related posts, industry content
    - Personal: Life updates, casual photos
    - Family: Family photos, personal milestones
    """
    # Send moments data to AI
    # Get relationship classification
    # Update contact category
```

### 5. Privacy & Authorization System

**Purpose**: Ensure no action without explicit user consent

**Authorization Levels**:
```python
AUTHORIZATION_LEVELS = {
    'read_chats': False,          # Read chat history
    'send_messages': False,       # Send messages
    'auto_reply': False,          # Auto-reply to messages
    'pin_messages': False,        # Pin/unpin messages
    'browse_moments': False,      # Browse moments
    'categorize_contacts': False, # Analyze and categorize
    'access_profile': False,      # Access contact profiles
}
```

**Authorization Flow**:
```python
def request_authorization(action, description):
    """
    Request user authorization for action

    UI shows:
    - What action will be performed
    - What data will be accessed
    - How data will be used
    - Option to allow once, always, or deny
    """
    # Show authorization dialog
    # Wait for user response
    # Store decision
    # Return authorization status

def check_authorization(action):
    """Check if action is authorized"""
    return AUTHORIZATION_LEVELS.get(action, False)

def revoke_authorization(action):
    """User can revoke authorization anytime"""
    AUTHORIZATION_LEVELS[action] = False
```

### 6. Agent Orchestration System

**Purpose**: Ensure only one agent runs at a time

**Agent States**:
- **ACTIVE**: Currently processing requests
- **DORMANT**: Idle, ready to activate
- **QUIT**: Terminated, needs restart

**Orchestration Logic**:
```python
class AgentOrchestrator:
    def __init__(self):
        self.active_agent = None
        self.agents = {
            'anthropic': {'state': 'DORMANT', 'instance': None},
            'zypher': {'state': 'DORMANT', 'instance': None},
            'openclaw': {'state': 'DORMANT', 'instance': None}
        }

    def activate_agent(self, agent_name):
        """Activate agent, deactivate others"""
        # Deactivate current agent
        if self.active_agent:
            self.deactivate_agent(self.active_agent)

        # Activate new agent
        self.agents[agent_name]['state'] = 'ACTIVE'
        self.active_agent = agent_name

        # Set others to DORMANT
        for name in self.agents:
            if name != agent_name:
                self.agents[name]['state'] = 'DORMANT'

    def deactivate_agent(self, agent_name):
        """Deactivate agent"""
        self.agents[agent_name]['state'] = 'DORMANT'
        if self.active_agent == agent_name:
            self.active_agent = None

    def quit_agent(self, agent_name):
        """Terminate agent"""
        self.agents[agent_name]['state'] = 'QUIT'
        self.agents[agent_name]['instance'] = None
```

### 7. Unified File Storage System

**Purpose**: Centralized data storage accessible by all components

**Storage Structure**:
```
~/.realchat/
├── config/
│   ├── user_profile.json
│   ├── response_templates.json
│   ├── authorization.json
│   └── agent_state.json
├── data/
│   ├── chat_history/
│   │   ├── {contact_id}.json
│   │   └── ...
│   ├── contacts/
│   │   ├── {contact_id}.json
│   │   └── categories.json
│   └── moments/
│       ├── {contact_id}_moments.json
│       └── feed_cache.json
├── backups/
│   ├── {timestamp}_backup.tar.gz
│   └── ...
└── logs/
    ├── app.log
    ├── agent.log
    └── authorization.log
```

**Storage API**:
```python
class UnifiedStorage:
    def __init__(self, base_path='~/.realchat'):
        self.base_path = os.path.expanduser(base_path)
        self.ensure_directories()

    def save_user_profile(self, profile_data):
        """Save user profile"""
        path = os.path.join(self.base_path, 'config', 'user_profile.json')
        with open(path, 'w') as f:
            json.dump(profile_data, f, indent=2)

    def load_user_profile(self):
        """Load user profile"""
        path = os.path.join(self.base_path, 'config', 'user_profile.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return {}

    def save_chat_history(self, contact_id, messages):
        """Save chat history"""
        path = os.path.join(self.base_path, 'data', 'chat_history', f'{contact_id}.json')
        with open(path, 'w') as f:
            json.dump(messages, f, indent=2)

    def load_chat_history(self, contact_id):
        """Load chat history"""
        path = os.path.join(self.base_path, 'data', 'chat_history', f'{contact_id}.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return []

    def save_contact_category(self, contact_id, category):
        """Save contact category"""
        categories_path = os.path.join(self.base_path, 'data', 'contacts', 'categories.json')
        categories = {}
        if os.path.exists(categories_path):
            with open(categories_path, 'r') as f:
                categories = json.load(f)

        categories[contact_id] = category

        with open(categories_path, 'w') as f:
            json.dump(categories, f, indent=2)

    def backup_all_data(self):
        """Create backup of all data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.base_path, 'backups', f'{timestamp}_backup.tar.gz')
        # Create tar.gz of data directory
        # Return backup path
```

## 🔄 User Flow

### Initial Setup

1. **User accesses web app** (http://localhost:5001)
2. **Setup wizard appears**:
   - Welcome screen
   - Privacy policy & consent
   - Personal information form
   - Response templates setup
   - Authorization preferences
   - AI provider selection
3. **WeChat detection**:
   - Auto-detect WeChat desktop app
   - Request accessibility permissions if needed
   - Verify connection
4. **Ready to use**

### Daily Usage

1. **User opens web app**
2. **Dashboard shows**:
   - Unread message count
   - Pinned chats
   - Recent activity
   - Agent status
3. **User can**:
   - Start/stop auto-reply
   - View and manage templates
   - Browse categorized contacts
   - Check authorization settings
   - Switch AI providers
   - Backup data

### Auto-Reply Flow

1. **User enables auto-reply**
2. **System scans unread messages**
3. **For each message**:
   - Analyze importance
   - Check if template applies
   - Get AI response if needed
   - Pin if important
   - Send reply (if authorized)
4. **User reviews pinned messages**
5. **System unpins when read**

### Agent Selection Flow

1. **User chats with themselves in WeChat**
2. **Types**: "use openclaw"
3. **System**:
   - Detects self-chat command
   - Switches to OpenClaw agent
   - Confirms switch
4. **Now OpenClaw handles requests**:
   - Can access local files
   - Can perform file operations
   - Can execute system commands

## 🔒 Privacy Guarantees

1. **No action without consent**: Every operation requires explicit authorization
2. **Transparent data usage**: User sees exactly what data is accessed
3. **Revocable permissions**: User can revoke any authorization anytime
4. **Local storage**: All data stored locally, not sent to external servers
5. **Audit log**: Complete log of all actions performed
6. **Data encryption**: Sensitive data encrypted at rest
7. **No tracking**: No analytics or tracking without consent

## 🎯 Implementation Priority

### Phase 1: Core Foundation (Week 1)
- ✅ Unified file storage system
- ✅ Privacy & authorization system
- ✅ WeChat desktop auto-detection
- ✅ Basic chat operations (locate, read, send)

### Phase 2: Message Management (Week 2)
- ✅ Unread message scanner
- ✅ Importance analyzer
- ✅ Pin/unpin controller
- ✅ Contact categorizer

### Phase 3: Advanced Features (Week 3)
- ✅ WeChat Moments browser
- ✅ Relationship analyzer
- ✅ Self-chat agent selector
- ✅ Template system

### Phase 4: Agent Orchestration (Week 4)
- ✅ Mutual exclusivity system
- ✅ Agent state management
- ✅ Seamless switching
- ✅ Performance optimization

### Phase 5: UI & Polish (Week 5)
- ✅ Setup wizard
- ✅ Dashboard
- ✅ Authorization manager
- ✅ Settings UI
- ✅ Documentation

## 📚 Next Steps

1. Implement unified storage system
2. Build privacy/authorization framework
3. Create WeChat desktop connector
4. Develop chat operations module
5. Build message management system
6. Implement moments browser
7. Create agent orchestrator
8. Build web UI components
9. Test integration
10. Deploy and document

---

**This architecture ensures privacy, user control, and intelligent automation while maintaining system independence and mutual exclusivity.**
