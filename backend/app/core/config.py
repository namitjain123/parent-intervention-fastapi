from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str

    # Azure CIAM (auth)
    TENANT_ID: str
    CLIENT_ID: str

    # Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING: str | None = None
    AZURE_STORAGE_CONTAINER_NAME: str = "episodes"

    # Azure Communication Services (email)
    AZURE_COMMUNICATION_CONNECTION_STRING: str | None = None
    AZURE_EMAIL_SENDER: str | None = None

    # URLs
    FRONTEND_URL: str = "https://www.diplatformlab.com"
    BACKEND_BASE_URL: str = "http://127.0.0.1:8000"

    # Uploads
    UPLOAD_DIR: str = "uploads"

    # Study flow timing
    # NOTE: originally hardcoded to 1 minute in main.py for testing.
    # Production value should be 30 days per class_flow_config.py's flow description.
    DELAYED_SURVEY_UNLOCK_MINUTES: int = 1

    # Scheduler intervals (minutes)
    # TODO: change to daily intervals (60 * 24) after testing, per original main.py TODO.
    DELAYED_UNLOCK_JOB_INTERVAL_MINUTES: int = 1
    INACTIVITY_REMINDER_JOB_INTERVAL_MINUTES: int = 100
    PROGRESS_REMINDER_JOB_INTERVAL_MINUTES: int = 100

    @property
    def openid_config_url(self) -> str:
        return (
            f"https://parentingplatform.ciamlogin.com/"
            f"{self.TENANT_ID}/v2.0/.well-known/openid-configuration"
        )


settings = Settings()
