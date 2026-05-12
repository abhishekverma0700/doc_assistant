from dotenv import load_dotenv
import os
load_dotenv()
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
GROQ_MODEL="llama-3.3-70b-versatile"

EMBEDDING_MODEL="all-MiniLM-L6-v2"
CHUNK_SIZE=500
CHUNK_OVERLAP=50

TOP_K_RESULTS=4
CHROMA_DB_PATH="./chromadb"