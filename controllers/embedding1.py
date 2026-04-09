import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional

# Load model once
# model = SentenceTransformer("all-MiniLM-L6-v2")
# embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # Reinitialize model
class FaissEmbeddingModel:
    def __init__(self, embedding_dim=384):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.documents = []

    def add_document(self, document_text):
        embeddings = self.model.encode([document_text], convert_to_numpy=True, normalize_embeddings=True)
        self.index.add(np.array(embeddings, dtype=np.float32))
        self.documents.append(document_text)
        return embeddings

    def search(self, query, top_k=1):
        query_embedding = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        D, I = self.index.search(np.array(query_embedding, dtype=np.float32), top_k)
        return [(self.documents[int(i)], float(D[0][idx])) for idx, i in enumerate(I[0])]

_embedding_model: Optional[FaissEmbeddingModel] = None
_tokenizer = None


def get_embedding_model() -> FaissEmbeddingModel:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = FaissEmbeddingModel()
    return _embedding_model


def get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        from transformers import AutoTokenizer
        _tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    return _tokenizer

def embed_texts(texts):
    model = get_embedding_model()
    embeddings = model.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.astype("float32")

def save_faiss_index(index, path):
    faiss.write_index(index, path)

def save_metadata(texts, path):
    with open(path, "wb") as f:
        pickle.dump({"texts": texts}, f)

def process_document_embedding(file_bytes: bytes, filename: str):
    try:
        raw_text = file_bytes.decode("utf-8")
        # Use token-based chunking for transformer compatibility
        texts = chunk_document(raw_text, max_tokens=384)
    except Exception:
        return None

    vectors = embed_texts(texts)
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    folder = os.path.join("faiss_indexes", os.path.splitext(filename)[0])
    os.makedirs(folder, exist_ok=True)
    save_faiss_index(index, os.path.join(folder, "faiss_index.bin"))
    # Save the chunks as documents.pkl (not as {"texts": ...})
    with open(os.path.join(folder, "documents.pkl"), "wb") as f:
        pickle.dump(texts, f)

    return {"vectors_added": len(texts), "folder": folder}

def chunk_document(text, max_tokens=384):
    words = text.split()
    chunks = []
    current_chunk = []
    current_len = 0

    # Prefer model tokenizer for better chunk lengths; fallback to word-count chunks if unavailable.
    tokenizer = None
    try:
        tokenizer = get_tokenizer()
    except Exception:
        tokenizer = None

    for word in words:
        word_tokens_len = len(tokenizer.encode(word, add_special_tokens=False)) if tokenizer else 1
        if current_len + word_tokens_len > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_len = word_tokens_len
        else:
            current_chunk.append(word)
            current_len += word_tokens_len
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def load_faiss_index(vector_name):
    import os, pickle
    model = get_embedding_model()
    index_path = os.path.join("faiss_indexes", vector_name, "faiss_index.bin")
    docs_path = os.path.join("faiss_indexes", vector_name, "documents.pkl")
    model.index = faiss.read_index(index_path)
    if os.path.exists(docs_path):
        with open(docs_path, "rb") as f:
            model.documents = pickle.load(f)
    else:
        model.documents = []
    ntotal = model.index.ntotal
    if len(model.documents) != ntotal:
        raise RuntimeError(
            f"Document count ({len(model.documents)}) does not match FAISS index vectors ({ntotal}). "
            "Please re-embed this document."
        )
    
def get_context_for_query(query, vector_name, top_k=4):
    load_faiss_index(vector_name)
    print(f"Searching for query: {query} in vector: {vector_name}")
    model = get_embedding_model()

    if not model.documents:
        return "No documents found."
    results = model.search(query, top_k=top_k)
    return "\n".join([doc for doc, _ in results])
