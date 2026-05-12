import sys
sys.path.append(".")

from app.services.document import extract_text_from_pdf, chunk_text
from app.services.embedding import store_embeddings
from app.services.retrieval import retrieve_relevant_chunks

# ---- STEP 1: Extract text from PDF ----
print("\n📄 Step 1: Extracting text from PDF...")
pages = extract_text_from_pdf("test.pdf")
print(f"✅ Extracted {len(pages)} pages")
for p in pages[:2]:  # print first 2 pages preview
    print(f"  Page {p['page_number']}: {p['text'][:100]}...")

# ---- STEP 2: Chunk the text ----
print("\n✂️  Step 2: Chunking text...")
chunks = chunk_text(pages)
print(f"✅ Created {len(chunks)} chunks")
for c in chunks[:2]:  # print first 2 chunks
    print(f"  Chunk {c['chunk_id']} (Page {c['page_number']}): {c['text'][:100]}...")

# ---- STEP 3: Store in ChromaDB ----
print("\n🗄️  Step 3: Storing embeddings in ChromaDB...")
doc_id = "test_document"
store_embeddings(doc_id, chunks)
print(f"✅ Embeddings stored successfully!")

# ---- STEP 4: Test Retrieval ----
print("\n🔍 Step 4: Testing retrieval...")
query = "What is this document about?"  # change this to match your PDF
results = retrieve_relevant_chunks(query, [doc_id])
print(f"✅ Retrieved {len(results)} relevant chunks for query: '{query}'")
for i, r in enumerate(results):
    print(f"\n  Result {i+1} (Page {r['metadata']['page_number']}):")
    print(f"  {r['text'][:150]}...")

print("\n🎉 All steps passed! Pipeline is working correctly.")