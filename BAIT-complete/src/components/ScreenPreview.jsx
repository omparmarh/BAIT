import React, { useState, useEffect } from 'react';
import './ScreenPreview.css';

/**
 * BAIT PRO ULTIMATE - Screen Preview Component
 * - Real-time screen capture preview
 * - OCR text extraction display
 * - Error detection overlay
 * - Code analysis results
 */

const ScreenPreview = () => {
    const [screenshot, setScreenshot] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [autoRefresh, setAutoRefresh] = useState(false);
    const [refreshInterval, setRefreshInterval] = useState(5);

    useEffect(() => {
        if (autoRefresh) {
            const interval = setInterval(() => {
                captureScreen();
            }, refreshInterval * 1000);
            return () => clearInterval(interval);
        }
    }, [autoRefresh, refreshInterval]);

    const captureScreen = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('/api/ultimate/vision/analyze-screen');
            if (response.ok) {
                const data = await response.json();
                setAnalysis(data);
                // In production, this would also fetch the actual screenshot image
                setScreenshot(`data:image/png;base64,${Date.now()}`); // Placeholder
            }
        } catch (error) {
            console.error('Failed to capture screen:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="screen-preview-container">
            <div className="screen-header">
                <h3>📸 Screen Context</h3>
                <div className="screen-controls">
                    <label className="auto-refresh">
                        <input
                            type="checkbox"
                            checked={autoRefresh}
                            onChange={(e) => setAutoRefresh(e.target.checked)}
                        />
                        Auto-refresh
                    </label>
                    {autoRefresh && (
                        <select
                            value={refreshInterval}
                            onChange={(e) => setRefreshInterval(Number(e.target.value))}
                            className="interval-select"
                        >
                            <option value={3}>3s</option>
                            <option value={5}>5s</option>
                            <option value={10}>10s</option>
                            <option value={30}>30s</option>
                        </select>
                    )}
                    <button onClick={captureScreen} disabled={isLoading} className="capture-btn">
                        {isLoading ? '⏳ Capturing...' : '📸 Capture'}
                    </button>
                </div>
            </div>

            {/* Screenshot Display */}
            <div className="screenshot-display">
                {!screenshot ? (
                    <div className="placeholder">
                        <div className="placeholder-icon">🖥️</div>
                        <p>No screenshot captured yet</p>
                        <button onClick={captureScreen} className="start-btn">
                            Capture Screen
                        </button>
                    </div>
                ) : (
                    <div className="screenshot-wrapper">
                        <div className="screenshot-placeholder">
                            {/* In production, display actual screenshot */}
                            <div className="mock-screenshot">
                                <div className="mock-window">
                                    <div className="mock-titlebar">Browser Window</div>
                                    <div className="mock-content">
                                        <div className="mock-text-line"></div>
                                        <div className="mock-text-line short"></div>
                                        <div className="mock-text-line"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Analysis Results */}
            {analysis && (
                <div className="analysis-results">
                    <h4>📊 Analysis</h4>
                    <div className="analysis-grid">
                        <div className="analysis-card">
                            <div className="card-icon">📝</div>
                            <div className="card-content">
                                <div className="card-label">Text Detected</div>
                                <div className="card-value">{analysis.text_length} chars</div>
                            </div>
                        </div>

                        <div className="analysis-card">
                            <div className="card-icon">❌</div>
                            <div className="card-content">
                                <div className="card-label">Errors Found</div>
                                <div className="card-value">{analysis.errors_detected?.length || 0}</div>
                            </div>
                        </div>

                        <div className="analysis-card">
                            <div className="card-icon">💻</div>
                            <div className="card-content">
                                <div className="card-label">Code Detected</div>
                                <div className="card-value">{analysis.has_code ? 'Yes' : 'No'}</div>
                            </div>
                        </div>

                        {analysis.language && (
                            <div className="analysis-card">
                                <div className="card-icon">🔤</div>
                                <div className="card-content">
                                    <div className="card-label">Language</div>
                                    <div className="card-value">{analysis.language}</div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Error Details */}
                    {analysis.errors_detected && analysis.errors_detected.length > 0 && (
                        <div className="error-details">
                            <h5>⚠️ Detected Errors:</h5>
                            <ul>
                                {analysis.errors_detected.map((error, idx) => (
                                    <li key={idx}>{error}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default ScreenPreview;
