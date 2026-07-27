import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
GROK_BASE_URL = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
GROK_MODEL_NAME = os.getenv("GROK_MODEL_NAME", "grok-2")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Validate required configuration
if not GROK_API_KEY:
    # We will raise a warning rather than crash immediately, so the server can start up and log the configuration error
    print("WARNING: GROK_API_KEY is not set. Chat completions will fail.")
if not PINECONE_API_KEY:
    print("WARNING: PINECONE_API_KEY is not set. Vector database operations will fail.")
