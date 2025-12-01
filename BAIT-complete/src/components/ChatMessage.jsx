export default function ChatMessage({ message }) {
    return (
        <div className={`message ${message.is_user ? 'user' : 'ai'}`}>
            <div className="message-content">
                {message.content}
            </div>
            <div className="message-time">
                {new Date(message.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                })}
            </div>
        </div>
    )
}
