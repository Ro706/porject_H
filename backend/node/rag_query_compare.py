import json
import dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import os
from groq import Groq
from datetime import datetime
import sys
import codecs

# Reconfigure stdout to use UTF-8 encoding
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Import functions from other local scripts
from searchurl import search_serper
from webscrap import scrape_webpage
from comprehensive_evaluate import comprehensive_evaluation

def main():
    # ======== STEP 1: SETUP ========
    dotenv.load_dotenv()
    PINECONE_API_KEY = dotenv.get_key(dotenv.find_dotenv(), "PINECONE_API_KEY")
    GROQ_API_KEY = dotenv.get_key(dotenv.find_dotenv(), "GROQ_API_KEY")

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index_name = "rag-knowledge-384"

    if index_name not in [i.name for i in pc.list_indexes()]:
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    index = pc.Index(index_name)

    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    groq_client = Groq(api_key=GROQ_API_KEY)

    # ======== STEP 2: GET USER QUESTION ========
    query = sys.stdin.read().strip()

    # ======== STEP 3: DYNAMIC DATA INGESTION ========
    search_results = search_serper(query, num_results=5)
    
    dynamic_vectors = []
    if search_results:
        for result in search_results:
            url = result.get('link')
            title = result.get('title')
            content = scrape_webpage(url)
            if len(content) < 200:
                continue
            
            text_to_embed = content[:4000]
            emb = embedder.encode(text_to_embed).tolist()
            
            dynamic_vectors.append({
                "id": f"dynamic-{datetime.now().timestamp()}",
                "values": emb,
                "metadata": {
                    "title": title,
                    "url": url,
                    "snippet": result.get('snippet', ''),
                    "query": query
                }
            })
        
        if dynamic_vectors:
            index.upsert(vectors=dynamic_vectors)

    # ======== STEP 4: EMBED & RETRIEVE ========
    query_emb = embedder.encode(query).tolist()
    results = index.query(vector=query_emb, top_k=5, include_metadata=True)
    
    context_texts = [match["metadata"].get("snippet", "") for match in results["matches"]]
    context = "\n\n".join(context_texts)

    # ======== STEP 5: GENERATE RAG ANSWER ========
    rag_answer = None
    try:
        prompt = f"Based on the following context, generate a comprehensive answer to the question.\\n\\nContext:\\n{context}\\n\\nQuestion: {query}"
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        rag_answer = response.choices[0].message.content.strip()
    except Exception:
        rag_answer = "Error generating RAG answer."

    # ======== STEP 6: GENERATE LLM ANSWER (NO RAG) ========
    llm_answer = None
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": query}]
        )
        llm_answer = response.choices[0].message.content.strip()
    except Exception:
        llm_answer = "Error generating LLM answer."

    # ======== STEP 7: EVALUATE ANSWERS ========
    evaluation = None
    if rag_answer and llm_answer and "Error" not in rag_answer and "Error" not in llm_answer:
        evaluation = comprehensive_evaluation(query, rag_answer, llm_answer)

    # ======== STEP 8: FINAL OUTPUT ========
    final_output = {
        "rag_answer": rag_answer,
        "llm_answer": llm_answer,
        "evaluation": evaluation
    }
    print(json.dumps(final_output))

if __name__ == "__main__":
    main()