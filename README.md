# Chatbot Application

This project is a chatbot application built using FastAPI, Ollama, and word embedding techniques. The chatbot is designed to provide answers based on the context of the documents provided. If a question is asked outside of the context, the chatbot will return an error message.

## Project Structure

```
chatbot-app
├── controllers
│   ├── ask_ollama.py      # Logic for interacting with the Ollama model
│   └── embedding.py        # Handles word embedding functionality
├── models
│   └── chat.py            # Defines data models for chat interactions
├── routes
│   ├── chat.py            # Routes for chat functionality
│   └── ingest.py          # Routes for ingesting documents
├── main.py                # Entry point for the FastAPI application
├── requirements.txt        # Lists project dependencies
└── README.md              # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone https://github.com/ishanpote/RagbasedChatbot.git
   cd chatbot-app
   ```

2. **Install dependencies:**
   Make sure you have Python installed. Then, create a virtual environment and install the required packages:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Run the application:**
   Start the FastAPI server by running:
   ```
   uvicorn main:app --reload
   ```

4. **Access the API:**
   Open your browser and go to `http://127.0.0.1:8000/docs` to view the API documentation and interact with the chatbot.

## Usage

- **Chat Functionality:**
  Send messages to the chatbot through the `/chat` endpoint. The chatbot will respond based on the context of the documents ingested.

- **Ingest Documents:**
  Use the `/ingest` endpoint to upload documents that the chatbot can use for context. 

## Error Handling

If a question is asked that is outside the context of the ingested documents, the chatbot will return an error message indicating that the question is out of context.

## License

This project is licensed under the MIT License.
