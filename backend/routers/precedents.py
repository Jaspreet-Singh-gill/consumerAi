import os
import json
from fastapi import APIRouter, HTTPException
from backend.models.schemas import PrecedentDoc

router = APIRouter()

@router.get("/precedents/{case_id}", response_model=PrecedentDoc)
async def get_precedent(case_id: str):
    # Locate precedents.json relative to this file
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    precedents_path = os.path.join(data_dir, "precedents.json")
    
    if not os.path.exists(precedents_path):
        raise HTTPException(status_code=404, detail="Precedents database file not found.")

    try:
        with open(precedents_path, "r", encoding="utf-8") as f:
            precedents = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read precedents database: {str(e)}")

    # Search for case_id (case-insensitive)
    for case in precedents:
        if case.get("case_id", "").strip().lower() == case_id.strip().lower():
            return PrecedentDoc(
                case_id=case["case_id"],
                category=case["category"],
                facts_summary=case["facts_summary"],
                sections_cited=case.get("sections_cited", []),
                outcome=case["outcome"],
                compensation_awarded=case.get("compensation_awarded", "None"),
                key_reasoning=case.get("key_reasoning", "No detail available.")
            )

    raise HTTPException(status_code=404, detail=f"Precedent case ID '{case_id}' not found.")
