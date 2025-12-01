import { useState } from 'react'

export default function InputBox({ onSend, conversationId }) {
    const [input, setInput] = useState('')
    const [sending, setSending] = useState(false)

    const handleSend = async () => {
        if (input.trim() && !sending) {
            setSending(true)
            try {
                await onSend(input, conversationId)
                setInput('')
            } catch (err) {
                console.error('Error sending message:', err)
            } finally {
                setSending(false)
            }
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <div className="input-box">
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="message-input"
                disabled={sending}
            />
            <button
                onClick={handleSend}
                className="send-btn"
                disabled={sending || !input.trim()}
            >
                {sending ? 'Sending...' : 'Send'}
            </button>
        </div>
    )
}
