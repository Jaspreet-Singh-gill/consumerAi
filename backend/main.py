from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import analyze, notice, precedents
from backend import config

app = FastAPI(
    title="ConsumerAi API",
    description="Backend service for assessing Indian Consumer Protection Act 2019 disputes and drafting legal notices.",
    version="1.0.0"
)

# Parse multiple origins if provided as comma-separated list
allowed_origins = [origin.strip() for origin in config.FRONTEND_URL.split(',')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],  
)

app.include_router(analyze.router, prefix="", tags=["Dispute Analysis"])
app.include_router(notice.router, prefix="", tags=["Notice Drafting"])
app.include_router(precedents.router, prefix="", tags=["Precedents"])

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "ConsumerAi API",
        "description": "This is an AI-generated preliminary assessment system. Not legal advice."
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

