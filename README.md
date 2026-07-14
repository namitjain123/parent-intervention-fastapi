# Parent Intervention Platform — Backend

A FastAPI backend that powers a parent-intervention research platform. Participants authenticate via Microsoft Azure CIAM, complete a pre-questionnaire on REDCap, listen to podcast episodes, take quizzes, and are automatically placed into one of two study flows (Class A or Class B) based on their teacher/grade assignment.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database & Models](#database--models)
- [How the Backend & Database Connect](#how-the-backend--database-connect)
- [Authentication Flow](#authentication-flow)
- [Study Flow: Class A vs Class B](#study-flow-class-a-vs-class-b)
- [API Endpoints](#api-endpoints)
- [Background Scheduler Jobs](#background-scheduler-jobs)
- [Environment Variables](#environment-variables)
- [Running Locally](#running-locally)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | Azure CIAM (JWT / RS256) |
| Blob Storage | Azure Blob Storage |
| Email | Microsoft Graph API / Azure Communication |
| Scheduler | APScheduler |
| Schema validation | Pydantic |

---

## Project Structure

```
backend/
├── main.py                  # FastAPI app, all routes, auth, scheduler startup
├── database.py              # Engine, session factory, get_db dependency
├── models.py                # SQLAlchemy ORM models (tables)
├── schemas.py               # Pydantic request/response schemas
├── class_flow_config.py     # Grade + teacher → Class A/B mapping
├── blob_service.py          # Azure Blob upload helper
├── seed_episodes.py         # One-time script to populate episodes table
├── migrate_add_grade_teacher.py  # DB migration script
└── utils/
    ├── activity.py          # Update last_activity_at on each request
    ├── email_service.py     # Inactivity + progress reminder emails
    ├── email_service_classflow.py  # Class B lock/unlock emails
    ├── reminder_service.py  # Query users who need reminders
    └── transcript_utils.py  # Extract text from .docx transcript files
```

---

## Database & Models

The database has five tables:

### `users`
Stores one row per authenticated participant.

| Column | Purpose |
|---|---|
| `azure_id` | Unique Microsoft identity, used to look up users on login |
| `user_class` | `"A"` (normal flow) or `"B"` (delayed flow) |
| `grade` | `"7"`, `"8"`, or `"9"` — from REDCap pre-questionnaire |
| `teacher_code` / `teacher_name` | Teacher selected in REDCap |
| `current_episode` | Next episode the user can access (starts at 0) |
| `pre_questionnaire_completed` | Unlocks episode access |
| `delayed_survey_unlocked` | Class B only — becomes `true` after 30-day wait |
| `delayed_survey_completed` | Class B only — must complete before episodes unlock |

### `episodes`
Stores each podcast episode (seeded via `seed_episodes.py`).

| Column | Purpose |
|---|---|
| `episode_number` | Sequential number (1–8+) |
| `audio_url` | Azure Blob URL to the MP3 |
| `transcript_url` / `transcript_text` | Optional transcript |
| `quiz_json` | JSON string of quiz questions |

### `user_episode_progress`
Join table: which user has started/completed which episode.

### `user_quiz_responses`
Stores each quiz answer (or skip) a user submits.

### `user_episode_reactions`
Stores emoji reactions tied to a specific audio timestamp in an episode.

---

## How the Backend & Database Connect

```
.env file
  └── DATABASE_URL
        ↓
database.py
  ├── create_engine()      → raw connection to SQLite/Postgres
  ├── SessionLocal()       → factory that creates DB sessions
  └── get_db()             → FastAPI dependency: opens session per request,
                             yields it to the route handler, closes it after

models.py
  └── Python classes (User, Episode, …) → SQLAlchemy maps these to SQL tables
      Base.metadata.create_all(bind=engine)  → creates tables if they don't exist

main.py (route handler example)
  @app.get("/me")
  def get_me(user=Depends(verify_token), db: Session = Depends(get_db)):
      db_user = db.query(User).filter(User.azure_id == ...).first()
      return db_user
```

Every HTTP request gets its own fresh DB session injected by `Depends(get_db)`. The session is automatically closed when the request finishes, preventing connection leaks.

---

## Authentication Flow

1. The frontend logs the user in via **Microsoft Azure CIAM** (OAuth2 / PKCE).
2. Azure returns a **JWT access token**.
3. Every API request sends the token in the `Authorization: Bearer <token>` header.
4. `verify_token()` in [main.py](backend/main.py) validates the token:
   - Fetches public keys from Azure's JWKS endpoint.
   - Verifies signature (RS256), audience (`CLIENT_ID`), and issuer.
5. `get_or_create_user()` looks up the user by `azure_id` (the `sub` claim). If they don't exist yet, a new `User` row is created automatically.

---

## Study Flow: Class A vs Class B

Participant flow is decided once during pre-questionnaire completion, based on grade + teacher (configured in [class_flow_config.py](backend/class_flow_config.py)).

```
POST /complete-pre-questionnaire
  ├── REDCap sends grade + teacher_code
  ├── resolve_flow(grade, teacher_code) → "A" or "B"
  │
  ├── Class A:  current_episode = 1  → episodes unlock immediately
  │
  └── Class B:  delayed_survey_unlocked = False
                delayed_unlock_at = now + 30 days
                Lock email sent → episodes locked for 30 days
                Background job checks every minute → when time expires:
                  delayed_survey_unlocked = True
                  Unlock email sent → participant completes delayed survey
                  delayed_survey_completed = True → episodes unlock
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/me` | Get current user's profile and study state |
| `GET` | `/dashboard` | Get all episodes with per-episode lock/unlock status |
| `POST` | `/complete-pre-questionnaire` | Mark pre-Q done, assign Class A/B, unlock episode 1 or start 30-day wait |
| `GET` | `/episode/{episode_number}` | Get episode content (audio, transcript, quiz) |
| `POST` | `/episode/{episode_number}/complete` | Mark episode completed, advance `current_episode` |
| `POST` | `/episode/{episode_number}/quiz` | Submit a quiz response |
| `POST` | `/episode/{episode_number}/reaction` | Submit an emoji reaction at an audio timestamp |
| `POST` | `/complete-post-questionnaire` | Mark post-questionnaire done |
| `POST` | `/complete-delayed-questionnaire` | Class B only — unlock episodes after delayed survey |
| `POST` | `/admin/episodes` | (Admin) Create a new episode |
| `POST` | `/admin/episodes/{id}/upload-audio` | (Admin) Upload audio to Azure Blob |
| `POST` | `/admin/process-delayed-unlocks` | (Admin) Manually trigger the delayed unlock job |

---

## Background Scheduler Jobs

Three jobs run automatically on startup via APScheduler:

| Job | Interval | What it does |
|---|---|---|
| `scheduled_process_delayed_unlocks` | Every 1 minute | Finds Class B users whose 30-day timer has expired and unlocks their survey, sends unlock email |
| `scheduled_send_inactivity_reminders` | Every 100 minutes | Emails users who have been inactive and haven't finished the program |
| `scheduled_send_25day_reminders` | Every 100 minutes | Emails users who are at the 25-day mark to encourage progress |

These jobs open their own DB sessions via `SessionLocal()` directly (no HTTP request to inject into).

---

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=sqlite:///./app.db

# Azure CIAM
TENANT_ID=your-azure-tenant-id
CLIENT_ID=your-azure-app-client-id

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_CONTAINER_NAME=your-container-name

# App URLs
FRONTEND_URL=https://www.yourdomain.com
BACKEND_BASE_URL=https://api.yourdomain.com

# Email / Microsoft Graph
EMAIL_CLIENT_ID=...
EMAIL_CLIENT_SECRET=...
EMAIL_TENANT_ID=...
SENDER_EMAIL=noreply@yourdomain.com
```

---

## Running Locally

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your values

# 4. Start the server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs (Swagger UI) are at `http://localhost:8000/docs`.

> **Note:** On first run, `Base.metadata.create_all(bind=engine)` automatically creates all database tables if they don't exist.
