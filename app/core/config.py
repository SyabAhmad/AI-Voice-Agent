from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    retell_agent_id: str
    retell_api_key: str

    groq_api_key: str

    brevo_api_key: str = "xsh-xxxxxxxxxxxxxxxxxxxxxxxx"

    resend_api_key: Optional[str] = None

    environment: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
