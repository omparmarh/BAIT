import { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';
import AIAvatar from './AIAvatar';
import CallRecorder from './CallRecorder';
import LiveNotes from './LiveNotes';
import VideoChat from './VideoChat';

const ChatInterface = ({ conversationId, onConversationCreated }) => {
    // ═══════════════════════════════════════════════════════════
    // STATE MANAGEMENT
    // ═══════════════════════════════════════════════════════════
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [voiceMode, setVoiceMode] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [avatarEmotion, setAvatarEmotion] = useState('neutral');
    const [isAvatarSpeaking, setIsAvatarSpeaking] = useState(false);

    // Modal states
    const [showRecorder, setShowRecorder] = useState(false);
    const [showNotes, setShowNotes] = useState(false);
    const [showVideoChat, setShowVideoChat] = useState(false);

    const messagesEndRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    // ═══════════════════════════════════════════════════════════
    // AUTO-SCROLL
    // ═══════════════════════════════════════════════════════════
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // ═══════════════════════════════════════════════════════════
    // LOAD CONVERSATION
    // ═══════════════════════════════════════════════════════════
    useEffect(() => {
        if (conversationId) {
            loadConversation(conversationId);
        } else {
            setMessages([]);
        }
    }, [conversationId]);

    const loadConversation = async (id) => {
        try {
            const response = await fetch(`http://localhost:8000/api/conversation/${id}`);
            const data = await response.json();
            setMessages(data.messages || []);
        } catch (error) {
            console.error('Failed to load conversation:', error);
        }
    };

    // ═══════════════════════════════════════════════════════════
    // SEND MESSAGE
    // ═══════════════════════════════════════════════════════════
    const sendMessage = async () => {
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setInput('');
        setLoading(true);

        // Add user message
        const newUserMessage = {
            role: 'user',
            content: userMessage,
            timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, newUserMessage]);

        try {
            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMessage,
                    conversation_id: conversationId
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Add assistant message
                const assistantMessage = {
                    role: 'assistant',
                    content: data.response,
                    timestamp: new Date().toISOString()
                };
                setMessages(prev => [...prev, assistantMessage]);

                // Update conversation ID if new
                if (!conversationId && data.conversation_id) {
                    onConversationCreated(data.conversation_id);
                }

                // Set avatar emotion
                if (data.emotion) {
                    setAvatarEmotion(data.emotion);
                }
                setIsAvatarSpeaking(true);

                // Reset after speaking
                setTimeout(() => {
                    setIsAvatarSpeaking(false);
                    setAvatarEmotion('neutral');
                }, 3000);
            }
        } catch (error) {
            console.error('Chat error:', error);
        } finally {
            setLoading(false);
        }
    };

    // ═══════════════════════════════════════════════════════════
    // VOICE RECORDING
    // ═══════════════════════════════════════════════════════════
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
                    const base64Audio = reader.result;

                    try {
                        const response = await fetch('http://localhost:8000/api/voice-to-text', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ audio_data: base64Audio })
                        });

                        const data = await response.json();
                        if (data.status === 'success' && data.text) {
                            setInput(data.text);
                        }
                    } catch (error) {
                        console.error('Voice processing error:', error);
                    }
                };

                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (error) {
            console.error('Microphone error:', error);
            alert('Could not access microphone');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    // ═══════════════════════════════════════════════════════════
    // RENDER
    // ═══════════════════════════════════════════════════════════
    return (
        <div className="chat-interface">
            {/* AVATAR SECTION */}
            <div className="avatar-section">
                <div className="ai-avatar-container">
                    <AIAvatar emotion={avatarEmotion} isSpeaking={isAvatarSpeaking} />
                </div>

                <div className="avatar-info">
                    <div className="info-row">
                        <span className="info-label">Emotion:</span>
                        <span className="info-value">{avatarEmotion.toUpperCase()}</span>
                    </div>
                    <div className="info-row">
                        <span className="info-label">Status:</span>
                        <span className="info-value">
                            {isAvatarSpeaking ? '🔊 Speaking' : '🎤 Ready'}
                        </span>
                    </div>
                </div>
            </div>

            {/* CHAT SECTION */}
            <div className="chat-section">
                {/* MESSAGES */}
                <div className="messages-container">
                    {messages.length === 0 ? (
                        <div className="welcome-message">
                            <h2>👋 Hey there! I'm BAIT</h2>
                            <p>Your personal AI assistant with voice, avatar & text!</p>

                            <div className="features-grid">
                                <div className="feature-card">
                                    <span className="feature-icon">🎤</span>
                                    <span>Voice Input</span>
                                </div>
                                <div className="feature-card">
                                    <span className="feature-icon">💬</span>
                                    <span>Text Chat</span>
                                </div>
                                <div className="feature-card">
                                    <span className="feature-icon">🤖</span>
                                    <span>AI Avatar</span>
                                </div>
                                <div className="feature-card">
                                    <span className="feature-icon">🌐</span>
                                    <span>Web Search</span>
                                </div>
                            </div>

                            <div className="suggestions">
                                <button onClick={() => setInput('😄 Tell me a joke')}>
                                    😄 Tell me a joke
                                </button>
                                <button onClick={() => setInput('🌍 Ask a question')}>
                                    🌍 Ask a question
                                </button>
                                <button onClick={() => setInput('😊 Share mood')}>
                                    😊 Share mood
                                </button>
                                <button onClick={() => setVoiceMode(true)}>
                                    🎤 Try Voice Mode
                                </button>
                            </div>
                        </div>
                    ) : (
                        messages.map((msg, idx) => (
                            <div key={idx} className={`message ${msg.role}`}>
                                <span className="message-avatar">
                                    {msg.role === 'user' ? '👤' : '🤖'}
                                </span>
                                <div className="message-content">{msg.content}</div>
                            </div>
                        ))
                    )}

                    {loading && (
                        <div className="message assistant">
                            <span className="message-avatar">🤖</span>
                            <div className="message-content typing">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* INPUT AREA */}
                <div className="input-container">
                    {voiceMode ? (
                        <div className="voice-input-mode">
                            {isRecording ? (
                                <div className="recording-indicator">
                                    <div className="recording-animation">
                                        <span className="pulse"></span>
                                        <span className="recording-icon">🎙️</span>
                                    </div>
                                    <span className="recording-text">Recording...</span>
                                </div>
                            ) : (
                                <div className="voice-ready">
                                    <span className="voice-icon">🎤</span>
                                    <span>Click microphone to speak</span>
                                </div>
                            )}
                        </div>
                    ) : (
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    sendMessage();
                                }
                            }}
                            placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
                            rows="3"
                        />
                    )}

                    <div className="input-buttons">
                        {/* VOICE MODE TOGGLE */}
                        <button
                            className={`mode-toggle ${voiceMode ? 'active' : ''}`}
                            onClick={() => {
                                setVoiceMode(!voiceMode);
                                if (isRecording) stopRecording();
                            }}
                            title={voiceMode ? 'Switch to Text Mode' : 'Switch to Voice Mode'}
                        >
                            {voiceMode ? '⌨️' : '🎤'}
                        </button>

                        {/* STOP SPEECH */}
                        <button
                            className="stop-speech-btn"
                            onClick={async () => {
                                try {
                                    await fetch('http://localhost:8000/api/stop-speech', {
                                        method: 'POST'
                                    });
                                    setIsAvatarSpeaking(false);
                                    setAvatarEmotion('neutral');
                                } catch (error) {
                                    console.error('Stop error:', error);
                                }
                            }}
                            title="Stop speaking"
                        >
                            🔇
                        </button>

                        {/* CALL RECORDER */}
                        <button
                            className="recorder-toggle-btn"
                            onClick={() => setShowRecorder(true)}
                            title="Record call"
                        >
                            🎬
                        </button>

                        {/* NOTES PANEL */}
                        <button
                            className="notes-toggle-btn"
                            onClick={() => setShowNotes(true)}
                            title="Open notes"
                        >
                            📝
                        </button>

                        {/* VIDEO CHAT */}
                        <button
                            className="video-chat-btn"
                            onClick={() => setShowVideoChat(true)}
                            title="Start video chat"
                        >
                            📹
                        </button>

                        {/* SEND OR VOICE BUTTON */}
                        {voiceMode ? (
                            <button
                                className={`voice-button ${isRecording ? 'recording' : ''}`}
                                onClick={isRecording ? stopRecording : startRecording}
                                disabled={loading}
                            >
                                {isRecording ? '⏹️' : '🎤'}
                            </button>
                        ) : (
                            <button
                                onClick={() => sendMessage()}
                                disabled={!input.trim() || loading}
                                className="send-button"
                            >
                                {loading ? '⏳' : '📤'}
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* MODALS */}
            {showRecorder && (
                <div className="modal-overlay" onClick={() => setShowRecorder(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <CallRecorder onClose={() => setShowRecorder(false)} />
                    </div>
                </div>
            )}

            {showNotes && (
                <div className="modal-overlay" onClick={() => setShowNotes(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <LiveNotes onClose={() => setShowNotes(false)} />
                    </div>
                </div>
            )}

            {showVideoChat && (
                <div className="modal-overlay" onClick={() => setShowVideoChat(false)}>
                    <div className="modal-content full-screen" onClick={(e) => e.stopPropagation()}>
                        <VideoChat onClose={() => setShowVideoChat(false)} />
                    </div>
                </div>
            )}
        </div>
    );
};

export default ChatInterface;
