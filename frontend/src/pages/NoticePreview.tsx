import React, { useState } from 'react';
import type { NoticeDraftResponse } from '../types';

interface NoticePreviewProps {
  notice: NoticeDraftResponse;
  onBack: () => void;
  onStartOver: () => void;
}

export const NoticePreview: React.FC<NoticePreviewProps> = ({ notice, onBack, onStartOver }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(notice.notice_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <div className="card">
      <div className="flex-between" style={{ marginBottom: '1.5rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '1rem' }}>
        <h2>Drafted Legal Notice</h2>
        <div>
          <button onClick={onBack} className="secondary" style={{ marginRight: '0.5rem' }}>
            &larr; Back to Results
          </button>
          <button onClick={onStartOver} className="secondary">
            Start Over
          </button>
        </div>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <p style={{ color: '#475569', fontSize: '0.95rem' }}>
          Below is the AI-generated legal notice draft. You can copy the text, fill in the placeholders 
          (such as names and addresses), and send it to the opposite party as a formal notice.
        </p>
      </div>

      <div style={{ textAlign: 'right', marginBottom: '0.5rem' }}>
        <button onClick={handleCopy} id="copy-btn" style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}>
          {copied ? '✓ Copied to Clipboard!' : '📋 Copy Notice Text'}
        </button>
      </div>

      <div className="notice-box" id="notice-content">
        {notice.notice_text}
      </div>

      <div className="disclaimer">
        {notice.disclaimer}
      </div>
    </div>
  );
};
