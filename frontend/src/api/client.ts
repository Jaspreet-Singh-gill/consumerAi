import type {
  DisputeAnalysisResponse,
  FactExtractionResult,
  NoticeDraftResponse,
  PrecedentDoc
} from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000';

export async function analyzeDispute(
  description: string,
  evidencePdf?: File
): Promise<DisputeAnalysisResponse> {
  const formData = new FormData();
  formData.append('description', description);
  if (evidencePdf) {
    formData.append('evidence_pdf', evidencePdf);
  }

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Analysis request failed with status ${response.status}`);
  }

  return response.json();
}

export async function draftNotice(
  facts: FactExtractionResult,
  citedSections: string[]
): Promise<NoticeDraftResponse> {
  const response = await fetch(`${API_BASE_URL}/draft-notice`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      facts,
      cited_sections: citedSections,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Notice drafting failed with status ${response.status}`);
  }

  return response.json();
}

export async function getPrecedent(caseId: string): Promise<PrecedentDoc> {
  const response = await fetch(`${API_BASE_URL}/precedents/${caseId}`, {
    method: 'GET',
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch precedent: ${caseId}`);
  }

  return response.json();
}
