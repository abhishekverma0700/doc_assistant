from fastapi import APIRouter, HTTPException
from app.services.retrieval import retrieve_relevant_chunks
from app.services.llm import generate_answer
from app.models.schemas import AskRequest, AskResponse, ChunkSource
import traceback

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if not request.doc_ids:
        raise HTTPException(status_code=400, detail="Please provide at least one document ID")

    try:
        # Retrieve relevant chunks
        chunks = retrieve_relevant_chunks(request.question, request.doc_ids)
        print(f"Retrieved chunks: {len(chunks)}")  # DEBUG

        if not chunks:
            return AskResponse(
                answer="I could not find relevant information in the provided documents.",
                sources=[]
            )

        # Generate answer using LLM
        answer = generate_answer(request.question, chunks)
        print(f"Answer generated: {answer[:100]}")  # DEBUG

        # Build sources list
        sources = [
            ChunkSource(
                doc_id=chunk["metadata"]["doc_id"],
                page_number=chunk["metadata"]["page_number"],
                text_preview=chunk["text"][:200] + "..."
            )
            for chunk in chunks
        ]

        return AskResponse(answer=answer, sources=sources)

    except Exception as e:
        traceback.print_exc()  # Full error in terminal
        raise HTTPException(status_code=500, detail=str(e))