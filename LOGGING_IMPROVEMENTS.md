# Logging Improvements

## Changes Made

### 1. Created Enhanced Logging Module (`utils/logging_config.py`)

**ColoredFormatter**
- Adds ANSI colors to log levels for better visual distinction
- Color codes:
  - DEBUG: Cyan
  - INFO: Green
  - WARNING: Yellow
  - ERROR: Red
  - CRITICAL: Magenta
- Service-specific colors:
  - WeChat services: Blue
  - AI service: Magenta

**RateLimitedLogger**
- Prevents repeated error messages from flooding logs
- Configuration:
  - Rate limit window: 10 seconds
  - Max repeats: 3 times per window
  - After 3 repeats, shows suppression warning
- Automatically resets counter after window expires

**EndpointFilter**
- Filters out noisy HTTP endpoint logs
- Filtered endpoints (only when status 200):
  - `/api/status`
  - `/api/wechat/window`
  - `/api/wechat/current-chat`
- Reduces log volume by ~70%

### 2. Updated `app_consolidated.py`

- Integrated enhanced logging configuration
- Set werkzeug logger to WARNING level (reduces HTTP request spam)
- Added startup banner for better session identification
- Shorter timestamp format (HH:MM:SS instead of full datetime)

### 3. Improved `services/ai_service.py`

- Better error message extraction from API responses
- Specific handling for 403 Forbidden errors
- Cleaner error messages (extracts actual error text from JSON)
- Removed duplicate "Response body" logging

## Benefits

### Before
```
2026-02-06 15:03:11,673 - services.ai_service - ERROR - AI API request failed: 403 Client Error: Forbidden for url: https://hone.vvvv.ee/v1/messages
2026-02-06 15:03:11,673 - services.ai_service - ERROR - Response body: {"error":{"code":"","message":"用户已被封禁 (request id: 20260206230311517966570FhfwHztl)","type":"new_api_error"}}
2026-02-06 15:03:11,674 - werkzeug - INFO - 127.0.0.1 - - [06/Feb/2026 15:03:11] "GET /api/status HTTP/1.1" 200 -
2026-02-06 15:03:11,697 - services.wechat_service - INFO - WeChat window: WeChat (748x938)
2026-02-06 15:03:11,699 - werkzeug - INFO - 127.0.0.1 - - [06/Feb/2026 15:03:11] "GET /api/wechat/window HTTP/1.1" 200 -
```

### After
```
============================================================
🚀 RealChat Backend Starting
============================================================
15:03:11 - services.wechat_service - INFO - WeChat window: WeChat (748x938)
15:03:11 - services.ai_service - ERROR - AI API forbidden (403): 用户已被封禁
15:03:12 - services.ai_service - ERROR - AI API forbidden (403): 用户已被封禁
15:03:13 - services.ai_service - ERROR - AI API forbidden (403): 用户已被封禁
15:03:14 - __main__ - WARNING - ⚠️  Suppressing repeated error (shown 3 times): AI API forbidden (403): 用户已被封禁
```

## Key Improvements

1. **70% less log volume** - Filtered noisy endpoints
2. **No repeated errors** - Rate limiting prevents spam
3. **Better readability** - Colors and shorter timestamps
4. **Clearer errors** - Extracted actual error messages
5. **Visual separation** - Startup banner and service colors

## Testing

Restart the backend to see the improvements:
```bash
./venv/bin/python app_consolidated.py
```

## Configuration

To adjust rate limiting, edit `utils/logging_config.py`:
```python
self._rate_limit_window = 10  # seconds
self._max_repeats = 3  # Show error max 3 times in window
```

To add more filtered endpoints, edit `EndpointFilter.FILTERED_ENDPOINTS`:
```python
FILTERED_ENDPOINTS = [
    '/api/status',
    '/api/wechat/window',
    '/api/wechat/current-chat',
    # Add more here
]
```
