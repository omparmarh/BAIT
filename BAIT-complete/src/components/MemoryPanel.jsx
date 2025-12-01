import React, { useState, useEffect } from 'react';
import './MemoryPanel.css';

/**
 * BAIT PRO ULTIMATE - Memory Panel Component
 * - Browse stored memories
 * - Search with semantic similarity
 * - Add new memories
 * - Memory type filtering
 */

const MemoryPanel = () => {
    const [memories, setMemories] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [newMemory, setNewMemory] = useState('');
    const [memoryType, setMemoryType] = useState('fact');
    const [importance, setImportance] = useState(5);
    const [isLoading, setIsLoading] = useState(false);
    const [filter, setFilter] = useState('all');

    // Fetch recent memories on mount
    useEffect(() => {
        loadRecentMemories();
    }, []);

    const loadRecentMemories = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('/api/ultimate/memory/recall', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: '', limit: 20 })
            });

            if (response.ok) {
                const data = await response.json();
                setMemories(data.memories || []);
            }
        } catch (error) {
            console.error('Failed to load memories:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const searchMemories = async () => {
        if (!searchQuery.trim()) {
            loadRecentMemories();
            return;
        }

        setIsLoading(true);
        try {
            const response = await fetch('/api/ultimate/memory/recall', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: searchQuery, limit: 20 })
            });

            if (response.ok) {
                const data = await response.json();
                setMemories(data.memories || []);
            }
        } catch (error) {
            console.error('Search failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const addMemory = async () => {
        if (!newMemory.trim()) return;

        try {
            const response = await fetch('/api/ultimate/memory/store', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: newMemory,
                    memory_type: memoryType,
                    importance: importance
                })
            });

            if (response.ok) {
                setNewMemory('');
                loadRecentMemories();
            }
        } catch (error) {
            console.error('Failed to add memory:', error);
        }
    };

    const getTypeIcon = (type) => {
        const icons = {
            preference: '❤️',
            fact: '📚',
            conversation: '💬',
            skill: '🎯',
            goal: '🎯',
            reminder: '⏰'
        };
        return icons[type] || '📝';
    };

    const getImportanceColor = (imp) => {
        if (imp >= 8) return '#ff6b6b';
        if (imp >= 5) return '#4ecdc4';
        return '#95a5a6';
    };

    const filteredMemories = memories.filter(m =>
        filter === 'all' || m.type === filter
    );

    return (
        <div className="memory-panel">
            <div className="memory-header">
                <h3>🧠 Memory System</h3>
                <div className="memory-stats">
                    {memories.length} memories
                </div>
            </div>

            {/* Search */}
            <div className="memory-search">
                <input
                    type="text"
                    placeholder="Search memories (semantic search)..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && searchMemories()}
                    className="search-input"
                />
                <button onClick={searchMemories} className="search-button">
                    🔍 Search
                </button>
            </div>

            {/* Add Memory */}
            <div className="memory-add">
                <textarea
                    placeholder="Add new memory..."
                    value={newMemory}
                    onChange={(e) => setNewMemory(e.target.value)}
                    className="memory-textarea"
                    rows={3}
                />
                <div className="memory-controls">
                    <select
                        value={memoryType}
                        onChange={(e) => setMemoryType(e.target.value)}
                        className="type-select"
                    >
                        <option value="fact">Fact</option>
                        <option value="preference">Preference</option>
                        <option value="conversation">Conversation</option>
                        <option value="skill">Skill</option>
                        <option value="goal">Goal</option>
                        <option value="reminder">Reminder</option>
                    </select>

                    <div className="importance-slider">
                        <label>Importance: {importance}</label>
                        <input
                            type="range"
                            min="1"
                            max="10"
                            value={importance}
                            onChange={(e) => setImportance(parseInt(e.target.value))}
                        />
                    </div>

                    <button onClick={addMemory} className="add-button">
                        ➕ Add Memory
                    </button>
                </div>
            </div>

            {/* Filter */}
            <div className="memory-filter">
                <button
                    className={filter === 'all' ? 'active' : ''}
                    onClick={() => setFilter('all')}
                >
                    All
                </button>
                <button
                    className={filter === 'preference' ? 'active' : ''}
                    onClick={() => setFilter('preference')}
                >
                    ❤️ Preferences
                </button>
                <button
                    className={filter === 'fact' ? 'active' : ''}
                    onClick={() => setFilter('fact')}
                >
                    📚 Facts
                </button>
                <button
                    className={filter === 'conversation' ? 'active' : ''}
                    onClick={() => setFilter('conversation')}
                >
                    💬 Conversations
                </button>
            </div>

            {/* Memory List */}
            <div className="memory-list">
                {isLoading ? (
                    <div className="loading">Loading memories...</div>
                ) : filteredMemories.length === 0 ? (
                    <div className="no-memories">No memories found</div>
                ) : (
                    filteredMemories.map((memory, index) => (
                        <div key={index} className="memory-item">
                            <div className="memory-icon">{getTypeIcon(memory.type)}</div>
                            <div className="memory-content">
                                <div className="memory-text">{memory.content}</div>
                                <div className="memory-meta">
                                    <span className="memory-type">{memory.type}</span>
                                    <span
                                        className="memory-importance"
                                        style={{ color: getImportanceColor(memory.importance) }}
                                    >
                                        ⭐ {memory.importance}/10
                                    </span>
                                    <span className="memory-date">
                                        {new Date(memory.timestamp).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default MemoryPanel;
