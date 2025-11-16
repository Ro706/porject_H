import json
import dotenv
from sentence_transformers import SentenceTransformer, util
from pinecone import Pinecone, ServerlessSpec
import os
from groq import Groq
from datetime import datetime
import sys

# Import search and scrape functions
from searchurl import search_serper
from webscrap import scrape_webpage

# ======== STEP 1: SETUP ========
dotenv.load_dotenv()
PINECONE_API_KEY = dotenv.get_key(dotenv.find_dotenv(), "PINECONE_API_KEY")
GROQ_API_KEY = dotenv.get_key(dotenv.find_dotenv(), "GROQ_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "rag-knowledge-384"

# Ensure Pinecone index exists (or create it if not)
if index_name not in [i.name for i in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=384,  # Hugging Face MiniLM outputs 384-dim embeddings
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
index = pc.Index(index_name)

embedder = SentenceTransformer("all-MiniLM-L6-v2")
groq_client = Groq(api_key=GROQ_API_KEY)

# ======== STEP 2: GET USER QUESTION ========
query = sys.stdin.read().strip()

# ======== STEP 3: DYNAMIC DATA INGESTION (Search, Scrape, Embed, Upsert) ========
print(f"Searching for relevant information for: '{query}'")
search_results = search_serper(query, num_results=5) # Get top 5 results

dynamic_vectors = []
dynamic_contexts = []
vector_id_counter = 0 # To ensure unique IDs for dynamically added vectors

if not search_results:
    print("No search results found. Proceeding with existing knowledge.")

for result in search_results:
    url = result.get('link')
    title = result.get('title')
    snippet = result.get('snippet')

    print(f"Scraping content from: '{title}' ({url})")
    content = scrape_webpage(url)

    if len(content) < 200:
        print(f"Skipping '{url}' — content too short.")
        continue

    text_to_embed = content[:4000] # Truncate for embedding
    emb = embedder.encode(text_to_embed).tolist()

    dynamic_vectors.append({
        "id": f"dynamic-{vector_id_counter}", # Unique ID for dynamic vectors
        "values": emb,
        "metadata": {
            "title": title,
            "url": url,
            "snippet": snippet,
            "query": query # Associate with the current user query
        }
    })
    dynamic_contexts.append(f"{title}: {snippet}")
    vector_id_counter += 1

if dynamic_vectors:
    print(f"Embedding and storing {len(dynamic_vectors)} new documents in Pinecone.")
    index.upsert(vectors=dynamic_vectors)
    print(f"Successfully updated knowledge base with new information.")
else:
    print("No new documents to embed and upload.")

# ======== STEP 4: EMBED THE QUESTION ========
print("Embedding user query.")
query_emb = embedder.encode(query).tolist()

# ======== STEP 5: RETRIEVE SIMILAR DOCUMENTS (including newly added) ========
print("Retrieving most relevant documents from knowledge base.")
results = index.query(vector=query_emb, top_k=5, include_metadata=True) # Increased top_k

context_texts = []
retrieved_contexts = []

if not results["matches"]:
    print("No relevant documents found in knowledge base.")

for match in results["matches"]:
    meta = match["metadata"]
    snippet = meta.get("snippet", "")
    title = meta.get("title", "No Title")
    url = meta.get("url", "No URL")

    retrieved_contexts.append({"title": title, "url": url, "snippet": snippet})
    context_texts.append(f"{title}: {snippet}")

# ======== STEP 6: BUILD CONTEXT FOR LLM ========
context = "\n\n".join(context_texts)
prompt = f"""
Based on the following context, generate a comprehensive and coherent answer to the question.
Integrate the information smoothly and avoid simply quoting the context directly.
Your response should be factual, concise, and derived solely from the provided data.

Context:
{context}

Question: {query}
"""

# ======== STEP 7: GENERATE LLM RESPONSE ======== 
print("Generating response using Groq LLM.")
try:
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    rag_answer = response.choices[0].message.content.strip()
    print("LLM response generated.")
    # Final answer and reward score will be printed in a specific format for Node.js to parse
    print(json.dumps({"type": "rag_answer", "answer": rag_answer}))

except Exception as e:
    print(f"Error generating answer: {e}")
    rag_answer = None

# ======== STEP 8: GENERATE SECOND LLM RESPONSE (HARDCODED) ========
llm_answer = "This is a hardcoded answer from the second LLM for comparison."
print(json.dumps({"type": "llm_answer", "answer": llm_answer}))