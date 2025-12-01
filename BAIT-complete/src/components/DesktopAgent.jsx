import React, { useState, useEffect } from 'react';
import './DesktopAgent.css';

/**
 * BAIT PRO ULTIMATE - Desktop Agent Component
 * - Window list and management
 * - Window control actions
 * - Split screen layouts
 * - Active window display
 */

const DesktopAgent = () => {
    const [windows, setWindows] = useState([]);
    const [selectedWindow, setSelectedWindow] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [lastAction, setLastAction] = useState('');

    useEffect(() => {
        loadWindows();
    }, []);

    const loadWindows = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('/api/ultimate/desktop/windows');
            if (response.ok) {
                const data = await response.json();
                setWindows(data.windows || []);
            }
        } catch (error) {
            console.error('Failed to load windows:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const executeCommand = async (type, params) => {
        try {
            const response = await fetch('/api/ultimate/desktop/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, params })
            });

            if (response.ok) {
                setLastAction(`${type} executed successfully`);
                setTimeout(() => setLastAction(''), 3000);
                loadWindows(); // Refresh list
            }
        } catch (error) {
            console.error('Command failed:', error);
            setLastAction(`Failed: ${type}`);
            setTimeout(() => setLastAction(''), 3000);
        }
    };

    const maximizeWindow = () => {
        if (selectedWindow) {
            executeCommand('window_maximize', { title: selectedWindow });
        }
    };

    const minimizeWindow = () => {
        if (selectedWindow) {
            executeCommand('window_minimize', { title: selectedWindow });
        }
    };

    const closeWindow = () => {
        if (selectedWindow) {
            executeCommand('window_close', { title: selectedWindow });
            setSelectedWindow(null);
        }
    };

    const splitScreenHorizontal = () => {
        if (windows.length >= 2) {
            executeCommand('split_screen', {
                title1: windows[0],
                title2: windows[1],
                orientation: 'horizontal'
            });
        }
    };

    const splitScreenVertical = () => {
        if (windows.length >= 2) {
            executeCommand('split_screen', {
                title1: windows[0],
                title2: windows[1],
                orientation: 'vertical'
            });
        }
    };

    return (
        <div className="desktop-agent">
            <div className="desktop-header">
                <h3>🖥️ Desktop Controller</h3>
                <button onClick={loadWindows} className="refresh-btn" disabled={isLoading}>
                    {isLoading ? '⏳' : '🔄'} Refresh
                </button>
            </div>

            {/* Last Action Notification */}
            {lastAction && (
                <div className="action-notification">
                    ✅ {lastAction}
                </div>
            )}

            {/* Quick Actions */}
            <div className="quick-actions">
                <h4>⚡ Quick Actions</h4>
                <div className="action-grid">
                    <button
                        onClick={splitScreenHorizontal}
                        disabled={windows.length < 2}
                        className="action-btn"
                    >
                        <div className="btn-icon">⬌</div>
                        <div className="btn-label">Split Horizontal</div>
                    </button>
                    <button
                        onClick={splitScreenVertical}
                        disabled={windows.length < 2}
                        className="action-btn"
                    >
                        <div className="btn-icon">⬍</div>
                        <div className="btn-label">Split Vertical</div>
                    </button>
                </div>
            </div>

            {/* Window List */}
            <div className="window-list-section">
                <h4>🪟 Active Windows ({windows.length})</h4>
                <div className="window-list">
                    {isLoading ? (
                        <div className="loading">Loading windows...</div>
                    ) : windows.length === 0 ? (
                        <div className="no-windows">No windows detected</div>
                    ) : (
                        windows.map((window, index) => (
                            <div
                                key={index}
                                className={`window-item ${selectedWindow === window ? 'selected' : ''}`}
                                onClick={() => setSelectedWindow(window)}
                            >
                                <div className="window-icon">🪟</div>
                                <div className="window-title">{window}</div>
                                {selectedWindow === window && (
                                    <div className="window-badge">Selected</div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Window Controls */}
            {selectedWindow && (
                <div className="window-controls">
                    <h4>🎛️ Window Controls</h4>
                    <div className="selected-window-info">
                        <strong>Selected:</strong> {selectedWindow}
                    </div>
                    <div className="control-buttons">
                        <button onClick={maximizeWindow} className="control-btn maximize">
                            ⬜ Maximize
                        </button>
                        <button onClick={minimizeWindow} className="control-btn minimize">
                            ➖ Minimize
                        </button>
                        <button onClick={closeWindow} className="control-btn close">
                            ❌ Close
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DesktopAgent;
