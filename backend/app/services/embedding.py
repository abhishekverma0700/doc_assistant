from sentence_transformers import SentenceTransformer
import chromadb
from typing import List ,Dict
from app.config import EMBEDDING_MODEL,CHROMA_DB_PATH

model=SentenceTransformer(EMBEDDING_MODEL)
client=chromadb.PersistentClient(path=CHROMA_DB_PATH)

def get_or_create_collection(doc_id: str):
    return client.get_or_create_collection(name=doc_id)
def store_embeddings(doc_id: str, chunks:List[Dict]):
    collection=get_or_create_collection(doc_id)

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(texts).tolist()

    ids = [f"{doc_id}_chunk_{c['chunk_id']}" for c in chunks]
    metadatas = [
        {
            "page_number": c["page_number"],
            "doc_id":doc_id,
            "chunk_id": c["chunk_id"]
        }
         for c in chunks
    ]

    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )
    
    print(f"stored {len(chunks)} chunks fro document: {doc_id}")