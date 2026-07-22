import os
import json
import argparse
import requests
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

# Load environment variables
# Check backend/.env first, then root .env
if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", ".env")):
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", ".env"))
elif os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")):
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
else:
    load_dotenv()

# We need KANOON_API_TOKEN in the environment
KANOON_API_TOKEN = os.getenv("KANOON_API_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_BASE_URL = os.getenv("GROK_BASE_URL", "https://api.groq.com/openai/v1")
GROK_MODEL_NAME = os.getenv("GROK_MODEL_NAME", "llama3-70b-8192") # Using Llama3 for extraction

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PRECEDENTS_PATH = os.path.join(DATA_DIR, "precedents.json")

# Define the Pydantic Schema for the LLM output
class Precedent(BaseModel):
    case_id: str = Field(description="The unique identifier or citation of the case (e.g. NCDRC-2024-01). Create a logical one if not explicitly present.")
    category: str = Field(description="The category of the consumer case (e.g. 'Defective goods', 'Deficiency in service', 'Unfair trade practice')")
    facts_summary: str = Field(description="A concise summary of the facts of the case.")
    sections_cited: List[str] = Field(description="List of sections of the Consumer Protection Act cited in the case (e.g. ['2(7)', '39']).")
    outcome: str = Field(description="The outcome of the case. Must be one of: 'consumer_won', 'consumer_lost', 'partial'.")
    compensation_awarded: str = Field(description="The compensation awarded to the consumer. Say 'None' if none.")
    key_reasoning: str = Field(description="The key legal reasoning behind the commission/court's decision.")

def clean_html(raw_html):
    """Remove HTML tags from a string."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def fetch_kanoon_search(query, max_results=3):
    """Search Indian Kanoon and return a list of doc IDs."""
    if not KANOON_API_TOKEN:
        raise ValueError("KANOON_API_TOKEN is not set in your .env file")
        
    url = f"https://api.indiankanoon.org/search/?formInput={query}"
    headers = {"Authorization": f"Token {KANOON_API_TOKEN}"}
    
    print(f"Searching Kanoon for: '{query}'")
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching search results: {response.status_code}")
        return []
        
    data = response.json()
    docs = data.get("docs", [])
    
    # Return the top N document IDs
    return [doc["tid"] for doc in docs[:max_results]]

def fetch_kanoon_document(doc_id):
    """Fetch the full text of a document from Indian Kanoon."""
    url = f"https://api.indiankanoon.org/doc/{doc_id}/"
    headers = {"Authorization": f"Token {KANOON_API_TOKEN}"}
    
    print(f"Fetching Document ID: {doc_id}")
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching document {doc_id}: {response.status_code}")
        return None
        
    data = response.json()
    html_content = data.get("doc", "")
    
    # Strip HTML and return raw text. (Taking only first 15000 chars to fit context limits)
    clean_text = clean_html(html_content)
    return clean_text[:15000] 

def extract_structured_data(raw_text):
    """Use Groq LLM to extract the required fields into JSON."""
    llm = ChatOpenAI(
        api_key=GROK_API_KEY,
        base_url=GROK_BASE_URL,
        model=GROK_MODEL_NAME,
        temperature=0
    )
    
    parser = JsonOutputParser(pydantic_object=Precedent)
    
    prompt = PromptTemplate(
        template="Extract the consumer protection case details from the following raw legal text.\n{format_instructions}\n\nRaw Text:\n{raw_text}\n",
        input_variables=["raw_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser
    
    print("Sending text to LLM for extraction...")
    try:
        result = chain.invoke({"raw_text": raw_text})
        return result
    except Exception as e:
        print(f"LLM Extraction failed: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Fetch legal precedents from Indian Kanoon and structure them.")
    parser.add_argument("--query", type=str, required=True, help="Search query for Indian Kanoon (e.g. 'defective goods consumer protection')")
    parser.add_argument("--max", type=int, default=3, help="Maximum number of cases to fetch (default: 3)")
    
    args = parser.parse_args()
    
    if not GROK_API_KEY:
        print("Error: GROK_API_KEY is not set. Cannot use LLM for extraction.")
        return
        
    # 1. Search Kanoon
    doc_ids = fetch_kanoon_search(args.query, args.max)
    if not doc_ids:
        print("No cases found or API error.")
        return
        
    print(f"Found {len(doc_ids)} case(s). Processing...")
    
    new_precedents = []
    
    # 2. Fetch and Extract each case
    for doc_id in doc_ids:
        raw_text = fetch_kanoon_document(doc_id)
        if raw_text:
            structured_data = extract_structured_data(raw_text)
            if structured_data:
                # Add original kanoon ID if case_id wasn't generated well
                if "case_id" not in structured_data or not structured_data["case_id"]:
                    structured_data["case_id"] = f"KANOON-{doc_id}"
                new_precedents.append(structured_data)
                print(f"Successfully extracted data for {doc_id}")
                
    # 3. Append to existing precedents.json
    if not new_precedents:
        print("No new precedents were extracted successfully.")
        return
        
    print(f"Appending {len(new_precedents)} new case(s) to {PRECEDENTS_PATH}")
    
    existing_data = []
    if os.path.exists(PRECEDENTS_PATH):
        with open(PRECEDENTS_PATH, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
                
    existing_data.extend(new_precedents)
    
    with open(PRECEDENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
    print("Done! You can now run `python scripts/ingest_to_pinecone.py` to push to Pinecone.")

if __name__ == "__main__":
    main()
