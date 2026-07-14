# Parent Intervention Platform

A full-stack research platform for a parent-intervention study. Participants authenticate via Microsoft Azure CIAM, complete a pre-questionnaire on REDCap, listen to podcast episodes, take quizzes, and are automatically placed into one of two study flows (Class A or Class B) based on their teacher/grade assignment.

- **Backend**: FastAPI + SQLAlchemy + Alembic ([backend/](backend/))
- **Frontend**: React + Vite + CSS Modules ([frontend/](frontend/))

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Backend Structure](#backend-structure)
- [Frontend Structure](#frontend-structure)
- [Database & Models](#database--models)
- [How the Backend & Database Connect](#how-the-backend--database-connect)
- [Authentication Flow](#authentication-flow)
- [Study Flow: Class A vs Class B](#study-flow-class-a-vs-class-b)
- [API Endpoints](#api-endpoints)
- [Background Scheduler Jobs](#background-scheduler-jobs)
- [Database Migrations (Alembic)](#database-migrations-alembic)
- [Environment Variables](#environment-variables)
- [Running Locally](#running-locally)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | Azure CIAM (JWT / RS256) |
| Blob Storage | Azure Blob Storage |
| Email | Azure Communication Services |
| Scheduler | APScheduler |
| Schema validation | Pydantic / Pydantic Settings |
| Frontend framework | React (Vite) |
| Routing | React Router |
| Styling | CSS Modules |
| Auth (frontend) | MSAL (`@azure/msal-react`) |

---

## Backend Structure

Routes are thin — they validate input, call a service, and return the result. All business logic lives in `app/services/`.

```
backend/
├── main.py                        # Thin entry point: `from app.main import app`
│                                   # (kept at top level so `uvicorn main:app` and the
│                                   #  Azure deploy workflow work unchanged)
├── requirements.txt
├── alembic.ini
│
├── app/
│   ├── main.py                    # FastAPI app factory: CORS, static mount, routers, lifespan
│   │
│   ├── core/
│   │   ├── config.py              # Settings (Pydantic Settings) — all env vars, typed & validated
│   │   ├── security.py            # JWT/JWKS verification, get_or_create_user()
│   │   └── scheduler.py           # APScheduler job definitions + start/stop
│   │
│   ├── db/
│   │   ├── base.py                # Base = declarative_base()
│   │   └── session.py             # engine, SessionLocal, get_db() dependency
│   │
│   ├── models.py                  # SQLAlchemy ORM models (tables)
│   ├── schemas.py                 # Pydantic request/response schemas
│   ├── class_flow_config.py       # Grade + teacher → Class A/B mapping
│   │
│   ├── services/                  # ⭐ Business logic lives here
│   │   ├── user_service.py        # Profile + dashboard payload building
│   │   ├── questionnaire_service.py  # Pre/post/delayed questionnaire completion, access status
│   │   ├── episode_service.py     # Episode CRUD, progress tracking, transcript/audio upload
│   │   ├── episode_access.py      # ensure_episode_access(), process_delayed_survey_unlocks()
│   │   ├── blob_service.py        # Azure Blob upload helper
│   │   ├── email_service.py       # Inactivity + progress reminder emails
│   │   ├── email_service_classflow.py  # Class B lock/unlock emails
│   │   ├── reminder_service.py    # Query users who need reminders
│   │   └── activity_service.py    # Update last_activity_at on each request
│   │
│   └── api/
│       ├── deps.py                # Shared get_current_user dependency
│       └── routes/
│           ├── users.py           # /me, /dashboard
│           ├── questionnaires.py  # mark-*-complete, /survey-access-status
│           ├── episodes.py        # /episodes/*, /upload-transcript/*
│           └── admin.py           # /admin/*
│
├── alembic/
│   ├── env.py                     # Wired to app.core.config.settings + app.models
│   └── versions/                  # Migration scripts
│
├── seed_episodes.py                # One-time script to populate the episodes table
├── migrate_add_grade_teacher.py    # Historical migration (superseded by Alembic)
├── send_reminder.py                # Standalone script to trigger reminder emails manually
└── uploads/                        # Local file storage (transcripts staged before Blob upload)
```

---

## Frontend Structure

Each page lives in its own folder with a co-located CSS Module. Shared config, hooks, and global styles are pulled out of `src/` root.

```
frontend/src/
├── main.jsx                        # App bootstrap: MSAL init + React Router routes
│
├── pages/
│   ├── DashboardPage/
│   │   ├── DashboardPage.jsx       # Main authenticated view (episode grid, questionnaire gates)
│   │   └── DashboardPage.module.css
│   ├── LoginPage/
│   │   ├── LoginPage.jsx           # Consent + Azure login
│   │   └── LoginPage.module.css
│   ├── EpisodePage/
│   │   ├── EpisodePage.jsx         # Audio player, transcript sync, quiz, reactions
│   │   └── EpisodePage.module.css
│   ├── ConsentPage/
│   │   ├── ConsentPage.jsx
│   │   └── ConsentPage.module.css
│   ├── RedcapCompletePage/         # REDCap pre-questionnaire redirect handler
│   ├── RedcapPostCompletePage/     # REDCap post-questionnaire redirect handler
│   └── DelayedRedcapCompletePage/  # REDCap delayed-survey redirect handler (Class B)
│
├── hooks/
│   └── useIsMobile.js              # Responsive breakpoint hook (768px)
│
├── config/
│   ├── authConfig.js               # MSAL config (msalConfig, loginRequest, apiRequest)
│   └── config.js                   # API_BASE_URL
│
├── styles/
│   └── global.css                  # Global resets (currently unused — no global classes yet)
│
└── assets/                         # Static images (react.svg, vite.svg, hero.png — unused scaffold)
```

**Styling convention**: static, structural styles live in each page's `*.module.css` (scoped, collision-proof class names). Genuinely dynamic per-render values — like a mobile/desktop breakpoint computed from `useIsMobile()`, or a reaction marker's `left: %` position computed from audio timestamp — stay as inline `style={{}}` alongside the module `className`. Don't move something into CSS just because it's a style; only static values belong there.

---

## Database & Models

The database has five tables (defined in [app/models.py](backend/app/models.py)):

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
| `delayed_survey_unlocked` | Class B only — becomes `true` after the wait period |
| `delayed_survey_completed` | Class B only — must complete before episodes unlock |

### `episodes`
Stores each podcast episode (seeded via `seed_episodes.py`, or created via `/admin/episodes/upload`).

| Column | Purpose |
|---|---|
| `episode_number` | Sequential number (1–8+) |
| `audio_url` | Azure Blob URL to the MP3 |
| `transcript_url` / `transcript_text` | Optional transcript |
| `quiz_json` | JSON string of quiz questions |

### `user_episode_progress`
Join table: which user has started/completed which episode, and time spent.

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
app/core/config.py (Settings)
        ↓
app/db/session.py
  ├── create_engine()      → raw connection to SQLite/Postgres
  ├── SessionLocal()       → factory that creates DB sessions
  └── get_db()             → FastAPI dependency: opens session per request,
                             yields it to the route handler, closes it after

app/models.py
  └── Python classes (User, Episode, …) → SQLAlchemy maps these to SQL tables

app/api/routes/users.py (route handler example)
  @router.get("/me")
  def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
      update_user_activity(user, db)
      return get_profile_payload(user)   # ← delegates to app/services/user_service.py
```

Every HTTP request gets its own fresh DB session injected by `Depends(get_db)`. The session is automatically closed when the request finishes, preventing connection leaks. Routes never touch business logic directly — they call into `app/services/`.

---

## Authentication Flow

1. The frontend logs the user in via **Microsoft Azure CIAM** (MSAL, OAuth2/PKCE) — see [frontend/src/config/authConfig.js](frontend/src/config/authConfig.js).
2. Azure returns a **JWT access token**.
3. Every API request sends the token in the `Authorization: Bearer <token>` header.
4. `verify_token()` in [app/core/security.py](backend/app/core/security.py) validates the token:
   - Fetches public keys from Azure's JWKS endpoint (once, at import time).
   - Verifies signature (RS256), audience (`CLIENT_ID`), and issuer.
5. `get_or_create_user()` looks up the user by `azure_id` (the `sub` claim). If they don't exist yet, a new `User` row is created automatically.
6. `app/api/deps.py`'s `get_current_user` dependency combines both steps and is what every authenticated route depends on.

---

## Study Flow: Class A vs Class B

Participant flow is decided once during pre-questionnaire completion, based on grade + teacher (configured in [app/class_flow_config.py](backend/app/class_flow_config.py)).

```
POST /mark-prequestionnaire-complete
  ├── REDCap sends grade + teacher_code
  ├── resolve_flow(grade, teacher_code) → "A" or "B"
  │
  ├── Class A:  current_episode = 1  → episodes unlock immediately
  │
  └── Class B:  delayed_survey_unlocked = False
                delayed_unlock_at = now + DELAYED_SURVEY_UNLOCK_MINUTES
                Lock email sent → episodes locked until the wait period ends
                Background job checks every minute → when time expires:
                  delayed_survey_unlocked = True
                  Unlock email sent → participant completes delayed survey
                  delayed_survey_completed = True → episodes unlock
```

> The delayed-unlock wait period is `DELAYED_SURVEY_UNLOCK_MINUTES` in [app/core/config.py](backend/app/core/config.py) (defaults to 1 minute for testing — set to `43200` for 30 days in production).

---

## API Endpoints

| Method | Path | Handler | Description |
|---|---|---|---|
| `GET` | `/me` | `users.py` | Get current user's profile and study state |
| `GET` | `/dashboard` | `users.py` | Get all episodes with per-episode lock/unlock status |
| `POST` | `/mark-prequestionnaire-complete` | `questionnaires.py` | Mark pre-Q done, assign Class A/B, unlock episode 1 or start the wait |
| `POST` | `/mark-delayed-survey-complete` | `questionnaires.py` | Class B only — unlock episodes after delayed survey |
| `POST` | `/mark-postquestionnaire-complete` | `questionnaires.py` | Mark post-questionnaire done |
| `GET` | `/survey-access-status` | `questionnaires.py` | Current lock/unlock state for the survey flow |
| `GET` | `/episodes/{episode_number}` | `episodes.py` | Get episode content (audio, transcript, quiz) |
| `POST` | `/episodes/{episode_number}/start` | `episodes.py` | Record that the user started this episode |
| `POST` | `/episodes/{episode_number}/complete` | `episodes.py` | Mark episode completed, advance `current_episode` |
| `POST` | `/episodes/{episode_number}/quiz-response` | `episodes.py` | Submit a quiz response |
| `POST` | `/episodes/{episode_number}/reaction` | `episodes.py` | Submit an emoji reaction at an audio timestamp |
| `POST` | `/upload-transcript/{episode_number}` | `episodes.py` | Upload/replace a transcript for an episode |
| `POST` | `/admin/episodes/upload` | `admin.py` | Create/update an episode (audio + transcript + quiz) |
| `POST` | `/admin/process-delayed-unlocks` | `admin.py` | Manually trigger the delayed-unlock job |

Interactive docs (Swagger UI) are always available at `/docs` when the server is running.

---

## Background Scheduler Jobs

Three jobs run automatically on startup via APScheduler (see [app/core/scheduler.py](backend/app/core/scheduler.py)):

| Job | Interval | What it does |
|---|---|---|
| `scheduled_process_delayed_unlocks` | Every 1 minute | Finds Class B users whose wait period has expired and unlocks their survey, sends unlock email |
| `scheduled_send_inactivity_reminders` | Every 100 minutes | Emails users who have been inactive and haven't finished the program |
| `scheduled_send_25day_reminders` | Every 100 minutes | Emails users who are at the 25-day mark to encourage progress |

These jobs open their own DB sessions via `SessionLocal()` directly (no HTTP request to inject into).

---

## Database Migrations (Alembic)

Schema changes are managed with Alembic (`app/db/base.py`'s `Base.metadata` is the source of truth, wired in [alembic/env.py](backend/alembic/env.py)).

```bash
# Generate a migration after changing app/models.py
alembic revision --autogenerate -m "describe the change"

# Apply pending migrations
alembic upgrade head

# Check current DB revision
alembic current
```

> `Base.metadata.create_all()` still runs on app startup as a safety net for brand-new environments (so the app doesn't crash if migrations haven't been run yet), but it only creates missing **tables** — it can't add columns to existing ones. Any schema change to an existing table must go through Alembic.

---

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=sqlite:///./local_test.db

# Azure CIAM
TENANT_ID=your-azure-tenant-id
CLIENT_ID=your-azure-app-client-id

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_STORAGE_CONTAINER_NAME=episodes

# Azure Communication Services (email)
AZURE_COMMUNICATION_CONNECTION_STRING=your-connection-string
AZURE_EMAIL_SENDER=noreply@yourdomain.com

# App URLs
FRONTEND_URL=https://www.yourdomain.com
BACKEND_BASE_URL=https://api.yourdomain.com
```

And a `.env` file in the `frontend/` directory:

```env
VITE_AZURE_CLIENT_ID=
VITE_AZURE_AUTHORITY=
VITE_AZURE_KNOWN_AUTHORITY=
VITE_AZURE_REDIRECT_URI=
VITE_AZURE_POST_LOGOUT_REDIRECT_URI=
VITE_API_SCOPE=
VITE_REDCAP_PREQ_URL=
VITE_REDCAP_POSTQ_URL=
VITE_REDCAP_DELAYED_URL=
VITE_REDCAP_CONSENT_URL=
VITE_API_BASE_URL=
```

---

## Running Locally

### Backend

```bash
cd backend

# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables (see above)

# 4. Apply migrations
alembic upgrade head

# 5. (Optional) seed sample episodes
python seed_episodes.py

# 6. Start the server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend

npm install
npm run dev
```

The app will be available at `http://localhost:5173`.
