import { useState, useRef, useEffect } from 'react';
import './CallRecorder.css';

const CallRecorder = ({ onClose }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const [recordings, setRecordings] = useState([]);
    const [loading, setLoading] = useState(false);

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const timerRef = useRef(null);

    useEffect(() => {
        loadRecordings();
    }, []);

    const loadRecordings = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/recordings');
            const data = await response.json();
            setRecordings(data);
        } catch (error) {
            console.error('Failed to load recordings:', error);
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
                    setLoading(true);
                    try {
                        const response = await fetch('http://localhost:8000/api/save-recording', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ audio_data: reader.result })
                        });

                        await response.json();
                        await loadRecordings();
                    } catch (error) {
                        console.error('Save error:', error);
                    } finally {
                        setLoading(false);
                    }
                };

                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
            setRecordingTime(0);

            timerRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1);
            }, 1000);
        } catch (error) {
            console.error('Microphone error:', error);
            alert('Could not access microphone');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            clearInterval(timerRef.current);
        }
    };

    const deleteRecording = async (id) => {
        if (!window.confirm('Delete this recording?')) return;

        try {
            await fetch(`http://localhost:8000/api/recordings/${id}`, {
                method: 'DELETE'
            });
            await loadRecordings();
        } catch (error) {
            console.error('Delete error:', error);
        }
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="call-recorder">
            <div className="recorder-header">
                <h2>🎬 Call Recorder</h2>
                <button className="close-btn" onClick={onClose}>✕</button>
            </div>

            <div className="recorder-controls">
                {isRecording ? (
                    <>
                        <div className="recording-status">
                            <span className="pulse-dot"></span>
                            <span>Recording: {formatTime(recordingTime)}</span>
                        </div>
                        <button className="stop-btn" onClick={stopRecording}>
                            ⏹️ Stop Recording
                        </button>
                    </>
                ) : (
                    <button className="start-btn" onClick={startRecording} disabled={loading}>
                        🎙️ Start Recording
                    </button>
                )}
            </div>

            <div className="recordings-list">
                <h3>📁 Saved Recordings ({recordings.length})</h3>
                {recordings.length === 0 ? (
                    <div className="empty-state">
                        <p>No recordings yet</p>
                        <small>Click "Start Recording" to begin</small>
                    </div>
                ) : (
                    recordings.map(rec => (
                        <div key={rec.id} className="recording-item">
                            <div className="recording-info">
                                <span className="recording-name">📼 Recording #{rec.id}</span>
                                <span className="recording-time">{new Date(rec.created_at).toLocaleString()}</span>
                            </div>
                            <div className="recording-actions">
                                <button onClick={() => window.open(rec.url)}>▶️</button>
                                <button onClick={() => deleteRecording(rec.id)}>🗑️</button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default CallRecorder;
