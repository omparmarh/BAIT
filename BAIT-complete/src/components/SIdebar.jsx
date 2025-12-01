import { useState, useEffect } from 'react';
import './Sidebar.css';

const Sidebar = ({ onConversationSelect }) => {
    const [conversations, setConversations] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isCollapsed, setIsCollapsed] = useState(false);

    // ═══════════════════════════════════════════════════════════
    // LOAD CONVERSATIONS
    // ═══════════════════════════════════════════════════════════
    useEffect(() => {
        loadConversations();
    }, []);

    const loadConversations = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/conversations');
            const data = await response.json();
            setConversations(data);
        } catch (error) {
            console.error('Failed to load conversations:', error);
        } finally {
            setLoading(false);
        }
    };

    // ═══════════════════════════════════════════════════════════
    // DELETE CONVERSATION
    // ═══════════════════════════════════════════════════════════
    const deleteConversation = async (id, e) => {
        e.stopPropagation();

        if (!window.confirm('Delete this conversation?')) return;

        try {
            await fetch(`http://localhost:8000/api/conversation/${id}`, {
                method: 'DELETE'
            });

            setConversations(prev => prev.filter(conv => conv.id !== id));
        } catch (error) {
            console.error('Failed to delete conversation:', error);
        }
    };

    // ═══════════════════════════════════════════════════════════
    // NEW CONVERSATION
    // ═══════════════════════════════════════════════════════════
    const startNewConversation = () => {
        onConversationSelect(null);
    };

    return (
        <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
            {/* HEADER */}
            <div className="sidebar-header">
                <h2>📚 Chats</h2>
                <button
                    className="collapse-btn"
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    title={isCollapsed ? 'Expand' : 'Collapse'}
                >
                    {isCollapsed ? '→' : '←'}
                </button>
            </div>

            {/* NEW CHAT BUTTON */}
            <button
                className="new-chat-btn"
                onClick={startNewConversation}
            >
                ✏️ New Chat
            </button>

            {/* CONVERSATIONS LIST */}
            <div className="conversations-list">
                {loading ? (
                    <div className="loading">Loading...</div>
                ) : conversations.length === 0 ? (
                    <div className="empty-state">
                        <p>📭 No conversations yet</p>
                        <small>Start a new chat to begin</small>
                    </div>
                ) : (
                    conversations.map(conv => (
                        <div
                            key={conv.id}
                            className="conversation-item"
                            onClick={() => onConversationSelect(conv.id)}
                            title={conv.title}
                        >
                            <div className="conversation-content">
                                <h4>Chat #{conv.id}</h4>
                                <p>{conv.title}</p>
                                <span className="meta">
                                    {conv.messages?.length || 0} messages
                                </span>
                            </div>
                            <button
                                className="delete-btn"
                                onClick={(e) => deleteConversation(conv.id, e)}
                                title="Delete conversation"
                            >
                                🗑️
                            </button>
                        </div>
                    ))
                )}
            </div>

            {/* FOOTER */}
            <div className="sidebar-footer">
                <button
                    className="refresh-btn"
                    onClick={loadConversations}
                    disabled={loading}
                >
                    🔄 Refresh
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
