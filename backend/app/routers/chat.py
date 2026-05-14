from fastapi import APIRouter, HTTPException
from uuid import uuid4
from typing import Dict, List
from app.services.retrieval import retrieve_relevant_chunks
from app.services.llm import generate_answer
from app.models.schemas import AskRequest, AskResponse, ChunkSource
import traceback

router = APIRouter()
conversation_history: Dict[str, List[Dict[str, str]]] = {}


def _build_history_context(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return history[-5:]


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if not request.doc_ids:
        raise HTTPException(status_code=400, detail="Please provide at least one document ID")

    try:
        session_id = request.session_id or str(uuid4())

        if request.history:
            normalized_history = [turn.dict() for turn in request.history]
            if session_id not in conversation_history or len(conversation_history[session_id]) < len(normalized_history):
                conversation_history[session_id] = normalized_history

        session_history = conversation_history.get(session_id, [])
        history_context = _build_history_context(session_history)

        # Retrieve relevant chunks
        chunks = retrieve_relevant_chunks(request.question, request.doc_ids)
        print(f"Retrieved chunks: {len(chunks)}")  # DEBUG

        if not chunks:
            return AskResponse(
                answer="I could not find relevant information in the provided documents.",
                sources=[],
                session_id=session_id
            )

        # Generate answer using LLM
        answer = generate_answer(request.question, chunks, conversation_history=history_context)
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

        conversation_history.setdefault(session_id, [])
        conversation_history[session_id].append({
            "question": request.question,
            "answer": answer
        })

        return AskResponse(answer=answer, sources=sources, session_id=session_id)

    except Exception as e:
        traceback.print_exc()  # Full error in terminal
        raise HTTPException(status_code=500, detail=str(e))