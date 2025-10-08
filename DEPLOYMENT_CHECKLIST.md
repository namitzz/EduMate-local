# Deployment Checklist ✅

Use this checklist to ensure EduMate is properly deployed.

## Pre-Deployment

- [ ] Forked/cloned the repository
- [ ] Have Fly.io account (sign up at fly.io)
- [ ] Have Streamlit Cloud account (sign up at share.streamlit.io)
- [ ] Have flyctl CLI installed (`curl -L https://fly.io/install.sh | sh`)

## Backend Deployment (Fly.io)

- [ ] Logged in to Fly.io: `fly auth login`
- [ ] Deployed backend: `cd backend && fly deploy`
- [ ] Health check passes: `curl https://edumate-local.fly.dev/health`
- [ ] Set spending limit: `fly orgs billing-limits set`
- [ ] Verified app name matches URL in `ui/app_simple.py`

## Frontend Deployment (Streamlit Cloud)

- [ ] Logged in to Streamlit Cloud with GitHub
- [ ] Created new app on Streamlit Cloud
- [ ] Selected correct repository
- [ ] Set branch to `main`
- [ ] Set main file path to `ui/app_simple.py`
- [ ] App deployed successfully (wait 2-3 minutes)
- [ ] Received Streamlit app URL

## Verification

- [ ] Backend health check: `curl https://edumate-local.fly.dev/health` returns `{"ok": true}`
- [ ] Frontend loads without errors
- [ ] API status shows "✅ API is online" in Streamlit sidebar
- [ ] Can send a test message
- [ ] Response received from backend
- [ ] Source citations displayed (if available)

## Configuration Verification

- [ ] `.streamlit/config.toml` exists
- [ ] `backend/fly.toml` configured for free tier
- [ ] `ui/app_simple.py` has correct API URL
- [ ] Backend uses OpenRouter (USE_OPENAI=1 in fly.toml)
- [ ] Auto-stop enabled (auto_stop_machines = true)
- [ ] Auto-start enabled (auto_start_machines = true)
- [ ] Min machines running = 0

## Cost Management

- [ ] Fly.io spending limit set
- [ ] Monitoring Fly.io usage: `fly billing show`
- [ ] Streamlit Cloud free tier confirmed
- [ ] Understand OpenRouter pricing (pay-per-use)

## Student Access

- [ ] Streamlit URL shared with students
- [ ] Verified students can access without login
- [ ] Tested on multiple devices (desktop, mobile)
- [ ] Chat functionality works for students

## Optional - Course Materials

- [ ] Documents added to `backend/corpus/`
- [ ] Ran ingestion: `python ingest.py`
- [ ] Redeployed backend: `fly deploy`
- [ ] Verified documents are searchable

## Documentation

- [ ] Read QUICKSTART.md
- [ ] Reviewed STREAMLIT_DEPLOYMENT.md
- [ ] Understand architecture (ARCHITECTURE.md)
- [ ] Know where to find help (README.md)

## Troubleshooting Tested

- [ ] Know how to view Fly.io logs: `fly logs`
- [ ] Know how to restart backend: `fly apps restart edumate-local`
- [ ] Know how to check Streamlit Cloud logs (deployment panel)
- [ ] Have backup plan if service goes down

---

## Final Checklist

✅ All items above completed?
✅ Students can access the app?
✅ Spending limits set?
✅ Documentation reviewed?

**You're ready to go! 🎉**

---

## Need Help?

- 📖 [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
- 📖 [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) - Full guide
- 🔧 [SETUP.md](SETUP.md) - Configuration details
- 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md) - How it works
