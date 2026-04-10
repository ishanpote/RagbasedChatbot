from fastapi import HTTPException
import os
from urllib.parse import urlparse

import ollama
import requests

from controllers.embedding1 import get_context_for_query


def _resolve_ollama_host() -> str:
    raw_host = os.getenv("OLLAMA_HOST", "").strip()
    if not raw_host:
        return "http://127.0.0.1:11434"

    if not raw_host.startswith("http://") and not raw_host.startswith("https://"):
        raw_host = f"http://{raw_host}"

    parsed = urlparse(raw_host)
    host = parsed.hostname or "127.0.0.1"
    if host == "0.0.0.0":
        host = "127.0.0.1"

    scheme = parsed.scheme or "http"
    port = parsed.port or 11434
    return f"{scheme}://{host}:{port}"


def _get_llm_provider() -> str:
    provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if provider == "auto":
        return "huggingface" if os.getenv("HF_API_TOKEN") else "ollama"
    return provider


def _build_system_prompt(context: str) -> str:
    return (
        "You are an AI assistant designed to help users with questions related to the context below.\n"
        f"Context:\n{context}\n\n"
        "Only answer questions that are relevant to this context. "
        "If a user asks something outside the scope of the context, politely state that you can only answer based on the provided context. "
        "Be clear, concise, and helpful."
    )


def _chat_with_ollama(system_prompt: str, message: str) -> str:
    payload = {
        "model": os.getenv("OLLAMA_MODEL", "llama3.2:latest"),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
    }

    try:
        client = ollama.Client(host=_resolve_ollama_host())
        response = client.chat(**payload)
        return response["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama chat failed: {str(e)}")


def _chat_with_huggingface(system_prompt: str, message: str) -> str:
    token = os.getenv("HF_API_TOKEN", "").strip()
    if not token:
        raise HTTPException(
            status_code=500,
            detail="HF_API_TOKEN is missing. Set HF_API_TOKEN or switch LLM_PROVIDER to ollama.",
        )

    model = os.getenv("HF_MODEL", "google/flan-t5-base").strip()
    hf_base_url = os.getenv("HF_API_BASE", "https://router.huggingface.co/hf-inference").strip().rstrip("/")
    endpoint = f"{hf_base_url}/models/{model}"

    prompt = f"{system_prompt}\n\nUser question: {message}\nAssistant answer:"
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 220,
            "temperature": 0.2,
            "return_full_text": False,
        },
    }

    try:
        response = requests.post(
            endpoint,
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
            timeout=90,
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Hugging Face API request failed: {str(e)}")

    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"Hugging Face API error {response.status_code}: {response.text}",
        )

    data = response.json()
    if isinstance(data, list) and data and isinstance(data[0], dict):
        generated = data[0].get("generated_text", "").strip()
        if generated:
            return generated
    if isinstance(data, dict):
        if data.get("error"):
            raise HTTPException(status_code=502, detail=f"Hugging Face API error: {data['error']}")
        generated = data.get("generated_text", "").strip()
        if generated:
            return generated

    raise HTTPException(status_code=502, detail="Unexpected Hugging Face API response format")


async def chat_ollama(message: str, vector_name: str) -> str:
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    try:
        context = get_context_for_query(message, vector_name, top_k=4)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No index found for vector: {vector_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching context: {str(e)}")

    system_prompt = _build_system_prompt(context)
    provider = _get_llm_provider()

    if provider == "huggingface":
        return _chat_with_huggingface(system_prompt, message)
    if provider == "ollama":
        return _chat_with_ollama(system_prompt, message)

    raise HTTPException(
        status_code=500,
        detail="Invalid LLM_PROVIDER. Use 'auto', 'ollama', or 'huggingface'.",
    )