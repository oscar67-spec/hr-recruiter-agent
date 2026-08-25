# HR Recruiter Agent - AI Assistant Context

> **Last Updated:** August 25, 2026  
> **Status:** ✅ Deployed and Operational  
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
   - 512MB memory for faster execution
7. **System Prompt Updated** - No markdown formatting in responses

### ⏸️ NOT STARTED

- Slack/Teams bot integration
- Web portal UI
- Sample data generation (jobs/candidates)
- Demo video for hackathon
- Hackathon submission

---

## 🏗️ Architecture

```
User (CLI/API)
    ↓
AWS Bedrock AgentCore Runtime
    ├── Strands Agent (agent.py)
    ├── 7 Tools (tools.py)
    │   ├── generate_job_posting
    │   ├── save_job_posting
    │   ├── list_job_postings
    │   ├── screen_resume
    │   ├── save_candidate
    │   ├── list_candidates
    │   └── draft_interview_email
    ├── S3 Storage (storage.py)
    └── Bedrock Nova Lite (AI model)
```

---

## 📁 Project Structure

```
HRRecruiterAgentNew/
├── AGENT.md                    # ← You are here (AI context file)
├── DEPLOYMENT_COMPLETE.md      # Full deployment documentation
├── agentcore/                  # AWS CDK infrastructure
│   ├── agentcore.json
│   ├── aws-targets.json
│   └── cdk/
└── app/HRRecruiterAgent/       # Python agent code
    ├── main.py                 # AgentCore entrypoint
    ├── agent.py                # Strands Agent + tools
    ├── tools.py                # 7 @tool functions
    ├── storage.py              # S3 operations
    ├── config.py               # Configuration
    ├── .env                    # Environment variables
    └── pyproject.toml          # Dependencies
```

---

## 🔑 Critical Information

### AWS Resources

| Resource | Value |
|----------|-------|
| **Account** | 416291742983 |
| **Region** | us-east-1 |
| **Runtime ID** | `HRRecruiterAgentNew_HRRecruiterAgent-L54zkOCNQx` |
| **Runtime ARN** | `arn:aws:bedrock-agentcore:us-east-1:416291742983:runtime/HRRecruiterAgentNew_HRRecruiterAgent-L54zkOCNQx` |
| **IAM Role** | `AgentCore-HRRecruiterAgen-ApplicationAgentHRRecruit-tQkdqNSB0BO1` |
| **S3 Bucket** | `hr-recruiter-agent-data` |
| **Stack** | `AgentCore-HRRecruiterAgentNew-default` |
| **Profile** | `chidiadioscar3` |

### Quick Commands

```powershell
# Navigate to project
cd C:\Users\LENOVO\Documents\HRRecruiterAgentNew\HRRecruiterAgentNew

# Set AWS profile
$env:AWS_PROFILE="chidiadioscar3"

# Test agent
agentcore invoke "List all open job postings"

# Check status
agentcore status

# View logs
agentcore logs

# Deploy changes
agentcore deploy --yes
```

---

## 🎓 What This Agent Does

### 7 Core Tools

1. **generate_job_posting** - AI writes professional job descriptions
2. **save_job_posting** - Persists JD to S3 with unique job_id
3. **list_job_postings** - Shows all open positions
4. **screen_resume** - Scores candidates 0-100 vs requirements
5. **save_candidate** - Stores screening records to S3
6. **list_candidates** - Ranked dashboard by score/role
7. **draft_interview_email** - Creates ready-to-send invitations

### Typical Workflow

```
User → "Generate job posting for Senior Engineer"
Agent → Uses Bedrock Nova Lite to write JD
Agent → Returns formatted job description
User → "Save it"
Agent → Saves to S3, returns job_id
User → "Screen this resume for that job..."
Agent → Analyzes resume, scores candidate
Agent → Returns score + recommendation
User → "Show all candidates with score > 80"
Agent → Queries S3, returns ranked list
```

---

## 💰 Cost Context

- **Budget:** $50 AWS credits
- **Cost per invocation:** ~$0.01
- **Total available:** ~5,000 invocations
- **No idle costs** - serverless, pay-per-use only

---

## 🚨 Important Rules for AI Assistants

### When Working on This Project:

1. **Always use us-east-1 region** - Everything is deployed there
2. **Always set AWS profile** - Use `chidiadioscar3`
3. **Never delete S3 data** - It contains job postings and candidates
4. **Test before deploying** - Use `agentcore invoke` to test locally first
5. **Update this file** - When you make significant changes, update AGENT.md

### Code Modification Rules:

- **agent.py** - Only edit tools list or system prompt
- **tools.py** - Can add new @tool functions, but test thoroughly
- **storage.py** - Don't change S3 structure (breaks existing data)
- **config.py** - Only change if user explicitly requests it

### Deployment Rules:

- **Before deploying:** Verify code changes don't break existing tools
- **After deploying:** Test with `agentcore invoke` to confirm it works
- **If deploy fails:** Check logs in `agentcore/.cli/logs/deploy/`

---

## 🐛 Known Issues & Solutions

### Issue: "Access Denied" on S3
**Solution:** IAM role needs S3 permissions. Already fixed with AmazonS3FullAccess policy.

### Issue: Wrong AWS Region in Console
**Solution:** Always switch to us-east-1 in top-right region selector.

### Issue: Agent Not Found
**Solution:** Check status with `agentcore status`, runtime should show READY.

---

## 📊 Session History Summary

### August 21, 2026 - Initial Deployment Session

**What We Did:**
1. Found existing HR agent code (not deployed)
2. Installed AgentCore CLI and AWS CDK
3. Bootstrapped CDK in us-east-1
4. Created proper AgentCore project structure
5. Copied working code to new structure
6. Deployed to AWS (~5 minutes)
7. Fixed IAM permissions (S3 access)
8. Tested successfully (job posting generation)
9. Documented everything in DEPLOYMENT_COMPLETE.md
10. Created this AGENT.md file

**Problems Solved:**
- Original project missing CDK infrastructure → Created new project
- S3 access denied errors → Added IAM policy
- Console showing wrong region → Provided correct us-east-1 links

**User Questions Answered:**
- "where are we" → Showed current project state
- "how do you deploy" → Explained and executed deployment
- "credits cover everything?" → Confirmed $50 = plenty
- "how do teams use it" → Explained 8 integration methods
- "how do i use the Agent" → Provided CLI commands and examples

---

## 🎯 Next Steps When Resuming

### Immediate Priorities (if user asks):
1. Generate sample data (2-3 job postings, 5-6 candidates)
2. Test full workflow end-to-end
3. Build Slack bot integration (most requested)
4. Create demo video for hackathon

### Medium Priority:
- Add more sophisticated features (calendar API, actual email sending)
- Build web portal UI
- Create monitoring dashboard
- Add analytics/reporting tools

### Low Priority:
- Multi-language support
- Advanced candidate scoring algorithms
- Integration with major ATS platforms

---

## 📝 Notes for Future Sessions

### User Preferences:
- Prefers detailed explanations with examples
- Wants to see things in AWS Console
- Asks for clarification when uncertain
- Appreciates comprehensive documentation

### Technical Context:
- User is AWS-experienced but new to AgentCore
- Comfortable with CLI but prefers visual confirmation
- Building for hackathon submission (deadline TBD)
- Budget-conscious (wants to stay within $50 credits)

### Communication Style:
- User asks "are you sure?" when skeptical → provide proof
- User says "continue with the work" → needs clarification on what work
- User sends screenshots → wants help interpreting AWS Console

---

## 🔗 Important Links

**AWS Console:**
- [AgentCore Runtime](https://us-east-1.console.aws.amazon.com/bedrock-agentcore/home?region=us-east-1)
- [S3 Bucket](https://s3.console.aws.amazon.com/s3/buckets/hr-recruiter-agent-data?region=us-east-1)
- [IAM Role](https://us-east-1.console.aws.amazon.com/iam/home#/roles/details/AgentCore-HRRecruiterAgen-ApplicationAgentHRRecruit-tQkdqNSB0BO1)
- [CloudFormation](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks)
- [CloudWatch Logs](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups)

**Documentation:**
- [AgentCore Docs](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html)
- [Strands SDK](https://github.com/strands-agents/strands)
- [Hackathon](https://agentsforhumans.devpost.com/)

---

## ✅ Pre-Session Checklist

Before starting work on this project:
- [ ] Read this AGENT.md file completely
- [ ] Check `DEPLOYMENT_COMPLETE.md` for technical details
- [ ] Navigate to project directory
- [ ] Set AWS profile: `$env:AWS_PROFILE="chidiadioscar3"`
- [ ] Verify agent status: `agentcore status` (should show READY)
- [ ] Test basic invocation: `agentcore invoke "List all open job postings"`

---

## 🚀 Quick Start for New AI Assistant

If you're a new AI assistant picking up this project:

1. **Read this entire file first** - It contains everything you need
2. **Check the status** - Run `agentcore status` to verify it's still deployed
3. **Review recent changes** - Check git log or file timestamps
4. **Ask clarifying questions** - If user says "continue", ask "continue with what?"
5. **Update this file** - When you make progress, update the "Current State" section
6. **Be evidence-based** - Always verify what you claim (check files, run commands)

---

## 🎪 Hackathon Context

**Event:** Agents for Humans Hackathon  
**Track:** Professional (HR/Recruiting use case)  
**Submission Requirements:** Code + demo video + description  
**Unique Selling Points:**
- End-to-end recruiting pipeline automation
- AI-powered resume screening with explainable scores
- Serverless, pay-per-use (cost-effective)
- Natural language interface (no complex UI)

**Competitive Advantages:**
- Uses cheapest AWS model (Nova Lite) for cost efficiency
- Stores everything in S3 (no vendor lock-in)
- Open-source Python code (hackable/extensible)
- Works via CLI, API, or can integrate with Slack/Teams

---

## 📞 Emergency Contact

**If Something Breaks:**
1. Check agent status: `agentcore status`
2. View logs: `agentcore logs`
3. Check CloudFormation in AWS Console
4. Worst case: Redeploy with `agentcore deploy --yes`

**If User is Confused:**
1. Show them this AGENT.md file
2. Point to DEPLOYMENT_COMPLETE.md for details
3. Demonstrate with live `agentcore invoke` commands
4. Show AWS Console (make sure they're in us-east-1)

---

**🤖 AI Assistant Instructions:**

When you read this file at the start of a new session:
- Understand you're picking up an **already deployed** agent
- Check if there are any updates needed to this file
- When user says "continue" or "where were we", reference this file
- Update the "Current State" section as you make progress
- Add any new issues/solutions to the "Known Issues" section
- Note any new user preferences in "Notes for Future Sessions"

---

**Last Session Summary:**  
Successfully deployed HR Recruiter Agent to AWS Bedrock AgentCore. Agent is live, tested, and fully functional. User understands deployment but wants to know how teams would use it in practice. Explained 8 integration methods (Slack, Teams, Web, API, etc.). User satisfied with explanation and asked for this AGENT.md file to track progress.

**Where We Left Off:**  
User just received comprehensive documentation (DEPLOYMENT_COMPLETE.md) and asked for an AGENT.md file to track session progress. This is that file.

**What to Do Next Session:**  
Ask user: "Would you like to test the agent with a full workflow (generate job → save → screen candidate), build a Slack integration, or work on something else?"

---

_This file serves as the single source of truth for AI assistants working on this project. Keep it updated!_
