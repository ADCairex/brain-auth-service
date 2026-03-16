from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/brain?options=-csearch_path%3Dauth"
    secret_key: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    environment: str = "development"

    model_config = {"env_file": ".env"}


settings = Settings()
