from app.models import Episode, User


def get_profile_payload(user: User) -> dict:
    return {
        "id": user.id,
        "azure_id": user.azure_id,
        "name": user.name,
        "email": user.email,
        "pre_questionnaire_completed": user.pre_questionnaire_completed,
        "post_questionnaire_completed": user.post_questionnaire_completed,
        "current_episode": user.current_episode,
        "user_class": user.user_class,
        "grade": user.grade,
        "teacher_name": user.teacher_name,
        "delayed_survey_unlocked": user.delayed_survey_unlocked,
        "delayed_survey_completed": user.delayed_survey_completed,
        "delayed_unlock_at": user.delayed_unlock_at,
    }


def compute_episode_status(user: User, episode: Episode) -> str:
    if not user.pre_questionnaire_completed:
        return "locked"
    if user.user_class == "B" and not user.delayed_survey_completed:
        return "locked"
    if episode.episode_number < user.current_episode:
        return "completed"
    if episode.episode_number == user.current_episode:
        return "unlocked"
    return "locked"


def get_dashboard_payload(user: User, episodes: list[Episode]) -> dict:
    episode_payload = [
        {
            "episode_number": ep.episode_number,
            "title": ep.title,
            "description": ep.description,
            "audio_url": ep.audio_url,
            "status": compute_episode_status(user, ep),
        }
        for ep in episodes
    ]

    return {
        "name": user.name,
        "email": user.email,
        "azure_id": user.azure_id,
        "pre_questionnaire_completed": user.pre_questionnaire_completed,
        "post_questionnaire_completed": user.post_questionnaire_completed,
        "current_episode": user.current_episode,
        "all_episodes_completed": user.current_episode > 8,
        "user_class": user.user_class,
        "grade": user.grade,
        "teacher_name": user.teacher_name,
        "delayed_survey_unlocked": user.delayed_survey_unlocked,
        "delayed_survey_completed": user.delayed_survey_completed,
        "delayed_unlock_at": user.delayed_unlock_at,
        "show_delayed_survey": (
            user.user_class == "B"
            and user.delayed_survey_unlocked
            and not user.delayed_survey_completed
        ),
        "delayed_survey_locked": (
            user.user_class == "B" and not user.delayed_survey_unlocked
        ),
        "episodes": episode_payload,
    }
