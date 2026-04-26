from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    pgvector_host: str = "pgvector"
    pgvector_port: int = 5432
    pgvector_database: str = "arch_review"
    pgvector_user: str = "arch_review"
    pgvector_password: str = "arch_review_dev"

    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "arch_review_dev"
