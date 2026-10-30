from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Learning Platform"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./learning_platform.db"
    secret_key: str = "development-only-change-this-key-before-deployment"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
