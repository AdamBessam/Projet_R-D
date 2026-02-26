def run_pipeline(question, user_access_level, rag, llm):
    documents = rag.retrieve(
        question,
        user_access_level
    )

    if not documents:
        system_prompt = """You are a secure document assistant. You can ONLY answer questions about your role and capabilities.
Your role: You are an intelligent assistant that helps users search for information in authorized documents based on their access level.
Your capabilities: You can answer questions about contracts and documents that the user is authorized to access.

If the question is about your role or capabilities, answer it.
If the question is about anything else, respond: 'You do not have access to this type of information.'

Question: """
        answer = llm.generate(system_prompt + question)
        return answer, []

    prompt = rag.build_prompt(
        question,
        documents
    )

    answer = llm.generate(prompt)

    return answer, documents
