from app.rag.vectorstore import add_documents

docs = [
    "Prompt engineering improves AI output quality.",
    "RAG reduces hallucinations by grounding answers.",
    "LLMs generate text token by token.",
]
add_documents(docs)
