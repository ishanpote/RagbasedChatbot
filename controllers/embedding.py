import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import pickle

class FaissEmbeddingModel:
    def __init__(self, embedding_dim=384):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.documents = []  # To keep track of original docs

    def add_document(self, document_text):
        embedding = self.model.encode([document_text])
        self.index.add(np.array(embedding, dtype=np.float32))
        self.documents.append(document_text)

    def search(self, query, top_k=1):
        query_embedding = self.model.encode([query])
        D, I = self.index.search(np.array(query_embedding, dtype=np.float32), top_k)
        return [(self.documents[int(i)], float(D[0][idx])) for idx, i in enumerate(I[0])]

# Singleton instance
embedding_model = FaissEmbeddingModel()

# # Maintain a mapping of document names to index file paths
# INDEX_PICKLE_PATH = f"faiss_indexes/{vector_name}/index.pkl"

# def save_index_mapping(mapping):
#     with open(INDEX_PICKLE_PATH, "wb") as f:
#         pickle.dump(mapping, f)

# def load_index_mapping():
#     if os.path.exists(INDEX_PICKLE_PATH):
#         with open(INDEX_PICKLE_PATH, "rb") as f:
#             return pickle.load(f)
#     return {}

# def load_documents_for_index(vector_name):
#     # Load all documents for the given index if available
#     doc_dir = os.path.join("faiss_indexes", vector_name)
#     mapping_path = os.path.join(doc_dir, "index.pkl")
#     if os.path.exists(mapping_path):
#         with open(mapping_path, "rb") as f:
#             mapping = pickle.load(f)
#         # Try to load documents.txt if exists
#         docs_path = os.path.join(doc_dir, "documents.pkl")
#         if os.path.exists(docs_path):
#             with open(docs_path, "rb") as f:
#                 embedding_model.documents = pickle.load(f)
#         else:
#             embedding_model.documents = []
#     else:
#         embedding_model.documents = []

# Update process_document_embedding to save all documents
def process_document_embedding(document_bytes, document_name):
    try:
        document_text = document_bytes.decode('utf-8')
    except Exception:
        return None
    embedding_model.add_document(document_text)
    base_dir = "faiss_indexes"
    safe_name = os.path.splitext(os.path.basename(document_name))[0]
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
    doc_dir = os.path.join(base_dir, safe_name)
    os.makedirs(doc_dir, exist_ok=True)
    index_path = os.path.join(doc_dir, "faiss_index.bin")
    mapping_path = os.path.join(doc_dir, "index.pkl")
    docs_path = os.path.join(doc_dir, "documents.pkl")
    faiss.write_index(embedding_model.index, index_path)
    mapping = {safe_name: index_path}
    with open(mapping_path, "wb") as f:
        pickle.dump(mapping, f)
    # Save all documents for this index
    with open(docs_path, "wb") as f:
        pickle.dump(embedding_model.documents, f)
    return {"message": f"Document embedded and added to {doc_dir}"}

def process_document_embedding(document_bytes, document_name):
    # Convert bytes to string (assuming utf-8 text files)
    try:
        document_text = document_bytes.decode('utf-8')
    except Exception:
        return None
    embedding_model.add_document(document_text)
    # Create a folder for this document inside faiss_indexes
    base_dir = "faiss_indexes"
    safe_name = os.path.splitext(os.path.basename(document_name))[0]
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
    doc_dir = os.path.join(base_dir, safe_name)
    os.makedirs(doc_dir, exist_ok=True)
    # Save FAISS index and mapping inside the folder
    index_path = os.path.join(doc_dir, "faiss_index.bin")
    mapping_path = os.path.join(doc_dir, "index.pkl")
    faiss.write_index(embedding_model.index, index_path)
    mapping = {safe_name: index_path}
    with open(mapping_path, "wb") as f:
        pickle.dump(mapping, f)
    return {"message": f"Document embedded and added to {doc_dir}"}
# ...existing code...

# def load_faiss_index(vector_name):
#     try:
#         embedding_model.index = faiss.read_index(f"./faiss_indexes/{vector_name}/faiss_index.bin")
#     except Exception:
#         pass  # Handle error as needed
def load_faiss_index(vector_name: str):
    try:
        index_path = os.path.join(f"faiss_indexes/{vector_name}/faiss_index.bin")
        docs_path = os.path.join(f"faiss_indexes/{vector_name}/index.pkl")
        embedding_model.index = faiss.read_index(index_path)
        if os.path.exists(docs_path):
            with open(docs_path, "rb") as f:
                embedding_model.documents = pickle.load(f)
        else:
            embedding_model.documents = []
    except Exception as e:
        print(f"Error loading FAISS index for {vector_name}: {e}")
        embedding_model.documents = []

def get_context_for_query(query, vector_name, top_k=1):
    load_faiss_index(vector_name)
    if not embedding_model.documents:
        return ""
    results = embedding_model.search(query, top_k=top_k)
    # Return the most relevant document(s) as context
    return "\n".join([doc for doc, _ in results])