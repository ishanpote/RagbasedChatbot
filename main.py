import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import chat, ingest


def _parse_allowed_origins() -> list[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS", "*").strip()
    if not raw:
        return ["*"]

    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    return origins or ["*"]

app = FastAPI()
allowed_origins = _parse_allowed_origins()
allow_credentials = "*" not in allowed_origins
allow_origin_regex = os.getenv("CORS_ALLOW_ORIGIN_REGEX", "").strip() or None

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("Starting FastAPI application...")
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(ingest.router, prefix="/api/v1", tags=["ingest"])
print("Routers included successfully.")
@app.get("/")
def read_root():
    return {"message": "Welcome to the Chatbot API"}
print("Root endpoint defined.")
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)