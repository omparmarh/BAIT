import React, { useState, useEffect } from 'react'
import ConversationItem from '../components/ConversationItem'
import axios from 'axios'

export default function HistoryPanel({
    onSelectConversation,
    onNewConversation,
    currentConversationId
}) {
    const [conversations, setConversations] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchConversations()
        const interval = setInterval(fetchConversations, 5000)
        return () => clearInterval(interval)
    }, [])

    const fetchConversations = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:8000/api/conversations')
            setConversations(response.data)
        } catch (err) {
            console.error('Error fetching conversations:', err)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="history-panel">
            <div className="panel-header">
                <h2>History</h2>
                <button onClick={onNewConversation} className="new-btn">+ New</button>
            </div>

            <div className="conversations-list">
                {loading ? (
                    <p className="loading">Loading...</p>
                ) : conversations.length === 0 ? (
                    <p className="empty">No conversations yet</p>
                ) : (
                    conversations.map(conv => (
                        <ConversationItem
                            key={conv.id}
                            conversation={conv}
                            isActive={conv.id === currentConversationId}
                            onClick={() => onSelectConversation(conv.id)}
                        />
                    ))
                )}
            </div>
        </div>
    )
}
