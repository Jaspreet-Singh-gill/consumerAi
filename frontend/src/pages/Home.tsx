import React, { useState } from 'react';
import { analyzeDispute } from '../api/client';
import type { DisputeAnalysisResponse } from '../types';

interface HomeProps {
  onAnalysisSuccess: (response: DisputeAnalysisResponse) => void;
}

export const Home: React.FC<HomeProps> = ({ onAnalysisSuccess }) => {
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) {
      setFile(null);
      return;
    }

    // Validation: Check file extension
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setError('Invalid file type. Only PDF documents are accepted.');
      setFile(null);
      e.target.value = '';
      return;
    }

    // Validation: Check file size (>5MB)
    const maxSize = 5 * 1024 * 1024;
    if (selectedFile.size > maxSize) {
      setError('File size exceeds the 5MB limit. Please upload a smaller PDF.');
      setFile(null);
      e.target.value = '';
      return;
    }

    setFile(selectedFile);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) {
      setError('Please provide a description of your dispute.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await analyzeDispute(description, file || undefined);
      onAnalysisSuccess(response);
    } catch (err: any) {
      console.error(err);
      setError(
        'An error occurred while analyzing the dispute. AI might be experiencing downtime; please try again later.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="card">
        <h2>Assess Your Dispute</h2>
        <p style={{ color: '#475569', marginBottom: '1.5rem' }}>
          Describe your dispute in detail. Our AI-assisted triage tool will extract key facts, 
          retrieve relevant provisions of India's Consumer Protection Act (CPA), 2019, 
          evaluate case strength based on past precedents, and draft a legal notice.
        </p>

        {error && (
          <div className="banner banner-error" id="error-banner">
            <strong>Error:</strong> {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="description" style={{ fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
              Dispute Details <span style={{ color: '#dc2626' }}>*</span>
            </label>
            <textarea
              id="description"
              placeholder="Example: I ordered a smartphone from Flipkart on June 10, 2026, for INR 15,000. However, when the parcel arrived, it contained a washing soap instead of the phone. I raised a complaint with customer support on June 12, but they rejected my refund claim saying the package was delivered successfully. I have the unboxing video and the invoice."
              value={description}
              onChange={(e) => {
                setDescription(e.target.value);
                if (error) setError(null);
              }}
              required
            />
          </div>

          <div className="file-input-wrapper">
            <label htmlFor="evidence" style={{ fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
              Upload Evidence PDF (Optional, max 5MB)
            </label>
            <input
              id="evidence"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
            />
            <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem' }}>
              Attach invoices, service reports, booking tickets, or emails as evidence.
            </p>
          </div>

          <button type="submit" disabled={loading} id="submit-btn" style={{ width: '100%' }}>
            {loading ? 'Analyzing Case Details' : 'Submit Assessment'}
          </button>
        </form>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h3>Categories Covered:</h3>
        <ul style={{ color: '#475569', paddingLeft: '1.25rem' }}>
          <li><strong>Defective/deficient goods:</strong> Manufacturing defects, faulty appliances, smart-phone disputes, auto-parts etc.</li>
          <li><strong>Deficiency in service:</strong> Flight cancellations, medical negligence, delay in construction, utility outages etc.</li>
          <li><strong>Unfair trade practice / refund denial:</strong> Misleading ads, Ed-tech platform refund delays, false discount representations.</li>
        </ul>
      </div>
    </div>
  );
};
