import { useEffect, useState } from 'react';
import './SystemStats.css';

const SystemStats = () => {
    const [stats, setStats] = useState({ cpu: 0, memory: 0, disk: 0 });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/stats');
                if (!response.ok) {
                    throw new Error('Failed to fetch stats');
                }
                const data = await response.json();

                // Check if data has the expected properties
                if (data && typeof data.cpu === 'number') {
                    setStats({
                        cpu: data.cpu || 0,
                        memory: data.memory || 0,
                        disk: data.disk || 0
                    });
                    setError(null);
                }
                setLoading(false);
            } catch (err) {
                console.error('Stats fetch error:', err);
                setError(err.message);
                setLoading(false);
                // Set default values on error
                setStats({ cpu: 0, memory: 0, disk: 0 });
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 2000);

        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="system-stats">
                <div className="stat-item">
                    <span className="stat-label">CPU</span>
                    <span className="stat-value">--</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">RAM</span>
                    <span className="stat-value">--</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">Disk</span>
                    <span className="stat-value">--</span>
                </div>
            </div>
        );
    }

    return (
        <div className="system-stats">
            <div className="stat-item">
                <span className="stat-label">CPU</span>
                <span className="stat-value">{stats.cpu?.toFixed(1) || 0}%</span>
            </div>
            <div className="stat-item">
                <span className="stat-label">RAM</span>
                <span className="stat-value">{stats.memory?.toFixed(1) || 0}%</span>
            </div>
            <div className="stat-item">
                <span className="stat-label">Disk</span>
                <span className="stat-value">{stats.disk?.toFixed(1) || 0}%</span>
            </div>
        </div>
    );
};

export default SystemStats;
