import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.document import extract_text, chunk_text
from app.services.embedding import store_embeddings
from app.models.schemas import UploadResponse
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

router = APIRouter()
documents_store = {}

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"]


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: PDF, DOCX, TXT"
        )

    try:
        doc_id = str(uuid.uuid4())[:8]
        file_path = f"{UPLOAD_DIR}/{doc_id}_{filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pages = extract_text(file_path, filename)

        if not pages:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text. If PDF, it may be scanned/image-based."
            )

        chunks = chunk_text(pages, CHUNK_SIZE, CHUNK_OVERLAP)

        store_embeddings(doc_id, chunks)

        documents_store[doc_id] = {
            "doc_id": doc_id,
            "filename": filename,
            "total_chunks": len(chunks),
            "file_path": file_path
        }

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
async def list_documents():
    return {"documents": list(documents_store.values())}


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")

    from app.services.embedding import delete_embeddings
    delete_embeddings(doc_id)

    file_path = documents_store[doc_id]["file_path"]
    if os.path.exists(file_path):
        os.remove(file_path)

    del documents_store[doc_id]

    return {"message": f"Document {doc_id} deleted successfully", "doc_id": doc_id}