from pydantic import BaseModel
from typing import List, Optional

class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    total_chunks: int
    
class ChunkSource(BaseModel):
    doc_id: str
    page_number: int
    text_preview: str

class AskResponse(BaseModel):
    answer: str
    sources: List[ChunkSource]

class UploadResponse(BaseModel):
    message: str
    doc_id: str
    filename: str
    total_chunks: int

class DeleteResponse(BaseModel):
    message: str
    doc_id: str

class LoginRequest(BaseModel):
    username: str
    password: str
class LoginResponse(BaseModel):
    success:bool
    message:str
    token:str
class AskRequest(BaseModel):
    question:str
    doc_ids:List[str]
    history:Optional[List[dict]] = []