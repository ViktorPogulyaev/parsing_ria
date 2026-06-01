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

    # Enrichment
    enrichment_user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        validation_alias="ENRICHMENT_USER_AGENT"
    )
    enrichment_request_timeout: int = Field(default=30, validation_alias="ENRICHMENT_REQUEST_TIMEOUT")
    enrichment_max_retries: int = Field(default=3, validation_alias="ENRICHMENT_MAX_RETRIES")
    enrichment_retry_delay: int = Field(default=1, validation_alias="ENRICHMENT_RETRY_DELAY")
    enrichment_retry_delay_max: int = Field(default=30, validation_alias="ENRICHMENT_RETRY_DELAY_MAX")
    enrichment_retry_delay_multiplier: float = Field(default=2, validation_alias="ENRICHMENT_RETRY_DELAY_MULTIPLIER")
    enrichment_retry_delay_max_value: int = Field(default=60, validation_alias="ENRICHMENT_RETRY_DELAY_MAX_VALUE")
    enrichment_schedule_interval: int = Field(
        default=300,
        validation_alias="ENRICHMENT_SCHEDULE_INTERVAL",
    )
    enrichment_batch_size: int = Field(default=50, validation_alias="ENRICHMENT_BATCH_SIZE")

    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="CELERY_BROKER_URL",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="CELERY_RESULT_BACKEND",
    )
    celery_task_serializer: str = Field(default="json", validation_alias="CELERY_TASK_SERIALIZER")
    celery_result_serializer: str = Field(default="json", validation_alias="CELERY_RESULT_SERIALIZER")
    celery_accept_content: str = Field(default="json", validation_alias="CELERY_ACCEPT_CONTENT")
    celery_timezone: str = Field(default="UTC", validation_alias="CELERY_TIMEZONE")
    celery_enable_utc: bool = Field(default=True, validation_alias="CELERY_ENABLE_UTC")
    celery_task_track_started: bool = Field(default=True, validation_alias="CELERY_TASK_TRACK_STARTED")
    celery_task_acks_late: bool = Field(default=True, validation_alias="CELERY_TASK_ACKS_LATE")

settings = Settings()
