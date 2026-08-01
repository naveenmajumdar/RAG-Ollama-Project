from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.ingest_routes import router as ingest_router
from app.api.query_routes import router as query_router
from app.api.health_routes import router as health_router

app = FastAPI(title="RAG-Ollama API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(query_router)
