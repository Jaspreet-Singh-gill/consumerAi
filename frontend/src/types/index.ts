export interface FactExtractionResult {
  category: string;
  amount: string;
  dates: string[];
  product_or_service: string;
  seller_response: string;
  evidence_available: string[];
  discrepancy_flag: boolean;
  discrepancy_description: string;
}

export interface AssessmentResult {
  strength: 'Weak' | 'Moderate' | 'Strong';
  confidence: number; // 0 to 1
  reasoning: string;
  cited_sections: string[];
  cited_precedent_ids: string[];
}

export interface CPASectionDoc {
  section_no: string;
  title: string;
  text: string;
  category_tags: string[];
}

export interface PrecedentDoc {
  case_id: string;
  category: string;
  facts_summary: string;
  sections_cited: string[];
  outcome: 'consumer_won' | 'consumer_lost' | 'partial';
  compensation_awarded: string;
  key_reasoning: string;
}

export interface DisputeAnalysisResponse {
  facts: FactExtractionResult;
  retrieved_sections: CPASectionDoc[];
  retrieved_precedents: PrecedentDoc[];
  assessment: AssessmentResult;
  discrepancy_flag: boolean;
  pdf_status: 'processed' | 'none' | 'scanned_unreadable';
  disclaimer: string;
}

export interface NoticeDraftRequest {
  facts: FactExtractionResult;
  cited_sections: string[];
}

export interface NoticeDraftResponse {
  notice_text: string;
  disclaimer: string;
}
