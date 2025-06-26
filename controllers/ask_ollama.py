from fastapi import HTTPException
import ollama
from controllers.embedding import get_context_for_query  # Import new function

async def chat_ollama(message: str,vector_name) -> str:
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    # Get relevant context from embedded documents
    context = get_context_for_query(message, vector_name,top_k=1)

    context_prompt = (
        f"You are an AI assistant designed to help users with questions related to the documents provided below.\n"
        f"Context:\n{context}\n\n"
        f"Only answer questions that are relevant to the information in these documents. "
        f"If a user asks something outside the scope of the documents, politely inform them that you can only answer questions related to the provided content. "
        f"Be clear, concise, and helpful in your responses."
    )

    payload = {
        "model": "llama3.2:latest",
        "messages": [
            {"role": "system", "content": context_prompt},
            {"role": "user", "content": message}
        ]
    }

    response = ollama.chat(**payload)
    return response['message']['content']