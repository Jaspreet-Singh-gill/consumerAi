import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.x.ai/v1")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "groq-2")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Validate required configuration
if not GROQ_API_KEY:
    # We will raise a warning rather than crash immediately, so the server can start up and log the configuration error
    print("WARNING: GROQ_API_KEY is not set. Chat completions will fail.")
if not PINECONE_API_KEY:
    print("WARNING: PINECONE_API_KEY is not set. Vector database operations will fail.")
