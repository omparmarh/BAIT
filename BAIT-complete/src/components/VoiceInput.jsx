import React, { useState, useEffect, useRef } from 'react';
import './VoiceInput.css';

/**
 * BAIT PRO ULTIMATE - Voice Input Component
 * - Microphone controls with waveform visualization
 * - Real-time voice activity detection
 * - Command status display
 */

const VoiceInput = ({ onCommand }) => {
    const [isListening, setIsListening] = useState(false);
    const [isActive, setIsActive] = useState(false);
    const [lastCommand, setLastCommand] = useState('');
    const [provider, setProvider] = useState('google'); // google, whisper, sphinx
    const [waveformData, setWaveformData] = useState(Array(20).fill(0));
    const canvasRef = useRef(null);
    const animationRef = useRef(null);

    // Initialize voice control
    const startVoiceControl = async () => {
        try {
            const response = await fetch('/api/ultimate/voice/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider })
            });

            if (response.ok) {
                setIsListening(true);
                startWaveformAnimation();
            }
        } catch (error) {
            console.error('Failed to start voice control:', error);
        }
    };

    const stopVoiceControl = async () => {
        try {
            await fetch('/api/ultimate/voice/stop', { method: 'POST' });
            setIsListening(false);
            stopWaveformAnimation();
        } catch (error) {
            console.error('Failed to stop voice control:', error);
        }
    };

    // Waveform visualization
    const startWaveformAnimation = () => {
        const animate = () => {
            // Simulate audio levels (in production, get from actual audio stream)
            const newData = waveformData.map(() => Math.random() * (isActive ? 100 : 20));
            setWaveformData(newData);
            drawWaveform(newData);
            animationRef.current = requestAnimationFrame(animate);
        };
        animate();
    };

    const stopWaveformAnimation = () => {
        if (animationRef.current) {
            cancelAnimationFrame(animationRef.current);
        }
        setWaveformData(Array(20).fill(0));
    };

    const drawWaveform = (data) => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        const barWidth = width / data.length;

        ctx.clearRect(0, 0, width, height);

        data.forEach((value, index) => {
            const barHeight = (value / 100) * height;
            const x = index * barWidth;
            const y = height - barHeight;

            // Gradient fill
            const gradient = ctx.createLinearGradient(0, y, 0, height);
            gradient.addColorStop(0, isActive ? '#00ff88' : '#4a90e2');
            gradient.addColorStop(1, isActive ? '#00cc66' : '#357abd');

            ctx.fillStyle = gradient;
            ctx.fillRect(x, y, barWidth - 2, barHeight);
        });
    };

    // Simulate voice activity (in production, receive from backend)
    useEffect(() => {
        if (isListening) {
            const interval = setInterval(() => {
                setIsActive(prev => !prev);
            }, 2000);
            return () => clearInterval(interval);
        }
    }, [isListening]);

    return (
        <div className="voice-input-container">
            <div className="voice-header">
                <h3>🎤 Voice Control</h3>
                <div className="voice-status">
                    {isListening ? (
                        <span className="status-active">● Listening</span>
                    ) : (
                        <span className="status-inactive">○ Inactive</span>
                    )}
                </div>
            </div>

            {/* Waveform Visualization */}
            <div className="waveform-container">
                <canvas
                    ref={canvasRef}
                    width={300}
                    height={80}
                    className="waveform-canvas"
                />
            </div>

            {/* Controls */}
            <div className="voice-controls">
                <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    disabled={isListening}
                    className="provider-select"
                >
                    <option value="google">Google Speech</option>
                    <option value="whisper">Whisper API</option>
                    <option value="sphinx">Sphinx (Offline)</option>
                </select>

                <button
                    onClick={isListening ? stopVoiceControl : startVoiceControl}
                    className={`voice-button ${isListening ? 'active' : ''}`}
                >
                    {isListening ? 'Stop' : 'Start'} Voice Control
                </button>
            </div>

            {/* Wake Word Status */}
            {isListening && (
                <div className="wake-word-status">
                    <p className="wake-word-text">
                        {isActive ? '🔊 Say "Hey BAIT"...' : '👂 Listening for wake word...'}
                    </p>
                </div>
            )}

            {/* Last Command */}
            {lastCommand && (
                <div className="last-command">
                    <strong>Last Command:</strong> {lastCommand}
                </div>
            )}
        </div>
    );
};

export default VoiceInput;
