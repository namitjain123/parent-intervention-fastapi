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

    # Study flow timing.
    # Class B wait: 28 days = 40320 minutes (matches the unlock email subject).
    DELAYED_SURVEY_UNLOCK_MINUTES: int = 2

    # Scheduler intervals (minutes) - how OFTEN each job checks, not the
    # actual eligibility threshold. Delayed-unlock stays frequent since it's a
    # single cheap indexed query and users should unlock promptly once their
    # wait is up; the reminder jobs check hourly since their thresholds are
    # measured in days - checking every minute for those was pure overhead
    # and caused APScheduler's "maximum instances reached" overlap warnings.
    DELAYED_UNLOCK_JOB_INTERVAL_MINUTES: int = 2
    INACTIVITY_REMINDER_JOB_INTERVAL_MINUTES: int = 2
    PRE_SURVEY_REMINDER_JOB_INTERVAL_MINUTES: int = 2
    POST_SURVEY_REMINDER_JOB_INTERVAL_MINUTES: int = 2

    # Inactivity nudge: post-Q not done, inactive this long. Repeats at the
    # same interval, up to INACTIVITY_REMINDER_MAX_COUNT times.
    # 7 days = 10080 minutes.
    INACTIVITY_REMINDER_INTERVAL_MINUTES: int = 5
    INACTIVITY_REMINDER_MAX_COUNT: int = 5

    # Pre-questionnaire nudge: registered but never started the pre-questionnaire.
    # Sent every PRE_SURVEY_REMINDER_INTERVAL_MINUTES, up to PRE_SURVEY_REMINDER_MAX_COUNT
    # times. 2 days = 2880 minutes.
    PRE_SURVEY_REMINDER_INTERVAL_MINUTES: int = 3
    PRE_SURVEY_REMINDER_MAX_COUNT: int = 5

    # Post-test nudge: all 8 episodes done but the post-questionnaire isn't.
    # Sent every POST_SURVEY_REMINDER_INTERVAL_MINUTES since completing the
    # last episode (or since the last reminder), up to
    # POST_SURVEY_REMINDER_MAX_COUNT times. 2 days = 2880 minutes.
    POST_SURVEY_REMINDER_INTERVAL_MINUTES: int = 1
    POST_SURVEY_REMINDER_MAX_COUNT: int = 5

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
