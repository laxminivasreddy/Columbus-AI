// Environment-specific configuration
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

const CONFIG = {
    // When deploying to Render, replace the below URL with your Render URL
    // e.g., 'https://columbus-ai-backend.onrender.com'
    API_BASE_URL: isLocal ? 'http://127.0.0.1:8000' : 'https://YOUR_RENDER_APP_URL.onrender.com',
    
    // When deploying to Render, replace the below URL with your Render WebSocket URL
    // e.g., 'wss://columbus-ai-backend.onrender.com'
    WS_BASE_URL: isLocal ? 'ws://127.0.0.1:8000' : 'wss://YOUR_RENDER_APP_URL.onrender.com'
};
