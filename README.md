# RAG-Ollama-Project

A fully local Retrieval-Augmented Generation (RAG) system powered by [Ollama](https://ollama.com), FastAPI, ChromaDB, and Streamlit. No API keys required.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.11+ | `python3 --version` |
| Ollama | latest | [ollama.com/download](https://ollama.com/download) |

---

## Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd RAG-Ollama-Project
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Edit `.env` if you need to change models or paths. Defaults work out of the box.

### 5. Install and start Ollama
Download from [ollama.com/download](https://ollama.com/download), open the app, then pull the required models:
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

---

## Running the Application

You need **two terminal tabs** both with the venv activated (`source .venv/bin/activate`).

### Terminal 1 — FastAPI backend
```bash
uvicorn app.api.main:app --reload
```
- API base: http://127.0.0.1:8000
- Interactive docs: http://localhost:8000/docs

### Terminal 2 — Streamlit UI
```bash
streamlit run ui/app.py
```
If you see `streamlit: command not found`, run Streamlit through the project venv Python:
```bash
.venv/bin/python -m streamlit run ui/app.py
```
- UI: http://localhost:8501

---

## Testing Steps

Run these checks after starting the backend and UI.

### 1. Verify backend is reachable
```bash
curl -sS http://127.0.0.1:8000/health
```
Expected response:
```json
{"status":"ok"}
```

### 2. Verify vector store stats endpoint
```bash
curl -sS http://127.0.0.1:8000/health/stats
```
Expected response shape:
```json
{"documents_indexed":0}
```
(`documents_indexed` can be any non-negative integer depending on your ingested data.)

### 3. Verify backend process is listening on port 8000 (macOS/Linux)
```bash
lsof -iTCP:8000 -sTCP:LISTEN -n -P
```

### 4. Verify UI can call the backend
The Streamlit app uses:
- `API_BASE_URL` environment variable if set
- otherwise defaults to `http://127.0.0.1:8000`

Optional override before launching Streamlit:
```bash
export API_BASE_URL=http://127.0.0.1:8000
python -m streamlit run ui/app.py
```

### 5. End-to-end smoke test
1. Open `http://localhost:8501`.
2. Upload a small `.txt` file.
3. Click **Ingest** and confirm a success message appears.
4. Ask a simple question about the uploaded text and verify the response includes relevant content.

### 6. Quick troubleshooting
- `API not reachable` in UI: make sure FastAPI is running and `/health` returns `{"status":"ok"}`.
- `streamlit: command not found`: run `python -m streamlit run ui/app.py` from the activated venv.
- `Ollama is not running`: start Ollama and ensure models are available:
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```
- `File exceeds size limit`: increase `MAX_FILE_SIZE_MB` in `.env` and restart FastAPI.

---

## Usage

1. Open http://localhost:8501 in your browser.
2. Use the **sidebar** to upload a PDF, CSV, XLSX, or TXT file.
3. Click **Ingest** — the file is chunked and embedded into ChromaDB.
4. Type a question in the chat box and get answers grounded in your documents.

---

## Project Structure

```
RAG-Ollama-Project/
├── app/
│   ├── agents/          # RAG chain (LangChain + Ollama LLM)
│   ├── api/             # FastAPI app and route handlers
│   ├── chunking/        # Text splitting logic
│   ├── ingestion/       # Document loaders (PDF, CSV, XLSX, TXT)
│   ├── utils/           # Config (pydantic-settings) and logger
│   └── vectorstore/     # ChromaDB wrapper
├── ui/
│   └── app.py           # Streamlit chat interface
├── sample_data/         # Place sample documents here
├── uploads/             # Uploaded files (git-ignored)
├── chroma_db/           # Persisted vector store (git-ignored)
├── .env.example         # Template for environment variables
├── requirements.txt
└── .gitignore
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_LLM_MODEL` | `llama3.2` | Chat model |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | Vector store path |
| `UPLOAD_DIR` | `./uploads` | Uploaded files path |
| `MAX_FILE_SIZE_MB` | `50` | Upload size limit |
| `CHUNK_SIZE` | `800` | Characters per chunk |
| `CHUNK_OVERLAP` | `150` | Overlap between chunks |
| `TOP_K_RETRIEVAL` | `5` | Documents retrieved per query |
| `MAX_QUERY_LENGTH` | `1000` | Max characters in a question |
