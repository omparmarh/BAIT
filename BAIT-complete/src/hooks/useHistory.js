import { useState, useEffect } from 'react'
import axios from 'axios'

export const useHistory = () => {
    const [conversations, setConversations] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const fetchConversations = async () => {
        try {
            setLoading(true)
            const response = await axios.get('http://127.0.0.1:8000/api/conversations')
            setConversations(response.data)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchConversations()
        const interval = setInterval(fetchConversations, 5000)
        return () => clearInterval(interval)
    }, [])

    return { conversations, loading, error, refetch: fetchConversations }
}
