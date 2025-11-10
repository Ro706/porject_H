import json
import dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import os

# ======== STEP 1: LOAD ENVIRONMENT VARIABLES ========
dotenv.load_dotenv()

PINECONE_API_KEY = dotenv.get_key(dotenv.find_dotenv(), "PINECONE_API_KEY")

# ======== STEP 2: INITIALIZE PINECONE ========
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "rag-knowledge-384"

# Create Pinecone index if it doesn’t exist
if index_name not in [i.name for i in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=384,  # Hugging Face MiniLM outputs 384-dim embeddings
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    print(f"Created Pinecone index: {index_name}")

index = pc.Index(index_name)
print(f"Connected to Pinecone index: {index_name}")

# ======== STEP 3: LOAD SCRAPED DATA ========
DATA_PATH = "backend/node/scraped_data.json"

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Could not find scraped data file: {DATA_PATH}")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    all_results = json.load(f)

print(f"Loaded {len(all_results)} documents from scraped_data.json")

# ======== STEP 4: EMBEDDING FUNCTION (Hugging Face MiniLM) ========
model = SentenceTransformer("all-MiniLM-L6-v2")  # Free, local 384-dim model

def generate_embedding(text):
    try:
        return model.encode(text).tolist()
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return [0.0] * 384

# ======== STEP 5: PREPARE & UPLOAD TO PINECONE ========
vectors = []

for i, item in enumerate(all_results):
    text = item.get("content", "")[:4000]  # Truncate overly long text
    emb = generate_embedding(text)
    
    vector = {
        "id": str(i),
        "values": emb,
        "metadata": {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("snippet", ""),
            "query": item.get("query", "")
        }
    }
    vectors.append(vector)

# Upload all vectors to Pinecone
if vectors:
    index.upsert(vectors=vectors)
    print(f"Uploaded {len(vectors)} documents to Pinecone successfully!")
else:
    print("No vectors found to upload.")

# ======== STEP 6: VERIFY INDEX ========

stats = index.describe_index_stats()
print("Pinecone Index Stats:")
print(stats.to_dict())

