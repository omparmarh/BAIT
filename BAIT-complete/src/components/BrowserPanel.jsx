import React, { useState } from 'react';
import './BrowserPanel.css';

/**
 * BAIT PRO ULTIMATE - Browser Panel Component
 * - Google search interface
 * - Web scraping controls
 * - Search results display
 * - URL navigation
 */

const BrowserPanel = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [scrapeUrl, setScrapeUrl] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [scrapeData, setScrapeData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('search'); // search or scrape

    const performSearch = async () => {
        if (!searchQuery.trim()) return;

        setIsLoading(true);
        try {
            const response = await fetch('/api/ultimate/browser/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: searchQuery })
            });

            if (response.ok) {
                const data = await response.json();
                setSearchResults(data.results || []);
            }
        } catch (error) {
            console.error('Search failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const scrapePage = async () => {
        if (!scrapeUrl.trim()) return;

        setIsLoading(true);
        try {
            const response = await fetch('/api/ultimate/browser/scrape', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: scrapeUrl })
            });

            if (response.ok) {
                const data = await response.json();
                setScrapeData(data.data || {});
            }
        } catch (error) {
            console.error('Scraping failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="browser-panel">
            <div className="browser-header">
                <h3>🌐 Web Browser Agent</h3>
                <div className="browser-tabs">
                    <button
                        className={activeTab === 'search' ? 'active' : ''}
                        onClick={() => setActiveTab('search')}
                    >
                        🔍 Search
                    </button>
                    <button
                        className={activeTab === 'scrape' ? 'active' : ''}
                        onClick={() => setActiveTab('scrape')}
                    >
                        📄 Scrape
                    </button>
                </div>
            </div>

            {/* Search Tab */}
            {activeTab === 'search' && (
                <div className="search-section">
                    <div className="search-bar">
                        <input
                            type="text"
                            placeholder="Search Google..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && performSearch()}
                            className="search-input"
                        />
                        <button
                            onClick={performSearch}
                            disabled={isLoading}
                            className="search-btn"
                        >
                            {isLoading ? '⏳' : '🔍'} Search
                        </button>
                    </div>

                    {/* Search Results */}
                    <div className="results-container">
                        {isLoading ? (
                            <div className="loading">Searching...</div>
                        ) : searchResults.length === 0 ? (
                            <div className="no-results">
                                <p>No results yet. Try searching above!</p>
                            </div>
                        ) : (
                            <div className="results-list">
                                <div className="results-count">
                                    {searchResults.length} results found
                                </div>
                                {searchResults.map((result, index) => (
                                    <div key={index} className="result-item">
                                        <a
                                            href={result.link}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="result-title"
                                        >
                                            {result.title}
                                        </a>
                                        <div className="result-url">{result.link}</div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Scrape Tab */}
            {activeTab === 'scrape' && (
                <div className="scrape-section">
                    <div className="scrape-bar">
                        <input
                            type="url"
                            placeholder="Enter URL to scrape..."
                            value={scrapeUrl}
                            onChange={(e) => setScrapeUrl(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && scrapePage()}
                            className="scrape-input"
                        />
                        <button
                            onClick={scrapePage}
                            disabled={isLoading}
                            className="scrape-btn"
                        >
                            {isLoading ? '⏳' : '📄'} Scrape
                        </button>
                    </div>

                    {/* Scrape Results */}
                    <div className="scrape-results">
                        {isLoading ? (
                            <div className="loading">Scraping page...</div>
                        ) : !scrapeData ? (
                            <div className="no-results">
                                <p>No data yet. Enter a URL above!</p>
                            </div>
                        ) : (
                            <div className="scrape-data">
                                <div className="data-section">
                                    <h5>📝 Extracted Text</h5>
                                    <div className="text-preview">
                                        {scrapeData.text
                                            ? scrapeData.text.substring(0, 500) + '...'
                                            : 'No text extracted'}
                                    </div>
                                    <div className="text-stats">
                                        {scrapeData.text?.length || 0} characters
                                    </div>
                                </div>

                                {scrapeData.links && scrapeData.links.length > 0 && (
                                    <div className="data-section">
                                        <h5>🔗 Links Found ({scrapeData.links.length})</h5>
                                        <div className="links-list">
                                            {scrapeData.links.slice(0, 10).map((link, idx) => (
                                                <div key={idx} className="link-item">
                                                    <a
                                                        href={link.href}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                    >
                                                        {link.text || link.href}
                                                    </a>
                                                </div>
                                            ))}
                                            {scrapeData.links.length > 10 && (
                                                <div className="more-links">
                                                    +{scrapeData.links.length - 10} more links
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default BrowserPanel;
