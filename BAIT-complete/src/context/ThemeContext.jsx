import { createContext, useContext, useEffect, useState } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
    const [theme, setTheme] = useState('dark');
    const [isSystemPreference, setIsSystemPreference] = useState(false);

    // ═══════════════════════════════════════════════════════════
    // INITIALIZE THEME FROM STORAGE OR SYSTEM
    // ═══════════════════════════════════════════════════════════
    useEffect(() => {
        const savedTheme = localStorage.getItem('bait-theme');
        const savedPreference = localStorage.getItem('bait-use-system');

        if (savedPreference === 'true') {
            setIsSystemPreference(true);
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            setTheme(systemTheme);
        } else if (savedTheme) {
            setTheme(savedTheme);
        }
    }, []);

    // ═══════════════════════════════════════════════════════════
    // APPLY THEME TO DOCUMENT
    // ═══════════════════════════════════════════════════════════
    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
    }, [theme]);

    // ═══════════════════════════════════════════════════════════
    // LISTEN TO SYSTEM THEME CHANGES
    // ═══════════════════════════════════════════════════════════
    useEffect(() => {
        if (!isSystemPreference) return;

        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const handleChange = (e) => {
            setTheme(e.matches ? 'dark' : 'light');
        };

        mediaQuery.addEventListener('change', handleChange);
        return () => mediaQuery.removeEventListener('change', handleChange);
    }, [isSystemPreference]);

    // ═══════════════════════════════════════════════════════════
    // TOGGLE THEME
    // ═══════════════════════════════════════════════════════════
    const toggleTheme = () => {
        const newTheme = theme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
        setIsSystemPreference(false);
        localStorage.setItem('bait-theme', newTheme);
        localStorage.setItem('bait-use-system', 'false');
    };

    // ═══════════════════════════════════════════════════════════
    // USE SYSTEM THEME
    // ═══════════════════════════════════════════════════════════
    const useSystemTheme = () => {
        setIsSystemPreference(true);
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        setTheme(systemTheme);
        localStorage.setItem('bait-use-system', 'true');
    };

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme, useSystemTheme, isSystemPreference }}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within ThemeProvider');
    }
    return context;
};
