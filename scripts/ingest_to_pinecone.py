import os
import json
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY environment variable is not set")

# 1. Initialize Pinecone client
print("Initializing Pinecone client...")
pc = Pinecone(api_key=PINECONE_API_KEY)

# Index Names
CPA_INDEX = "cpa-sections"
PRECEDENTS_INDEX = "precedents"
DIMENSION = 384  # Dimension for sentence-transformers/all-MiniLM-L6-v2
METRIC = "cosine"

def setup_pinecone_index(index_name):
    """Ensure the Pinecone index exists, creating it if it doesn't."""
    existing_indexes = [index.name for index in pc.list_indexes()]
    if index_name not in existing_indexes:
        print(f"Creating index '{index_name}'...")
        pc.create_index(
            name=index_name,
            dimension=DIMENSION,
            metric=METRIC,
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"  # Free tier serverless region
            )
        )
        print(f"Index '{index_name}' created. Waiting for initialization...")
        # Wait for index to be ready
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
        print(f"Index '{index_name}' is ready.")
    else:
        print(f"Index '{index_name}' already exists.")

# Setup both indexes
setup_pinecone_index(CPA_INDEX)
setup_pinecone_index(PRECEDENTS_INDEX)

# Initialize embeddings model
print("Initializing local HuggingFace Embeddings model...")
# Choice of sentence-transformers/all-MiniLM-L6-v2 noted as local, high-quality, lightweight embedding
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load data files
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
cpa_path = os.path.join(DATA_DIR, "cpa_sections.json")
precedents_path = os.path.join(DATA_DIR, "precedents.json")

print(f"Loading CPA sections from: {cpa_path}")
with open(cpa_path, "r", encoding="utf-8") as f:
    cpa_data = json.load(f)

print(f"Loading precedents from: {precedents_path}")
with open(precedents_path, "r", encoding="utf-8") as f:
    precedents_data = json.load(f)

# 2. Convert and chunk CPA sections
cpa_docs = []
splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)

for entry in cpa_data:
    metadata = {
        "section_no": entry["section_no"],
        "title": entry["title"],
        "category_tags": entry["category_tags"]
    }
    # Prepare text for embedding, maybe prefixing with section metadata helps retrieval
    full_text = f"Section {entry['section_no']}: {entry['title']}\n{entry['text']}"
    
    # We chunk sections since they might be long
    temp_docs = splitter.create_documents(texts=[full_text], metadatas=[metadata])
    cpa_docs.extend(temp_docs)

print(f"Prepared {len(cpa_docs)} document chunks for CPA sections.")

# 3. Convert precedents (no chunking required as facts_summary is short)
precedent_docs = []
for entry in precedents_data:
    metadata = {
        "case_id": entry["case_id"],
        "category": entry["category"],
        "sections_cited": entry["sections_cited"],
        "outcome": entry["outcome"],
        "compensation_awarded": entry["compensation_awarded"],
        "key_reasoning": entry["key_reasoning"]
    }
    # page_content is the facts_summary as requested
    doc = Document(page_content=entry["facts_summary"], metadata=metadata)
    precedent_docs.append(doc)

print(f"Prepared {len(precedent_docs)} documents for precedents.")

# 4. Upsert to Pinecone Vector Stores
print(f"Upserting CPA sections to index '{CPA_INDEX}'...")
cpa_vectorstore = PineconeVectorStore.from_documents(
    documents=cpa_docs,
    embedding=embeddings,
    index_name=CPA_INDEX
)
print("CPA sections ingested successfully.")

print(f"Upserting precedents to index '{PRECEDENTS_INDEX}'...")
precedent_vectorstore = PineconeVectorStore.from_documents(
    documents=precedent_docs,
    embedding=embeddings,
    index_name=PRECEDENTS_INDEX
)
print("Precedents ingested successfully.")

print("Ingestion script completed successfully!")
