Users (Parents / Researchers / Admin)
                |
                v
         React Frontend
   (mobile-friendly web app)
                |
                v
 Azure / Microsoft Entra Auth
 (login, signup, identity tokens)
                |
                v
          FastAPI Backend
  ---------------------------------
  | Auth token validation          |
  | User profile + unique user ID  |
  | Pre/post questionnaire logic   |
  | Episode unlock rules           |
  | Progress tracking              |
  | Research/admin APIs            |
  | Export APIs                    |
  ---------------------------------
         |               |
         |               |
         v               v
 Azure Database      Azure Blob Storage
 for PostgreSQL      audio files / transcripts /
 app data            uploaded assets
         
                |
                v
      Optional Azure Functions
 (weekly release emails, reminders,
 scheduled jobs, background tasks)


 What each part does
1. React frontend

This is the website parents and researchers see:

login/signup button

questionnaire pages

episode player page

progress bar

admin/research dashboard

2. Azure authentication

This handles:

sign up

sign in

password/security

identity tokens

So you do not need to build your own password system.

3. FastAPI backend

This is the brain of the system. It should handle:

verify Azure tokens

create/find the user in your database

check whether pre-questionnaire is completed

allow episode 1 only after pre-questionnaire

unlock episode 2 only after episode 1 + activities complete

block unreleased weekly content

save questionnaire/activity responses

save timestamps and engagement duration

expose researcher/admin export endpoints

4. PostgreSQL database

Store tables like:

users

questionnaires

episodes

episode_progress

activity_responses

release_schedule

audit/export logs

5. Blob storage

Store:

podcast/audio files

text transcripts

images or downloadable assets

6. Azure Functions

Only use these for:

weekly episode release scheduler

reminder emails

“episode now available” emails

maybe nightly export/backup jobs

Very simple table of what to use
Need	Best choice
Login/signup	Azure / Microsoft Entra
Main backend API	FastAPI
Structured app data	Azure PostgreSQL
Audio/files	Azure Blob Storage
Scheduled emails/jobs	Azure Functions
Frontend UI	React


api://0c14d865-04b2-4427-9e4f-273649aee872
api://f6b1eb6a-3323-4ac9-908a-98799bed15a1/access_as_user