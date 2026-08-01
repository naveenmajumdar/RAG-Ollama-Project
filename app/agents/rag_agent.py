from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from better_profanity import profanity
from app.utils.config import settings
from app.utils.logger import get_logger
from app.vectorstore import chroma_store

logger = get_logger(__name__)

profanity.load_censor_words()

_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't have enough information to answer that."

Context:
{context}

Question: {question}

Answer:"""
)


def _llm() -> ChatOllama:
    return ChatOllama(model=settings.ollama_llm_model, base_url=settings.ollama_base_url)


def _format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def query(question: str) -> dict:
    if len(question) > settings.max_query_length:
        return {"answer": "Query exceeds maximum allowed length.", "sources": []}

    if profanity.contains_profanity(question):
        return {"answer": "Your query contains inappropriate language.", "sources": []}

    docs = chroma_store.similarity_search(question)
    if not docs:
        return {"answer": "No relevant documents found. Please upload documents first.", "sources": []}

    context = _format_docs(docs)
    chain = _PROMPT | _llm() | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})

    sources = list({doc.metadata.get("source", "unknown") for doc in docs})
    logger.info("Query answered. Sources: %s", sources)
    return {"answer": answer, "sources": sources}
