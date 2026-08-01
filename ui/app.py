import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="RAG Ollama", page_icon="🔍", layout="wide")
st.title("🔍 RAG with Ollama")

# ── Sidebar: upload documents ──────────────────────────────────────────────
with st.sidebar:
    st.header("Upload Documents")
    uploaded = st.file_uploader(
        "PDF, CSV, XLSX, TXT",
        type=["pdf", "csv", "xlsx", "xls", "txt"],
        accept_multiple_files=True,
    )

    if st.button("Ingest", disabled=not uploaded):
        for f in uploaded:
            with st.spinner(f"Ingesting {f.name}…"):
                try:
                    resp = requests.post(
                        f"{API_BASE}/ingest/upload",
                        files={"file": (f.name, f.getvalue(), f.type)},
                        timeout=120,
                    )
                    if resp.ok:
                        data = resp.json()
                        st.success(f"{f.name}: {data['chunks_indexed']} chunks indexed")
                    else:
                        st.error(f"{f.name}: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach the API. Start the backend first:\n\n`uvicorn app.api.main:app --reload`")

    st.divider()
    try:
        health = requests.get(f"{API_BASE}/health", timeout=5).json()
        st.metric("Documents indexed", health.get("documents_indexed", "—"))
    except Exception:
        st.warning("API not reachable")

# ── Main: chat interface ───────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption("Sources: " + ", ".join(msg["sources"]))

if prompt := st.chat_input("Ask a question about your documents…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                resp = requests.post(
                    f"{API_BASE}/query",
                    json={"question": prompt},
                    timeout=120,
                )
                data = resp.json() if resp.ok else {"answer": f"Error: {resp.text}", "sources": []}
            except Exception as exc:
                data = {"answer": f"Could not reach API: {exc}", "sources": []}

        st.markdown(data["answer"])
        if data.get("sources"):
            st.caption("Sources: " + ", ".join(data["sources"]))

    st.session_state.messages.append({
        "role": "assistant",
        "content": data["answer"],
        "sources": data.get("sources", []),
    })
