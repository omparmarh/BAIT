import { useState } from 'react'
import axios from 'axios'

export const useChat = (initialConversationId = null) => {
    const [messages, setMessages] = useState([])
    const [conversationId, setConversationId] = useState(initialConversationId)

    const sendMessage = async (content, convId) => {
        if (!content.trim()) return

        const activeConvId = convId || conversationId

        try {
            // Add user message IMMEDIATELY to UI
            const userMsg = {
                id: Date.now(),
                content: content,
                is_user: true,
                timestamp: new Date().toISOString()
            }
            setMessages(prev => [...prev, userMsg])

            // Send to API
            const response = await axios.post('http://127.0.0.1:8000/api/chat', {
                conversation_id: activeConvId,
                content: content,
                is_user: true
            })

            // Add AI response from API
            const aiMsg = {
                id: response.data.id,
                content: response.data.content,
                is_user: false,
                timestamp: response.data.timestamp
            }

            // Add AI response to messages
            setMessages(prev => [...prev, aiMsg])

            // Update conversation ID if new
            if (!conversationId) {
                setConversationId(activeConvId)
            }
        } catch (err) {
            console.error('Error sending message:', err)
            // Show error in chat
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                content: `Error: ${err.message}`,
                is_user: false,
                timestamp: new Date().toISOString()
            }])
        }
    }

    const loadConversation = async (convId) => {
        try {
            const response = await axios.get(`http://127.0.0.1:8000/api/conversation/${convId}`)
            setConversationId(convId)
            setMessages(response.data.messages || [])
        } catch (err) {
            console.error('Error loading conversation:', err)
            setMessages([])
        }
    }

    const createNewConversation = async () => {
        try {
            const response = await axios.post('http://127.0.0.1:8000/api/conversation', {
                title: `Chat - ${new Date().toLocaleString()}`
            })
            setConversationId(response.data.id)
            setMessages([])
        } catch (err) {
            console.error('Error creating conversation:', err)
        }
    }

    return {
        messages,
        conversationId,
        sendMessage,
        loadConversation,
        createNewConversation
    }
}