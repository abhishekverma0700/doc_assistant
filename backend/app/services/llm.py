from groq import Groq
from typing import List, Dict
from app.config import GROQ_API_KEY, GROQ_MODEL

client=Groq(api_key=GROQ_API_KEY)

def generate_answer(query:str,context_chunks:List[Dict])->str:
    context=""
    for i, chunk in enumerate(context_chunks):
        page =chunk["metadata"]["page_number"]
        context += f"\n[Source {i+1} -Page {page}]:\n{chunk['text']}\n"

    system_prompt ="""You are a helpful assistant
      that answers questions based on the provided context."""

    user_prompt = f"""Context:
    {context}
    Question: {query}
    Answer:"""
    response =client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role":"system","content":system_prompt},
            {"role":"user","content":user_prompt}
        ],
        temperature=0.2,
        max_tokens=1024
    )
    return response.choices[0].message.content