import { useState, useEffect } from 'react';
import './HistorySidebar.css';

const HistorySidebar = ({ isOpen, currentConversationId, onSelectConversation, onNewConversation }) => {
    const [conversations, setConversations] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchConversations = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/conversations');
            const data = await response.json();
            setConversations(data);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch conversations:', error);
            setLoading(false);
        }
    };

    useEffect(() => {
        if (isOpen) {
            fetchConversations();
            const interval = setInterval(fetchConversations, 3000);
            return () => clearInterval(interval);
        }
    }, [isOpen]);

    const deleteConversation = async (id) => {
        try {
            await fetch(`http://localhost:8000/api/conversation/${id}`, {
                method: 'DELETE'
            });
            setConversations(conversations.filter(c => c.id !== id));
            if (currentConversationId === id) {
                onNewConversation();
            }
        } catch (error) {
            console.error('Failed to delete conversation:', error);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="history-sidebar">
            <div className="sidebar-header">
                <h2>💬 History</h2>
                <button className="new-chat-btn" onClick={onNewConversation}>
                    ➕ New Chat
                </button>
            </div>

            <div className="conversations-list">
                {loading ? (
                    <div className="loading-conversations">Loading...</div>
                ) : conversations.length === 0 ? (
                    <div className="no-conversations">
                        <p>No conversations yet</p>
                        <p>Start a new chat!</p>
                    </div>
                ) : (
                    conversations.map(conv => (
                        <div
                            key={conv.id}
                            className={`conversation-item ${currentConversationId === conv.id ? 'active' : ''}`}
                            onClick={() => onSelectConversation(conv.id)}
                        >
                            <div className="conversation-content">
                                <div className="conversation-title">{conv.title}</div>
                                <div className="conversation-preview">
                                    {conv.messages.length} messages
                                </div>
                            </div>
                            <button
                                className="delete-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    deleteConversation(conv.id);
                                }}
                            >
                                🗑️
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default HistorySidebar;
