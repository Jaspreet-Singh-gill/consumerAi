from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.models.schemas import (
    DisputeAnalysisResponse,
    CPASectionDoc,
    PrecedentDoc
)
from backend.services.pdf_extractor import extract_text_from_pdf
from backend.services.retrieval_service import retrieve_context
from backend.chains.fact_extraction_chain import fact_extraction_chain
from backend.chains.assessment_chain import assessment_chain

router = APIRouter()

@router.post("/analyze", response_model=DisputeAnalysisResponse)
async def analyze_dispute(
    description: str = Form(...),
    evidence_pdf: Optional[UploadFile] = File(None)
):
    # Validate empty input
    if not description.strip():
        raise HTTPException(status_code=400, detail="Description text cannot be empty.")

    pdf_bytes = b""
    pdf_status = "none"
    evidence_text = ""

    # Process PDF evidence if uploaded
    if evidence_pdf:
        # Check file extension
        if not evidence_pdf.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
        
        pdf_bytes = await evidence_pdf.read()
        
        # Check file size (>5MB)
        if len(pdf_bytes) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="PDF file size exceeds the 5MB limit.")

        # Extract text
        evidence_text, pdf_status = extract_text_from_pdf(pdf_bytes)

    # 1. Run Fact Extraction Chain
    try:
        facts = fact_extraction_chain.invoke({
            "description": description,
            "evidence_text": evidence_text
        })
    except Exception as e:
        print(f"Fact extraction failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract facts using Grok LLM. Error: {str(e)}"
        )

    # 2. Retrieve relevant CPA sections and precedents
    try:
        sections, precedents = retrieve_context(
            query=description, 
            category=facts.category
        )
    except Exception as e:
        print(f"Retrieval from Pinecone failed: {e}")
        # Return fallback empty lists for retrieval rather than crashing, 
        # but log the issue.
        sections, precedents = [], []

    # Format retrieved contexts for the assessment LLM
    sections_context = ""
    retrieved_sections_docs = []
    for doc in sections:
        section_no = doc.metadata.get("section_no", "Unknown")
        title = doc.metadata.get("title", "Unknown")
        text = doc.page_content
        category_tags = doc.metadata.get("category_tags", [])
        
        sections_context += f"Section {section_no} - {title}:\n{text}\n\n"
        retrieved_sections_docs.append(
            CPASectionDoc(
                section_no=section_no,
                title=title,
                text=text,
                category_tags=category_tags
            )
        )

    precedents_context = ""
    retrieved_precedents_docs = []
    for doc in precedents:
        case_id = doc.metadata.get("case_id", "Unknown")
        category = doc.metadata.get("category", "Unknown")
        facts_summary = doc.page_content
        sections_cited = doc.metadata.get("sections_cited", [])
        outcome = doc.metadata.get("outcome", "Unknown")
        compensation_awarded = doc.metadata.get("compensation_awarded", "None")
        key_reasoning = doc.metadata.get("key_reasoning", "No details")

        precedents_context += (
            f"Case ID: {case_id}\n"
            f"Category: {category}\n"
            f"Facts Summary: {facts_summary}\n"
            f"Sections Cited: {', '.join(sections_cited)}\n"
            f"Outcome: {outcome}\n"
            f"Compensation: {compensation_awarded}\n"
            f"Key Reasoning: {key_reasoning}\n\n"
        )
        retrieved_precedents_docs.append(
            PrecedentDoc(
                case_id=case_id,
                category=category,
                facts_summary=facts_summary,
                sections_cited=sections_cited,
                outcome=outcome,
                compensation_awarded=compensation_awarded,
                key_reasoning=key_reasoning
            )
        )

    # If no retrieval context was found, provide a placeholder so the LLM doesn't hallucinate
    if not sections_context.strip():
        sections_context = "No relevant CPA sections found in database."
    if not precedents_context.strip():
        precedents_context = "No relevant past precedents found in database."

    # 3. Run Dispute Assessment Chain
    discrepancy_info = f"Contradiction flagged: {facts.discrepancy_description}" if facts.discrepancy_flag else "None"
    try:
        assessment = assessment_chain.invoke({
            "category": facts.category,
            "product_or_service": facts.product_or_service,
            "amount": facts.amount,
            "dates": ", ".join(facts.dates),
            "seller_response": facts.seller_response,
            "evidence_available": ", ".join(facts.evidence_available),
            "discrepancy_info": discrepancy_info,
            "sections_context": sections_context,
            "precedents_context": precedents_context
        })
    except Exception as e:
        print(f"Assessment failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to assess dispute using Grok LLM. Error: {str(e)}"
        )

    # 4. Construct response
    return DisputeAnalysisResponse(
        facts=facts,
        retrieved_sections=retrieved_sections_docs,
        retrieved_precedents=retrieved_precedents_docs,
        assessment=assessment,
        discrepancy_flag=facts.discrepancy_flag,
        pdf_status=pdf_status
    )
