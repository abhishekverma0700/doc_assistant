from sentence_transformers import SentenceTransformer
import chromadb
from typing import List, Dict
from app.config import EMBEDDING_MODEL, CHROMA_DB_PATH, TOP_K_RESULTS

model = SentenceTransformer(EMBEDDING_MODEL)
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)


def retrieve_relevant_chunks(query: str, doc_ids: List[str]) -> List[Dict]:
    query_embedding = model.encode([query]).tolist()[0]
    
    all_results = []

    for doc_id in doc_ids:
        try:
            collection = client.get_collection(name=doc_id)
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=TOP_K_RESULTS
            )
            
            for i in range(len(results["documents"][0])):
                all_results.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })
        except Exception as e:
            print(f"Error querying {doc_id}: {e}")
    
   
    all_results.sort(key=lambda x: x["distance"])
    
    return all_results[:TOP_K_RESULTS]