from fastapi import HTTPException
import ollama
from controllers.embedding1 import get_context_for_query  # Your context retriever

async def chat_ollama(message: str, vector_name: str) -> str:
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    # Retrieve top-K context from vector store
    try:
        context = get_context_for_query(message, vector_name, top_k=4)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No index found for vector: {vector_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching context: {str(e)}")

    context_prompt =  (f"""You are an AI assistant designed to help users with questions related to the context provided below.\n"
                       Context:\n{context}\n\n
                       **Only answer questions that are relevant to the information in these context.**
                       If a user asks something outside the scope of the context, politely inform them that you can only answer questions related to the provided context.
                       Be clear, concise, and helpful in your responses."""
    )

    # Debug: Print context and prompt being sent to Llama
    print("==== CONTEXT SENT TO LLAMA ====")
    print(context)
    print("==== FULL PROMPT SENT TO LLAMA ====")
    print(context_prompt)

    payload = {
        "model": "llama3.2:latest",
        "messages": [
            {"role": "system", "content": context_prompt},
            {"role": "user", "content": message}
        ]
    }
    
    try:
        response = ollama.chat(**payload)
        print("==== RESPONSE FROM LLAMA ====")
        print(response['message']['content'])
        return response['message']['content']
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama chat failed: {str(e)}")