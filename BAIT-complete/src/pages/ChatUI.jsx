import React, { useState, useEffect, useRef } from 'react'
import ChatMessage from '../components/ChatMessage'
import InputBox from '../components/InputBox'
import SystemStats from '../components/SystemStats'
import HistoryPanel from './HistoryPanel'
import { useChat } from '../hooks/useChat'
import '../styles/bait.css'
import '../styles/animations.css'

export default function ChatUI({ initialConversationId, onConversationSelect }) {
    const {
        messages,
        conversationId,
        sendMessage,
        loadConversation,
        createNewConversation
    } = useChat(initialConversationId)

    const messagesEndRef = useRef(null)

    useEffect(() => {
        if (initialConversationId) {
            loadConversation(initialConversationId)
        } else {
            createNewConversation()
        }
    }, [initialConversationId])

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const handleNewConversation = () => {
        createNewConversation()
    }

    return (
        <div className="chat-container">
            <HistoryPanel
                onSelectConversation={onConversationSelect}
                onNewConversation={handleNewConversation}
                currentConversationId={conversationId}
            />

            <div className="chat-main">
                <div className="bait-circle"></div>
                <div className="messages-area">
                    {messages.length === 0 ? (
                        <div className="empty-state">
                            <p>Start a conversation!</p>
                        </div>
                    ) : (
                        messages.map((msg, idx) => (
                            <ChatMessage key={idx} message={msg} />
                        ))
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <InputBox onSend={sendMessage} conversationId={conversationId} />
            </div>

            <SystemStats />
        </div>
    )
}
