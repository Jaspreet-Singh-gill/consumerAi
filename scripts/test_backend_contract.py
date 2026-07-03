import os
import sys
from fastapi.testclient import TestClient

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.main import app

client = TestClient(app)

def test_root_endpoint():
    print("Testing GET / ...")
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    print("PASS: GET / is online!")

def test_precedent_lookup():
    print("\nTesting GET /precedents/{case_id} ...")
    
    # Valid case ID
    response = client.get("/precedents/NCDRC-2024-DS01")
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "NCDRC-2024-DS01"
    assert "airline" in data["facts_summary"].lower()
    print("PASS: Successfully retrieved valid precedent case!")

    # Non-existent case ID
    response = client.get("/precedents/NON_EXISTING_CASE")
    assert response.status_code == 404
    print("PASS: Correctly returned 404 for invalid precedent case ID!")

def test_analyze_validation_errors():
    print("\nTesting POST /analyze validation errors...")

    # 1. Empty description
    response = client.post("/analyze", data={"description": "   "})
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"].lower()
    print("PASS: Correctly rejected empty dispute description!")

    # 2. Non-PDF file upload
    fake_file = ("test.txt", b"dummy text content", "text/plain")
    response = client.post(
        "/analyze", 
        data={"description": "Valid description text"},
        files={"evidence_pdf": fake_file}
    )
    assert response.status_code == 400
    assert "only pdf files" in response.json()["detail"].lower()
    print("PASS: Correctly rejected non-PDF file upload!")

    # 3. Oversized PDF file upload (>5MB)
    large_pdf_bytes = b"0" * (5 * 1024 * 1024 + 100)  # slightly larger than 5MB
    fake_large_pdf = ("too_large.pdf", large_pdf_bytes, "application/pdf")
    response = client.post(
        "/analyze",
        data={"description": "Valid description text"},
        files={"evidence_pdf": fake_large_pdf}
    )
    assert response.status_code == 400
    assert "exceeds the 5mb limit" in response.json()["detail"].lower()
    print("PASS: Correctly rejected PDF exceeding 5MB limit!")

if __name__ == "__main__":
    try:
        test_root_endpoint()
        test_precedent_lookup()
        test_analyze_validation_errors()
        print("\nAll API contract tests PASSED successfully!")
    except AssertionError as e:
        print(f"\nFAIL: Test validation failed: {str(e)}")
        sys.exit(1)
