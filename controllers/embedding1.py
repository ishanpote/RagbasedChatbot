import os
import pickle
from typing import List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TfidfEmbeddingModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.documents: List[str] = []
        self.matrix = None

    def fit(self, documents: List[str]):
        self.documents = documents
        self.matrix = self.vectorizer.fit_transform(documents)

    def search(self, query: str, top_k: int = 1):
        if self.matrix is None or not self.documents:
            return []

        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix)[0]
        ranked_indices = np.argsort(scores)[::-1][:top_k]
        return [(self.documents[int(index)], float(scores[int(index)])) for index in ranked_indices]


_embedding_model: TfidfEmbeddingModel | None = None


def get_embedding_model() -> TfidfEmbeddingModel:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TfidfEmbeddingModel()
    return _embedding_model


def embed_texts(texts):
    model = get_embedding_model()
    model.fit(texts)
    return model.matrix


def save_faiss_index(index, path):
    # Kept for compatibility with existing callers; TF-IDF pipeline stores data separately.
    with open(path, "wb") as f:
        pickle.dump(index, f)


def save_metadata(texts, path):
    with open(path, "wb") as f:
        pickle.dump({"texts": texts}, f)


def process_document_embedding(file_bytes: bytes, filename: str):
    try:
        raw_text = file_bytes.decode("utf-8")
        texts = chunk_document(raw_text, max_tokens=384)
    except Exception:
        return None

    model = get_embedding_model()
    model.fit(texts)

    folder = os.path.join("faiss_indexes", os.path.splitext(filename)[0])
    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, "vectorizer.pkl"), "wb") as f:
        pickle.dump(model.vectorizer, f)

    with open(os.path.join(folder, "matrix.pkl"), "wb") as f:
        pickle.dump(model.matrix, f)

    with open(os.path.join(folder, "documents.pkl"), "wb") as f:
        pickle.dump(texts, f)

    return {"vectors_added": len(texts), "folder": folder}


def chunk_document(text, max_tokens=384):
    words = text.split()
    chunks = []
    current_chunk = []
    current_len = 0

    for word in words:
        word_len = max(1, len(word) // 4)
        if current_len + word_len > max_tokens:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_len = word_len
        else:
            current_chunk.append(word)
            current_len += word_len

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def load_faiss_index(vector_name):
    import pickle

    folder = os.path.join("faiss_indexes", vector_name)
    docs_path = os.path.join(folder, "documents.pkl")
    vectorizer_path = os.path.join(folder, "vectorizer.pkl")
    matrix_path = os.path.join(folder, "matrix.pkl")

    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"Index file not found: {docs_path}")

    model = get_embedding_model()

    with open(docs_path, "rb") as f:
        model.documents = pickle.load(f)

    if os.path.exists(vectorizer_path):
        with open(vectorizer_path, "rb") as f:
            model.vectorizer = pickle.load(f)

    if os.path.exists(matrix_path):
        with open(matrix_path, "rb") as f:
            model.matrix = pickle.load(f)
    else:
        model.matrix = model.vectorizer.fit_transform(model.documents)

    if len(model.documents) != model.matrix.shape[0]:
        raise RuntimeError(
            f"Document count ({len(model.documents)}) does not match indexed rows ({model.matrix.shape[0]}). Please re-embed this document."
        )


def get_context_for_query(query, vector_name, top_k=4):
    load_faiss_index(vector_name)
    print(f"Searching for query: {query} in vector: {vector_name}")
    model = get_embedding_model()

    if not model.documents:
        return "No documents found."

    results = model.search(query, top_k=top_k)
    return "\n".join([doc for doc, _ in results])
