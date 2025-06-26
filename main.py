from fastapi import FastAPI
from routes import chat, ingest
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
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