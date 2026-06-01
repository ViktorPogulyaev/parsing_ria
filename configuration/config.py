from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: str = "development"
    secret_key: str = "change-me"
    debug: bool = False
    log_level: str = "INFO"

    # Database
    postgres_user: str = "news"
    postgres_password: str = "news"
    postgres_db: str = "parsing_ria"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None

    # Broker
    broker_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="CELERY_BROKER_URL",
    )
    result_backend: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="CELERY_RESULT_BACKEND",
    )
    task_serializer: str = Field(default="json", validation_alias="CELERY_TASK_SERIALIZER")
    result_serializer: str = Field(
        default="json", validation_alias="CELERY_RESULT_SERIALIZER"
    )
    accept_content: str = Field(default="json", validation_alias="CELERY_ACCEPT_CONTENT")


settings = Settings()
