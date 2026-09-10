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
    PRE_SURVEY_REMINDER_JOB_INTERVAL_MINUTES: int = 10

    # Pre-questionnaire nudge: registered but never started the pre-questionnaire.
    # Sent every PRE_SURVEY_REMINDER_INTERVAL_MINUTES, up to PRE_SURVEY_REMINDER_MAX_COUNT
    # times. In minutes (not days) so it can be sped up for testing, same as
    # DELAYED_SURVEY_UNLOCK_MINUTES above. Production value should be 2 days = 2880.
    PRE_SURVEY_REMINDER_INTERVAL_MINUTES: int = 10
    PRE_SURVEY_REMINDER_MAX_COUNT: int = 7


    

    @property
    def openid_config_url(self) -> str:
        return (
            f"https://parentingplatform.ciamlogin.com/"
            f"{self.TENANT_ID}/v2.0/.well-known/openid-configuration"
        )

    @property
    def cors_origins(self) -> list[str]:
        """
        FRONTEND_URL plus its www / non-www counterpart, so the browser's exact
        Origin header matches regardless of which one a visitor actually lands on
        (CORS treats www.example.com and example.com as different origins).
        """
        origins = {self.FRONTEND_URL, "http://localhost:5173"}

        if "://www." in self.FRONTEND_URL:
            origins.add(self.FRONTEND_URL.replace("://www.", "://", 1))
        else:
            scheme, _, rest = self.FRONTEND_URL.partition("://")
            if scheme and rest:
                origins.add(f"{scheme}://www.{rest}")

        return sorted(origins)


settings = Settings()
