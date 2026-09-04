# Integration Setup Guide

## What Was Built

The HR Recruiter Agent now has 21 tools across 5 categories:

| Category | Tools |
|---|---|
| Core HR | generate JD, save JD, list roles, screen resume, save candidate, list candidates, draft email |
| Google Drive | read resume from Drive, save document to Drive, list Drive files |
| Gmail | send email now, list unread emails |
| Google Calendar | schedule interview (with Meet link), check availability |
| Greenhouse | list jobs, get applications, update application |
| BambooHR | list applicants, update applicant |
| Lever | list candidates, update candidate |

---

## Step 1 — Google Setup (Gmail + Drive + Calendar)

### 1.1 Create a Google Cloud Project

1. Go to https://console.cloud.google.com
2. Click the project dropdown at the top → **New Project**
3. Name it `HR Recruiter Agent` → Create

### 1.2 Enable APIs

In the left menu go to **APIs & Services → Library** and enable all three:
- **Gmail API**
- **Google Drive API**
- **Google Calendar API**

### 1.3 Create OAuth Credentials

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. If prompted to configure the consent screen:
   - User type: **External**
   - App name: `HR Recruiter Agent`
   - Add your Google account as a test user
4. Application type: **Desktop app**
5. Name it anything (e.g. `HR Agent Local`)
6. Click **Create** → **Download JSON**
7. Save the downloaded file as `setup/credentials.json`

### 1.4 Run the Auth Script (one time)

```powershell
cd C:\Users\LENOVO\Documents\HRRecruiterAgentNew\HRRecruiterAgentNew
pip install google-auth-oauthlib
python setup/google_auth.py --credentials setup/credentials.json
```

A browser opens. Log in with the Google account the agent should use.

Copy the three lines printed at the end into `app/HRRecruiterAgent/.env`:
```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REFRESH_TOKEN=1//your-refresh-token
```

---

## Step 2 — Greenhouse Setup

1. Sign up at https://www.greenhouse.io (free trial available)
2. Go to **Settings → Dev Center → API Credential Management**
3. Click **Create New API Key**
   - Type: **Harvest**
   - Name: `HR Recruiter Agent`
4. Copy the key and add to `.env`:
```
GREENHOUSE_API_KEY=your-greenhouse-api-key
```

---

## Step 3 — BambooHR Setup

1. Sign up at https://www.bamboohr.com (free trial available)
2. Once logged in, click your name (top right) → **API Keys**
3. Click **Add New Key**
   - Name: `HR Recruiter Agent`
4. Copy the key. Your company subdomain is in the URL:
   `https://acme.bamboohr.com` → subdomain is `acme`
5. Add to `.env`:
```
BAMBOOHR_API_KEY=your-bamboohr-api-key
BAMBOOHR_COMPANY=your-company-subdomain
```

---

## Step 4 — Lever Setup

1. Sign up at https://www.lever.co (free trial available)
2. Go to **Settings → Integrations → API Credentials**
3. Click **Generate New API Key**
   - Name: `HR Recruiter Agent`
4. Add to `.env`:
```
LEVER_API_KEY=your-lever-api-key
```

---

## Step 5 — Install New Dependencies

```powershell
cd C:\Users\LENOVO\Documents\HRRecruiterAgentNew\HRRecruiterAgentNew\app\HRRecruiterAgent
uv sync
```

---

## Step 6 — Deploy

```powershell
cd C:\Users\LENOVO\Documents\HRRecruiterAgentNew\HRRecruiterAgentNew
$env:AWS_PROFILE = "chidiadioscar3"
agentcore deploy --yes
```

---

## Step 7 — Test in Slack

Try these prompts:

**Google Drive:**
> "Read John Smith's resume from my Google Drive and screen him for the Engineering role"

**Gmail:**
> "Send John Smith an interview invitation for next Tuesday at 2pm"

**Calendar:**
> "Check my availability on September 10th and schedule an interview with Sarah"

**Greenhouse:**
> "Pull all active applications from Greenhouse for job 123 and screen them"

**BambooHR:**
> "Show me all active applicants in BambooHR"

---

## .env File Template

Your complete `app/HRRecruiterAgent/.env` should look like this:

```
# AWS
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
HR_S3_BUCKET=hr-recruiter-agent-data
HR_S3_PREFIX=hr-agent
MEMORY_NAME=HRRecruiterMemory

# Google
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=

# ATS
GREENHOUSE_API_KEY=
BAMBOOHR_API_KEY=
BAMBOOHR_COMPANY=
LEVER_API_KEY=
```
