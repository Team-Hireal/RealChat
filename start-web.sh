#!/bin/bash

echo "============================================"
echo "WeChat Auto-Reply Bot - Web Interface"
echo "============================================"
echo ""

# Check if we're in development or production mode
MODE="${1:-dev}"

if [ "$MODE" = "dev" ]; then
    echo "Starting in DEVELOPMENT mode..."
    echo ""
    echo "This will start two servers:"
    echo "  - Flask backend on http://localhost:5001"
    echo "  - React dev server on http://localhost:5173"
    echo ""
    echo "Open http://localhost:5173 in your browser"
    echo ""

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Virtual environment not found. Creating..."
        python3 -m venv venv
    fi

    # Activate virtual environment and start Flask
    source venv/bin/activate

    # Install dependencies if needed
    if ! python3 -c "import flask" 2>/dev/null; then
        echo "Installing Flask dependencies..."
        pip install -r requirements.txt
    fi

    # Start Flask in background
    echo "Starting Flask backend..."
    python3 app.py &
    FLASK_PID=$!

    # Wait a moment for Flask to start
    sleep 2

    # Start React dev server
    echo "Starting React dev server..."
    cd frontend
    npm run dev

    # Cleanup on exit
    kill $FLASK_PID

elif [ "$MODE" = "prod" ]; then
    echo "Starting in PRODUCTION mode..."
    echo ""

    # Build React app
    echo "Building React app..."
    cd frontend
    npm run build
    cd ..

    # Start Flask (which will serve the React build)
    echo "Starting Flask server..."
    echo "Open http://localhost:5001 in your browser"
    source venv/bin/activate
    python3 app.py

else
    echo "Usage: ./start-web.sh [dev|prod]"
    echo "  dev  - Development mode (Flask + React dev server)"
    echo "  prod - Production mode (Flask serves React build)"
    exit 1
fi

