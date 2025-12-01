import { useState, useRef, useEffect } from 'react';
import './LiveNotes.css';

const LiveNotes = () => {
    const [notes, setNotes] = useState([]);
    const [isRecording, setIsRecording] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const [editingId, setEditingId] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const recordingTimerRef = useRef(null);

    // Fetch notes on mount
    useEffect(() => {
        fetchNotes();
        const interval = setInterval(fetchNotes, 3000);
        return () => clearInterval(interval);
    }, []);

    const fetchNotes = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/notes');
            const data = await response.json();
            setNotes(data.reverse()); // Most recent first
        } catch (error) {
            console.error('Failed to fetch notes:', error);
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
                    const base64Audio = reader.result;
                    setIsLoading(true);

                    try {
                        const response = await fetch('http://localhost:8000/api/voice-to-text', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ audio_data: base64Audio })
                        });

                        const data = await response.json();

                        if (data.status === 'success' && data.text) {
                            await addNote(data.text);
                        } else {
                            alert(data.message || 'Could not understand speech');
                        }
                    } catch (error) {
                        console.error('Voice processing error:', error);
                        alert('Error processing voice');
                    } finally {
                        setIsLoading(false);
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
            console.error('Microphone error:', error);
            alert('Could not access microphone. Check permissions.');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            clearInterval(recordingTimerRef.current);
        }
    };

    const addNote = async (text) => {
        try {
            const response = await fetch('http://localhost:8000/api/notes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            const newNote = await response.json();
            setNotes(prev => [newNote, ...prev]);
        } catch (error) {
            console.error('Failed to create note:', error);
        }
    };

    const updateNote = async (id, newText) => {
        try {
            const response = await fetch('http://localhost:8000/api/notes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, text: newText })
            });

            const updated = await response.json();
            setNotes(prev => prev.map(n => n.id === id ? updated : n));
            setEditingId(null);
        } catch (error) {
            console.error('Failed to update note:', error);
        }
    };

    const deleteNote = async (id) => {
        try {
            await fetch(`http://localhost:8000/api/notes/${id}`, {
                method: 'DELETE'
            });
            setNotes(prev => prev.filter(n => n.id !== id));
        } catch (error) {
            console.error('Failed to delete note:', error);
        }
    };

    const exportNotes = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/notes/export');
            const data = await response.json();

            const element = document.createElement('a');
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(data.content));
            element.setAttribute('download', `bait_notes_${new Date().toISOString().split('T')[0]}.txt`);
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        } catch (error) {
            console.error('Export error:', error);
        }
    };

    const formatTime = (iso) => {
        if (!iso) return '';
        return new Date(iso).toLocaleTimeString();
    };

    return (
        <div className="live-notes-container">
            <div className="notes-panel">
                <div className="notes-header">
                    <h3>📝 Live Notes</h3>
                    <div className="notes-actions">
                        <button
                            onClick={exportNotes}
                            className="action-btn export-btn"
                            title="Export all notes"
                        >
                            💾 Export
                        </button>
                        {isRecording ? (
                            <button
                                onClick={stopRecording}
                                className="action-btn stop-btn recording"
                            >
                                ⏹️ Stop ({recordingTime}s)
                            </button>
                        ) : (
                            <button
                                onClick={startRecording}
                                className="action-btn record-btn"
                                disabled={isLoading}
                            >
                                {isLoading ? '⏳' : '🎤'} Record
                            </button>
                        )}
                    </div>
                </div>

                <div className="notes-list">
                    {notes.length === 0 ? (
                        <div className="empty-notes">
                            <p>📭 No notes yet</p>
                            <p>Click the record button to start!</p>
                        </div>
                    ) : (
                        notes.map(note => (
                            <div key={note.id} className="note-card">
                                <div className="note-header-card">
                                    <span className="note-time">
                                        🕐 {formatTime(note.created_at)}
                                    </span>
                                    <div className="note-buttons">
                                        <button
                                            onClick={() => setEditingId(editingId === note.id ? null : note.id)}
                                            className="note-btn edit-btn"
                                            title="Edit note"
                                        >
                                            ✏️
                                        </button>
                                        <button
                                            onClick={() => deleteNote(note.id)}
                                            className="note-btn delete-btn"
                                            title="Delete note"
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                </div>

                                {editingId === note.id ? (
                                    <div className="note-edit">
                                        <textarea
                                            className="note-textarea"
                                            defaultValue={note.text}
                                            id={`textarea-${note.id}`}
                                            autoFocus
                                            rows={3}
                                        />
                                        <div className="edit-actions">
                                            <button
                                                onClick={() => {
                                                    const textarea = document.getElementById(`textarea-${note.id}`);
                                                    updateNote(note.id, textarea.value);
                                                }}
                                                className="btn-save"
                                            >
                                                💾 Save
                                            </button>
                                            <button
                                                onClick={() => setEditingId(null)}
                                                className="btn-cancel"
                                            >
                                                ❌ Cancel
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="note-content">
                                        <p>{note.text}</p>
                                    </div>
                                )}

                                <div className="note-footer">
                                    <small>Updated: {formatTime(note.updated_at)}</small>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default LiveNotes;
