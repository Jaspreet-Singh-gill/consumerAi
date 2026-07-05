import os
import json
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
import backend.config as config

# Initialize embeddings globally
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def is_pinecone_configured() -> bool:
    """Checks if Pinecone is configured with a valid API key."""
    key = config.PINECONE_API_KEY
    return bool(key and not key.startswith("your_") and key != "")

def get_cpa_vectorstore() -> PineconeVectorStore:
    return PineconeVectorStore(
        index_name="cpa-sections", 
        embedding=embeddings,
        pinecone_api_key=config.PINECONE_API_KEY
    )

def get_precedents_vectorstore() -> PineconeVectorStore:
    return PineconeVectorStore(
        index_name="precedents",
        embedding=embeddings,
        pinecone_api_key=config.PINECONE_API_KEY
    )

def local_fallback_retrieval(query: str, category: str, k_sections: int = 3, k_precedents: int = 3):
    """
    Local fallback retrieval that searches cpa_sections.json and precedents.json
    using simple text search when Pinecone is not configured.
    """
    print("INFO: Pinecone is not configured. Using local file-based retrieval fallback.")
    
    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    cpa_path = os.path.join(base_dir, "data", "cpa_sections.json")
    precedents_path = os.path.join(base_dir, "data", "precedents.json")

    retrieved_sections = []
    retrieved_precedents = []

    # 1. Local CPA Retrieval
    if os.path.exists(cpa_path):
        with open(cpa_path, "r", encoding="utf-8") as f:
            cpa_data = json.load(f)
        
        # Filter sections by category tag
        filtered_sections = [
            item for item in cpa_data 
            if any(category.lower() in tag.lower() for tag in item.get("category_tags", []))
        ]

        # Score based on word overlap with query
        query_words = set(query.lower().split())
        scored_sections = []
        for item in filtered_sections:
            text_to_search = (item.get("title", "") + " " + item.get("text", "")).lower()
            score = sum(1 for w in query_words if w in text_to_search)
            scored_sections.append((score, item))
        
        # Sort and take top k
        scored_sections.sort(key=lambda x: x[0], reverse=True)
        for _, item in scored_sections[:k_sections]:
            doc = Document(
                page_content=item["text"],
                metadata={
                    "section_no": item["section_no"],
                    "title": item["title"],
                    "category_tags": item["category_tags"]
                }
            )
            retrieved_sections.append(doc)

    # 2. Local Precedents Retrieval
    if os.path.exists(precedents_path):
        with open(precedents_path, "r", encoding="utf-8") as f:
            prec_data = json.load(f)
        
        # Filter precedents by category (exact or loose check)
        filtered_precedents = [
            item for item in prec_data 
            if category.lower() in item.get("category", "").lower()
        ]

        # Score based on facts summary search
        query_words = set(query.lower().split())
        scored_precedents = []
        for item in filtered_precedents:
            facts = item.get("facts_summary", "").lower()
            score = sum(1 for w in query_words if w in facts)
            scored_precedents.append((score, item))

        scored_precedents.sort(key=lambda x: x[0], reverse=True)
        for _, item in scored_precedents[:k_precedents]:
            doc = Document(
                page_content=item["facts_summary"],
                metadata={
                    "case_id": item["case_id"],
                    "category": item["category"],
                    "sections_cited": item.get("sections_cited", []),
                    "outcome": item["outcome"],
                    "compensation_awarded": item.get("compensation_awarded", "None"),
                    "key_reasoning": item.get("key_reasoning", "")
                }
            )
            retrieved_precedents.append(doc)

    return retrieved_sections, retrieved_precedents

def retrieve_context(query: str, category: str, k_sections: int = 3, k_precedents: int = 3):
    """
    Exposes similarity search for CPA sections and precedents,
    filtering results by the selected dispute category.
    Falls back to local file search if Pinecone is not set up.
    """
    if not is_pinecone_configured():
        return local_fallback_retrieval(query, category, k_sections, k_precedents)

    try:
        cpa_vs = get_cpa_vectorstore()
        sections_filter = {"category_tags": category}
        sections = cpa_vs.similarity_search(query, k=k_sections)

        precedents_vs = get_precedents_vectorstore()
        precedents_filter = {"category": category}
        precedents = precedents_vs.similarity_search(query, k=k_precedents)

        return sections, precedents
    except Exception as e:
        print(f"Error querying Pinecone vector store: {e}. Falling back to local file search.")
        return local_fallback_retrieval(query, category, k_sections, k_precedents)
