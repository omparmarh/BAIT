import { useTheme } from '../context/ThemeContext';
import './ThemeToggle.css';
import { useState } from 'react';

const ThemeToggle = () => {
    const { theme, toggleTheme, useSystemTheme, isSystemPreference } = useTheme();
    const [showSettings, setShowSettings] = useState(false);

    return (
        <div className="theme-toggle-wrapper">
            {/* MAIN TOGGLE BUTTON */}
            <button
                className="theme-toggle-btn"
                onClick={toggleTheme}
                title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
            >
                {theme === 'dark' ? '☀️' : '🌙'}
            </button>

            {/* SETTINGS MENU */}
            <div className={`theme-settings ${showSettings ? 'open' : ''}`}>
                <button
                    className="settings-toggle"
                    onClick={() => setShowSettings(!showSettings)}
                    title="Theme Settings"
                >
                    ⚙️
                </button>

                {showSettings && (
                    <div className="theme-menu">
                        <div className="theme-menu-header">
                            <h4>🎨 Theme Settings</h4>
                            <button
                                className="menu-close"
                                onClick={() => setShowSettings(false)}
                            >
                                ✕
                            </button>
                        </div>

                        <div className="theme-options">
                            {/* DARK MODE */}
                            <button
                                className={`theme-option ${theme === 'dark' && !isSystemPreference ? 'active' : ''}`}
                                onClick={() => {
                                    const root = document.documentElement;
                                    root.setAttribute('data-theme', 'dark');
                                    localStorage.setItem('bait-theme', 'dark');
                                    localStorage.setItem('bait-use-system-theme', 'false');
                                    toggleTheme();
                                }}
                            >
                                <span className="option-icon">🌙</span>
                                <span className="option-label">Dark Mode</span>
                                {theme === 'dark' && !isSystemPreference && (
                                    <span className="option-check">✓</span>
                                )}
                            </button>

                            {/* LIGHT MODE */}
                            <button
                                className={`theme-option ${theme === 'light' && !isSystemPreference ? 'active' : ''}`}
                                onClick={() => {
                                    const root = document.documentElement;
                                    root.setAttribute('data-theme', 'light');
                                    localStorage.setItem('bait-theme', 'light');
                                    localStorage.setItem('bait-use-system-theme', 'false');
                                    toggleTheme();
                                }}
                            >
                                <span className="option-icon">☀️</span>
                                <span className="option-label">Light Mode</span>
                                {theme === 'light' && !isSystemPreference && (
                                    <span className="option-check">✓</span>
                                )}
                            </button>

                            {/* SYSTEM */}
                            <button
                                className={`theme-option ${isSystemPreference ? 'active' : ''}`}
                                onClick={useSystemTheme}
                            >
                                <span className="option-icon">🖥️</span>
                                <span className="option-label">System Preference</span>
                                {isSystemPreference && <span className="option-check">✓</span>}
                            </button>
                        </div>

                        <div className="theme-preview">
                            <div className="preview-label">Current Theme:</div>
                            <div className={`preview-box ${theme}`}>
                                {theme === 'dark' ? 'Dark Mode 🌙' : 'Light Mode ☀️'}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ThemeToggle;
