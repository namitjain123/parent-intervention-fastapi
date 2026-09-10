"""
Pre-questionnaire grade / teacher -> flow mapping.

The pre-questionnaire (REDCap) collects a GRADE (7, 8 or 9) and, branched on
that grade, a TEACHER. Which flow a participant follows is decided here by the
selected teacher:

    flow "A" -> normal flow      (episode unlocks immediately)
    flow "B" -> delayed flow      (lock email, 28-day wait, delayed survey, then unlock)

REDCap sends the teacher's CODED value (the value, not the label). Keep the keys
below in sync with the coded values configured in the REDCap teacher dropdowns.

To change who is delayed, just edit the "flow" for a teacher. Each grade has its
own teacher list, so the delayed teacher can differ per grade.
"""

# grade -> teacher_code -> {"name": <display name>, "flow": "A" | "B"}
TEACHER_FLOW_CONFIG = {
    "7": {
        "1": {"name": "Ms B Huynh", "flow": "A"},
        "2": {"name": "Mrs A Reddy", "flow": "A"},
        "3": {"name": "Mr T Greszewski", "flow": "A"},
        "4": {"name": "Mrs J Piccin", "flow": "B"},
        "5": {"name": "Mrs S Hudson", "flow": "B"},
    },
    "8": {
        "1": {"name": "Mrs S Hudson", "flow": "A"},
        "2": {"name": "Mrs J Piccin", "flow": "A"},
        "3": {"name": "Ms A Gray", "flow": "B"},
        "4": {"name": "Mr T Greszewski", "flow": "B"},
        "5": {"name": "Ms J Zarebski", "flow": "B"},
    },
    "9": {
        "1": {"name": "Mr T Greszewski", "flow": "A"},
        "2": {"name": "Mrs J Piccin", "flow": "A"},
        "3": {"name": "Ms A Gray", "flow": "A"},
        "4": {"name": "Ms M van Bever Donker", "flow": "B"},
        "5": {"name": "Ms B Huynh", "flow": "B"},
    },
}

VALID_GRADES = set(TEACHER_FLOW_CONFIG.keys())


def resolve_flow(grade: str, teacher_code: str):
    """
    Resolve (grade, teacher_code) -> (flow, teacher_name).

    Raises ValueError if the grade or teacher is not in the config.
    """
    grade = (grade or "").strip()
    teacher_code = (teacher_code or "").strip()

    # Normalise "Grade 7" -> "7" in case REDCap sends the label instead of the code
    if grade.lower().startswith("grade"):
        grade = grade.split()[-1]

    grade_teachers = TEACHER_FLOW_CONFIG.get(grade)
    if grade_teachers is None:
        raise ValueError(f"Unknown grade: {grade!r}. Expected one of {sorted(VALID_GRADES)}.")

    teacher = grade_teachers.get(teacher_code)
    if teacher is None:
        raise ValueError(
            f"Unknown teacher {teacher_code!r} for grade {grade!r}. "
            f"Expected one of {sorted(grade_teachers.keys())}."
        )

    return teacher["flow"], teacher["name"]
