#!/bin/bash
set -e

# ============================================================
# RealChat — Production Startup
# Single command to build and launch all services
# ============================================================

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"
PID_FILE="$ROOT_DIR/.realchat.pids"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PIDS=()

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down RealChat...${NC}"
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null && wait "$pid" 2>/dev/null
        fi
    done
    rm -f "$PID_FILE"
    echo -e "${GREEN}All services stopped.${NC}"
    exit 0
}

trap cleanup INT TERM

fail() { echo -e "${RED}$1${NC}"; exit 1; }

mkdir -p "$LOG_DIR"

# ---- Prerequisites ----
echo -e "${CYAN}RealChat${NC} — checking prerequisites..."

[ -f "$ROOT_DIR/.env" ] || fail "No .env file found. Copy .env.example to .env and add your API key."
command -v node  >/dev/null 2>&1 || fail "Node.js is required. Install from https://nodejs.org"
command -v deno  >/dev/null 2>&1 || fail "Deno is required. Install from https://deno.land"
[ -d "$ROOT_DIR/venv" ]         || fail "Python venv not found. Run: python3 -m venv venv && ./venv/bin/pip install -r requirements_consolidated.txt"

PYTHON="$ROOT_DIR/venv/bin/python"
[ -x "$PYTHON" ] || fail "Python not found in venv."

echo -e "${GREEN}Prerequisites OK${NC}"

# ---- Build frontend (if needed) ----
FRONTEND_DIST="$ROOT_DIR/frontend/dist"
FRONTEND_SRC="$ROOT_DIR/frontend/src"

needs_build=false
if [ ! -d "$FRONTEND_DIST" ]; then
    needs_build=true
elif [ -n "$(find "$FRONTEND_SRC" -newer "$FRONTEND_DIST/index.html" -print -quit 2>/dev/null)" ]; then
    needs_build=true
fi

if $needs_build; then
    echo -e "${CYAN}Building frontend...${NC}"
    (cd "$ROOT_DIR/frontend" && npm install --silent && npm run build) \
        || fail "Frontend build failed."
    echo -e "${GREEN}Frontend built${NC}"
else
    echo -e "${GREEN}Frontend up to date${NC}"
fi

# ---- Install wechat-bridge deps if needed ----
if [ ! -d "$ROOT_DIR/wechat-bridge/node_modules" ]; then
    echo -e "${CYAN}Installing WeChat Bridge dependencies...${NC}"
    (cd "$ROOT_DIR/wechat-bridge" && npm install --silent) \
        || fail "WeChat Bridge npm install failed."
fi

# ---- Start services ----
echo ""
echo -e "${CYAN}Starting services...${NC}"

# 1) WeChat Bridge (port 8080/8081)
echo -n "  WeChat Bridge ... "
(cd "$ROOT_DIR/wechat-bridge" && node index.js) \
    >> "$LOG_DIR/bridge.log" 2>&1 &
PIDS+=($!)
echo "$!" >> "$PID_FILE"
echo -e "${GREEN}started${NC}  (log: logs/bridge.log)"

# 2) Zypher Agent (port 8000)
echo -n "  Zypher Agent  ... "
(cd "$ROOT_DIR/zypher-agent" && deno task start) \
    >> "$LOG_DIR/zypher.log" 2>&1 &
PIDS+=($!)
echo "$!" >> "$PID_FILE"
echo -e "${GREEN}started${NC}  (log: logs/zypher.log)"

# 3) Flask Backend (port 5001) — started last, runs in foreground
echo -n "  Flask Backend  ... "
"$PYTHON" "$ROOT_DIR/app_consolidated.py" \
    >> "$LOG_DIR/flask.log" 2>&1 &
PIDS+=($!)
echo "$!" >> "$PID_FILE"
echo -e "${GREEN}started${NC}  (log: logs/flask.log)"

# ---- Health checks ----
echo ""
echo -n "Waiting for services"
for i in $(seq 1 10); do
    sleep 1
    echo -n "."
done
echo ""

echo ""
echo -e "${CYAN}Service health:${NC}"

check_port() {
    lsof -ti :"$1" >/dev/null 2>&1
}

if check_port 5001; then
    echo -e "  Flask Backend  :5001  ${GREEN}UP${NC}"
else
    echo -e "  Flask Backend  :5001  ${RED}DOWN${NC} — check logs/flask.log"
fi

if check_port 8000; then
    echo -e "  Zypher Agent   :8000  ${GREEN}UP${NC}"
else
    echo -e "  Zypher Agent   :8000  ${RED}DOWN${NC} — check logs/zypher.log"
fi

if check_port 8080; then
    echo -e "  WeChat Bridge  :8080  ${GREEN}UP${NC}"
else
    echo -e "  WeChat Bridge  :8080  ${YELLOW}WAITING${NC} — may need QR scan (check logs/bridge.log)"
fi

# ---- Ready ----
echo ""
echo -e "${GREEN}RealChat is running.${NC}"
echo ""
echo "  Web UI:        http://localhost:5001"
echo "  API:           http://localhost:5001/api/status"
echo "  Zypher Agent:  http://localhost:8000"
echo "  Bridge status: http://localhost:8081/status"
echo ""
echo "  Ctrl+C to stop all services."
echo ""

# Open browser
if command -v open >/dev/null 2>&1; then
    open "http://localhost:5001" 2>/dev/null || true
fi

# Keep alive — wait for any child to exit
wait
