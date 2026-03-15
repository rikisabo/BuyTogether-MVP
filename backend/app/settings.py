from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    CORS_ORIGINS: str = "http://localhost:5173"
    LOG_LEVEL: str = "info"
    # email configuration (SMTP); if SMTP_HOST is unset, emails are logged
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "s0533160580@gmail.com"
    SMTP_PASS: str = "mxad oslv chad zgcr"
    EMAIL_FROM: str = "s0533160580@gmail.com"
    # frontend url for constructing confirmation links
    FRONTEND_URL: AnyUrl = "http://localhost:5173"

settings = Settings()