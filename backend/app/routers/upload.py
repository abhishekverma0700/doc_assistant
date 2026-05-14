import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from typing import Optional
from app.services.document import extract_text, chunk_text
from app.services.embedding import store_embeddings
from app.models.schemas import UploadResponse
from app.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.services.database import save_document, get_user_documents, delete_document_db

router = APIRouter()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"]

def get_username_from_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token_parts = authorization.split(" ", 1)[1].strip()
    if ":" in token_parts:
        return token_parts.split(":")[1]
    return None

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...), authorization: Optional[str] = Header(default=None)):
    username = get_username_from_token(authorization)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed: PDF, DOCX, TXT")

    try:
        doc_id = str(uuid.uuid4())[:8]
        file_path = f"{UPLOAD_DIR}/{doc_id}_{filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pages = extract_text(file_path, filename)

        if not pages:
            raise HTTPException(status_code=400, detail="Could not extract text.")

        chunks = chunk_text(pages, CHUNK_SIZE, CHUNK_OVERLAP)
        store_embeddings(doc_id, chunks)
        save_document(doc_id, filename, len(chunks), file_path, username)

        return UploadResponse(
            message="Document uploaded and processed successfully",
            doc_id=doc_id,
            filename=filename,
            total_chunks=len(chunks)
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents(authorization: Optional[str] = Header(default=None)):
    username = get_username_from_token(authorization)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    docs = get_user_documents(username)
    return {"documents": docs}


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, authorization: Optional[str] = Header(default=None)):
    username = get_username_from_token(authorization)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    from app.services.embedding import delete_embeddings
    delete_embeddings(doc_id)
    delete_document_db(doc_id, username)

    return {"message": f"Document {doc_id} deleted successfully", "doc_id": doc_id}