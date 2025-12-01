// Placeholder - add content from COMPLETE_BUILD_GUIDE.md
import React, { useState } from 'react'
import '../styles/bait.css'

export default function LoadingScreen({ onStart }) {
    const [loading, setLoading] = useState(false)

    const handleStart = () => {
        setLoading(true)
        setTimeout(() => {
            onStart()
        }, 500)
    }

    return (
        <div className="loading-container">
            <img src="/loading-screen.jpg" alt="Loading" className="bg-image" />
            <div className="overlay"></div>
            <div className="content">
                <h1 className="bait-title pulse-text">BAIT</h1>
                <p className="subtitle">Bharat's Adaptively Inteligent Technology - Your Personal Assistant</p>
                <button
                    className={`start-button ${loading ? 'loading' : ''}`}
                    onClick={handleStart}
                    disabled={loading}
                >
                    {loading ? 'INITIALIZING...' : 'START'}
                </button>
            </div>
        </div>
    )
}
