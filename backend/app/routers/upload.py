import os
import uuid
import shutil
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.document import extract_text_from_pdf, chunk_text
from app.services.embedding import store_embeddings
from app.models.schemas import UploadResponse
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

router =APIRouter()

documents_store ={}

UPLOAD_DIR ="./uplaods"
os.makedirs(UPLOAD_DIR, exist_ok=True)
@router.post("/upload",response_model=UploadResponse)
async def uplaod_document(file:UploadFile =File(...)):
    if not file.filename.endswith("pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    try:
        doc_id =str(uuid.uuid4())[:8]
        file_path =f"{UPLOAD_DIR}/{doc_id}_{file.filename}"

        with open(file_path,"wb") as buffer:
            shutil.copyfileobj(file.file,buffer)

        pages =extract_text_from_pdf(file_path)
        if not pages:
            raise HTTPException(status_code=400,detail="Could not extract text from Pdf ")
            
        chunks =chunk_text(pages, CHUNK_SIZE, CHUNK_OVERLAP)
        store_embeddings(doc_id, chunks)

        documents_store[doc_id] = {
            "doc_id":doc_id,
            "filename":file.filename,
            "total_chunks":len(chunks),
            "file_path":file_path
        }
        return UplaodResponse(
            message="Document uplaod and processed Succsfully",
            doc_id=doc_id,
            filename=file.filename,
            total_chunks=len(chunks)
               )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents():
    return {"documents":list(documents_store.values())}

@router.delete("/documents/{doc_id}")
async def delete_documents(doc_id: str):
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    from app.services.embedding import delete_embeddings
    delete_embeddings(doc_id)
    file_path=documents_store[doc_id]["file_path"]
    if os.path.exist(file_path):
        os.remove(file_path)
    del documents_store[doc_id]
    return{"message":f"Document{doc_id} deleted successfully","doc_id":doc_id}

