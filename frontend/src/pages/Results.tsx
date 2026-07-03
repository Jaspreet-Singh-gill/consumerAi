import React, { useState } from 'react';
import type { DisputeAnalysisResponse, NoticeDraftResponse } from '../types';
import { draftNotice } from '../api/client';

interface ResultsProps {
  analysis: DisputeAnalysisResponse;
  onNoticeGenerated: (noticeResponse: NoticeDraftResponse) => void;
  onBack: () => void;
}

export const Results: React.FC<ResultsProps> = ({ analysis, onNoticeGenerated, onBack }) => {
  const { facts, retrieved_sections, retrieved_precedents, assessment, discrepancy_flag, pdf_status } = analysis;
  const [drafting, setDrafting] = useState(false);
  const [draftError, setDraftError] = useState<string | null>(null);

  // States to track open/close for accordion sections
  const [openSectionIndex, setOpenSectionIndex] = useState<number | null>(null);
  const [openPrecedentIndex, setOpenPrecedentIndex] = useState<number | null>(null);

  const getStrengthBadgeClass = (strength: string) => {
    switch (strength.toLowerCase()) {
      case 'strong':
        return 'badge badge-strong';
      case 'moderate':
        return 'badge badge-moderate';
      case 'weak':
        return 'badge badge-weak';
      default:
        return 'badge';
    }
  };

  const getOutcomeBadgeClass = (outcome: string) => {
    switch (outcome.toLowerCase()) {
      case 'consumer_won':
        return 'badge badge-outcome-won';
      case 'consumer_lost':
        return 'badge badge-outcome-lost';
      case 'partial':
        return 'badge badge-outcome-partial';
      default:
        return 'badge';
    }
  };

  const getOutcomeText = (outcome: string) => {
    switch (outcome.toLowerCase()) {
      case 'consumer_won':
        return 'Consumer Won';
      case 'consumer_lost':
        return 'Consumer Lost';
      case 'partial':
        return 'Partial Success';
      default:
        return outcome;
    }
  };

  const handleGenerateNotice = async () => {
    setDrafting(true);
    setDraftError(null);

    try {
      const response = await draftNotice(facts, assessment.cited_sections);
      onNoticeGenerated(response);
    } catch (err: any) {
      console.error(err);
      setDraftError(err.message || 'Failed to generate legal notice draft.');
    } finally {
      setDrafting(false);
    }
  };

  // Find detailed objects for cited sections and precedents from our retrieved lists
  const citedSectionsWithDetails = assessment.cited_sections.map(secNo => {
    const detail = retrieved_sections.find(s => s.section_no === secNo);
    return {
      section_no: secNo,
      title: detail ? detail.title : 'Consumer Protection Act Provision',
      text: detail ? detail.text : 'Details retrieved from standard CPA reference.',
    };
  });

  const citedPrecedentsWithDetails = assessment.cited_precedent_ids.map(caseId => {
    const detail = retrieved_precedents.find(p => p.case_id === caseId);
    return {
      case_id: caseId,
      category: detail ? detail.category : 'NCDRC Judgment',
      facts_summary: detail ? detail.facts_summary : 'Facts of NCDRC Precedent case.',
      outcome: detail ? detail.outcome : 'consumer_won',
      compensation_awarded: detail ? detail.compensation_awarded : 'Unknown',
      key_reasoning: detail ? detail.key_reasoning : 'Legal interpretation.',
    };
  });

  return (
    <div>
      <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
        <button onClick={onBack} className="secondary">
          &larr; Back to Assessment
        </button>
        <span style={{ fontSize: '0.9rem', color: '#64748b' }}>
          PDF Status: <strong>{pdf_status}</strong>
        </span>
      </div>

      {discrepancy_flag && (
        <div className="banner banner-warning" id="discrepancy-banner">
          <strong>⚠️ Discrepancy Flagged:</strong> {facts.discrepancy_description || 'There is an inconsistency between the claims made in your statement and the details found in your evidence.'}
        </div>
      )}

      {pdf_status === 'scanned_unreadable' && (
        <div className="banner banner-info">
          <strong>ℹ️ PDF Text Unreadable:</strong> The uploaded document appears to be scanned or contains near-empty text. The system proceeded using your typed description only.
        </div>
      )}

      <div className="card">
        <div className="flex-between" style={{ borderBottom: '1px solid #f1f5f9', paddingBottom: '1rem', marginBottom: '1rem' }}>
          <div>
            <h2 style={{ marginBottom: '0.25rem' }}>Case Analysis</h2>
            <span style={{ fontSize: '0.9rem', color: '#64748b' }}>
              Category: <strong>{facts.category}</strong> | Product/Service: <strong>{facts.product_or_service}</strong>
            </span>
          </div>
          <div className="text-right">
            <span className={getStrengthBadgeClass(assessment.strength)} style={{ fontSize: '1.2rem', padding: '0.5rem 1rem' }}>
              {assessment.strength} Case
            </span>
            <div style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '0.25rem' }}>
              Confidence: <strong>{Math.round(assessment.confidence * 100)}%</strong>
            </div>
          </div>
        </div>

        <div style={{ margin: '1.5rem 0' }}>
          <h3>Extracted Case Facts</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.95rem' }}>
            <tbody>
              <tr style={{ borderBottom: '1px solid #f1f5f9' }}>
                <td style={{ padding: '0.5rem 0', fontWeight: 600, width: '30%', color: '#475569' }}>Dispute Value:</td>
                <td style={{ padding: '0.5rem 0' }}>{facts.amount}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid #f1f5f9' }}>
                <td style={{ padding: '0.5rem 0', fontWeight: 600, color: '#475569' }}>Dates Referenced:</td>
                <td style={{ padding: '0.5rem 0' }}>{facts.dates.join(', ') || 'None specified'}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid #f1f5f9' }}>
                <td style={{ padding: '0.5rem 0', fontWeight: 600, color: '#475569' }}>Seller Response:</td>
                <td style={{ padding: '0.5rem 0' }}>{facts.seller_response}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid #f1f5f9' }}>
                <td style={{ padding: '0.5rem 0', fontWeight: 600, color: '#475569' }}>Available Evidence:</td>
                <td style={{ padding: '0.5rem 0' }}>{facts.evidence_available.join(', ') || 'No file uploaded'}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div style={{ margin: '1.5rem 0' }}>
          <h3>Legal Reasoning & Strength Assessment</h3>
          <p style={{ whiteSpace: 'pre-wrap', color: '#334155', lineHeight: 1.6 }}>{assessment.reasoning}</p>
        </div>
      </div>

      <div className="grid-2">
        <div>
          <h3>Cited CPA 2019 Sections ({citedSectionsWithDetails.length})</h3>
          <p style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '0.75rem' }}>
            Sections of the Act applicable to your claim:
          </p>
          {citedSectionsWithDetails.map((sec, idx) => (
            <div className="accordion" key={sec.section_no}>
              <div 
                className="accordion-header" 
                onClick={() => setOpenSectionIndex(openSectionIndex === idx ? null : idx)}
              >
                <span>Section {sec.section_no}: {sec.title}</span>
                <span>{openSectionIndex === idx ? '▲' : '▼'}</span>
              </div>
              {openSectionIndex === idx && (
                <div className="accordion-content">
                  <p style={{ fontSize: '0.9rem', color: '#334155', margin: 0, fontStyle: 'italic' }}>
                    {sec.text}
                  </p>
                </div>
              )}
            </div>
          ))}
          {citedSectionsWithDetails.length === 0 && (
            <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>No specific CPA sections cited in reasoning.</p>
          )}
        </div>

        <div>
          <h3>Supporting Precedents ({citedPrecedentsWithDetails.length})</h3>
          <p style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '0.75rem' }}>
            NCDRC decisions supporting this assessment:
          </p>
          {citedPrecedentsWithDetails.map((prec, idx) => (
            <div className="accordion" key={prec.case_id}>
              <div 
                className="accordion-header" 
                onClick={() => setOpenPrecedentIndex(openPrecedentIndex === idx ? null : idx)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <strong>{prec.case_id}</strong>
                  <span className={getOutcomeBadgeClass(prec.outcome)}>
                    {getOutcomeText(prec.outcome)}
                  </span>
                </div>
                <span>{openPrecedentIndex === idx ? '▲' : '▼'}</span>
              </div>
              {openPrecedentIndex === idx && (
                <div className="accordion-content" style={{ fontSize: '0.9rem', color: '#334155' }}>
                  <p style={{ margin: '0 0 0.5rem 0' }}><strong>Facts:</strong> {prec.facts_summary}</p>
                  <p style={{ margin: '0 0 0.5rem 0' }}><strong>Awarded:</strong> {prec.compensation_awarded}</p>
                  <p style={{ margin: 0 }}><strong>Reasoning:</strong> {prec.key_reasoning}</p>
                </div>
              )}
            </div>
          ))}
          {citedPrecedentsWithDetails.length === 0 && (
            <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>No past case precedents cited in reasoning.</p>
          )}
        </div>
      </div>

      {draftError && (
        <div className="banner banner-error" style={{ marginTop: '1.5rem' }}>
          <strong>Notice Drafting Error:</strong> {draftError}
        </div>
      )}

      <div style={{ marginTop: '2.5rem', textAlign: 'center' }}>
        <button 
          onClick={handleGenerateNotice} 
          disabled={drafting || citedSectionsWithDetails.length === 0} 
          id="draft-notice-btn"
          style={{ padding: '1rem 3rem', fontSize: '1.1rem' }}
        >
          {drafting ? 'Drafting Legal Notice with Grok...' : 'Generate Legal Notice Draft'}
        </button>
        {citedSectionsWithDetails.length === 0 && (
          <p style={{ color: '#ef4444', fontSize: '0.85rem', marginTop: '0.5rem' }}>
            Cannot generate notice without applicable legal sections cited in the reasoning.
          </p>
        )}
      </div>

      <div className="disclaimer">
        {analysis.disclaimer}
      </div>
    </div>
  );
};
