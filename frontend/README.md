# WeChat Auto-Reply Bot - React Frontend

This is the modern React frontend for the WeChat Auto-Reply Bot, built with React 18 and Vite.

## Technology Stack

- **React 18** - Functional components with hooks
- **Vite** - Fast build tool and dev server
- **Axios** - HTTP client for API calls
- **Context API + useReducer** - State management
- **CSS Modules** - Component-scoped styling

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Header.jsx
│   │   ├── StatusBadge.jsx
│   │   ├── ControlPanel.jsx
│   │   ├── ConfigurationForm.jsx
│   │   ├── ActivityLogs.jsx
│   │   └── ContactTracking.jsx
│   ├── context/            # State management
│   │   ├── AppContext.jsx
│   │   └── AppReducer.js
│   ├── hooks/              # Custom hooks
│   │   ├── useApi.js
│   │   ├── usePolling.js
│   │   ├── useBotControl.js
│   │   └── useConfig.js
│   ├── services/           # API service layer
│   │   └── api.js
│   ├── App.jsx
│   └── main.jsx
├── package.json
├── vite.config.js
└── .env.development
```

## Development Setup

### Prerequisites

- Node.js 16+ and npm
- Python 3.x with Flask backend running

### Installation

```bash
cd frontend
npm install
```

### Running Development Server

The easiest way is to use the provided script from the parent directory:

```bash
cd ..
./start-web.sh dev
```

This will start both:
- Flask backend on http://localhost:5001
- React dev server on http://localhost:5173 (or 5174 if 5173 is busy)

Or manually:

```bash
# Terminal 1: Start Flask backend
cd /path/to/wemac
source venv/bin/activate
python3 app.py

# Terminal 2: Start React dev server
cd /path/to/wemac/frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

## Production Build

### Build the React App

```bash
cd frontend
npm run build
```

This creates an optimized production build in `frontend/dist/`.

### Run Production Server

```bash
cd ..
./start-web.sh prod
```

Or manually:

```bash
source venv/bin/activate
python3 app.py
```

The Flask server will automatically serve the React build from `frontend/dist/`.

Open http://localhost:5001 in your browser.

## Features

- **Real-time Status** - Bot status updates every 2 seconds via polling
- **Configuration Management** - Save and load bot configuration
- **Activity Logs** - Color-coded logs with auto-scrolling
- **Contact Tracking** - View list of replied contacts
- **Bot Control** - Start, stop, and refresh bot status
- **Responsive Design** - Works on desktop and mobile

## API Integration

The frontend communicates with the Flask backend via REST API:

- `GET /api/config` - Get configuration
- `POST /api/config` - Update configuration
- `GET /api/status` - Get bot status
- `GET /api/logs` - Get activity logs
- `GET /api/tracking` - Get replied contacts
- `POST /api/start` - Start the bot
- `POST /api/stop` - Stop the bot

## State Management

The app uses React Context API with useReducer for global state management:

- **botStatus** - Current bot running status
- **config** - Bot configuration
- **logs** - Activity logs
- **tracking** - Replied contacts
- **loading** - Loading states for various operations
- **error** - Error messages

## Custom Hooks

- **useApi** - Generic API call hook with loading/error states
- **usePolling** - Polling hook for real-time updates
- **useBotControl** - Bot control operations (start/stop/refresh)
- **useConfig** - Configuration management (load/save)

## Styling

The app maintains the original purple gradient theme with:
- Purple gradient background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- White card-based layout
- Color-coded logs (blue=info, green=success, red=error, yellow=warning)
- Responsive design with mobile breakpoints

## Troubleshooting

### Port Already in Use

If port 5173 is already in use, Vite will automatically try the next available port (5174, 5175, etc.).

### CORS Errors

Make sure Flask-CORS is installed and the Flask backend is running:

```bash
pip install flask-cors
```

### API Connection Issues

Check that:
1. Flask backend is running on port 5001
2. Vite proxy is configured correctly in `vite.config.js`
3. `.env.development` has the correct API URL

## License

Same as parent project.

