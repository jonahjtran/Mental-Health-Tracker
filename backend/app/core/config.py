from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = Field(validation_alias="DATABASE_URL")
    jwt_secret: str = Field(validation_alias="JWT_SECRET")
    jwt_expiration_minutes: int = Field(validation_alias="JWT_EXPIRES_MINUTES")
    google_client_id: Optional[str] = Field(default=None, validation_alias="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, validation_alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: Optional[str] = Field(default=None, validation_alias="GOOGLE_REDIRECT_URI")
    frontend_url: str = Field(validation_alias="FRONTEND_URL")
    insights_model: Optional[str] = Field(default=None, validation_alias="INSIGHTS_MODEL")
    insights_api_key: Optional[str] = Field(default=None, validation_alias="INSIGHTS_API_KEY")

settings = Settings()
