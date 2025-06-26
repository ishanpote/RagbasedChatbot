from fastapi import APIRouter, UploadFile, File
from controllers.embedding1 import process_document_embedding

router = APIRouter()

@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    contents = await file.read()
    # Process the document and generate embeddings
    embedding = process_document_embedding(contents,file.filename)
    if embedding:
        return {"message": "Document ingested successfully", "embedding": embedding}
    else:
        return {"error": "Failed to process the document"}