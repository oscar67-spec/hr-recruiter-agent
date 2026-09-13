# HR Recruiter Agent - AI Assistant Context

> **Last Updated:** September 10, 2026
> **Status:** ✅ Deployed and Operational | 🔄 Testing in Progress
> **Session Owner:** chidiadioscar3

---

## 🎯 Project Mission

Build and deploy an AI-powered HR and recruitment assistant for the **Agents for Humans Hackathon** that helps hiring managers manage their end-to-end recruiting pipeline through natural conversation.

---

## 📍 Current State

### ✅ COMPLETED (August 21, 2026)
1. **Agent Code** - 7 HR tools fully implemented in Python
2. **AWS Deployment** - Live on Bedrock AgentCore in us-east-1
3. **S3 Storage** - Bucket created and IAM permissions configured
4. **Testing** - Successfully invoked, generates job postings, screens resumes
5. **Documentation** - Comprehensive `DEPLOYMENT_COMPLETE.md` created

### ✅ COMPLETED (August 25, 2026)
6. **Slack Integration** - HR Agent bot live in ASK-ME workspace
   - Two Lambda functions deployed (hr-slack-receiver, hr-slack-worker)
   - API Gateway wired and verified
   - Bot responds to @mentions and DMs
   - Plain text responses (no markdown asterisks)
   - Lambda warmed every 5 minutes (no cold starts)
7. **System Prompt Updated** - No markdown formatting in responses

### ✅ COMPLETED (September 4, 2026)
8. **Google Integrations** - Gmail, Drive, Calendar, Forms, Sheets
   - OAuth2 credentials configured and refresh token stored in .env
   - Google Cloud project: `hr-recruiter-agent` (project ID: hr-recruiter-agent-507412)
   - APIs enabled: Gmail, Drive, Calendar, Forms, Sheets
   - Credentials: `setup/credentials.json` (gitignored)
9. **ATS Integrations** - Zoho Recruit + Workable
   - Zoho Recruit: OAuth2 tokens stored in .env
   - Workable: API token stored in .env, subdomain = `builditt`
   - Greenhouse/BambooHR/Lever replaced (required sales demo, no free signup)
10. **Agent expanded to 23 tools** (was 7) - all deployed to AWS
11. **Old duplicate directory deleted** - `C:\Users\LENOVO\Documents\HRRecruiterAgent` removed
12. **Recruiter Dashboard** - Next.js 15 app running locally
    - Login page (email/password auth via NextAuth)
    - Overview with Soft UI design (gradient stat cards, white sidebar)
    - Jobs page, Candidates page with filters, Pipeline/kanban, Candidate detail
    - Reads live data from S3 bucket
    - Running at http://localhost:3000
    - **NOT yet deployed to Vercel** (next step)

## 📍 Current State

### ✅ COMPLETED (September 12, 2026)
1. **Agent Code** - 31 tools fully implemented and deployed
2. **AWS Deployment** - Live on Bedrock AgentCore in us-east-1
3. **S3 Storage** - Bucket created, permanent IAM credentials (no more SSO expiry)
4. **Slack Integration** - HR Agent bot live in ASK-ME workspace
5. **Google Integrations** - Gmail, Drive, Calendar, Forms, Sheets (all fixed and working)
6. **ATS Integrations** - Zoho Recruit (full CRUD) + Workable (read + update)
7. **Dashboard** - Rebuilt with Apple design system, deployed to Vercel
8. **AWS SSO Fixed** - Permanent IAM users for both dashboard and agentcore deploy
9. **Agent Fixes** - Raw JSON output bug fixed, model upgraded to Nova Pro
10. **Zoho Fixed** - list_zoho_jobs fixed, create_zoho_job fixed (Client_Name required field)
11. **Google Forms Fixed** - create_job_application_form fully working
12. **System Prompt Rewritten** - Agent is now fully autonomous, no passive suggestions
13. **GitHub** - All code pushed, secrets removed, MIT license added
14. **README** - Full README with ASCII architecture diagram pushed to GitHub

### ⏳ TODO (September 13, 2026 session):
- Replace ASCII architecture diagram in README with proper Mermaid visual diagram
- Screenshot/export the diagram for Devpost submission
- Rigorous testing of all 31 tools via Slack
- Record 5-minute demo video
- Get AWS Builder ID (email: info@abiaskillsmarket.com)
- Publish build story on builder.aws.com (bonus points)
- Submit to Devpost before September 14, 5pm PDT

### Testing Checklist (via Slack):
- [x] Job generation working
- [x] Create job in Zoho Recruit
- [x] Google Forms creation
- [x] Gmail send
- [x] Gmail list unread
- [x] Google Calendar check availability
- [x] Google Calendar schedule interview
- [ ] Zoho: list jobs
- [ ] Zoho: get candidates
- [ ] Zoho: create candidate
- [ ] Zoho: update candidate
- [ ] Zoho: close job
- [ ] Workable: list jobs
- [ ] Workable: get candidates
- [ ] Workable: update candidate
- [ ] Google Drive: list files
- [ ] Google Drive: save document
- [ ] Google Drive: read resume
- [ ] S3: save job posting
- [ ] S3: list job postings
- [ ] S3: save candidate
- [ ] S3: list candidates
- [ ] End-to-end: pull candidates from Zoho → screen → push results back
- [ ] Dashboard: verify data shows up correctly

---

## 🏗️ Architecture

```
User (Slack / Dashboard / CLI)
     ↓
AWS Bedrock AgentCore Runtime (us-east-1)
     ├── Strands Agent (agent.py)
     ├── 23 Tools across 6 categories
     │   ├── tools.py          — 7 core HR tools
     │   ├── google_tools.py   — Drive, Gmail, Calendar, Forms, Sheets
     │   └── ats_tools.py      — Zoho Recruit, Workable
     ├── S3 Storage (storage.py)
     ├── AgentCore Memory (memory_manager.py)
     └── Bedrock Nova Lite (AI model)

Dashboard (Next.js 15 — local only)
     ├── app/login/             — Login page
     ├── app/dashboard/         — Overview, Jobs, Candidates, Pipeline
     ├── lib/s3.ts              — Reads S3 data directly
     └── lib/auth.ts            — NextAuth credentials provider
```

---

## 📁 Project Structure

```
HRRecruiterAgentNew/
├── AGENT.md                        # ← You are here
├── SETUP_GUIDE.md                  # Integration setup instructions
├── DEPLOYMENT_COMPLETE.md          # Full deployment documentation
├── agentcore/
│   ├── agentcore.json              # Infrastructure source of truth
│   ├── aws-targets.json
│   ├── .env.local                  # Secrets for deployed env (gitignored)
│   └── cdk/
├── app/HRRecruiterAgent/
│   ├── main.py                     # AgentCore HTTP entrypoint
│   ├── agent.py                    # Strands Agent + 23 tools registered
│   ├── tools.py                    # 7 core HR tools
│   ├── google_tools.py             # Google Drive/Gmail/Calendar/Forms/Sheets
│   ├── ats_tools.py                # Zoho Recruit + Workable
│   ├── storage.py                  # S3 persistence layer
│   ├── memory_manager.py           # AgentCore Memory integration
│   ├── config.py                   # All env var config
│   ├── .env                        # Runtime secrets (gitignored)
│   └── pyproject.toml              # Python dependencies
├── dashboard/                      # Next.js recruiter dashboard
│   ├── app/
│   │   ├── login/page.tsx
│   │   ├── dashboard/
│   │   │   ├── layout.tsx          # Sidebar + TopNav wrapper
│   │   │   ├── page.tsx            # Overview (stats + charts + table)
│   │   │   ├── jobs/page.tsx
│   │   │   ├── candidates/page.tsx
│   │   │   ├── candidates/[...id]/page.tsx
│   │   │   └── pipeline/page.tsx
│   │   └── api/auth/[...nextauth]/
│   ├── components/
│   │   ├── Sidebar.tsx
│   │   ├── TopNav.tsx
│   │   ├── StatsCard.tsx
│   │   ├── RecentCandidates.tsx
│   │   └── Badges.tsx
│   ├── lib/
│   │   ├── s3.ts                   # S3 data reader
│   │   └── auth.ts                 # NextAuth config
│   ├── .env.local                  # Dashboard secrets (gitignored)
│   └── .env.local.example          # Template for .env.local
└── setup/
    ├── google_auth.py              # One-time Google OAuth script
    └── credentials.json            # Google OAuth app credentials (gitignored)
```

---

## 🔑 Critical Information

### AWS Resources

| Resource | Value |
|---|---|
| **Account** | 416291742983 |
| **Region** | us-east-1 |
| **Runtime ID** | `HRRecruiterAgentNew_HRRecruiterAgent-L54zkOCNQx` |
| **Runtime ARN** | `arn:aws:bedrock-agentcore:us-east-1:416291742983:runtime/HRRecruiterAgentNew_HRRecruiterAgent-L54zkOCNQx` |
| **IAM Role** | `AgentCore-HRRecruiterAgen-ApplicationAgentHRRecruit-tQkdqNSB0BO1` |
| **S3 Bucket** | `hr-recruiter-agent-data` |
| **Stack** | `AgentCore-HRRecruiterAgentNew-default` |
| **Profile** | `chidiadioscar3` |

### Google Cloud

| Resource | Value |
|---|---|
| **Project** | `hr-recruiter-agent` |
| **Project ID** | `hr-recruiter-agent-507412` |
| **Client ID** | `117366709450-mho9d9i2pqk5q7l2dpvbgn06poctubq5.apps.googleusercontent.com` |
| **Test user** | `chidiadi.works@gmail.com` |
| **APIs enabled** | Gmail, Drive, Calendar, Forms, Sheets |

### ATS Credentials

| Platform | Key Location |
|---|---|
| **Zoho Recruit** | `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN` in `.env` |
| **Workable** | `WORKABLE_API_KEY`, `WORKABLE_SUBDOMAIN=builditt` in `.env` |

### Dashboard Login (local)

| Field | Value |
|---|---|
| **URL** | http://localhost:3000 |
| **Email** | `admin@hr.com` |
| **Password** | `recruiter123` |

---

## ⚡ Quick Commands

```powershell
# ── Agent ─────────────────────────────────────────────
cd C:\Users\LENOVO\Documents\HRRecruiterAgentNew\HRRecruiterAgentNew
$env:AWS_PROFILE = "chidiadioscar3"

# Refresh SSO (do this every session — expires every ~8 hours)
aws sso login --profile chidiadioscar3

# Test agent
agentcore invoke "List all open job postings"
agentcore status
agentcore logs
agentcore deploy --yes

# ── Dashboard ─────────────────────────────────────────
cd dashboard
.\node_modules\.bin\next.cmd dev
# Then open http://localhost:3000

# ── After SSO refresh, update dashboard AWS creds ─────
# Run this, copy the 3 values into dashboard/.env.local
$env:AWS_PROFILE="chidiadioscar3"
aws configure export-credentials --format env-no-export
```

---

## 🎓 24 Agent Tools (23 deployed, 1 pending)

### Core HR (tools.py)
1. `generate_job_posting` — AI writes job descriptions
2. `save_job_posting` — Saves to S3
3. `list_job_postings` — Lists open roles
4. `screen_resume` — Scores candidates 0-100
5. `save_candidate` — Saves screening records
6. `list_candidates` — Ranked candidate dashboard
7. `draft_interview_email` — Writes interview invites

### Google Drive (google_tools.py)
8. `read_resume_from_drive` — Reads resume from Drive by name
9. `save_document_to_drive` — Saves JD/offer letters to Drive
10. `list_drive_files` — Lists HR files in Drive folder

### Gmail (google_tools.py)
11. `send_email_now` — Actually sends emails via Gmail
12. `list_unread_emails` — Checks inbox for resume submissions

### Google Calendar (google_tools.py)
13. `schedule_interview` — Creates calendar event + Google Meet link
14. `check_availability` — Checks interviewer's free/busy slots

### Google Forms + Sheets (google_tools.py)
15. `create_job_application_form` — Creates Google Forms for job applications (⏳ deployment pending)
16. `list_form_responses` — Reads job application form submissions
17. `read_sheet` — Reads candidate data from Google Sheets

### Zoho Recruit (ats_tools.py)
18. `list_zoho_jobs` — Lists open jobs in Zoho
19. `get_zoho_candidates` — Gets candidates from Zoho
20. `update_zoho_candidate` — Pushes AI screening back to Zoho

### Workable (ats_tools.py)
21. `list_workable_jobs` — Lists open jobs in Workable
22. `get_workable_candidates` — Gets candidates from Workable
23. `update_workable_candidate` — Pushes AI screening back to Workable (advance/disqualify/comment)
24. ⏳ **Note:** Total will be 24 tools when `create_job_application_form` deployment completes

---

## 🐛 Known Issues & Solutions

### Issue: AWS SSO token expired (dashboard shows ExpiredToken error)
**Solution:**
```powershell
aws sso login --profile chidiadioscar3
$env:AWS_PROFILE="chidiadioscar3"
aws configure export-credentials --format env-no-export
# Copy AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN into dashboard/.env.local
# Restart dashboard dev server
```

### Issue: Google OAuth "Access blocked" error
**Solution:** Go to Google Cloud Console → Google Auth Platform → Audience → Add test user email.

### Issue: "Access Denied" on S3
**Solution:** IAM role needs S3 permissions. Already fixed with AmazonS3FullAccess policy.

### Issue: Next.js SWC binary fails on Windows (Node 24)
**Solution:** Already on Next.js 15.2.4 which supports Node 24. If it fails again, delete `node_modules` and re-run `npm install`.

### Issue: Agent Not Found
**Solution:** Check status with `agentcore status`, runtime should show READY.

---

## 📊 Session History

### August 21, 2026 — Initial Deployment
- Created AgentCore project, deployed agent, fixed IAM, tested successfully.

### August 25, 2026 — Slack Integration
- Built two-Lambda Slack integration (receiver + worker pattern).
- Bot live in ASK-ME workspace, responds to @mentions and DMs.

### September 4, 2026 — Major Expansion Session
- Deleted old duplicate directory (`HRRecruiterAgent`).
- Expanded agent from 7 to 23 tools.
- Added Google integrations (Drive, Gmail, Calendar, Forms, Sheets).
- Set up Google Cloud project, enabled 5 APIs, completed OAuth2 flow.
- Added ATS integrations (Zoho Recruit + Workable) — Greenhouse/BambooHR/Lever dropped (no free signup).
- Deployed updated agent to AWS.
- Built full recruiter dashboard in Next.js 15 with Tailwind.
- Dashboard has login, overview, jobs, candidates, pipeline, candidate detail.
- Began Soft UI redesign of dashboard (components updated, pending token refresh to verify).
- Pushed all changes to GitHub: `oscar67-spec/hr-recruiter-agent`.

### September 10, 2026 — Google Forms + Hackathon Prep
- Added Google Forms creation tool (`create_job_application_form`)
- Updated OAuth scope to `forms.body`, re-authorized, got new refresh token
- Expanded agent to 24 tools (1 pending deployment)
- Refreshed AWS SSO credentials, documented all console access links
- Reviewed Agents for Humans Hackathon requirements (4 days to deadline)
- Track selected: Professional Agents ($5k-$10k prizes)
- Started testing phase via Slack bot
- Job generation confirmed working
- Preparing to test ATS integrations with real data from Zoho Recruit and Workable

---

## 🎯 Next Steps When Resuming

### Immediate (September 10, 2026 session):
1. **Test ATS integrations via Slack** — Pull real jobs and candidates from Zoho Recruit and Workable
2. **Verify data syncs to S3** — Check S3 bucket for saved jobs and candidates
3. **Test dashboard with real data** — Ensure dashboard displays ATS data correctly
4. **Complete hackathon requirements:**
   - Add MIT/Apache license to repo
   - Create README with architecture diagram  
   - Record 5-minute demo video
   - Get AWS Builder ID
   - Submit to Devpost before September 14, 5pm PDT

### Testing Checklist (via Slack):
- [x] Job generation working
- [ ] Zoho Recruit: list jobs
- [ ] Zoho Recruit: get candidates
- [ ] Workable: list jobs  
- [ ] Workable: get candidates
- [ ] Resume screening with real data
- [ ] Email sending (Gmail)
- [ ] Calendar scheduling
- [ ] Dashboard display verification

---

## 📝 Notes for Future Sessions

### User Preferences:
- Prefers brief direct answers, not lengthy explanations
- Says "continue" or "yeah do that" to approve — just proceed
- Sends screenshots when something isn't working
- Leaves decisions to AI when saying "leaving it to you"
- Will come back and pick up where left off

### Technical Context:
- Node.js v24.12.0 on this machine (Next.js 15 required for compatibility)
- AWS SSO tokens expire every ~8 hours — must refresh at start of each session
- Dashboard AWS credentials in `.env.local` are temporary and expire — update each session
- Google OAuth refresh token does NOT expire (permanent unless revoked)
- Zoho OAuth refresh token does NOT expire

### Communication Style:
- Short messages = ready to proceed
- "run it yourself" = run the command in terminal
- "where should i run it" = needs directory clarification
- "check" at start of session = read AGENT.md and report status

---

## 🔗 Important Links

**AWS Console:**
- [AgentCore Runtime](https://us-east-1.console.aws.amazon.com/bedrock-agentcore/home?region=us-east-1)
- [S3 Bucket](https://s3.console.aws.amazon.com/s3/buckets/hr-recruiter-agent-data?region=us-east-1)
- [CloudFormation](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks)
- [CloudWatch Logs](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups)

**Integrations:**
- [Zoho API Console](https://api-console.zoho.com)
- [Workable Settings](https://builditt.workable.com/backend/settings/integrations)
- [Google Cloud Console](https://console.cloud.google.com)

**Hackathon:**
- [Agents for Humans](https://agentsforhumans.devpost.com/)
- [GitHub Repo](https://github.com/oscar67-spec/hr-recruiter-agent)

---

## ✅ Pre-Session Checklist

Before starting work:
- [ ] Read this AGENT.md completely
- [ ] `cd C:\Users\LENOVO\Documents\HRRecruiterAgentNew\HRRecruiterAgentNew`
- [ ] `aws sso login --profile chidiadioscar3` (refresh SSO)
- [ ] `$env:AWS_PROFILE="chidiadioscar3"`
- [ ] `agentcore status` → should show READY
- [ ] Update `dashboard/.env.local` with fresh AWS credentials
- [ ] Start dashboard: `cd dashboard && .\node_modules\.bin\next.cmd dev`

---

_This file is the single source of truth for AI assistants working on this project. Always update it at the end of a session._
