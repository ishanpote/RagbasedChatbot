from fastapi import APIRouter, HTTPException  
from controllers.ask_ollama1 import chat_ollama
from models.chat import ChatRequest, ChatResponse 

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, vector_name: str):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query required")
    try:
        response = await chat_ollama(request.query, vector_name)
        return ChatResponse(response=response)
    except HTTPException as e:
        raise e
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="FAISS index not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))