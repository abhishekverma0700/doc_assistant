from groq import Groq
from typing import List, Dict
from app.config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)


def generate_answer(query: str, context_chunks: List[Dict], history: List[Dict] = []) -> str:
    context = ""
    for i, chunk in enumerate(context_chunks):
        page = chunk["metadata"]["page_number"]
        context += f"\n[Source {i+1} - Page {page}]:\n{chunk['text']}\n"

    system_prompt = """You are a helpful document assistant.
."""

    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history exactly as it happened
    for h in history:
        if h["role"] in ["user", "assistant"]:
            messages.append({"role": h["role"], "content": h["content"]})

    # Current question with document context
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