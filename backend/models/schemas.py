from typing import List, Optional
from pydantic import BaseModel, Field

# 1. Structured Output from Fact Extraction Chain
class FactExtractionResult(BaseModel):
    category: str = Field(
        ..., 
        description="The category of the dispute. Must be one of: 'Defective/deficient goods', 'Deficiency in service', or 'Unfair trade practice / refund denial'."
    )
    amount: str = Field(
        ..., 
        description="The financial amount involved in the dispute (e.g. price paid, refund claimed, compensation requested). Format as currency like 'INR 50,000' or similar if available, otherwise 'Unknown'."
    )
    dates: List[str] = Field(
        default=[], 
        description="List of relevant dates mentioned in the dispute (e.g., date of purchase, date of flight, date of refund request)."
    )
    product_or_service: str = Field(
        ..., 
        description="The specific product or service in dispute (e.g., 'SUV', 'domestic flight ticket', 'UPSC course')."
    )
    seller_response: str = Field(
        ..., 
        description="The response or stance of the seller/service provider, or 'No response' if they didn't reply."
    )
    evidence_available: List[str] = Field(
        default=[], 
        description="List of evidence items mentioned (e.g. invoice, emails, service reports, photos)."
    )
    discrepancy_flag: bool = Field(
        ..., 
        description="True if there is an explicit contradiction between the buyer's claims and the seller's response, or between details, otherwise False."
    )
    discrepancy_description: str = Field(
        default="", 
        description="Description of the discrepancy if discrepancy_flag is True, otherwise empty."
    )


# 2. Structured Output from Assessment Chain
class AssessmentResult(BaseModel):
    strength: str = Field(
        ..., 
        description="The assessed strength of the consumer's case. Must be one of: 'Weak', 'Moderate', 'Strong'."
    )
    confidence: float = Field(
        ..., 
        description="Confidence score for the assessment between 0.0 (no confidence) and 1.0 (perfect confidence)."
    )
    reasoning: str = Field(
        ..., 
        description="Detailed legal and factual reasoning for the strength rating, based strictly on the provided context."
    )
    cited_sections: List[str] = Field(
        ..., 
        description="List of section numbers from the CPA 2019 that directly support the consumer's case (e.g. ['2(11)', '39'])."
    )
    cited_precedent_ids: List[str] = Field(
        ..., 
        description="List of case IDs of the retrieved precedents that are relevant and support the reasoning (e.g. ['NCDRC-2024-DS01'])."
    )


# 3. Document Representation for API Responses
class CPASectionDoc(BaseModel):
    section_no: str
    title: str
    text: str
    category_tags: List[str]


class PrecedentDoc(BaseModel):
    case_id: str
    category: str
    facts_summary: str
    sections_cited: List[str]
    outcome: str
    compensation_awarded: str
    key_reasoning: str


# 4. API Endpoints Payloads
class DisputeAnalysisResponse(BaseModel):
    facts: FactExtractionResult
    retrieved_sections: List[CPASectionDoc] = []
    retrieved_precedents: List[PrecedentDoc] = []
    assessment: AssessmentResult
    discrepancy_flag: bool
    pdf_status: str  # "processed" | "none" | "scanned_unreadable"
    disclaimer: str = "This is an AI-generated preliminary assessment, not legal advice."


class NoticeDraftRequest(BaseModel):
    facts: FactExtractionResult
    cited_sections: List[str]


class NoticeDraftResponse(BaseModel):
    notice_text: str
    disclaimer: str = "This is an AI-generated preliminary assessment, not legal advice."
