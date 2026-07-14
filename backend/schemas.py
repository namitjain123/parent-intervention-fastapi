from pydantic import BaseModel
from typing import Optional, List


# =========================
# USER
# =========================
class UserOut(BaseModel):
    id: int
    azure_id: str
    name: str
    email: str

    pre_questionnaire_completed: bool
    current_episode: int

    # 🔥 ADD THIS
    user_class: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# QUIZ
# =========================
class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: str


# =========================
# EPISODE
# =========================
class EpisodeOut(BaseModel):
    episode_number: int
    title: str
    description: Optional[str]

    audio_url: str

    transcript_url: Optional[str] = None
    transcript_text: Optional[str] = ""

    # 🔥 CHANGE THIS (since DB stores JSON string)
    quiz_json: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# DASHBOARD
# =========================
class DashboardOut(BaseModel):
    name: str
    email: str

    pre_questionnaire_completed: bool
    current_episode: int

    # 🔥 OPTIONAL (for Class B flow)
    user_class: Optional[str] = None
    delayed_survey_unlocked: Optional[bool] = False

    episodes: List[EpisodeOut]


# =========================
# REQUESTS
# =========================
class CompletePreQRequest(BaseModel):
    participant_id: str

    # 🔥 grade (7/8/9) + teacher coded value from REDCap.
    # The A/B flow is derived from these on the backend.
    grade: str
    teacher: str


class EpisodeCompleteRequest(BaseModel):
    time_spent_seconds: int


class QuizResponseRequest(BaseModel):
    question_text: Optional[str] = None
    response_text: Optional[str] = None
    skipped: bool = False


class EpisodeReactionRequest(BaseModel):
    emoji: str
    audio_timestamp_seconds: int