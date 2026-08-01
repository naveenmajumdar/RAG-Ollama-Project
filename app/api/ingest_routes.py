import os
import shutil
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.utils.config import settings
from app.utils.logger import get_logger
from app.ingestion.loader import load_file
from app.chunking.splitter import split_documents
from app.vectorstore import chroma_store

router = APIRouter(prefix="/ingest", tags=["ingestion"])
logger = get_logger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".csv", ".xlsx", ".xls", ".txt"}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    size_limit = settings.max_file_size_mb * 1024 * 1024
    contents = await file.read()
    if len(contents) > size_limit:
        raise HTTPException(status_code=413, detail="File exceeds size limit")

    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    dest = upload_path / file.filename
    dest.write_bytes(contents)

    try:
        raw_docs = load_file(str(dest))
        chunks = split_documents(raw_docs)
        count = chroma_store.add_documents(chunks)
    except ConnectionRefusedError as exc:
        logger.error("Ollama not reachable during ingestion of %s: %s", file.filename, exc)
        raise HTTPException(status_code=503, detail="Ollama is not running. Start it with: ollama serve")
    except Exception as exc:
        # catch-all: includes httpx/requests connection errors from Ollama
        if "Connection refused" in str(exc) or "11434" in str(exc):
            logger.error("Ollama not reachable during ingestion of %s", file.filename)
            raise HTTPException(status_code=503, detail="Ollama is not running. Start it with: ollama serve")
        logger.exception("Ingestion failed for %s", file.filename)
        raise HTTPException(status_code=500, detail=str(exc))

    return JSONResponse({"filename": file.filename, "chunks_indexed": count})
