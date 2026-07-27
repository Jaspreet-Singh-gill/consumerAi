import { useState } from 'react';
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { Results } from './pages/Results';
import { NoticePreview } from './pages/NoticePreview';
import type { DisputeAnalysisResponse, NoticeDraftResponse } from './types';

function App() {
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<DisputeAnalysisResponse | null>(null);
  const [notice, setNotice] = useState<NoticeDraftResponse | null>(null);

  const handleAnalysisSuccess = (response: DisputeAnalysisResponse) => {
    setAnalysis(response);
    navigate('/results');
  };

  const handleNoticeGenerated = (response: NoticeDraftResponse) => {
    setNotice(response);
    navigate('/notice');
  };

  const handleStartOver = () => {
    setAnalysis(null);
    setNotice(null);
    navigate('/');
  };

  return (
    <>
      <header>
        <div>
          <h1>⚖️ ConsumerAi</h1>
          <span style={{ fontSize: '0.85rem', color: '#64748b' }}>
            India's Consumer Protection Act (CPA) 2019 Assessor
          </span>
        </div>
        <div style={{ fontSize: '0.9rem', color: '#4f46e5', fontWeight: 600 }}>
          RAG-Powered Legal Triaging
        </div>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<Home onAnalysisSuccess={handleAnalysisSuccess} />} />
          <Route path="/results" element={
            analysis ? (
              <Results 
                analysis={analysis} 
                onNoticeGenerated={handleNoticeGenerated}
                onBack={() => navigate('/')}
              />
            ) : (
              <Navigate to="/" replace />
            )
          } />
          <Route path="/notice" element={
            notice ? (
              <NoticePreview 
                notice={notice} 
                onBack={() => navigate('/results')}
                onStartOver={handleStartOver}
              />
            ) : (
              <Navigate to="/" replace />
            )
          } />
        </Routes>
      </main>
    </>
  );
}

export default App;
