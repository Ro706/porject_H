import json
import dotenv
from sentence_transformers import SentenceTransformer, util
from pinecone import Pinecone
import os
from groq import Groq
from datetime import datetime

# ======== STEP 1: SETUP ========
dotenv.load_dotenv()
PINECONE_API_KEY = dotenv.get_key(dotenv.find_dotenv(), "PINECONE_API_KEY")
GROQ_API_KEY = dotenv.get_key(dotenv.find_dotenv(), "GROQ_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("rag-knowledge-384")

embedder = SentenceTransformer("all-MiniLM-L6-v2")
groq_client = Groq(api_key=GROQ_API_KEY)

# ======== STEP 2: GET USER QUESTION ========
query = input("Ask a question about your data: ")

# ======== STEP 3: EMBED THE QUESTION ========
query_emb = embedder.encode(query).tolist()

# ======== STEP 4: RETRIEVE SIMILAR DOCUMENTS ========
results = index.query(vector=query_emb, top_k=3, include_metadata=True)

print("\n🔍 Retrieved Contexts:")
context_texts = []
retrieved_contexts = []

for match in results["matches"]:
    meta = match["metadata"]
    snippet = meta.get("snippet", "")
    title = meta.get("title", "No Title")
    url = meta.get("url", "No URL")

    print(f"- {title} ({url})")
    print(f"  Snippet: {snippet[:200]}...\n")

    retrieved_contexts.append({"title": title, "url": url, "snippet": snippet})
    context_texts.append(f"{title}: {snippet}")

# ======== STEP 5: BUILD CONTEXT ========
context = "\n\n".join(context_texts)
prompt = f"""
Use the following knowledge to answer the question factually, concisely, and based on real data.

Context:
{context}

Question: {query}
"""

# ======== STEP 6: GENERATE LLM RESPONSE ========
try:
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content.strip()
    print("\n LLM Answer:")
    print(answer)

except Exception as e:
    print(f"Error generating answer: {e}")
    answer = None

# ======== STEP 7: COMPUTE REWARD SIGNAL ========
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
print(f"\n Reward Score (semantic alignment): {reward_score}")

# ======== STEP 8: LOG REWARD MEMORY ========
def log_reward(query, contexts, answer, reward, log_file="backend/node/reward_memory.json"):
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

    print(f"Logged reward data to {log_file}")

# Save to log
if answer:
    log_reward(query, retrieved_contexts, answer, reward_score)
