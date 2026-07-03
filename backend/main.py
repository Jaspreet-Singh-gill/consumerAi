from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import analyze, notice, precedents

app = FastAPI(
    title="Consumer Rights Triage API",
    description="Backend service for assessing Indian Consumer Protection Act (CPA) 2019 disputes and drafting legal notices.",
    version="1.0.0"
)

# CORS setup to allow integration with React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development and demo testing
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Register routers
app.include_router(analyze.router, prefix="", tags=["Dispute Analysis"])
app.include_router(notice.router, prefix="", tags=["Notice Drafting"])
app.include_router(precedents.router, prefix="", tags=["Precedents"])

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Consumer Rights Triage API",
        "description": "This is an AI-generated preliminary assessment system. Not legal advice."
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
