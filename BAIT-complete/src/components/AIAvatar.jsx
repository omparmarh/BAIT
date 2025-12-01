import React, { useState } from 'react';
import './AIAvatar.css';

/**
 * BAIT PRO ULTIMATE - AI Avatar Component  
 * - Animated avatar display
 * - Expression control
 * - Speech animation
 */

const AIAvatar = () => {
    const [expression, setExpression] = useState('neutral');
    const [isTalking, setIsTalking] = useState(false);

    const toggleTalk = () => setIsTalking(!isTalking);

    return (
        <div className="avatar-container">
            <div className="avatar-display">
                <div className="avatar-frame">
                    <img
                        src="/avatar.png"
                        alt="BAIT Avatar"
                        className={`avatar-image ${isTalking ? 'talking' : ''} expression-${expression}`}
                        onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.parentElement.innerHTML = '<div class="emoji-avatar">🤖</div>';
                        }}
                    />
                </div>
            </div>

            <div className="avatar-controls">
                <div className="control-group">
                    <label>Expression:</label>
                    <div className="expression-buttons">
                        {['neutral', 'happy', 'sad', 'thinking', 'surprised', 'angry'].map(exp => (
                            <button
                                key={exp}
                                className={`exp-btn ${expression === exp ? 'active' : ''}`}
                                onClick={() => setExpression(exp)}
                            >
                                {exp}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="control-group">
                    <button
                        className={`talk-btn ${isTalking ? 'active' : ''}`}
                        onClick={toggleTalk}
                    >
                        {isTalking ? '🎤 Speaking...' : '▶️ Test Speech'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AIAvatar;
