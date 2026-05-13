from groq import Groq
from typing import List, Dict
from app.config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)


def generate_answer(query: str, context_chunks: List[Dict], history: List[Dict] = None) -> str:
    history = history or []

    context = ""
    for i, chunk in enumerate(context_chunks):
        page = chunk["metadata"]["page_number"]
        context += f"\n[Source {i+1} - Page {page}]:\n{chunk['text']}\n"

    system_prompt = """You are DocAssist AI, a helpful document question-answering assistant.
Use the recent conversation history to resolve follow-up questions, references, and vague prompts.
Use the document context as the primary source of truth.
If the user asks for "more", "summarize it", "the second point", or "give examples", infer what they refer to from the recent chat and answer naturally.
If the answer is not supported by the documents or conversation, say that clearly and briefly.
Keep responses concise, coherent, and human-like."""

    messages = [{"role": "system", "content": system_prompt}]

    for h in history[-10:]:
        role = h.get("role") if isinstance(h, dict) else None
        content = h.get("content") if isinstance(h, dict) else None
        if role in ["user", "assistant"] and content:
            messages.append({"role": role, "content": content})

    messages.append({
        "role": "user",
        "content": f"Document Context:\n{context}\n\nCurrent Question: {query}"
    })

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=1024
    )

    return response.choices[0].message.content