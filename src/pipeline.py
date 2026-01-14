def run_pipeline(question, user_access_level, rag, llm):
    documents = rag.retrieve(
        question,
        user_access_level
    )

    if not documents:
        return "No authorized information allows answering this question.", []

    prompt = rag.build_prompt(
        question,
        documents
    )

    answer = llm.generate(prompt)

    return answer, documents
