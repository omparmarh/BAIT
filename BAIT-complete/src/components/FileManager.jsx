import React, { useState } from 'react';
import './FileManager.css';

/**
 * BAIT PRO ULTIMATE - File Manager Component
 * - File search with indexing
 * - Directory organization
 * - Duplicate file detection
 * - File operations
 */

const FileManager = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchDirectory, setSearchDirectory] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [organizeDir, setOrganizeDir] = useState('');
    const [organizeMethod, setOrganizeMethod] = useState('type');
    const [duplicates, setDuplicates] = useState({});
    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('search'); // search, organize, duplicates

    const searchFiles = async () => {
        if (!searchQuery.trim()) return;

        setIsLoading(true);
        try {
            const response = await fetch('/api/ultimate/files/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: searchQuery,
                    directory: searchDirectory || null,
                    limit: 50
                })
            });

            if (response.ok) {
                const data = await response.json();
                setSearchResults(data.files || []);
            }
        } catch (error) {
            console.error('Search failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const organizeDirectory = async () => {
        if (!organizeDir.trim()) return;

        setIsLoading(true);
        try {
            const response = await fetch('/api/ultimate/files/organize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    directory: organizeDir,
                    method: organizeMethod
                })
            });

            if (response.ok) {
                const data = await response.json();
                alert(`Organized! Stats: ${JSON.stringify(data.stats)}`);
            }
        } catch (error) {
            console.error('Organization failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const findDuplicates = async () => {
        if (!organizeDir.trim()) return;

        setIsLoading(true);
        try {
            const response = await fetch(`/api/ultimate/files/duplicates/${encodeURIComponent(organizeDir)}`);

            if (response.ok) {
                const data = await response.json();
                setDuplicates(data.duplicates || {});
            }
        } catch (error) {
            console.error('Duplicate search failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const formatFileSize = (bytes) => {
        if (!bytes) return 'Unknown';
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
        if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
        return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
    };

    return (
        <div className="file-manager">
            <div className="file-header">
                <h3>📁 File Manager</h3>
                <div className="file-tabs">
                    <button
                        className={activeTab === 'search' ? 'active' : ''}
                        onClick={() => setActiveTab('search')}
                    >
                        🔍 Search
                    </button>
                    <button
                        className={activeTab === 'organize' ? 'active' : ''}
                        onClick={() => setActiveTab('organize')}
                    >
                        📂 Organize
                    </button>
                    <button
                        className={activeTab === 'duplicates' ? 'active' : ''}
                        onClick={() => setActiveTab('duplicates')}
                    >
                        🔄 Duplicates
                    </button>
                </div>
            </div>

            {/* Search Tab */}
            {activeTab === 'search' && (
                <div className="search-tab">
                    <div className="search-inputs">
                        <input
                            type="text"
                            placeholder="Search for files..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && searchFiles()}
                            className="file-input"
                        />
                        <input
                            type="text"
                            placeholder="Directory (optional)"
                            value={searchDirectory}
                            onChange={(e) => setSearchDirectory(e.target.value)}
                            className="file-input small"
                        />
                        <button onClick={searchFiles} disabled={isLoading} className="file-btn">
                            {isLoading ? '⏳' : '🔍'} Search
                        </button>
                    </div>

                    <div className="results-area">
                        {isLoading ? (
                            <div className="loading">Searching...</div>
                        ) : searchResults.length === 0 ? (
                            <div className="no-results">No files found</div>
                        ) : (
                            <div className="file-results">
                                <div className="results-header">
                                    {searchResults.length} files found
                                </div>
                                {searchResults.map((file, idx) => (
                                    <div key={idx} className="file-item">
                                        <div className="file-icon">📄</div>
                                        <div className="file-info">
                                            <div className="file-name">{file.filename}</div>
                                            <div className="file-meta">
                                                <span>{formatFileSize(file.size)}</span>
                                                <span>{file.modified}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Organize Tab */}
            {activeTab === 'organize' && (
                <div className="organize-tab">
                    <div className="organize-inputs">
                        <input
                            type="text"
                            placeholder="Directory to organize..."
                            value={organizeDir}
                            onChange={(e) => setOrganizeDir(e.target.value)}
                            className="file-input"
                        />
                        <select
                            value={organizeMethod}
                            onChange={(e) => setOrganizeMethod(e.target.value)}
                            className="file-select"
                        >
                            <option value="type">By File Type</option>
                            <option value="date">By Date</option>
                        </select>
                        <button onClick={organizeDirectory} disabled={isLoading} className="file-btn">
                            {isLoading ? '⏳' : '📂'} Organize
                        </button>
                    </div>

                    <div className="organize-info">
                        <h5>How it works:</h5>
                        <ul>
                            <li><strong>By Type:</strong> Groups files into folders (Documents, Images, Videos, etc.)</li>
                            <li><strong>By Date:</strong> Groups files by modification date (Year/Month folders)</li>
                        </ul>
                    </div>
                </div>
            )}

            {/* Duplicates Tab */}
            {activeTab === 'duplicates' && (
                <div className="duplicates-tab">
                    <div className="duplicate-inputs">
                        <input
                            type="text"
                            placeholder="Directory to scan..."
                            value={organizeDir}
                            onChange={(e) => setOrganizeDir(e.target.value)}
                            className="file-input"
                        />
                        <button onClick={findDuplicates} disabled={isLoading} className="file-btn">
                            {isLoading ? '⏳' : '🔄'} Find Duplicates
                        </button>
                    </div>

                    <div className="duplicates-results">
                        {isLoading ? (
                            <div className="loading">Scanning for duplicates...</div>
                        ) : Object.keys(duplicates).length === 0 ? (
                            <div className="no-results">No duplicates found</div>
                        ) : (
                            <div className="duplicate-groups">
                                <div className="results-header">
                                    {Object.keys(duplicates).length} duplicate groups found
                                </div>
                                {Object.entries(duplicates).map(([hash, files], idx) => (
                                    <div key={idx} className="duplicate-group">
                                        <div className="group-header">
                                            Group {idx + 1} ({files.length} files)
                                        </div>
                                        {files.map((file, fileIdx) => (
                                            <div key={fileIdx} className="duplicate-file">
                                                📄 {file}
                                            </div>
                                        ))}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default FileManager;
