from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    cors_origins_raw: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]

    pgvector_host: str = "pgvector"
    pgvector_port: int = 5432
    pgvector_database: str = "arch_review"
    pgvector_user: str = "arch_review"
    pgvector_password: str = "arch_review_dev"

    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "arch_review_dev"

    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen3-8b-12k:latest"
    llm_temperature: float = 0.0
    embedding_model: str = "bge-m3:latest"
