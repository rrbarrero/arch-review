from functools import lru_cache

from langchain_ollama import ChatOllama, OllamaEmbeddings

from app.settings import Settings

settings = Settings()


@lru_cache
def get_llm(
    model: str | None = None, temperature: float | None = None
) -> ChatOllama:
    return ChatOllama(
        model=model or settings.llm_model,
        temperature=temperature if temperature is not None else settings.llm_temperature,
        base_url=settings.ollama_base_url,
    )


@lru_cache
def get_embeddings(model: str | None = None) -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=model or settings.embedding_model,
        base_url=settings.ollama_base_url,
    )
