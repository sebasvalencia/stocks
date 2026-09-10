from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://acciones:acciones@localhost:5432/acciones"


settings = Settings()
