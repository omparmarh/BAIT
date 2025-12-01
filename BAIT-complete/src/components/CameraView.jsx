import React, { useState, useEffect, useRef } from 'react';
import './CameraView.css';

/**
 * BAIT PRO ULTIMATE - Camera View Component
 * - Live webcam feed
 * - Face detection overlay
 * - Gesture recognition display
 * - Presence detection status
 */

const CameraView = () => {
    const [isActive, setIsActive] = useState(false);
    const [cameraStatus, setCameraStatus] = useState(null);
    const [faceDetected, setFaceDetected] = useState(false);
    const [currentGesture, setCurrentGesture] = useState(null);
    const [permissionGranted, setPermissionGranted] = useState(null);
    const videoRef = useRef(null);
    const streamRef = useRef(null);

    // Poll camera status
    useEffect(() => {
        if (isActive) {
            const interval = setInterval(pollCameraStatus, 1000);
            return () => clearInterval(interval);
        }
    }, [isActive]);

    const pollCameraStatus = async () => {
        try {
            const response = await fetch('/api/ultimate/vision/camera-status');
            if (response.ok) {
                const data = await response.json();
                setCameraStatus(data);
                setFaceDetected(data.face_detected);
                setCurrentGesture(data.gesture);
            }
        } catch (error) {
            console.error('Failed to get camera status:', error);
        }
    };

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 }
            });

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                streamRef.current = stream;
            }

            setIsActive(true);
            setPermissionGranted(true);
        } catch (error) {
            console.error('Camera access denied:', error);
            setPermissionGranted(false);
        }
    };

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        if (videoRef.current) {
            videoRef.current.srcObject = null;
        }
        setIsActive(false);
    };

    const getGestureIcon = (gesture) => {
        const icons = {
            'fist': '✊',
            'point': '👆',
            'peace': '✌️',
            'open_hand': '✋',
            'thumbs_up': '👍',
            'thumbs_down': '👎'
        };
        return icons[gesture] || '👋';
    };

    const getGestureAction = (gesture) => {
        const actions = {
            'fist': 'Stop/Pause',
            'point': 'Select/Click',
            'peace': 'Scroll',
            'open_hand': 'Navigate',
            'thumbs_up': 'Like/Confirm',
            'thumbs_down': 'Dislike/Cancel'
        };
        return actions[gesture] || 'Unknown';
    };

    return (
        <div className="camera-view-container">
            <div className="camera-header">
                <h3>📷 Camera & Gestures</h3>
                <div className="camera-status-indicator">
                    {isActive ? (
                        <span className="status-live">● LIVE</span>
                    ) : (
                        <span className="status-off">○ OFF</span>
                    )}
                </div>
            </div>

            {/* Camera Feed */}
            <div className="camera-feed">
                {!isActive ? (
                    <div className="camera-placeholder">
                        <div className="placeholder-icon">📹</div>
                        <p>Camera is off</p>
                        {permissionGranted === false && (
                            <p className="permission-denied">Camera permission denied</p>
                        )}
                        <button onClick={startCamera} className="start-camera-btn">
                            Start Camera
                        </button>
                    </div>
                ) : (
                    <div className="video-wrapper">
                        <video
                            ref={videoRef}
                            autoPlay
                            playsInline
                            muted
                            className="camera-video"
                        />

                        {/* Face Detection Overlay */}
                        {faceDetected && (
                            <div className="face-overlay">
                                <div className="face-box">
                                    <div className="face-corner tl"></div>
                                    <div className="face-corner tr"></div>
                                    <div className="face-corner bl"></div>
                                    <div className="face-corner br"></div>
                                    <div className="face-label">😊 Face Detected</div>
                                </div>
                            </div>
                        )}

                        {/* Recording Indicator */}
                        <div className="recording-indicator">
                            <div className="rec-dot"></div>
                            <span>REC</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Camera Controls */}
            {isActive && (
                <div className="camera-controls">
                    <button onClick={stopCamera} className="stop-btn">
                        Stop Camera
                    </button>
                </div>
            )}

            {/* Detection Info */}
            {isActive && (
                <div className="detection-info">
                    <div className="info-grid">
                        <div className="info-card">
                            <div className="info-icon">👤</div>
                            <div className="info-content">
                                <div className="info-label">Presence</div>
                                <div className={`info-value ${faceDetected ? 'detected' : ''}`}>
                                    {faceDetected ? 'Detected' : 'Not Detected'}
                                </div>
                            </div>
                        </div>

                        <div className="info-card">
                            <div className="info-icon">
                                {currentGesture ? getGestureIcon(currentGesture) : '🤚'}
                            </div>
                            <div className="info-content">
                                <div className="info-label">Gesture</div>
                                <div className="info-value">
                                    {currentGesture || 'None'}
                                </div>
                            </div>
                        </div>

                        {currentGesture && (
                            <div className="info-card">
                                <div className="info-icon">⚡</div>
                                <div className="info-content">
                                    <div className="info-label">Action</div>
                                    <div className="info-value">
                                        {getGestureAction(currentGesture)}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Gesture Guide */}
            {isActive && (
                <div className="gesture-guide">
                    <h5>🤟 Gesture Controls</h5>
                    <div className="gesture-list">
                        <div className="gesture-item">✊ Fist → Stop/Pause</div>
                        <div className="gesture-item">👆 Point → Select</div>
                        <div className="gesture-item">✌️ Peace → Scroll</div>
                        <div className="gesture-item">✋ Open Hand → Navigate</div>
                        <div className="gesture-item">👍 Thumbs Up → Confirm</div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CameraView;
