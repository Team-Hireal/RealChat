#!/usr/bin/env python3
"""
WeChat Auto-Reply Bot - Web Interface
A simple Flask web app for managing the WeChat auto-reply bot
Supports both desktop app automation and WeChat Web
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import subprocess
import os
import json
import threading
import time
from pathlib import Path

# Import WeChat Web automation
try:
    from wechat_web import wechat_web
    WECHAT_WEB_AVAILABLE = True
except ImportError:
    WECHAT_WEB_AVAILABLE = False
    print("Warning: WeChat Web automation not available. Install selenium and webdriver-manager.")

# Import WeChat Service
try:
    from services.wechat_service import WeChatService
    WECHAT_SERVICE_AVAILABLE = True
except ImportError:
    WECHAT_SERVICE_AVAILABLE = False
    print("Warning: WeChat Service not available.")

app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration file path
CONFIG_FILE = Path.home() / '.wechat_autoreply_config'
TRACKING_FILE = Path.home() / '.wechat_autoreply_tracking'
AI_SETTINGS_FILE = Path.home() / '.wechat_ai_settings.json'

# Global state
bot_process = None
bot_running = False
bot_logs = []
MAX_LOGS = 100
automation_method = 'desktop'  # 'desktop' or 'web'
web_browser_started = False
current_chat_monitor_thread = None
current_chat_monitor_running = False

# Initialize WeChat Service
wechat_service = None
if WECHAT_SERVICE_AVAILABLE:
    wechat_config = {
        'chat_names': ['File Transfer', '文件传输助手'],
        'scan_method': 'applescript'
    }
    wechat_service = WeChatService(wechat_config)


def load_config():
    """Load configuration from file"""
    if not CONFIG_FILE.exists():
        return {
            'chat_name': '',
            'user_name': '',
            'user_title': '',
            'intro_template': "Hi! I'm {{NAME}}, {{TITLE}}. It was great meeting you! Let's stay in touch.",
            'default_reply': 'Thanks for your message!',
            'reply_mode': 'c',
            'dry_run': 'yes'
        }

    config = {}
    with open(CONFIG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                config[key] = value
    return config


def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")


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

            # Migrate old format to new unified format
            if 'claude_api_key' in settings:
                # Old format detected, migrate to new format
                return {
                    'api_key': settings.get('claude_api_key', ''),
                    'base_url': settings.get('claude_base_url', 'https://api.anthropic.com'),
                    'model': settings.get('claude_model', 'claude-sonnet-4-5-20250929')
                }

            # New unified format
            if 'api_key' not in settings:
                settings['api_key'] = ''
            if 'base_url' not in settings:
                settings['base_url'] = 'https://api.anthropic.com'
            if 'model' not in settings:
                settings['model'] = 'claude-sonnet-4-5-20250929'

            return settings
    except Exception as e:
        print(f"Error loading AI settings: {e}")
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
        print(f"Error saving AI settings: {e}")
        return False



def add_log(message, level='info'):
    """Add a log message"""
    global bot_logs
    timestamp = time.strftime('%H:%M:%S')
    bot_logs.append({
        'timestamp': timestamp,
        'level': level,
        'message': message
    })
    # Keep only last MAX_LOGS messages
    if len(bot_logs) > MAX_LOGS:
        bot_logs = bot_logs[-MAX_LOGS:]


def get_current_chat():
    """Get the currently active chat name from WeChat using AppleScript"""
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'get_current_chat.applescript')
        result = subprocess.run(
            ['osascript', script_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return {'success': False, 'error': result.stderr or 'Unknown error'}

        # Parse JSON output
        try:
            output = json.loads(result.stdout.strip())
            return output
        except json.JSONDecodeError as e:
            return {'success': False, 'error': f'Invalid JSON: {str(e)}'}

    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def monitor_current_chat():
    """Background thread to monitor the current chat and emit updates via Socket.IO"""
    global current_chat_monitor_running
    last_chat = None
    last_cursor_in_wechat = False
    error_count = 0
    max_errors = 5

    print("🔍 Starting current chat monitor with cursor-triggered updates...")

    while current_chat_monitor_running:
        try:
            # Check if cursor is in WeChat window
            cursor_in_wechat = False
            if wechat_service:
                try:
                    window_under_cursor = wechat_service.get_window_under_cursor()
                    cursor_in_wechat = window_under_cursor and window_under_cursor.get('process_name') == 'WeChat'
                except:
                    pass

            # Trigger immediate update if cursor just entered WeChat window
            cursor_just_entered = cursor_in_wechat and not last_cursor_in_wechat

            if cursor_just_entered:
                print("🖱️  Cursor entered WeChat - triggering immediate chat update")

            # Get current chat
            result = get_current_chat()

            if result.get('success'):
                chat_name = result.get('chat', 'No active chat')
                detected = result.get('detected', False)

                # Emit if chat changed OR cursor just entered WeChat
                if chat_name != last_chat or cursor_just_entered:
                    last_chat = chat_name
                    data = {
                        'chat': chat_name,
                        'detected': detected
                    }

                    # Use app context for background thread emit
                    with app.app_context():
                        socketio.emit('current_chat_update', data)
                        print(f"📤 Emitted chat update: {data}")

                # Reset error count on success
                error_count = 0
            else:
                error_count += 1
                print(f"⚠️  Error getting chat (attempt {error_count}/{max_errors}): {result.get('error')}")
                if error_count >= max_errors:
                    # Emit error state after multiple failures
                    with app.app_context():
                        socketio.emit('current_chat_update', {
                            'chat': 'No active chat',
                            'detected': False
                        })
                    last_chat = None
                    error_count = 0  # Reset to try again

            # Update cursor state
            last_cursor_in_wechat = cursor_in_wechat

        except Exception as e:
            print(f"❌ Error in chat monitor: {e}")
            error_count += 1

        # Wait before next check
        # Use shorter interval (0.2s) when cursor is in WeChat for responsiveness
        # Use longer interval (1s) when cursor is outside WeChat to reduce CPU usage
        if cursor_in_wechat:
            time.sleep(0.2)
        else:
            time.sleep(1.0)

    print("🛑 Current chat monitor stopped")


def start_chat_monitor():
    """Start the background thread to monitor current chat"""
    global current_chat_monitor_thread, current_chat_monitor_running

    if current_chat_monitor_running:
        return

    current_chat_monitor_running = True
    current_chat_monitor_thread = threading.Thread(target=monitor_current_chat, daemon=True)
    current_chat_monitor_thread.start()
    print("✅ Current chat monitor started")


@app.route('/')
def index():
    """Main page - serve React app if built, otherwise fallback to template"""
    react_build = Path('frontend/dist/index.html')
    if react_build.exists():
        return send_from_directory('frontend/dist', 'index.html')
    return render_template('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    config = load_config()
    return jsonify(config)


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        config = request.json
        save_config(config)
        add_log('Configuration updated', 'success')
        return jsonify({'success': True})
    except Exception as e:
        add_log(f'Failed to update config: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get bot status"""
    global bot_running, bot_process

    # Check if WeChat is running
    wechat_running = False
    if wechat_service:
        wechat_running = wechat_service.is_wechat_running()

    return jsonify({
        'running': bot_running,
        'agent_running': bot_running,
        'wechat_running': wechat_running,
        'pid': bot_process.pid if bot_process else None
    })


@app.route('/api/wechat/window', methods=['GET'])
def get_wechat_window():
    """Get WeChat window information"""
    if not wechat_service:
        return jsonify({
            'success': False,
            'error': 'WeChat service not available'
        }), 503

    try:
        window_info = wechat_service.get_wechat_window_info()
        cursor_pos = wechat_service.get_cursor_position()
        window_under_cursor = wechat_service.get_window_under_cursor()
        is_focused = wechat_service.verify_wechat_active_and_focused()

        if window_info:
            return jsonify({
                'success': True,
                'window': window_info,
                'cursor': cursor_pos,
                'window_under_cursor': window_under_cursor,
                'is_running': True,
                'is_focused': is_focused,
                'cursor_in_window': window_under_cursor and window_under_cursor.get('process_name') == 'WeChat'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'WeChat window not found',
                'is_running': wechat_service.is_wechat_running()
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get recent logs"""
    return jsonify(bot_logs)


@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the bot"""
    global bot_process, bot_running

    if bot_running:
        return jsonify({'success': False, 'error': 'Bot is already running'}), 400

    try:
        add_log('Starting bot...', 'info')

        # Run the bot script
        bot_process = subprocess.Popen(
            ['./run.sh'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        bot_running = True

        # Start a thread to read output
        def read_output():
            global bot_running
            try:
                for line in bot_process.stdout:
                    line = line.strip()
                    if line:
                        # Determine log level based on content
                        level = 'info'
                        if 'ERROR' in line or 'error' in line:
                            level = 'error'
                        elif 'SUCCESS' in line or '✓' in line:
                            level = 'success'
                        elif 'WARNING' in line:
                            level = 'warning'
                        add_log(line, level)
                bot_process.wait()
            except Exception as e:
                add_log(f'Error reading output: {str(e)}', 'error')
            finally:
                bot_running = False
                add_log('Bot stopped', 'info')

        thread = threading.Thread(target=read_output, daemon=True)
        thread.start()

        return jsonify({'success': True})
    except Exception as e:
        bot_running = False
        add_log(f'Failed to start bot: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the bot"""
    global bot_process, bot_running

    if not bot_running:
        return jsonify({'success': False, 'error': 'Bot is not running'}), 400

    try:
        if bot_process:
            bot_process.terminate()
            bot_process.wait(timeout=5)
        bot_running = False
        add_log('Bot stopped by user', 'info')
        return jsonify({'success': True})
    except Exception as e:
        add_log(f'Failed to stop bot: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tracking', methods=['GET'])
def get_tracking():
    """Get tracking data (who we've replied to)"""
    if not TRACKING_FILE.exists():
        return jsonify([])

    tracking = []
    with open(TRACKING_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                tracking.append(line)
    return jsonify(tracking)


# ============================================================================
# WeChat Web Automation Endpoints
# ============================================================================

@app.route('/api/method', methods=['GET'])
def get_method():
    """Get current automation method"""
    global automation_method
    return jsonify({
        'method': automation_method,
        'web_available': WECHAT_WEB_AVAILABLE,
        'web_browser_started': web_browser_started
    })


@app.route('/api/method', methods=['POST'])
def set_method():
    """Set automation method (desktop or web)"""
    global automation_method
    try:
        data = request.json
        method = data.get('method', 'desktop')

        if method not in ['desktop', 'web']:
            return jsonify({'success': False, 'error': 'Invalid method'}), 400

        if method == 'web' and not WECHAT_WEB_AVAILABLE:
            return jsonify({'success': False, 'error': 'WeChat Web not available'}), 400

        automation_method = method
        add_log(f'Automation method set to: {method}', 'info')
        return jsonify({'success': True, 'method': method})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/web/start', methods=['POST'])
def start_web_browser():
    """Start WeChat Web browser"""
    global web_browser_started

    if not WECHAT_WEB_AVAILABLE:
        return jsonify({'success': False, 'error': 'WeChat Web not available'}), 400

    if web_browser_started:
        return jsonify({'success': False, 'error': 'Browser already started'}), 400

    try:
        add_log('Starting WeChat Web browser...', 'info')
        success = wechat_web.start_browser()

        if success:
            web_browser_started = True
            add_log('✓ Browser started. Please scan QR code to log in.', 'success')

            # Start login check in background
            def check_login():
                if wechat_web.wait_for_login(timeout=120):
                    add_log('✓ Successfully logged in to WeChat Web', 'success')
                else:
                    add_log('Login timeout or failed', 'error')
                    global web_browser_started
                    web_browser_started = False

            thread = threading.Thread(target=check_login, daemon=True)
            thread.start()

            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to start browser'}), 500

    except Exception as e:
        add_log(f'Failed to start browser: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/web/status', methods=['GET'])
def get_web_status():
    """Get WeChat Web login status"""
    if not WECHAT_WEB_AVAILABLE:
        return jsonify({'available': False, 'logged_in': False})

    return jsonify({
        'available': True,
        'browser_started': web_browser_started,
        'logged_in': wechat_web.logged_in if web_browser_started else False
    })


@app.route('/api/web/send', methods=['POST'])
def send_web_message():
    """Send message via WeChat Web"""
    if not WECHAT_WEB_AVAILABLE or not web_browser_started:
        return jsonify({'success': False, 'error': 'WeChat Web not available'}), 400

    try:
        data = request.json
        chat_name = data.get('chat_name')
        message = data.get('message')

        if not chat_name or not message:
            return jsonify({'success': False, 'error': 'Missing chat_name or message'}), 400

        # Find chat
        if not wechat_web.find_chat(chat_name):
            return jsonify({'success': False, 'error': f'Chat not found: {chat_name}'}), 404

        # Send message
        if wechat_web.send_message(message):
            add_log(f'✓ Message sent to {chat_name}', 'success')
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to send message'}), 500

    except Exception as e:
        add_log(f'Failed to send message: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/check-accessibility', methods=['GET'])
def check_accessibility():
    """Check if accessibility permissions are granted"""
    try:
        result = subprocess.run(
            ['./check_accessibility.sh'],
            capture_output=True,
            text=True,
            timeout=10
        )

        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/scan-chats', methods=['GET'])
def scan_chats():
    """Scan available WeChat chats"""
    try:
        # Get max_chats parameter (default 10)
        max_chats = request.args.get('max_chats', '10')

        add_log('Scanning available chats...', 'info')

        # Run the scan_chats.applescript
        script_path = os.path.join(os.path.dirname(__file__), 'scan_chats.applescript')
        result = subprocess.run(
            ['osascript', script_path, max_chats],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            error_msg = result.stderr or 'Unknown error'
            add_log(f'Failed to scan chats: {error_msg}', 'error')
            return jsonify({'success': False, 'error': error_msg}), 500

        # Parse JSON output
        try:
            # Clean up the output - remove any literal newlines in strings
            cleaned_output = result.stdout.strip().replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            output = json.loads(cleaned_output)
            if 'error' in output:
                add_log(f'Chat scan error: {output["error"]}', 'error')
                return jsonify({'success': False, 'error': output['error']}), 500

            chats = output.get('chats', [])
            # Clean up chat names - remove escaped characters
            chats = [chat.replace('\\n', ' ').replace('\\r', '').replace('\\t', ' ').strip() for chat in chats]
            add_log(f'Found {len(chats)} chat(s)', 'success')
            return jsonify({'success': True, 'chats': chats})

        except json.JSONDecodeError as e:
            add_log(f'Failed to parse chat scan output: {str(e)}', 'error')
            return jsonify({'success': False, 'error': 'Invalid JSON response'}), 500

    except subprocess.TimeoutExpired:
        add_log('Chat scan timed out', 'error')
        return jsonify({'success': False, 'error': 'Scan timed out'}), 500

    except Exception as e:
        add_log(f'Failed to scan chats: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/send-test-message', methods=['POST'])
def send_test_message():
    """Send a test message to the currently open chat"""
    try:
        data = request.json
        message = data.get('message', 'Test message from automation')

        add_log(f'Sending test message: {message}', 'info')

        # Run the send_test_message.applescript
        script_path = os.path.join(os.path.dirname(__file__), 'send_test_message.applescript')
        result = subprocess.run(
            ['osascript', script_path, message],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            error_msg = result.stderr or 'Unknown error'
            add_log(f'Failed to send message: {error_msg}', 'error')
            return jsonify({'success': False, 'error': error_msg}), 500

        # Parse JSON output
        try:
            output = json.loads(result.stdout.strip())
            if output.get('success'):
                add_log('✓ Test message sent successfully', 'success')
                return jsonify({'success': True})
            else:
                error = output.get('error', 'Unknown error')
                add_log(f'Failed to send message: {error}', 'error')
                return jsonify({'success': False, 'error': error}), 500

        except json.JSONDecodeError as e:
            add_log(f'Failed to parse send message output: {str(e)}', 'error')
            return jsonify({'success': False, 'error': 'Invalid JSON response'}), 500

    except subprocess.TimeoutExpired:
        add_log('Send message timed out', 'error')
        return jsonify({'success': False, 'error': 'Send timed out'}), 500

    except Exception as e:
        add_log(f'Failed to send message: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# AI Agent Settings Endpoints
# ============================================================================

@app.route('/api/ai/config', methods=['GET'])
def get_ai_config():
    """Get AI agent configuration"""
    try:
        # Proxy request to agent orchestrator
        import requests
        response = requests.get('http://localhost:8082/api/config', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/config', methods=['POST'])
def update_ai_config():
    """Update AI agent configuration"""
    try:
        import requests
        data = request.json
        response = requests.post(
            'http://localhost:8082/api/config',
            json=data,
            timeout=5
        )
        add_log('AI configuration updated', 'success')
        return jsonify(response.json())
    except Exception as e:
        add_log(f'Failed to update AI config: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/provider', methods=['GET'])
def get_ai_provider():
    """Get current AI provider status"""
    try:
        import requests
        response = requests.get('http://localhost:8082/api/provider', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/provider', methods=['POST'])
def set_ai_provider():
    """Set active AI provider"""
    try:
        import requests
        data = request.json
        response = requests.post(
            'http://localhost:8082/api/provider',
            json=data,
            timeout=5
        )
        add_log(f'AI provider changed to: {data.get("provider")}', 'success')
        return jsonify(response.json())
    except Exception as e:
        add_log(f'Failed to change AI provider: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """Chat with Claude or Zypher AI"""
    try:
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'claude')
        history = data.get('history', [])

        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        # Load AI settings (unified format)
        ai_settings = load_ai_settings()

        # Check if API key is configured
        if not ai_settings.get('api_key'):
            return jsonify({
                'success': False,
                'error': 'Please configure API key in settings'
            }), 400

        # Try to use actual API if anthropic is available
        try:
            from anthropic import Anthropic

            client = Anthropic(
                api_key=ai_settings['api_key'],
                base_url=ai_settings.get('base_url', 'https://api.anthropic.com')
            )

            # Convert history to Claude format
            messages = []
            for msg in history:
                if msg.get('role') in ['user', 'assistant']:
                    messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })

            # Add current message
            messages.append({
                'role': 'user',
                'content': message
            })

            # Call Claude API with configured model
            model_name = ai_settings.get('model', 'claude-sonnet-4-5-20250929')
            response = client.messages.create(
                model=model_name,
                max_tokens=2048,
                messages=messages
            )

            response_text = response.content[0].text
            add_log(f'AI responded to: {message[:50]}...', 'success')

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
            add_log(f'AI API error: {str(api_error)}', 'error')
            return jsonify({
                'success': False,
                'error': f'API error: {str(api_error)}'
            }), 500

    except Exception as e:
        add_log(f'Chat error: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


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
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai-settings', methods=['POST'])
def update_ai_settings():
    """Update AI settings"""
    try:
        settings = request.json

        # Validate settings - use unified format
        required_fields = ['api_key', 'base_url', 'model']
        for field in required_fields:
            if field not in settings:
                settings[field] = ''

        # Save settings
        if save_ai_settings(settings):
            add_log('AI settings updated', 'success')
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to save settings'}), 500

    except Exception as e:
        add_log(f'Failed to update AI settings: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/backend/config', methods=['GET'])
def get_backend_config():
    """Get backend configuration"""
    try:
        config = load_config()
        return jsonify({
            'success': True,
            'config': {
                'ai_model': config.get('ai_model', 'claude-sonnet-4-5-20250929'),
                'scan_method': config.get('scan_method', 'applescript'),
                'ai_max_tokens': int(config.get('ai_max_tokens', 1024))
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/backend/config', methods=['POST'])
def update_backend_config():
    """Update backend configuration"""
    try:
        data = request.json
        config = load_config()

        # Update config with new values
        if 'ai_model' in data:
            config['ai_model'] = data['ai_model']
        if 'scan_method' in data:
            config['scan_method'] = data['scan_method']
        if 'ai_max_tokens' in data:
            config['ai_max_tokens'] = str(data['ai_max_tokens'])

        save_config(config)
        add_log('Backend config updated', 'success')
        return jsonify({'success': True})
    except Exception as e:
        add_log(f'Failed to update backend config: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/wechat/chats/search', methods=['GET'])
def search_chats():
    """Search for chats by name"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'error': 'Query parameter required'}), 400

        # Try to use the scan_chats endpoint to get all chats, then filter
        try:
            result = subprocess.run(
                ['osascript', 'scripts/scan_chats.applescript'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    if data.get('success'):
                        chats = data.get('chats', [])
                        # Filter chats by query
                        filtered = [chat for chat in chats if query.lower() in chat.get('name', '').lower()]
                        return jsonify({
                            'success': True,
                            'results': filtered,
                            'count': len(filtered)
                        })
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

        # If script fails, return a simple match based on query
        # This allows the UI to continue working even if we can't scan chats
        return jsonify({
            'success': True,
            'results': [{'name': query, 'type': 'chat'}],
            'count': 1
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/wechat/send', methods=['POST'])
def send_wechat_message():
    """Send a message to WeChat"""
    try:
        data = request.json
        chat_name = data.get('chat_name', '')
        message = data.get('message', '')

        if not chat_name or not message:
            return jsonify({'success': False, 'error': 'chat_name and message required'}), 400

        # Use the send_test_message script
        result = subprocess.run(
            ['osascript', 'scripts/send_message.applescript', chat_name, message],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            try:
                response_data = json.loads(result.stdout)
                if response_data.get('success'):
                    add_log(f'Message sent to {chat_name}', 'success')
                    socketio.emit('message_sent', {'chat': chat_name, 'message': message})
                    return jsonify({'success': True})
            except json.JSONDecodeError:
                pass

        add_log(f'Failed to send message to {chat_name}', 'error')
        return jsonify({'success': False, 'error': 'Failed to send message'}), 500
    except Exception as e:
        add_log(f'Error sending message: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/wechat/read', methods=['GET'])
def read_wechat_messages():
    """Read messages from WeChat"""
    try:
        chat_name = request.args.get('chat_name', '')
        structured = request.args.get('structured', 'false').lower() == 'true'

        if not chat_name:
            return jsonify({'success': False, 'error': 'chat_name parameter required'}), 400

        # Use get_chat_messages script
        result = subprocess.run(
            ['osascript', 'scripts/get_chat_messages.applescript'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if data.get('success'):
                    add_log(f'Read {data.get("count", 0)} messages from {chat_name}', 'info')
                    return jsonify({
                        'success': True,
                        'messages': data.get('messages', []),
                        'count': data.get('count', 0)
                    })
            except json.JSONDecodeError:
                pass

        return jsonify({'success': False, 'error': 'Failed to read messages'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Socket.IO Event Handlers
# ============================================================================

@socketio.on('connect')
def handle_connect_and_start_monitor():
    """Handle client connection and ensure monitor is running"""
    global current_chat_monitor_running

    print('🔌 Client connected to Socket.IO')

    # Start monitor if not already running
    if not current_chat_monitor_running:
        start_chat_monitor()

    # Send initial chat state
    result = get_current_chat()
    if result.get('success'):
        data = {
            'chat': result.get('chat', 'No active chat'),
            'detected': result.get('detected', False)
        }
        emit('current_chat_update', data)
        print(f'📤 Sent initial state to client: {data}')
    else:
        data = {
            'chat': 'No active chat',
            'detected': False
        }
        emit('current_chat_update', data)
        print(f'📤 Sent error state to client: {data}')


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('🔌 Client disconnected from Socket.IO')


if __name__ == '__main__':
    add_log('Web interface started', 'success')

    print('=' * 50)
    print('WeChat Auto-Reply Bot - Web Interface')
    print('=' * 50)
    print('')
    print('Open your browser and go to:')
    print('  http://localhost:5001')
    print('')
    print('Press Ctrl+C to stop the server')
    print('=' * 50)

    # Use socketio.run instead of app.run
    socketio.run(app, debug=True, host='127.0.0.1', port=5001, allow_unsafe_werkzeug=True)
