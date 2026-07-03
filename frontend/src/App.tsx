import { useState } from 'react';
import { Home } from './pages/Home';
import { Results } from './pages/Results';
import { NoticePreview } from './pages/NoticePreview';
import type { DisputeAnalysisResponse, NoticeDraftResponse } from './types';

function App() {
  const [page, setPage] = useState<'home' | 'results' | 'notice'>('home');
  const [analysis, setAnalysis] = useState<DisputeAnalysisResponse | null>(null);
  const [notice, setNotice] = useState<NoticeDraftResponse | null>(null);

  const handleAnalysisSuccess = (response: DisputeAnalysisResponse) => {
    setAnalysis(response);
    setPage('results');
  };

  const handleNoticeGenerated = (response: NoticeDraftResponse) => {
    setNotice(response);
    setPage('notice');
  };

  const handleStartOver = () => {
    setAnalysis(null);
    setNotice(null);
    setPage('home');
  };

  return (
    <>
      <header>
        <div>
          <h1>⚖️ Consumer Rights Triage</h1>
          <span style={{ fontSize: '0.85rem', color: '#64748b' }}>
            India's Consumer Protection Act (CPA) 2019 Assessor
          </span>
        </div>
        <div style={{ fontSize: '0.9rem', color: '#4f46e5', fontWeight: 600 }}>
          RAG-Powered Legal Triaging
        </div>
      </header>

      <main>
        {page === 'home' && (
          <Home onAnalysisSuccess={handleAnalysisSuccess} />
        )}

        {page === 'results' && analysis && (
          <Results 
            analysis={analysis} 
            onNoticeGenerated={handleNoticeGenerated}
            onBack={() => setPage('home')}
          />
        )}

        {page === 'notice' && notice && (
          <NoticePreview 
            notice={notice} 
            onBack={() => setPage('results')}
            onStartOver={handleStartOver}
          />
        )}
      </main>
    </>
  );
}

export default App;
