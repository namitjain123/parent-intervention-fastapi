from pydantic import BaseModel
from typing import Optional, List


class UserOut(BaseModel):
    id: int
    azure_id: str
    name: str
    email: str
    pre_questionnaire_completed: bool
    current_episode: int

    class Config:
        from_attributes = True


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: str


class EpisodeOut(BaseModel):
    episode_number: int
    title: str
    description: Optional[str]
    audio_url: str
    transcript_url: Optional[str] = None
    transcript_text: Optional[str] = ""
    quiz: List[QuizQuestion] = []

    class Config:
        from_attributes = True


class DashboardOut(BaseModel):
    name: str
    email: str
    pre_questionnaire_completed: bool
    current_episode: int
    episodes: List[EpisodeOut]


class CompletePreQRequest(BaseModel):
    participant_id: str

class EpisodeCompleteRequest(BaseModel):
    time_spent_seconds: int

class QuizResponseRequest(BaseModel):
    question_text: Optional[str] = None
    response_text: Optional[str] = None
    skipped: bool = False

class EpisodeReactionRequest(BaseModel):
    emoji: str
    audio_timestamp_seconds: int