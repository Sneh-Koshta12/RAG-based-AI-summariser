import requests
from flashrank import Ranker, RerankRequest
from app.core.config import settings
from app.services.vector_store import vector_store

# Initialize FlashRank (Lightweight cross-encoder that runs easily on CPU)
ranker = Ranker()

def query_rag_system(user_query: str) -> str:
    """
    1. Vector Search MongoDB
    2. FlashRank Re-rank
    3. Generate response via Groq Llama 3
    """
    # Step 1: Fetch top 10 raw documents from MongoDB using local embeddings
    docs = vector_store.similarity_search(query=user_query, k=10)
    
    if not docs:
        return "No relevant context found in the document database."

    # Format documents for FlashRank syntax
    passages = [
        {"id": idx, "text": doc.page_content, "meta": doc.metadata}
        for idx, doc in enumerate(docs)
    ]

    # Step 2: Re-rank using FlashRank
    # This pushes the most contextually accurate chunks to the top
    rerank_request = RerankRequest(query=user_query, passages=passages)
    rerank_results = ranker.rerank(rerank_request)
    
    # Take the top 3 highest scoring chunks for our LLM context prompt
    top_chunks = [result["text"] for result in rerank_results[:3]]
    context_str = "\n\n---\n\n".join(top_chunks)

    # Step 3: LLM Generation via external Groq API (Zero local memory footprint)
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert production-grade RAG Assistant. "
                    "Answer the user's question accurately using ONLY the provided context below. "
                    "If the answer cannot be found in the context, say 'I cannot find that information in the document.'\n\n"
                    f"CONTEXT:\n{context_str}"
                )
            },
            {"role": "user", "content": user_query}
        ],
        "temperature": 0.2 # Keeps the LLM focused on facts rather than creative writing
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"LLM Generation Error: {response.text}"