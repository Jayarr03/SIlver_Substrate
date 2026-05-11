import { useState } from 'react';
import './App.css';
import ComponentForm from './ComponentForm';
import AssessmentList from './AssessmentList';

function App() {
  const [view, setView] = useState('list');
  const [refreshKey, setRefreshKey] = useState(0);

  const handleAssessmentCreated = () => {
    setRefreshKey(prev => prev + 1);
    setView('list');
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🔒 Silver Substrate</h1>
        <p className="subtitle">Silicon-Layer Threat Modeling</p>
      </header>

      <nav className="app-nav">
        <button 
          className={view === 'list' ? 'active' : ''}
          onClick={() => setView('list')}
        >
          📚 Library
        </button>
        <button 
          className={view === 'create' ? 'active' : ''}
          onClick={() => setView('create')}
        >
          ➕ New Assessment
        </button>
      </nav>

      <main className="app-main">
        {view === 'list' && (
          <AssessmentList refreshKey={refreshKey} />
        )}
        {view === 'create' && (
          <ComponentForm onAssessmentCreated={handleAssessmentCreated} />
        )}
      </main>
    </div>
  );
}

export default App;
