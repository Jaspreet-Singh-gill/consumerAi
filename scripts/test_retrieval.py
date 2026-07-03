import os
import sys

# Add the project root to python path to resolve imports correctly
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.services.retrieval_service import retrieve_context

def test_local_retrieval():
    print("Testing local retrieval fallback for 'Deficiency in service'...")
    query = "domestic flight booking cancelled by airline hotel expenses"
    category = "Deficiency in service"
    
    sections, precedents = retrieve_context(query, category)
    
    print("\n--- RETRIEVED SECTIONS ---")
    for doc in sections:
        print(f"Section {doc.metadata['section_no']}: {doc.metadata['title']}")
        print(f"Snippet: {doc.page_content[:200]}...")
        print("-" * 30)
        
    print("\n--- RETRIEVED PRECEDENTS ---")
    for doc in precedents:
        print(f"Case ID: {doc.metadata['case_id']}")
        print(f"Outcome: {doc.metadata['outcome']}")
        print(f"Snippet: {doc.page_content[:200]}...")
        print("-" * 30)

if __name__ == "__main__":
    test_local_retrieval()
