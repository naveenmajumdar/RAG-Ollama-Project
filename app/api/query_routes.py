from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from app.utils.config import settings
from app.agents import rag_agent

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Question must not be empty")
        return v


@router.post("")
def ask(req: QueryRequest):
    result = rag_agent.query(req.question)
    return result
