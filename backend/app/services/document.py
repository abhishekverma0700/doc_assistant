import fitz
from typing import List, Dict
def extract_text_from_pdf(file_path:str)->List[Dict]:
    pages=[]
    doc=fitz.open(file_path)

    for page_num in range(len(doc)):
        page =doc[page_num]
        text=page.get_text()
        if text.strip():
            pages.append({
                "page_number":page_num+1,
                "text":text.strip()
            })
    doc.close()
    return pages
def chunk_text(pages: list[dict],chunk_size: int=500, overlap:int=50)-> List[Dict]:
    chunks=[]
    chunk_id = 0

    for page in pages:
        words=page["text"].split()
        start=0
        while start<len(words):
            end=start+chunk_size
            chunk_words =words[start:end]
            chunk_text=" ".join(chunk_words)
            chunks.append({
                "chunk_id":chunk_id,
                "text":chunk_text,
                "page_number":page["page_number"]
            })
            chunk_id += 1
            start = end - overlap
    return chunks