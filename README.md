# Consumer Rights Triage

Consumer Rights Triage is a full-stack AI-assisted legal triaging application that helps Indian consumers assess the strength of their disputes under the **Consumer Protection Act (CPA), 2019**, view similar past case outcomes from the NCDRC, and draft professional legal notices.

The application leverages a state-of-the-art **Retrieval-Augmented Generation (RAG)** pipeline orchestrated with **LangChain**, utilizing **Groq API** for reasoning and a local **Sentence Transformers** model for embedding vector search.

---

## 🏗️ Architecture & Technical Stack

- **Backend**: Python, FastAPI
- **Frontend**: React, TypeScript, Vite, Vanilla CSS
- **LLM Orchestration**: LangChain (Expression Language - LCEL)
  - `fact_extraction_chain`: Dynamically extracts dispute parameters into a structured Pydantic format using `with_structured_output`.
  - `assessment_chain`: Triages case strength ("Weak" | "Moderate" | "Strong") and cited provisions/precedents, grounding reasoning strictly in retrieved context.
  - `notice_drafting_chain`: Generates formal, category-specific legal notices citing relevant CPA sections and unboxing/invoice evidence.
- **LLM Model**:Groq API (accessed via LangChain's OpenAI-compatible `ChatOpenAI` wrapper)
- **Vector DB**: Pinecone (using `langchain-pinecone` for vector storage/search)
- **Embeddings**: Local HuggingFace sentence transformer (`all-MiniLM-L6-v2` via `langchain-huggingface`).
  - *Design Note*: Groq does not expose a general-purpose, standalone `v1/embeddings` endpoint. Using a local embedding model saves cost, runs completely free, and eliminates the need for a separate embedding API key.
- **PDF Extraction**: `PyPDFLoader` (extracts text from evidence documents with an automatic OCR/scanned fallback warning).

### 🔄 Retrieval Fallback Mechanism (Zero-Config Testing)
To ensure the application runs seamlessly out-of-the-box, a **local search fallback** is built into the retrieval service. If no `PINECONE_API_KEY` is provided (or if it is left as the placeholder `your_...`), the system automatically loads data from `data/cpa_sections.json` and `data/precedents.json` and ranks relevant clauses/past cases using a keyword-scoring retriever. Setting up Pinecone credentials will automatically swap search execution to cloud index retrieval.

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory (or `backend/` subfolder) with the following variables:

```env
#Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_BASE_URL=https://api.x.ai/v1
GROQ_MODEL_NAME=groq-2

# Pinecone Vector DB Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENV=us-east-1
```

---

## 🚀 Setup & Execution Instructions

### 1. Ingest Data to Pinecone (Optional)
If you have a Pinecone account, make sure your `.env` is configured, then run the ingestion script to create indexes and embed data:

```bash
python scripts/ingest_to_pinecone.py
```
*If skipped, the backend will automatically use the high-quality local JSON-based fallback retriever.*

### 2. Start the Backend Server (FastAPI)
From the root directory, install dependencies and launch Uvicorn:

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start the server (runs on http://127.0.0.1:8000)
python backend/main.py
```

### 3. Start the Frontend Application (Vite + React)
In a separate terminal, navigate to the `frontend` directory:

```bash
cd frontend

# Install dependencies
npm install

# Run the development server (runs on http://localhost:5173)
npm run dev
```

---

## 🧪 Running Automated Tests

We have written offline verification scripts to test individual modules and API contracts:

1. **Test Retrieval Fallback**:
   Checks that keyword sorting correctly filters legal sections and past cases:
   ```bash
   python scripts/test_retrieval.py
   ```

2. **Test Backend Endpoints**:
   Runs FastAPI integration tests for CORS, error handling, validation, and route parameters:
   ```bash
   python scripts/test_backend_contract.py
   ```

