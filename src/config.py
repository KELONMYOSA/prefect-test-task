from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    TG_TOKEN: str
    TG_CHAT_ID: str

    API_URL: str
    API_KEY: str


settings = Settings()
