from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Mapea DATABASE_URL del entorno. Sin default: en un servidor cambia."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        extra="ignore",
    )

    database_url: str


settings = Settings()
