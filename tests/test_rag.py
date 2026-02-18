from src.rag_strategies.simple_rag import SimpleRAG


class _Doc:
    def __init__(self, text):
        self.page_content = text


def test_simple_build_prompt_contains_query_and_docs():
    rag = SimpleRAG()
    docs = [_Doc("Clause A details"), _Doc("Clause B text")]
    prompt = rag.build_prompt("What is Clause A?", docs)
    assert "Clause A details" in prompt
    assert "What is Clause A?" in prompt
