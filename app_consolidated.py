#!/usr/bin/env python3
"""
RealChat - Consolidated Flask Application
Single monorepo deployment with all services integrated
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json
import logging
import threading
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import services
from services.wechat_service import WeChatService
from services.ai_service import AIService
from modules.command_parser import CommandParser, CommandExecutor
from utils.logging_config import ColoredFormatter, RateLimitedLogger, EndpointFilter

# Configure enhanced logging
logging.setLoggerClass(RateLimitedLogger)

# Create console handler with colored formatter
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = ColoredFormatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
console_handler.setFormatter(formatter)
console_handler.addFilter(EndpointFilter())

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(console_handler)

# Reduce werkzeug verbosity
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Get logger for this module
logger = logging.getLogger(__name__)

# Log startup message
logger.info("=" * 60)
logger.info("🚀 RealChat Backend Starting")
logger.info("=" * 60)

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize services
wechat_config = {
    'chat_names': os.getenv('WECHAT_CHAT_NAMES', 'File Transfer,文件传输助手').split(','),
    'scan_method': os.getenv('WECHAT_SCAN_METHOD', 'applescript'),
    'auto_detect_messages': True  # Auto-detect incoming messages
}
wechat_service = WeChatService(wechat_config)

# Message deduplication cache: {message_hash: timestamp}
# Prevents sending the same message multiple times within a short window
sent_messages_cache = {}
send_message_lock = threading.Lock()  # Thread lock to prevent race conditions
DEDUP_WINDOW_SECONDS = 3  # Prevent duplicates within 3 seconds

ai_config = {
    'api_key': os.getenv('AI_API_KEY'),
    'base_url': os.getenv('AI_BASE_URL', 'https://api.anthropic.com'),
    'model': os.getenv('AI_MODEL', 'claude-sonnet-4-5-20250929'),
    'max_tokens': os.getenv('AI_MAX_TOKENS', '1024')
}
ai_service = AIService(ai_config)

# Initialize command executor
command_executor = CommandExecutor(wechat_service)

# Global state
agent_running = False
agent_thread = None
last_message = ""
selected_chat = None  # Store selected chat for agent
DEFAULT_COMMAND_CHAT = "File Transfer"  # Actual chat name for File Transfer
DEFAULT_SEARCH_TERM = "File"  # Search term to find File Transfer chat

# AI Settings file
AI_SETTINGS_FILE = Path('ai_settings.json')


# ============================================================================
# Helper Functions
# ============================================================================

def load_ai_settings():
    """Load AI settings from JSON file"""
    if not AI_SETTINGS_FILE.exists():
        return {
            'api_key': '',
            'base_url': 'https://api.anthropic.com',
            'model': 'claude-sonnet-4-5-20250929'
        }

    try:
        with open(AI_SETTINGS_FILE, 'r') as f:
            settings = json.load(f)

            # Ensure all required fields exist
            if 'api_key' not in settings:
                settings['api_key'] = ''
            if 'base_url' not in settings:
                settings['base_url'] = 'https://api.anthropic.com'
            if 'model' not in settings:
                settings['model'] = 'claude-sonnet-4-5-20250929'

            return settings
    except Exception as e:
        logger.error(f"Error loading AI settings: {e}")
        return {
            'api_key': '',
            'base_url': 'https://api.anthropic.com',
            'model': 'claude-sonnet-4-5-20250929'
        }


def save_ai_settings(settings):
    """Save AI settings to JSON file"""
    try:
        with open(AI_SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving AI settings: {e}")
        return False


# ============================================================================
# Web Routes
# ============================================================================

@app.route('/')
def index():
    """Serve web client"""
    # Try control panel first (primary interface)
    control_panel = Path('control_panel.html')
    if control_panel.exists():
        return send_from_directory('.', 'control_panel.html')

    # Try enhanced client
    enhanced_client = Path('client_enhanced.html')
    if enhanced_client.exists():
        return send_from_directory('.', 'client_enhanced.html')

    client_html = Path('client.html')
    if client_html.exists():
        return send_from_directory('.', 'client.html')

    react_build = Path('frontend/dist/index.html')
    if react_build.exists():
        return send_from_directory('frontend/dist', 'index.html')

    return jsonify({"message": "RealChat API", "version": "2.0.0"})


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "services": {
            "wechat": wechat_service.is_wechat_running(),
            "ai": ai_service.health_check()
        }
    })


@app.route('/api/status')
def status():
    """Get system status"""
    return jsonify({
        "agent_running": agent_running,
        "wechat_running": wechat_service.is_wechat_running(),
        "ai_status": ai_service.get_status(),
        "config": {
            "chat_names": wechat_service.chat_names,
            "scan_method": wechat_service.scan_method,
            "ai_model": ai_service.model
        }
    })


# ============================================================================
# WeChat API Routes
# ============================================================================

@app.route('/api/wechat/chats', methods=['GET'])
def get_chats():
    """Scan and return available chats"""
    try:
        max_chats = request.args.get('max', 10, type=int)
        structured = request.args.get('structured', 'false').lower() == 'true'

        if structured:
            chats = wechat_service.scan_chats_structured(max_chats)
        else:
            chats = wechat_service.scan_chats(max_chats)

        return jsonify({
            "success": True,
            "chats": chats,
            "count": len(chats),
            "method": wechat_service.scan_method,
            "structured": structured
        })
    except Exception as e:
        logger.error(f"Error scanning chats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/wechat/chats/search', methods=['GET'])
def search_chats():
    """Search for chats"""
    try:
        query = request.args.get('q', '')
        max_results = request.args.get('max', 5, type=int)

        if not query:
            return jsonify({"success": False, "error": "Query parameter 'q' is required"}), 400

        results = wechat_service.search_chats(query, max_results)

        return jsonify({
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        })
    except Exception as e:
        logger.error(f"Error searching chats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/wechat/send', methods=['POST'])
def send_message():
    """Send message to WeChat with deduplication and thread safety"""
    global selected_chat, sent_messages_cache, send_message_lock

    # Use thread lock to prevent race conditions
    with send_message_lock:
        try:
            data = request.json
            message = data.get('message')
            chat_name = data.get('chat_name')

            logger.info(f"📥 SEND REQUEST: Chat={chat_name}, Msg={message[:50]}...")

            if not message:
                return jsonify({"success": False, "error": "Message is required"}), 400

            # Create a unique hash for this message
            message_hash = f"{chat_name}:{message}"
            current_time = time.time()

            logger.info(f"🔍 Cache check: {len(sent_messages_cache)} entries")

            # Check if this exact message was sent recently
            if message_hash in sent_messages_cache:
                last_sent_time = sent_messages_cache[message_hash]
                time_since_last_send = current_time - last_sent_time

                if time_since_last_send < DEDUP_WINDOW_SECONDS:
                    logger.warning(f"⚠️ DUPLICATE BLOCKED (sent {time_since_last_send:.2f}s ago)")
                    return jsonify({
                        "success": True,
                        "message": "Duplicate message blocked (already sent)",
                        "deduplicated": True
                    })

            # Clean up old entries from cache (older than dedup window)
            sent_messages_cache = {
                k: v for k, v in sent_messages_cache.items()
                if current_time - v < DEDUP_WINDOW_SECONDS
            }

            # Update selected chat
            if chat_name:
                selected_chat = chat_name

            # Send the message
            logger.info(f"📤 SENDING to WeChat...")
            success = wechat_service.send_message(message, chat_name)

            if success:
                # Cache this message to prevent duplicates
                sent_messages_cache[message_hash] = current_time
                logger.info(f"✅ SENT AND CACHED")

            # Emit chat change event
            if success and chat_name:
                socketio.emit('current_chat_update', {
                    'chat': chat_name,
                    'detected': False,
                    'selected': chat_name,
                    'timestamp': time.time()
                })

            return jsonify({
                "success": success,
                "message": "Message sent" if success else "Failed to send message"
            })
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/wechat/open-chat', methods=['POST'])
def open_chat():
    """Open a chat by name (programmatically double-click)"""
    global selected_chat
    try:
        data = request.json
        chat_name = data.get('chat_name')

        if not chat_name:
            return jsonify({"success": False, "error": "chat_name is required"}), 400

        logger.info(f"API: Opening chat '{chat_name}'")

        # Open the chat
        success = wechat_service.open_chat(chat_name)

        if success:
            # Update selected chat
            selected_chat = chat_name

            # Emit chat change event
            socketio.emit('current_chat_update', {
                'chat': chat_name,
                'detected': True,
                'selected': chat_name,
                'timestamp': time.time()
            })

            return jsonify({
                "success": True,
                "message": f"Chat '{chat_name}' opened successfully",
                "chat": chat_name
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Failed to open chat '{chat_name}'"
            }), 500

    except Exception as e:
        logger.error(f"Error opening chat: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/wechat/read', methods=['GET'])
def read_messages():
    """Read messages from WeChat"""
    try:
        chat_name = request.args.get('chat_name')
        structured = request.args.get('structured', 'false').lower() == 'true'
        use_ocr = request.args.get('ocr', 'false').lower() == 'true'
        load_context = request.args.get('load_context', 'false').lower() == 'true'

        # OCR-based reading
        if use_ocr:
            messages = wechat_service.read_messages_ocr()

            # If load_context is true, emit event to ChatBox
            if load_context and messages:
                # Combine all messages into one text block
                context_text = '\n'.join([
                    f"[{msg.get('timestamp', 'Unknown')}] {msg.get('text', '')}"
                    for msg in messages
                    if msg.get('text', '').strip()
                ])

                if context_text:
                    socketio.emit('load_context', {
                        'context': f"Here are the current messages from WeChat:\n\n{context_text}",
                        'message_count': len([m for m in messages if m.get('text', '').strip()])
                    })
                    logger.info(f"Emitted context load event with {len(messages)} messages")

            return jsonify({
                "success": True,
                "method": "ocr",
                "messages": messages,
                "count": len(messages)
            })

        # Traditional reading methods
        if structured:
            data = wechat_service.read_messages_structured(chat_name)
            if data:
                return jsonify({
                    "success": True,
                    "data": data
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to read messages"
                }), 500
        else:
            content = wechat_service.read_last_message(chat_name)
            return jsonify({
                "success": True,
                "content": content,
                "length": len(content) if content else 0
            })
    except Exception as e:
        logger.error(f"Error reading messages: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/wechat/messages/new', methods=['GET'])
def get_new_messages():
    """Get new messages using OCR (only messages since last check)"""
    try:
        new_messages = wechat_service.get_new_messages_ocr()
        return jsonify({
            "success": True,
            "messages": new_messages,
            "count": len(new_messages),
            "method": "ocr"
        })
    except Exception as e:
        logger.error(f"Error getting new messages: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/wechat/messages/check', methods=['GET'])
def check_new_messages():
    """Check if there are new messages (without reading them)"""
    try:
        has_new = wechat_service.has_new_message()
        return jsonify({
            "success": True,
            "has_new_message": has_new
        })
    except Exception as e:
        logger.error(f"Error checking for new messages: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/wechat/history', methods=['GET'])
def scan_history():
    """Scan conversation history"""
    try:
        chat_name = request.args.get('chat_name')
        max_messages = request.args.get('max', 50, type=int)

        history = wechat_service.scan_conversation_history(chat_name, max_messages)

        if history:
            return jsonify({
                "success": True,
                "history": history
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to scan history"
            }), 500
    except Exception as e:
        logger.error(f"Error scanning history: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/wechat/current-chat', methods=['GET'])
def get_current_chat():
    """Get currently selected chat from WeChat window"""
    try:
        # Try to detect current chat from window title
        current_chat = wechat_service.get_current_chat_name()

        # Show accurate status - don't fall back to selected_chat
        if not current_chat:
            current_chat = "No chat open (open a chat to detect)"

        return jsonify({
            "success": True,
            "chat": current_chat,
            "detected": current_chat != "No chat open (open a chat to detect)",
            "selected": selected_chat
        })
    except Exception as e:
        logger.error(f"Error getting current chat: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "chat": selected_chat or "Unknown"
        }), 500


@app.route('/api/wechat/window', methods=['GET'])
def get_window_info():
    """Get WeChat window information"""
    try:
        window_info = wechat_service.get_wechat_window_info()
        cursor_pos = wechat_service.get_cursor_position()
        window_under_cursor = wechat_service.get_window_under_cursor()
        is_focused = wechat_service.verify_wechat_active_and_focused()

        if window_info:
            return jsonify({
                "success": True,
                "window": window_info,
                "cursor": cursor_pos,
                "window_under_cursor": window_under_cursor,
                "is_running": True,
                "is_ready": wechat_service.ensure_wechat_ready(),
                "is_focused": is_focused,
                "cursor_in_window": window_under_cursor and window_under_cursor.get('process_name') == 'WeChat'
            })
        else:
            return jsonify({
                "success": False,
                "error": "WeChat window not found",
                "is_running": wechat_service.is_wechat_running()
            }), 404
    except Exception as e:
        logger.error(f"Error getting window info: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/wechat/ocr-debug-image', methods=['GET'])
def get_ocr_debug_image():
    """Serve the debug OCR screenshot for live preview"""
    try:
        debug_path = '/tmp/wechat_ocr_debug.png'
        if os.path.exists(debug_path):
            return send_from_directory('/tmp', 'wechat_ocr_debug.png', mimetype='image/png')
        else:
            # Return a placeholder or 404
            return jsonify({"success": False, "error": "No debug screenshot available"}), 404
    except Exception as e:
        logger.error(f"Error serving debug image: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# AI API Routes
# ============================================================================

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """Get AI response"""
    try:
        data = request.json
        message = data.get('message')
        context = data.get('context', {})

        if not message:
            return jsonify({"success": False, "error": "Message is required"}), 400

        response = ai_service.get_chat_response(message, context)

        return jsonify({
            "success": True,
            "response": response
        })
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/analyze', methods=['POST'])
def analyze_message():
    """Analyze message importance"""
    try:
        data = request.json
        message = data.get('message')
        contact_info = data.get('contact_info', {})

        if not message:
            return jsonify({"success": False, "error": "Message is required"}), 400

        analysis = ai_service.analyze_message_importance(message, contact_info)

        return jsonify({
            "success": True,
            "analysis": analysis
        })
    except Exception as e:
        logger.error(f"Error analyzing message: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# Agent Control Routes
# ============================================================================

@app.route('/api/agent/start', methods=['POST'])
def start_agent():
    """Start the AI agent"""
    global agent_running, agent_thread, selected_chat

    if agent_running:
        return jsonify({"success": False, "error": "Agent already running"})

    try:
        # Get chat name from request
        data = request.json or {}
        chat_name = data.get('chat_name')

        if chat_name:
            selected_chat = chat_name
            logger.info(f"Agent will monitor chat: {selected_chat}")
            # Emit chat change event
            socketio.emit('current_chat_update', {
                'chat': selected_chat,
                'detected': False,
                'selected': selected_chat,
                'timestamp': time.time()
            })

        agent_running = True
        agent_thread = threading.Thread(target=agent_worker, daemon=True)
        agent_thread.start()

        return jsonify({
            "success": True,
            "message": f"Agent started{' monitoring: ' + selected_chat if selected_chat else ''}"
        })
    except Exception as e:
        agent_running = False
        logger.error(f"Error starting agent: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agent/stop', methods=['POST'])
def stop_agent():
    """Stop the AI agent"""
    global agent_running

    if not agent_running:
        return jsonify({"success": False, "error": "Agent not running"})

    agent_running = False

    return jsonify({
        "success": True,
        "message": "Agent stopped"
    })


@app.route('/api/agent/switch-chat', methods=['POST'])
def switch_chat():
    """Switch agent to monitor a different chat"""
    global selected_chat, agent_running

    if not agent_running:
        return jsonify({"success": False, "error": "Agent not running"})

    data = request.json or {}
    new_chat = data.get('chat_name')

    if not new_chat:
        return jsonify({"success": False, "error": "chat_name required"}), 400

    previous_chat = selected_chat
    selected_chat = new_chat

    logger.info(f"Agent switched from '{previous_chat}' to '{new_chat}'")
    socketio.emit('chat_switched', {
        'from': previous_chat,
        'to': new_chat
    })

    return jsonify({
        "success": True,
        "previous_chat": previous_chat,
        "current_chat": new_chat,
        "message": f"Agent switched to {new_chat}"
    })


@app.route('/api/messages/history/<chat_name>', methods=['GET'])
def get_message_history(chat_name):
    """Get conversation history for a specific chat"""
    try:
        limit = int(request.args.get('limit', 50))

        # Read messages from WeChat
        data = wechat_service.read_messages_structured(chat_name)

        if not data:
            return jsonify({
                "success": False,
                "error": "Failed to read messages"
            }), 500

        # Parse messages from raw content
        messages = []
        if data.get('messages'):
            for msg in data['messages']:
                messages.append({
                    'index': msg.get('index', 0),
                    'text': msg.get('text', ''),
                    'length': msg.get('length', 0)
                })

        return jsonify({
            "success": True,
            "chat_name": chat_name,
            "total_messages": data.get('message_count', 0),
            "timestamp": data.get('timestamp', 0),
            "messages": messages[:limit],
            "latest_message": data.get('latest_message', '')
        })

    except Exception as e:
        logger.error(f"Error getting message history: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/messages/send', methods=['POST'])
def send_message_api():
    """Send a message and optionally track the reply"""
    try:
        data = request.json or {}
        chat_name = data.get('chat_name')
        message = data.get('message')
        track_reply = data.get('track_reply', False)

        if not chat_name or not message:
            return jsonify({
                "success": False,
                "error": "chat_name and message required"
            }), 400

        # Send message
        success = wechat_service.send_message(message, chat_name)

        if not success:
            return jsonify({
                "success": False,
                "error": "Failed to send message"
            }), 500

        response = {
            "success": True,
            "message_id": f"msg_{int(time.time())}",
            "sent_at": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "chat_name": chat_name
        }

        # If tracking reply, emit WebSocket event
        if track_reply:
            socketio.emit('message_sent', {
                'message': message,
                'chat': chat_name,
                'timestamp': response['sent_at']
            })
            response['reply'] = {
                'text': 'Message sent successfully',
                'displayed': True
            }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# Backend Configuration Routes
# ============================================================================

@app.route('/api/backend/status', methods=['GET'])
def get_backend_status():
    """Get backend system status"""
    return jsonify({
        "success": True,
        "status": {
            "agent_running": agent_running,
            "wechat_running": wechat_service.is_wechat_running(),
            "selected_chat": selected_chat,
            "ai_model": ai_config['model'],
            "scan_method": wechat_config['scan_method']
        }
    })


@app.route('/api/backend/config', methods=['GET'])
def get_backend_config():
    """Get current backend configuration"""
    return jsonify({
        "success": True,
        "config": {
            "ai_model": ai_config['model'],
            "ai_base_url": ai_config['base_url'],
            "ai_max_tokens": ai_config['max_tokens'],
            "scan_method": wechat_config['scan_method'],
            "chat_names": wechat_config['chat_names'],
            "agent_running": agent_running,
            "selected_chat": selected_chat,
            "auto_detect_messages": wechat_config.get('auto_detect_messages', False),
            "available_models": [
                "claude-sonnet-4-5-20250929",
                "claude-opus-4-5-20251101",
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229"
            ],
            "available_scan_methods": ["applescript", "ocr", "manual"]
        }
    })


@app.route('/api/backend/config', methods=['POST'])
def update_backend_config():
    """Update backend configuration"""
    try:
        data = request.json

        # Update AI config
        if 'ai_model' in data:
            ai_config['model'] = data['ai_model']
        if 'ai_max_tokens' in data:
            ai_config['max_tokens'] = int(data['ai_max_tokens'])

        # Update WeChat config
        if 'scan_method' in data:
            wechat_config['scan_method'] = data['scan_method']
        if 'auto_detect_messages' in data:
            wechat_config['auto_detect_messages'] = bool(data['auto_detect_messages'])
            logger.info(f"Auto-detect messages: {wechat_config['auto_detect_messages']}")

        logger.info(f"Backend config updated: {data}")

        return jsonify({
            "success": True,
            "message": "Configuration updated successfully"
        })
    except Exception as e:
        logger.error(f"Error updating backend config: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# WeChat Bridge Integration Routes
# ============================================================================

@app.route('/api/bridge/status', methods=['GET'])
def get_bridge_status():
    """Get WeChat Bridge status"""
    try:
        import requests
        response = requests.get('http://localhost:8081/status', timeout=2)
        if response.ok:
            bridge_data = response.json()
            return jsonify({
                "success": True,
                "bridge": {
                    "connected": True,
                    "logged_in": bridge_data.get('isLoggedIn', False),
                    "user": bridge_data.get('user'),
                    "clients": bridge_data.get('clients', 0)
                }
            })
        else:
            return jsonify({
                "success": False,
                "bridge": {"connected": False},
                "error": "Bridge not responding"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "bridge": {"connected": False},
            "error": str(e)
        })


@app.route('/api/bridge/message', methods=['POST'])
def receive_bridge_message():
    """Receive message from WeChat Bridge"""
    try:
        data = request.json
        message_text = data.get('text', '')
        sender = data.get('from', {})
        room = data.get('room')
        message_id = data.get('id')

        sender_name = sender.get('name', 'Unknown')
        chat_name = room.get('topic') if room else sender_name

        logger.info(f"📨 Bridge message from {sender_name}: {message_text[:50]}...")

        # Emit to frontend via Socket.IO
        socketio.emit('bridge_message', {
            'id': message_id,
            'text': message_text,
            'sender': sender_name,
            'chat': chat_name,
            'timestamp': data.get('timestamp'),
            'room': room is not None
        })

        # Log activity
        socketio.emit('log', {
            'type': 'info',
            'message': f"📨 Bridge: Message from {sender_name} in {chat_name}",
            'timestamp': time.time()
        })

        # Process with AI if agent is running
        ai_response = None
        if agent_running:
            try:
                ai_response = ai_service.chat(message_text, context={
                    'sender': sender_name,
                    'chat': chat_name
                })

                logger.info(f"🤖 AI response: {ai_response[:50]}...")

                # Emit AI response to frontend
                socketio.emit('ai_response', {
                    'message_id': message_id,
                    'response': ai_response,
                    'chat': chat_name
                })

                # Log AI response
                socketio.emit('log', {
                    'type': 'success',
                    'message': f"🤖 AI responded to {sender_name}",
                    'timestamp': time.time()
                })
            except Exception as e:
                logger.error(f"Error processing with AI: {e}")
                socketio.emit('log', {
                    'type': 'error',
                    'message': f"❌ AI error: {str(e)}",
                    'timestamp': time.time()
                })

        return jsonify({
            "success": True,
            "response": ai_response,
            "processed": agent_running
        })

    except Exception as e:
        logger.error(f"Error receiving bridge message: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/bridge/send', methods=['POST'])
def send_via_bridge():
    """Send message via WeChat Bridge"""
    try:
        data = request.json
        message = data.get('message')
        chat_name = data.get('chat_name')
        contact_name = data.get('contact_name')
        room_name = data.get('room_name')

        if not message:
            return jsonify({"success": False, "error": "Message is required"}), 400

        # Forward to bridge
        import requests
        response = requests.post('http://localhost:8081/send', json={
            'text': message,
            'contactName': contact_name or chat_name,
            'roomName': room_name
        }, timeout=5)

        if response.ok:
            result = response.json()

            # Emit to frontend
            socketio.emit('message_sent', {
                'message': message,
                'chat': chat_name or contact_name or room_name,
                'via': 'bridge'
            })

            socketio.emit('log', {
                'type': 'success',
                'message': f"✅ Message sent via bridge to {chat_name or contact_name or room_name}",
                'timestamp': time.time()
            })

            return jsonify({
                "success": True,
                "message": "Message sent via bridge"
            })
        else:
            error_msg = response.json().get('error', 'Unknown error')
            socketio.emit('log', {
                'type': 'error',
                'message': f"❌ Bridge send failed: {error_msg}",
                'timestamp': time.time()
            })
            return jsonify({"success": False, "error": error_msg}), 500

    except Exception as e:
        logger.error(f"Error sending via bridge: {e}")
        socketio.emit('log', {
            'type': 'error',
            'message': f"❌ Bridge error: {str(e)}",
            'timestamp': time.time()
        })
        return jsonify({"success": False, "error": str(e)}), 500



# ============================================================================
# Legacy API Routes (for React frontend compatibility)
# ============================================================================

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get configuration (legacy endpoint)"""
    return jsonify({
        "chat_name": wechat_service.chat_names[0] if wechat_service.chat_names else "",
        "user_name": "",
        "user_title": "",
        "intro_template": "Hi! I'm {{NAME}}, {{TITLE}}. It was great meeting you!",
        "default_reply": "Thanks for your message!",
        "reply_mode": "c",
        "dry_run": "no"
    })


@app.route('/api/config', methods=['POST'])
def save_config():
    """Save configuration (legacy endpoint)"""
    try:
        data = request.json
        # Configuration is now in .env file, so just return success
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai-settings', methods=['GET'])
def get_ai_settings():
    """Get AI settings"""
    try:
        settings = load_ai_settings()
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        logger.error(f"Error getting AI settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai-settings', methods=['POST'])
def update_ai_settings():
    """Update AI settings"""
    try:
        settings = request.json

        # Validate settings
        required_fields = ['api_key', 'base_url', 'model']
        for field in required_fields:
            if field not in settings:
                settings[field] = ''

        # Save settings
        if save_ai_settings(settings):
            logger.info('AI settings updated')
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to save settings'}), 500

    except Exception as e:
        logger.error(f'Failed to update AI settings: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """Chat with Claude AI"""
    try:
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'claude')
        history = data.get('history', [])
        send_to_wechat = data.get('send_to_wechat', True)  # Default: send to WeChat

        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        # Route to Zypher Agent if selected
        if model == 'zypher':
            try:
                zypher_url = os.getenv('ZYPHER_URL', 'http://localhost:8000')
                logger.info(f"Routing to Zypher Agent at {zypher_url}")

                response = requests.post(
                    f"{zypher_url}/api/chat",
                    json={
                        'message': message,
                        'model': 'claude-sonnet-4-20250514',
                        'history': history
                    },
                    timeout=10  # Reduced from 30 to 10 seconds
                )

                if response.status_code == 200:
                    zypher_data = response.json()
                    if zypher_data.get('success'):
                        response_text = zypher_data.get('response', '')

                        # Send response back to WeChat if enabled
                        if send_to_wechat:
                            logger.info("Attempting to send Zypher response back to WeChat...")
                            try:
                                current_chat = wechat_service.get_current_chat()
                                invalid_chats = ['No active chat', 'File Transfer', 'Search', 'Photos and Videos',
                                                'Favorites', 'Official Accounts', 'Settings', 'Profile', 'Log Out',
                                                'Help', 'Moments']

                                if current_chat and current_chat not in invalid_chats:
                                    if wechat_service.ocr_reader:
                                        wechat_service.ocr_reader.mark_as_agent_message(response_text)

                                    success = wechat_service.send_message(response_text, current_chat)

                                    if success and wechat_service.ocr_reader:
                                        wechat_service.ocr_reader.mark_as_agent_message(response_text)
                                        socketio.emit('log', {
                                            'type': 'success',
                                            'message': f'🤖 Sent Zypher response to {current_chat}',
                                            'timestamp': time.time()
                                        })
                            except Exception as send_error:
                                logger.error(f"Error sending Zypher response to WeChat: {send_error}")

                        return jsonify({
                            'success': True,
                            'response': response_text,
                            'model': 'zypher'
                        })
                else:
                    logger.warning(f'Zypher Agent returned status {response.status_code}, falling back to Claude')
                    # Fall through to Claude backend below

            except requests.exceptions.ConnectionError:
                logger.warning('Zypher Agent service is not running, falling back to Claude')
                # Fall through to Claude backend below
            except Exception as e:
                logger.error(f"Error connecting to Zypher Agent: {e}, falling back to Claude")
                # Fall through to Claude backend below

        # Load AI settings
        ai_settings = load_ai_settings()

        # Check if API key is configured
        if not ai_settings.get('api_key'):
            return jsonify({
                'success': False,
                'error': 'Please configure API key in settings'
            }), 400

        # Try to use Anthropic API
        try:
            from anthropic import Anthropic

            # IMPORTANT: Override system environment variables with settings from ai_settings.json
            # This ensures ai_settings.json takes priority over system env vars
            os.environ['ANTHROPIC_API_KEY'] = ai_settings['api_key']
            os.environ['ANTHROPIC_BASE_URL'] = ai_settings.get('base_url', 'https://api.anthropic.com')

            client = Anthropic(
                api_key=ai_settings['api_key'],
                base_url=ai_settings.get('base_url', 'https://api.anthropic.com')
            )

            # Build system prompt with [Agent] prefix requirement
            system_prompt = "You are a WeChat messaging assistant.\n\n"
            system_prompt += "CRITICAL RULES:\n"
            system_prompt += "1. Always start with '[Agent]'\n"
            system_prompt += "2. MATCH USER'S MESSAGE LENGTH - if they send 2 words, you send 2-3 words. If they send 10 words, you send 10-12 words.\n"
            system_prompt += "3. ONE LINE ONLY - no line breaks, no lists, no paragraphs\n"
            system_prompt += "4. Be casual and conversational like texting\n\n"
            system_prompt += "Examples:\n"
            system_prompt += "User: 'hey' → '[Agent] Hey!'\n"
            system_prompt += "User: 'Test, hi' → '[Agent] Hi there!'\n"
            system_prompt += "User: 'what's up?' → '[Agent] Not much, you?'\n"
            system_prompt += "User: 'how are you doing today?' → '[Agent] Good thanks, how about you?'\n\n"
            system_prompt += "Keep responses SHORT. Match their length exactly."

            # Convert history to Claude format
            messages = []

            # Add system prompt as first user message if no history
            if not history or len(history) == 0:
                messages.append({
                    'role': 'user',
                    'content': system_prompt
                })
                messages.append({
                    'role': 'assistant',
                    'content': '[Agent] Got it - short responses only, match their length'
                })

            for msg in history:
                if msg.get('role') in ['user', 'assistant']:
                    messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })

            # Add current message with explicit word count instruction
            user_word_count = len(message.split())

            # Determine target response length based on user's word count
            if user_word_count <= 5:
                target_words = "1-5 words"
            elif user_word_count <= 15:
                target_words = "6-15 words"
            else:
                target_words = "15-25 words"

            # Add explicit instruction to the message
            message_with_instruction = f"{message}\n\n[INSTRUCTION: User sent {user_word_count} words. Respond with {target_words} ONLY. Keep it SHORT.]"

            messages.append({
                'role': 'user',
                'content': message_with_instruction
            })

            # Call Claude API with configured model
            # Try with system parameter first (official API), fallback to messages only (custom API)
            model_name = ai_settings.get('model', 'claude-sonnet-4-5-20250929')
            try:
                response = client.messages.create(
                    model=model_name,
                    max_tokens=40,  # ~30 words max - very strict limit
                    temperature=0.7,  # Slightly lower for more predictable responses
                    system=system_prompt,
                    messages=messages
                )
            except Exception as system_error:
                # If system parameter fails, try without it (for custom APIs)
                logger.warning(f"System parameter not supported, retrying without it: {system_error}")
                response = client.messages.create(
                    model=model_name,
                    max_tokens=40,  # ~30 words max - very strict limit
                    temperature=0.7,  # Slightly lower for more predictable responses
                    messages=messages
                )

            response_text = response.content[0].text

            # SAFETY CHECK: Remove all line breaks and newlines
            response_text = response_text.replace('\n', ' ').replace('\r', ' ')
            # Remove multiple spaces
            response_text = ' '.join(response_text.split())

            # SAFETY CHECK: Ensure [Agent] prefix is always present
            if not response_text.strip().startswith('[Agent]'):
                response_text = f"[Agent] {response_text}"
                logger.info("Added [Agent] prefix to chat response")

            logger.info(f'AI responded to: {message[:50]}...')

            # Send response back to WeChat if enabled
            if send_to_wechat:
                logger.info("Attempting to send AI response back to WeChat...")
                try:
                    # Get current chat name
                    current_chat = wechat_service.get_current_chat()
                    logger.info(f"Current chat detected: {current_chat}")

                    # Filter out UI elements and invalid chats
                    invalid_chats = ['No active chat', 'File Transfer', 'Search', 'Photos and Videos',
                                    'Favorites', 'Official Accounts', 'Settings', 'Profile', 'Log Out',
                                    'Help', 'Moments']

                    if current_chat and current_chat not in invalid_chats:
                        logger.info(f"Valid chat detected, sending message to: {current_chat}")

                        # Mark as agent message BEFORE sending to prevent OCR from detecting it
                        if wechat_service.ocr_reader:
                            wechat_service.ocr_reader.mark_as_agent_message(response_text)
                            logger.info("Pre-marked message as agent message (before sending)")

                        # Send message to WeChat
                        success = wechat_service.send_message(response_text, current_chat)

                        if success:
                            logger.info(f"✅ Sent AI response to WeChat: {current_chat}")

                            # Mark as agent message again after sending (double safety)
                            if wechat_service.ocr_reader:
                                wechat_service.ocr_reader.mark_as_agent_message(response_text)
                                logger.info("Post-marked message as agent message (after sending)")

                            # Emit log event
                            socketio.emit('log', {
                                'type': 'success',
                                'message': f'🤖 Sent AI response to {current_chat}',
                                'timestamp': time.time()
                            })
                        else:
                            logger.warning(f"Failed to send AI response to WeChat")
                            socketio.emit('log', {
                                'type': 'warning',
                                'message': f'⚠️ Failed to send AI response to WeChat',
                                'timestamp': time.time()
                            })
                    else:
                        logger.warning(f"No valid chat to send response to. Current chat: {current_chat}")
                        socketio.emit('log', {
                            'type': 'warning',
                            'message': f'⚠️ Cannot send to "{current_chat}" - please open a real chat',
                            'timestamp': time.time()
                        })
                except Exception as send_error:
                    logger.error(f"Error sending to WeChat: {send_error}")
                    import traceback
                    logger.error(traceback.format_exc())

            return jsonify({
                'success': True,
                'response': response_text,
                'model': model
            })

        except ImportError:
            # Anthropic package not installed
            return jsonify({
                'success': False,
                'error': 'Anthropic package not installed. Run: pip install anthropic'
            }), 500
        except Exception as api_error:
            # API call failed
            logger.error(f'AI API error: {api_error}')
            return jsonify({
                'success': False,
                'error': f'API error: {str(api_error)}'
            }), 500

    except Exception as e:
        logger.error(f'Chat error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get bot logs (legacy endpoint)"""
    # Return empty logs for now
    return jsonify([])


@app.route('/api/tracking', methods=['GET'])
def get_tracking():
    """Get tracking data (legacy endpoint)"""
    # Return empty tracking for now
    return jsonify({
        "total_messages": 0,
        "total_replies": 0,
        "contacts": []
    })


@app.route('/api/scan-chats', methods=['GET'])
def scan_chats_legacy():
    """Scan chats (legacy endpoint)"""
    try:
        max_chats = request.args.get('max_chats', 10, type=int)
        chats = wechat_service.scan_chats(max_chats)
        return jsonify({
            "success": True,
            "chats": chats
        })
    except Exception as e:
        logger.error(f"Error scanning chats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/send-test-message', methods=['POST'])
def send_test_message_legacy():
    """Send test message (legacy endpoint)"""
    try:
        data = request.json
        message = data.get('message', 'Test message')
        chat_name = data.get('chat_name')

        success = wechat_service.send_message(message, chat_name)

        return jsonify({
            "success": success,
            "message": "Message sent" if success else "Failed to send message"
        })
    except Exception as e:
        logger.error(f"Error sending test message: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# Agent Worker (Background Thread)
# ============================================================================

def agent_worker():
    """Background worker that monitors WeChat and responds with AI"""
    global agent_running, last_message, selected_chat, command_executor

    logger.info("Agent worker started")
    socketio.emit('agent_status', {'status': 'started'})

    # Use selected chat or default command chat (no search needed - we already know the names)
    command_chat = DEFAULT_COMMAND_CHAT
    target_chat = selected_chat if selected_chat else command_chat

    logger.info(f"Agent monitoring chat: {target_chat}")

    # Send startup message
    startup_msg = f"RealChat Agent | {time.strftime('%H:%M:%S')} | Test: OK"

    wechat_service.send_message(startup_msg, command_chat)
    last_message = startup_msg

    # Update command executor with current chat
    if command_executor:
        command_executor.set_current_chat(selected_chat)

    monitor_interval = int(os.getenv('AGENT_MONITOR_INTERVAL', '1'))  # Reduced to 1 second for faster response

    # Track message history to avoid duplicates
    message_history = set()

    while agent_running:
        try:
            # Comprehensive verification: WeChat must be frontmost AND cursor must be in window
            if not wechat_service.verify_wechat_active_and_focused():
                logger.debug("WeChat not active or cursor outside window, pausing agent actions")
                time.sleep(monitor_interval)
                continue

            # Always monitor File Transfer for commands
            command_data = wechat_service.read_messages_structured(command_chat)

            if command_data and command_data.get('latest_message'):
                latest_command = command_data['latest_message']

                # Check if new message (not from us and not seen before)
                if (latest_command != last_message and
                    "RealChat" not in latest_command and
                    "🤖" not in latest_command and
                    latest_command not in message_history):

                    logger.info(f"File Transfer message: {latest_command[:50]}...")
                    message_history.add(latest_command)

                    # Check if it's a command
                    if command_executor:
                        parsed_cmd = command_executor.parser.parse(latest_command)

                        if parsed_cmd:
                            # Execute command
                            logger.info(f"Executing command: {parsed_cmd['command']}")
                            response = command_executor.execute(parsed_cmd)

                            # Send response to File Transfer
                            wechat_service.send_message(response, command_chat)
                            last_message = response

                            # Update target chat if monitoring changed
                            new_target = command_executor.get_current_chat()
                            if new_target != selected_chat:
                                selected_chat = new_target
                                target_chat = selected_chat if selected_chat else command_chat
                                logger.info(f"Switched monitoring to: {target_chat}")
                                socketio.emit('chat_switched', {'chat': target_chat})

                            socketio.emit('command_executed', {
                                'command': parsed_cmd['command'],
                                'response': response
                            })
                            continue

            # Monitor target chat if specified (not File Transfer)
            if selected_chat and selected_chat != command_chat:
                target_data = wechat_service.read_messages_structured(selected_chat)

                if target_data and target_data.get('latest_message'):
                    latest_msg = target_data['latest_message']

                    # Check if new message (not from us and not seen before)
                    if (latest_msg != last_message and
                        "RealChat" not in latest_msg and
                        "🤖" not in latest_msg and
                        latest_msg not in message_history):

                        logger.info(f"New message in {selected_chat}: {latest_msg[:50]}...")
                        message_history.add(latest_msg)

                        socketio.emit('new_message', {
                            'message': latest_msg,
                            'chat': selected_chat,
                            'metadata': {
                                'message_count': target_data.get('message_count', 0),
                                'timestamp': target_data.get('timestamp', 0)
                            }
                        })

                        # Build conversation history for context
                        conversation_history = []
                        if target_data.get('messages'):
                            # Get last 10 messages for context
                            recent_messages = target_data['messages'][-10:]
                            for msg in recent_messages:
                                conversation_history.append({
                                    'text': msg.get('text', ''),
                                    'index': msg.get('index', 0)
                                })

                        # Get AI response with full conversation context
                        context = {
                            'chat_name': selected_chat,
                            'message_count': target_data.get('message_count', 0),
                            'conversation_history': conversation_history
                        }

                        logger.info(f"Generating AI response with {len(conversation_history)} messages of context")
                        ai_response = ai_service.get_chat_response(latest_msg, context)

                        if ai_response:
                            logger.info(f"AI response: {ai_response[:50]}...")
                            socketio.emit('ai_response', {
                                'response': ai_response,
                                'chat': selected_chat
                            })

                            # Send response to target chat
                            if wechat_service.send_message(ai_response, selected_chat):
                                logger.info("Response sent successfully")
                                last_message = ai_response
                                message_history.add(ai_response)
                                socketio.emit('message_sent', {
                                    'message': ai_response,
                                    'chat': selected_chat
                                })
                            else:
                                logger.error("Failed to send response")
                                socketio.emit('error', {'error': 'Failed to send message'})

            # Clean up old messages from history (keep last 100)
            if len(message_history) > 100:
                message_history.clear()
                logger.info("Cleared message history")

            time.sleep(monitor_interval)

        except Exception as e:
            logger.error(f"Agent worker error: {e}")
            socketio.emit('error', {'error': str(e)})
            time.sleep(monitor_interval)

    logger.info("Agent worker stopped")
    socketio.emit('agent_status', {'status': 'stopped'})


# ============================================================================
# WebSocket Events
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")
    emit('status', {
        'agent_running': agent_running,
        'wechat_running': wechat_service.is_wechat_running()
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")


# Background task to emit current chat updates
def emit_current_chat_updates():
    """Background task to emit current chat updates via WebSocket"""
    global selected_chat
    last_emitted_chat = None
    iteration_count = 0
    last_messages = []  # Track last messages for deduplication
    last_ocr_check = 0  # Rate limit OCR checks
    initial_context_loaded = False  # Track if initial context scan has been done
    previous_auto_detect_state = False  # Track previous auto-detect state

    logger.info("🚀 High-frequency chat detection started (10 Hz / 100ms)")

    while True:
        try:
            detected_chat = None
            iteration_count += 1

            # Try to detect current chat if WeChat is running
            if wechat_service.is_wechat_running():
                # Detect the current chat from WeChat UI
                detected_chat = wechat_service.get_current_chat_name()

                # Only log every 10 iterations (once per second) to reduce log spam
                if iteration_count % 10 == 0:
                    logger.debug(f"[SCAN] Iteration {iteration_count}: {repr(detected_chat)}")

                # Check for new messages if auto-detect is enabled
                # Run OCR every 1 second to detect text changes
                auto_detect_enabled = wechat_config.get('auto_detect_messages', False)

                # Reset initial context flag if auto-detect was toggled off and back on
                if auto_detect_enabled and not previous_auto_detect_state:
                    logger.info("🔄 [AUTO-DETECT] Auto-detect re-enabled, will reload initial context")
                    initial_context_loaded = False
                previous_auto_detect_state = auto_detect_enabled

                if iteration_count % 10 == 0:  # Log every second
                    logger.info(f"[AUTO-DETECT] Enabled: {auto_detect_enabled}")

                if auto_detect_enabled:
                    # Load initial context on first run to avoid processing old messages
                    if not initial_context_loaded:
                        logger.info("🔍 [INITIAL SCAN] Loading initial context to mark existing messages...")
                        try:
                            if wechat_service.ocr_reader:
                                success = wechat_service.ocr_reader.load_initial_context()
                                if success:
                                    logger.info("✅ [INITIAL SCAN] Initial context loaded successfully")
                                    socketio.emit('log', {
                                        'type': 'success',
                                        'message': '✅ Initial context loaded - ready to detect new messages',
                                        'timestamp': time.time()
                                    })
                                else:
                                    logger.warning("⚠️ [INITIAL SCAN] Failed to load initial context")
                                    socketio.emit('log', {
                                        'type': 'warning',
                                        'message': '⚠️ Failed to load initial context',
                                        'timestamp': time.time()
                                    })
                            initial_context_loaded = True
                        except Exception as e:
                            logger.error(f"❌ [INITIAL SCAN] Error loading initial context: {e}")
                            initial_context_loaded = True  # Set to True anyway to avoid infinite retries

                    current_time = time.time()
                    # Run OCR every 1 second
                    if current_time - last_ocr_check >= 1.0:
                        last_ocr_check = current_time

                        # Check if cursor is in WeChat window before running OCR
                        cursor_in_wechat = wechat_service.is_cursor_in_wechat_window()

                        if not cursor_in_wechat:
                            if iteration_count % 10 == 0:  # Log every 10 seconds
                                logger.debug("[AUTO-DETECT] Skipping OCR - cursor not in WeChat window")
                            time.sleep(0.1)
                            continue

                        try:
                            logger.info("[AUTO-DETECT] Running Accessibility API scan...")
                            # Use Accessibility API instead of OCR (100% accurate!)
                            messages = wechat_service.read_messages_accessibility()

                            if messages:
                                # Deduplicate: only show new messages
                                last_message_texts = {msg.get('text', '') for msg in last_messages}
                                new_messages = [msg for msg in messages if msg.get('text', '') not in last_message_texts]

                                if new_messages:
                                    logger.info(f"🔔 {len(new_messages)} new message(s) detected!")

                                    # Emit log for new messages
                                    socketio.emit('log', {
                                        'type': 'info',
                                        'message': f'📨 {len(new_messages)} new message(s) detected',
                                        'timestamp': current_time
                                    })

                                    # Log all new messages to activity log
                                    for msg in new_messages:
                                        timestamp = msg.get('timestamp', 'Unknown time')
                                        text = msg.get('text', '')
                                        if text:  # Only emit non-empty messages
                                            socketio.emit('log', {
                                                'type': 'info',
                                                'message': f'💬 [{timestamp}] {text[:100]}{"..." if len(text) > 100 else ""}',
                                                'timestamp': current_time
                                            })

                                    # Only send the LAST (newest) message to chatbox for AI processing
                                    last_msg = new_messages[-1]
                                    last_timestamp = last_msg.get('timestamp', 'Unknown time')
                                    last_text = last_msg.get('text', '')

                                    if last_text:
                                        logger.info(f"📤 Sending last message to chatbox: {last_text[:50]}...")

                                        # Mark as user message to avoid echo
                                        if wechat_service.ocr_reader:
                                            wechat_service.ocr_reader.mark_as_user_message(last_text)

                                        socketio.emit('wechat_message', {
                                            'timestamp': last_timestamp,
                                            'text': last_text,
                                            'source': 'wechat'
                                        })

                                    # Update last_messages to current messages
                                    last_messages = messages
                                    logger.info(f"✅ Emitted 1 message to chatbox (out of {len(new_messages)} new)")
                                else:
                                    logger.debug("No new messages (all duplicates)")

                                # Always update last_messages even if no new ones
                                last_messages = messages
                            else:
                                logger.debug("OCR returned no messages")

                        except Exception as e:
                            logger.error(f"Error running OCR scan: {e}")
                            import traceback
                            logger.error(traceback.format_exc())
            else:
                if last_emitted_chat != "WeChat not running":
                    logger.warning("[MONITOR] WeChat is not running")

            # Use detected chat if available
            if detected_chat:
                current_chat = detected_chat
            else:
                current_chat = "No chat open (open a chat to detect)"

            # Emit if changed (this is the key - emit immediately on change)
            if current_chat != last_emitted_chat:
                socketio.emit('current_chat_update', {
                    'chat': current_chat,
                    'detected': detected_chat is not None,
                    'selected': selected_chat,
                    'timestamp': time.time()
                })

                # Emit log for activity feed
                if detected_chat:
                    socketio.emit('log', {
                        'type': 'success',
                        'message': f'✅ Chat detected: "{current_chat}"',
                        'timestamp': time.time()
                    })
                    logger.info(f"✅ CHAT CHANGE: {current_chat}")
                else:
                    logger.info(f"📭 NO CHAT: {current_chat}")

                last_emitted_chat = current_chat

            # High-frequency scanning: 100ms = 10 Hz
            time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error in chat detection loop: {e}")
            import traceback
            logger.error(traceback.format_exc())
            time.sleep(1)  # Wait longer on error


# Start background task for current chat updates
import threading
current_chat_thread = threading.Thread(target=emit_current_chat_updates, daemon=True)
current_chat_thread.start()


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', '5001'))
    debug = os.getenv('FLASK_ENV') == 'development'

    logger.info("=" * 60)
    logger.info("RealChat - Consolidated Flask Application")
    logger.info("=" * 60)
    logger.info(f"Port: {port}")
    logger.info(f"Debug: {debug}")
    logger.info(f"WeChat: {'Running' if wechat_service.is_wechat_running() else 'Not running'}")
    logger.info(f"AI Model: {ai_service.model}")
    logger.info("=" * 60)

    # Auto-start agent if configured
    if os.getenv('AGENT_AUTO_START', 'false').lower() == 'true':
        logger.info("Auto-starting agent...")
        agent_running = True
        agent_thread = threading.Thread(target=agent_worker, daemon=True)
        agent_thread.start()

    # Run Flask app with SocketIO
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
