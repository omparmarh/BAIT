import React, { useState, useEffect } from 'react';
import './IntegrationPanel.css';

/**
 * BAIT PRO ULTIMATE - Integration Panel Component
 * - API integration status display
 * - Spotify music controls
 * - Gmail notifications
 * - Weather display
 * - Integration management
 */

const IntegrationPanel = () => {
    const [integrations, setIntegrations] = useState({
        spotify: { status: 'disconnected', data: null },
        gmail: { status: 'disconnected', data: null },
        weather: { status: 'disconnected', data: null }
    });
    const [selectedIntegration, setSelectedIntegration] = useState(null);

    useEffect(() => {
        checkIntegrations();
    }, []);

    const checkIntegrations = async () => {
        try {
            const response = await fetch('/api/ultimate/health');
            if (response.ok) {
                const data = await response.json();
                // Update integration statuses based on available modules
                console.log('Health check:', data);
            }
        } catch (error) {
            console.error('Health check failed:', error);
        }
    };

    const getStatusColor = (status) => {
        return status === 'connected' ? '#2ecc71' : '#95a5a6';
    };

    const getStatusIcon = (status) => {
        return status === 'connected' ? '✓' : '○';
    };

    return (
        <div className="integration-panel">
            <div className="integration-header">
                <h3>🔌 API Integrations</h3>
                <button onClick={checkIntegrations} className="refresh-integrations">
                    🔄 Refresh
                </button>
            </div>

            {/* Integration Cards */}
            <div className="integration-grid">
                {/* Spotify */}
                <div className="integration-card spotify">
                    <div className="card-header">
                        <div className="integration-icon">🎵</div>
                        <div className="integration-name">Spotify</div>
                        <div
                            className="status-dot"
                            style={{ backgroundColor: getStatusColor(integrations.spotify.status) }}
                        ></div>
                    </div>
                    <div className="card-body">
                        <div className="integration-status">
                            {getStatusIcon(integrations.spotify.status)} {integrations.spotify.status}
                        </div>
                        {integrations.spotify.status === 'connected' ? (
                            <div className="integration-controls">
                                <button className="control-btn">⏮️</button>
                                <button className="control-btn large">⏯️</button>
                                <button className="control-btn">⏭️</button>
                            </div>
                        ) : (
                            <button className="connect-btn">Connect Spotify</button>
                        )}
                    </div>
                </div>

                {/* Gmail */}
                <div className="integration-card gmail">
                    <div className="card-header">
                        <div className="integration-icon">📧</div>
                        <div className="integration-name">Gmail</div>
                        <div
                            className="status-dot"
                            style={{ backgroundColor: getStatusColor(integrations.gmail.status) }}
                        ></div>
                    </div>
                    <div className="card-body">
                        <div className="integration-status">
                            {getStatusIcon(integrations.gmail.status)} {integrations.gmail.status}
                        </div>
                        {integrations.gmail.status === 'connected' ? (
                            <div className="integration-info">
                                <div className="info-item">
                                    <strong>Unread:</strong> 0
                                </div>
                                <button className="action-btn">View Inbox</button>
                            </div>
                        ) : (
                            <button className="connect-btn">Connect Gmail</button>
                        )}
                    </div>
                </div>

                {/* Weather */}
                <div className="integration-card weather">
                    <div className="card-header">
                        <div className="integration-icon">🌤️</div>
                        <div className="integration-name">Weather</div>
                        <div
                            className="status-dot"
                            style={{ backgroundColor: getStatusColor(integrations.weather.status) }}
                        ></div>
                    </div>
                    <div className="card-body">
                        <div className="integration-status">
                            {getStatusIcon(integrations.weather.status)} {integrations.weather.status}
                        </div>
                        {integrations.weather.status === 'connected' ? (
                            <div className="weather-info">
                                <div className="temperature">--°C</div>
                                <div className="condition">--</div>
                            </div>
                        ) : (
                            <button className="connect-btn">Setup Weather</button>
                        )}
                    </div>
                </div>

                {/* Google Calendar */}
                <div className="integration-card calendar">
                    <div className="card-header">
                        <div className="integration-icon">📅</div>
                        <div className="integration-name">Calendar</div>
                        <div className="status-dot" style={{ backgroundColor: '#95a5a6' }}></div>
                    </div>
                    <div className="card-body">
                        <div className="integration-status">○ disconnected</div>
                        <button className="connect-btn">Connect Calendar</button>
                    </div>
                </div>

                {/* News API */}
                <div className="integration-card news">
                    <div className="card-header">
                        <div className="integration-icon">📰</div>
                        <div className="integration-name">News</div>
                        <div className="status-dot" style={{ backgroundColor: '#95a5a6' }}></div>
                    </div>
                    <div className="card-body">
                        <div className="integration-status">○ disconnected</div>
                        <button className="connect-btn">Setup News API</button>
                    </div>
                </div>

                {/* Todoist */}
                <div className="integration-card todoist">
                    <div className="card-header">
                        <div className="integration-icon">✅</div>
                        <div className="integration-name">Todoist</div>
                        <div className="status-dot" style={{ backgroundColor: '#95a5a6' }}></div>
                    </div>
                    <div className="card-body">
                        <div className="integration-status">○ disconnected</div>
                        <button className="connect-btn">Connect Todoist</button>
                    </div>
                </div>
            </div>

            {/* Setup Instructions */}
            <div className="setup-instructions">
                <h4>⚙️ Setup Instructions</h4>
                <p>To enable API integrations, add the following to your <code>.env</code> file:</p>
                <div className="instruction-code">
                    <pre>
                        {`# Spotify
SPOTIFY_CLIENT_ID=your-client-id
SPOTIFY_CLIENT_SECRET=your-client-secret

# Weather
OPENWEATHER_API_KEY=your-api-key

# Gmail (requires OAuth)
GMAIL_CREDENTIALS_PATH=credentials.json`}
                    </pre>
                </div>
            </div>
        </div>
    );
};

export default IntegrationPanel;
