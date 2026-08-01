import os
from pathlib import Path
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from app.utils.logger import get_logger

logger = get_logger(__name__)


def load_file(file_path: str) -> list[Document]:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        loader = PyPDFLoader(str(path))
    elif suffix == ".csv":
        loader = CSVLoader(str(path))
    elif suffix in {".xlsx", ".xls"}:
        return _load_excel(path)
    elif suffix == ".txt":
        return _load_text(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    docs = loader.load()
    logger.info("Loaded %d chunks from %s", len(docs), path.name)
    return docs


def _load_excel(path: Path) -> list[Document]:
    import pandas as pd

    df = pd.read_excel(path)
    docs = []
    for i, row in df.iterrows():
        text = " | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
        docs.append(Document(page_content=text, metadata={"source": path.name, "row": i}))
    return docs


def _load_text(path: Path) -> list[Document]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return [Document(page_content=text, metadata={"source": path.name})]
