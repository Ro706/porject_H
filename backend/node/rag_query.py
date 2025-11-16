import json
import dotenv
from sentence_transformers import SentenceTransformer, util
from pinecone import Pinecone, ServerlessSpec
import os
from groq import Groq
from datetime import datetime
import sys
import codecs

# Reconfigure stdout to use UTF-8 encoding
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


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
You are an expert assistant. Using only the information provided in the context below,
compose a single, clear, and well-structured answer to the question.

Requirements:
- Use the context as a knowledge base and synthesize all relevant details.
- Do NOT invent or assume facts that are not present in the context.
- Do NOT copy large chunks of text; rewrite and integrate the ideas naturally.
- Ensure the answer is complete, factual, and directly addresses the question.
- If the context lacks enough information to fully answer, state that clearly.

Context:
{context}

Question:
{query}

Answer:
"""

# ======== STEP 7: GENERATE LLM RESPONSE ======== 
print("Generating response using Groq LLM.")
try:
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content.strip()
    print("LLM response generated.")
    # Final answer and reward score will be printed in a specific format for Node.js to parse
    print(json.dumps({"type": "final_answer", "answer": answer}))

except Exception as e:
    print(f"Error generating answer: {e}")
    answer = None

# ======== STEP 8: COMPUTE REWARD SIGNAL ======== 
def compute_reward(answer_text, contexts):
    """Compute semantic similarity between the answer and retrieved context."""
    if not answer_text or not contexts:
        return 0.0
    context_text = " ".join([c["snippet"] for c in contexts])
    emb_answer = embedder.encode(answer_text, convert_to_tensor=True)
    emb_context = embedder.encode(context_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(emb_answer, emb_context).item()
    return round(float(similarity), 3)

reward_score = compute_reward(answer, retrieved_contexts)
print(json.dumps({"type": "reward_score", "score": reward_score}))

# ======== STEP 9: LOG REWARD MEMORY ========
def log_reward(query, contexts, answer, reward, log_file=os.path.join(os.path.dirname(__file__), 'reward_memory.json')):
    entry = {
        "query": query,
        "contexts": [c["url"] for c in contexts],
        "answer": answer,
        "reward_score": reward,
        "timestamp": datetime.now().isoformat()
    }

    # Load old data or create new
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(entry)

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# Save to log
if answer:
    log_reward(query, retrieved_contexts, answer, reward_score)