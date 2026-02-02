#!/usr/bin/env python3
"""
RealChat - Consolidated Flask Application
Single monorepo deployment with all services integrated
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import logging
import threading
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import services
from services.wechat_service import WeChatService
from services.ai_service import AIService
from modules.command_parser import CommandParser, CommandExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize services
wechat_config = {
    'chat_names': os.getenv('WECHAT_CHAT_NAMES', 'File Transfer,文件传输助手').split(','),
    'scan_method': os.getenv('WECHAT_SCAN_METHOD', 'applescript')
}
wechat_service = WeChatService(wechat_config)

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
DEFAULT_COMMAND_CHAT = "File Transfer"  # Default chat for commands


# ============================================================================
# Web Routes
# ============================================================================

@app.route('/')
def index():
    """Serve web client"""
    # Try enhanced client first
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
        chats = wechat_service.scan_chats(max_chats)
        return jsonify({
            "success": True,
            "chats": chats,
            "count": len(chats),
            "method": wechat_service.scan_method
        })
    except Exception as e:
        logger.error(f"Error scanning chats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/wechat/send', methods=['POST'])
def send_message():
    """Send message to WeChat"""
    try:
        data = request.json
        message = data.get('message')
        chat_name = data.get('chat_name')

        if not message:
            return jsonify({"success": False, "error": "Message is required"}), 400

        success = wechat_service.send_message(message, chat_name)

        return jsonify({
            "success": success,
            "message": "Message sent" if success else "Failed to send message"
        })
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/wechat/read', methods=['GET'])
def read_messages():
    """Read messages from WeChat"""
    try:
        chat_name = request.args.get('chat_name')
        content = wechat_service.read_last_message(chat_name)

        return jsonify({
            "success": True,
            "content": content,
            "length": len(content) if content else 0
        })
    except Exception as e:
        logger.error(f"Error reading messages: {e}")
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

    # Default to File Transfer for commands, unless user specified a chat
    command_chat = DEFAULT_COMMAND_CHAT
    target_chat = selected_chat if selected_chat else command_chat

    # Send startup message - ONLY ONE MESSAGE to File Transfer
    startup_msg = f"RealChat Agent | {time.strftime('%H:%M:%S')} | Test: OK"

    wechat_service.send_message(startup_msg, command_chat)
    last_message = startup_msg

    # Update command executor with current chat
    if command_executor:
        command_executor.set_current_chat(selected_chat)

    monitor_interval = int(os.getenv('AGENT_MONITOR_INTERVAL', '3'))

    while agent_running:
        try:
            # Always monitor File Transfer for commands
            command_content = wechat_service.read_last_message(command_chat)

            if command_content:
                lines = [l.strip() for l in command_content.split('\n') if l.strip()]
                if lines:
                    latest_command = lines[-1]

                    # Check if new message (not from us)
                    if latest_command != last_message and "RealChat" not in latest_command and "🤖" not in latest_command:
                        logger.info(f"File Transfer message: {latest_command[:50]}...")

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
                target_content = wechat_service.read_last_message(selected_chat)

                if target_content:
                    lines = [l.strip() for l in target_content.split('\n') if l.strip()]
                    if lines:
                        latest_msg = lines[-1]

                        # Check if new message (not from us)
                        if latest_msg != last_message and "RealChat" not in latest_msg and "🤖" not in latest_msg:
                            logger.info(f"New message in {selected_chat}: {latest_msg[:50]}...")
                            socketio.emit('new_message', {
                                'message': latest_msg,
                                'chat': selected_chat
                            })

                            # Get AI response
                            ai_response = ai_service.get_chat_response(latest_msg)

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
                                    socketio.emit('message_sent', {
                                        'message': ai_response,
                                        'chat': selected_chat
                                    })
                                else:
                                    logger.error("Failed to send response")
                                    socketio.emit('error', {'error': 'Failed to send message'})

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
