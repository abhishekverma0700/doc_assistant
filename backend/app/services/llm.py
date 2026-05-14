from groq import Groq
from typing import Dict, List, Optional
from app.config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

def generate_answer(
    query: str,
    context_chunks: List[Dict],
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    context = ""
    for i, chunk in enumerate(context_chunks):
        page = chunk["metadata"]["page_number"]
        context += f"\n[Source {i+1} -Page {page}]:\n{chunk['text']}\n"

    history_context = ""
    if conversation_history:
        history_lines = []
        for i, turn in enumerate(conversation_history):
            question = turn.get("question", "")
            answer = turn.get("answer", "")
            history_lines.append(f"[Turn {i + 1}]\nQuestion: {question}\nAnswer: {answer}")
        history_context = "\n\nConversation history:\n" + "\n\n".join(history_lines)

    system_prompt = """You are a helpful assistant
      that answers questions based on the provided context and conversation history when available."""

    user_prompt = f"""Context:
    {context}{history_context}
    Question: {query}
    Answer:"""
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=1024
    )
    return response.choices[0].message.content