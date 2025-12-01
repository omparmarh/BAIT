import { useState } from 'react';
import './App.css';
import './styles/themes.css';
import { ThemeProvider } from './context/ThemeContext';
import ThemeToggle from './components/ThemeToggle';
import SystemStats from './components/SystemStats';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';

// BAIT PRO ULTIMATE Components
import VoiceInput from './components/VoiceInput';
import MemoryPanel from './components/MemoryPanel';
import WorkflowManager from './components/WorkflowManager';
import ScreenPreview from './components/ScreenPreview';
import CameraView from './components/CameraView';
import BrowserPanel from './components/BrowserPanel';
import DesktopAgent from './components/DesktopAgent';
import FileManager from './components/FileManager';
import IntegrationPanel from './components/IntegrationPanel';

function App() {
  const [conversationId, setConversationId] = useState(null);
  const [activeFeature, setActiveFeature] = useState('chat'); // Default to chat

  const features = [
    { id: 'chat', name: '💬 Chat', component: null },
    { id: 'voice', name: '🎤 Voice', component: <VoiceInput /> },
    { id: 'memory', name: '🧠 Memory', component: <MemoryPanel /> },
    { id: 'workflow', name: '⚡ Workflows', component: <WorkflowManager /> },
    { id: 'screen', name: '📸 Screen', component: <ScreenPreview /> },
    { id: 'camera', name: '📷 Camera', component: <CameraView /> },
    { id: 'browser', name: '🌐 Browser', component: <BrowserPanel /> },
    { id: 'desktop', name: '🖥️ Desktop', component: <DesktopAgent /> },
    { id: 'files', name: '📁 Files', component: <FileManager /> },
    { id: 'integrations', name: '🔌 APIs', component: <IntegrationPanel /> }
  ];

  return (
    <ThemeProvider>
      <div className="app-container bait-ultimate">
        {/* HEADER WITH THEME TOGGLE */}
        <header className="app-header ultimate-header">
          <div className="header-left">
            <h1>🤖 BAIT PRO ULTIMATE</h1>
            <p>Advanced AI Assistant with 10 Modules</p>
          </div>
          <div className="header-right">
            <SystemStats />
            <ThemeToggle />
          </div>
        </header>

        {/* FEATURE NAVIGATION */}
        <nav className="feature-nav">
          {features.map(feature => (
            <button
              key={feature.id}
              className={`feature-tab ${activeFeature === feature.id ? 'active' : ''}`}
              onClick={() => setActiveFeature(feature.id)}
            >
              {feature.name}
            </button>
          ))}
        </nav>

        {/* MAIN CONTENT */}
        <div className="app-main ultimate-main">
          {activeFeature === 'chat' ? (
            <>
              <Sidebar onConversationSelect={setConversationId} />
              <ChatInterface
                conversationId={conversationId}
                onConversationCreated={setConversationId}
              />
            </>
          ) : (
            <div className="feature-panel">
              {features.find(f => f.id === activeFeature)?.component}
            </div>
          )}
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;

