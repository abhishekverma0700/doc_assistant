from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, chat, auth
from app.services.database import init_db

app = FastAPI(
    title="GENAI Document Assistant",
    description="RAG-based Document Q&A chatbot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()

app.include_router(auth.router)
app.include_router(upload.router, tags=["Documents"])
app.include_router(chat.router, tags=["Chat"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Server is running!"}