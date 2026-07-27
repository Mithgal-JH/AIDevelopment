def retrieve_context(query: str) -> str:
    results = query_documents(query)
    docs = results["documents"][0]
    return "\n".join(docs)
