from pydantic import BaseModel
from typing import List, Optional

class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    total_chunks: int


class ConversationTurn(BaseModel):
    question: str
    answer: str

class AskRequest(BaseModel):
    question: str
    doc_ids: List[str]
    session_id: Optional[str] = None
    history: Optional[List[ConversationTurn]] = None

class ChunkSource(BaseModel):
    doc_id: str
    page_number: int
    text_preview: str

class AskResponse(BaseModel):
    answer: str
    sources: List[ChunkSource]
    session_id: str

class UploadResponse(BaseModel):
    message: str
    doc_id: str
    filename: str
    total_chunks: int

class DeleteResponse(BaseModel):
    message: str
    doc_id: str