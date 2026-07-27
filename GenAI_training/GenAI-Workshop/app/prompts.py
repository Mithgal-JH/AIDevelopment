def build_rag_prompt(context: str, question: str) -> str:
    return f"""
    You are a helpful AI assistant.
    Use ONLY the context below to answer the question.
    CONTEXT:
    {context}
    QUESTION:
    {question}
    RULES:
    - Do not invent information
    - If answer is missing, say "I don't know"
    """

