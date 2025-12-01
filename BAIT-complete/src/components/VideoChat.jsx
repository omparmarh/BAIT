import { useState, useRef, useEffect } from 'react';
import './VideoChat.css';

const VideoChat = () => {
    const [sessionId, setSessionId] = useState(null);
    const [ws, setWs] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [isConnected, setIsConnected] = useState(false);
    const [videoEnabled, setVideoEnabled] = useState(true);
    const [audioEnabled, setAudioEnabled] = useState(true);
    const [isRecording, setIsRecording] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);

    const localVideoRef = useRef(null);
    const remoteVideoRef = useRef(null);
    const messagesEndRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const recordingTimerRef = useRef(null);
    const peerConnectionRef = useRef(null);
    const localStreamRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Initialize video chat
    useEffect(() => {
        initializeVideoChat();
        return () => {
            if (ws) ws.close();
            if (localStreamRef.current) {
                localStreamRef.current.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    const initializeVideoChat = async () => {
        try {
            // Get user media
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: 1280 }, height: { ideal: 720 } },
                audio: true
            });

            localStreamRef.current = stream;

            // Display local video
            if (localVideoRef.current) {
                localVideoRef.current.srcObject = stream;
            }

            // Create session
            const response = await fetch('http://localhost:8000/api/video-chat/session');
            const data = await response.json();
            const newSessionId = data.session_id;
            setSessionId(newSessionId);

            // Connect WebSocket
            const wsUrl = `ws://localhost:8000/ws/video-chat/${newSessionId}`;
            const websocket = new WebSocket(wsUrl);

            websocket.onopen = () => {
                setIsConnected(true);
                console.log('Video chat connected');
            };

            websocket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                handleWebSocketMessage(message);
            };

            websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            websocket.onclose = () => {
                setIsConnected(false);
                console.log('Video chat disconnected');
            };

            setWs(websocket);

            // Setup WebRTC
            setupWebRTC(stream);

        } catch (error) {
            console.error('Failed to initialize video chat:', error);
            alert('Could not access camera/microphone. Check permissions.');
        }
    };

    const setupWebRTC = async (localStream) => {
        try {
            const config = {
                iceServers: [
                    { urls: ['stun:stun.l.google.com:19302'] },
                    { urls: ['stun:stun1.l.google.com:19302'] }
                ]
            };

            peerConnectionRef.current = new RTCPeerConnection(config);

            // Add local stream tracks
            localStream.getTracks().forEach(track => {
                peerConnectionRef.current.addTrack(track, localStream);
            });

            // Handle remote stream
            peerConnectionRef.current.ontrack = (event) => {
                if (remoteVideoRef.current) {
                    remoteVideoRef.current.srcObject = event.streams[0];
                }
            };

            // Handle ICE candidates
            peerConnectionRef.current.onicecandidate = (event) => {
                if (event.candidate && ws) {
                    ws.send(JSON.stringify({
                        type: 'ice-candidate',
                        candidate: event.candidate
                    }));
                }
            };

            // Create offer
            const offer = await peerConnectionRef.current.createOffer();
            await peerConnectionRef.current.setLocalDescription(offer);

            if (ws) {
                ws.send(JSON.stringify({
                    type: 'offer',
                    sdp: offer
                }));
            }

        } catch (error) {
            console.error('WebRTC setup error:', error);
        }
    };

    const handleWebSocketMessage = async (message) => {
        try {
            if (message.type === 'chat') {
                setMessages(prev => [...prev, {
                    role: message.role,
                    content: message.content,
                    timestamp: message.timestamp
                }]);
            }
            else if (message.type === 'offer' && peerConnectionRef.current) {
                const offer = new RTCSessionDescription(message.sdp);
                await peerConnectionRef.current.setRemoteDescription(offer);

                const answer = await peerConnectionRef.current.createAnswer();
                await peerConnectionRef.current.setLocalDescription(answer);

                ws.send(JSON.stringify({
                    type: 'answer',
                    sdp: answer
                }));
            }
            else if (message.type === 'answer' && peerConnectionRef.current) {
                const answer = new RTCSessionDescription(message.sdp);
                await peerConnectionRef.current.setRemoteDescription(answer);
            }
            else if (message.type === 'ice-candidate' && peerConnectionRef.current) {
                const candidate = new RTCIceCandidate(message.candidate);
                await peerConnectionRef.current.addIceCandidate(candidate);
            }
            else if (message.type === 'status') {
                setVideoEnabled(message.video_enabled);
                setAudioEnabled(message.audio_enabled);
            }
        } catch (error) {
            console.error('Error handling WebSocket message:', error);
        }
    };

    const sendChatMessage = () => {
        if (!inputText.trim() || !ws) return;

        const message = {
            type: 'chat',
            sender: 'user',
            content: inputText
        };

        ws.send(JSON.stringify(message));
        setMessages(prev => [...prev, {
            role: 'user',
            content: inputText,
            timestamp: new Date().toISOString()
        }]);
        setInputText('');
    };

    const toggleVideo = () => {
        if (localStreamRef.current) {
            localStreamRef.current.getVideoTracks().forEach(track => {
                track.enabled = !videoEnabled;
            });
            setVideoEnabled(!videoEnabled);

            if (ws) {
                ws.send(JSON.stringify({
                    type: 'status',
                    video_enabled: !videoEnabled
                }));
            }
        }
    };

    const toggleAudio = () => {
        if (localStreamRef.current) {
            localStreamRef.current.getAudioTracks().forEach(track => {
                track.enabled = !audioEnabled;
            });
            setAudioEnabled(!audioEnabled);

            if (ws) {
                ws.send(JSON.stringify({
                    type: 'status',
                    audio_enabled: !audioEnabled
                }));
            }
        }
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);

                reader.onloadend = async () => {
                    const response = await fetch('http://localhost:8000/api/voice-to-text', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ audio_data: reader.result })
                    });

                    const data = await response.json();
                    if (data.status === 'success') {
                        setInputText(data.text);
                    }
                };

                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
            setRecordingTime(0);

            recordingTimerRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1);
            }, 1000);

        } catch (error) {
            console.error('Recording error:', error);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            clearInterval(recordingTimerRef.current);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    };

    return (
        <div className="video-chat-container">
            {/* Video Section - Gemini Style */}
            <div className="video-section">
                <div className="video-grid">
                    {/* Remote Video (AI) - Larger */}
                    <div className="video-container remote">
                        <video
                            ref={remoteVideoRef}
                            autoPlay
                            playsInline
                            className="video-feed"
                            style={{ display: isConnected ? 'block' : 'none' }}
                        />
                        {!isConnected && (
                            <div className="video-placeholder">
                                <div className="placeholder-icon">🤖</div>
                                <p>Waiting for AI connection...</p>
                            </div>
                        )}
                    </div>

                    {/* Local Video (User) - Smaller, Bottom Right */}
                    <div className="video-container local">
                        <video
                            ref={localVideoRef}
                            autoPlay
                            playsInline
                            muted
                            className="video-feed"
                        />
                        <div className="local-label">You</div>
                    </div>
                </div>

                {/* Video Controls */}
                <div className="video-controls">
                    <button
                        className={`control-btn ${videoEnabled ? 'active' : 'disabled'}`}
                        onClick={toggleVideo}
                        title="Toggle video"
                    >
                        {videoEnabled ? '📹' : '📷'}
                    </button>

                    <button
                        className={`control-btn ${audioEnabled ? 'active' : 'disabled'}`}
                        onClick={toggleAudio}
                        title="Toggle audio"
                    >
                        {audioEnabled ? '🎤' : '🔇'}
                    </button>

                    <button
                        className="control-btn hangup"
                        onClick={() => {
                            if (ws) ws.close();
                            if (localStreamRef.current) {
                                localStreamRef.current.getTracks().forEach(track => track.stop());
                            }
                            setIsConnected(false);
                        }}
                        title="End call"
                    >
                        ☎️ End
                    </button>
                </div>
            </div>

            {/* Chat Section - Gemini Style */}
            <div className="chat-section">
                <div className="chat-header">
                    <h3>💬 Conversation</h3>
                    <span className="connection-status">
                        {isConnected ? '🟢 Connected' : '🔴 Connecting...'}
                    </span>
                </div>

                <div className="chat-messages">
                    {messages.length === 0 ? (
                        <div className="chat-empty">
                            <p>Start your video chat with BAIT!</p>
                            <p>Use voice or text to interact.</p>
                        </div>
                    ) : (
                        messages.map((msg, idx) => (
                            <div key={idx} className={`chat-message ${msg.role}`}>
                                <div className="message-avatar">
                                    {msg.role === 'user' ? '👤' : '🤖'}
                                </div>
                                <div className="message-content">
                                    {msg.content}
                                </div>
                            </div>
                        ))
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Chat Input */}
                <div className="chat-input-area">
                    <div className="input-wrapper">
                        <textarea
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Type or press 🎤 to speak..."
                            rows="2"
                            className="chat-input"
                        />
                        <div className="input-actions">
                            {isRecording ? (
                                <button
                                    onClick={stopRecording}
                                    className="action-btn recording"
                                >
                                    ⏹️ Stop ({recordingTime}s)
                                </button>
                            ) : (
                                <button
                                    onClick={startRecording}
                                    className="action-btn"
                                >
                                    🎤
                                </button>
                            )}

                            <button
                                onClick={sendChatMessage}
                                disabled={!inputText.trim()}
                                className="action-btn send"
                            >
                                📤
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default VideoChat;
