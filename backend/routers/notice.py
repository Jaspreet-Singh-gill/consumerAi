from fastapi import APIRouter, HTTPException
from backend.models.schemas import NoticeDraftRequest, NoticeDraftResponse
from backend.chains.notice_drafting_chain import notice_drafting_chain, GUIDELINES_MAP

router = APIRouter()

@router.post("/draft-notice", response_model=NoticeDraftResponse)
async def draft_notice(request: NoticeDraftRequest):
    facts = request.facts
    cited_sections = request.cited_sections

    category_guidelines = GUIDELINES_MAP.get(
        facts.category, 
        "Draft a standard legal notice demanding a resolution and invoking appropriate CPA sections."
    )

    try:
        # Invoke the notice drafting LCEL chain
        notice_text = notice_drafting_chain.invoke({
            "category": facts.category,
            "product_or_service": facts.product_or_service,
            "amount": facts.amount,
            "dates": ", ".join(facts.dates),
            "seller_response": facts.seller_response,
            "evidence_available": ", ".join(facts.evidence_available),
            "cited_sections": ", ".join(cited_sections),
            "category_guidelines": category_guidelines
        })
    except Exception as e:
        print(f"Notice drafting failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to draft notice using Groq LLM. Error: {str(e)}"
        )

    return NoticeDraftResponse(
        notice_text=notice_text
    )
