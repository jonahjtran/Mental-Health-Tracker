from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = Field(validation_alias="DATABASE_URL")
    jwt_secret: str = Field(validation_alias="JWT_SECRET")
    jwt_expiration_minutes: int = Field(validation_alias="JWT_EXPIRES_MINUTES")
    google_client_id: str = Field(validation_alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(validation_alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(validation_alias="GOOGLE_REDIRECT_URI")
    frontend_url: str = Field(validation_alias="FRONTEND_URL")
    #insights_prompt: str = Field(validation_alias="INSIGHTS_PROMPT")
    insights_model: str = Field(validation_alias="INSIGHTS_MODEL")
    insights_api_key: str = Field(validation_alias="INSIGHTS_API_KEY")

settings = Settings()