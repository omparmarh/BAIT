export default function ConversationItem({ conversation, isActive, onClick }) {
    return (
        <div
            className={`conversation-item ${isActive ? 'active' : ''}`}
            onClick={onClick}
        >
            <div className="conv-title">{conversation.title}</div>
            <div className="conv-meta">
                {conversation.message_count} messages
            </div>
            <div className="conv-time">
                {new Date(conversation.updated_at).toLocaleDateString()}
            </div>
        </div>
    )
}
