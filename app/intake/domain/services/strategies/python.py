from langchain_text_splitters import Language, RecursiveCharacterTextSplitter


class PythonChunkingStrategy:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        self._splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def chunk(self, text: str) -> list[str]:
        return self._splitter.split_text(text)
