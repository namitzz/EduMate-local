# 🚀 Quick Start - Deploy EduMate in 5 Minutes

This guide gets EduMate running on Streamlit Cloud + Fly.io for free.

## ⚡ 5-Minute Setup

### 1️⃣ Deploy Backend (2 minutes)

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy (from backend directory)
cd backend
fly deploy
```

✅ Your backend is live at `https://edumate-local.fly.dev` (or your app name)

### 2️⃣ Deploy Frontend (3 minutes)

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"New app"**
3. Configure:
   - **Repository**: Your fork of this repo
   - **Branch**: `main`
   - **Main file path**: `ui/app_simple.py`
4. Click **"Deploy"**

✅ Your app is live at `https://your-app-name.streamlit.app`

### 3️⃣ Share with Students

Just share the Streamlit URL:
```
https://your-app-name.streamlit.app
```

Students can access immediately - no login needed! 🎓

---

## 💰 It's Free!

- ✅ **Streamlit Cloud**: Free tier (1 GB RAM, unlimited viewers)
- ✅ **Fly.io**: Free tier (3 VMs, 160GB transfer/month)
- ✅ **OpenRouter**: Pay-per-use (~$3-5 per 1,000 questions)

**Total**: $0/month + minimal API costs only when used

---

## 🛠️ Update Course Materials

```bash
# Add documents to backend/corpus/
cd backend
python ingest.py
fly deploy
```

Frontend updates automatically!

---

## 📚 Need More Help?

- **Full Guide**: [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md)
- **Setup Details**: [SETUP.md](SETUP.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## ✅ Verify Everything Works

```bash
# Check backend
curl https://edumate-local.fly.dev/health
# Should return: {"ok": true}

# Check frontend
# Just open the Streamlit URL in your browser
```

---

## 🆘 Troubleshooting

**Backend not responding?**
```bash
fly status
fly logs
fly apps restart edumate-local
```

**Frontend offline?**
- Check Streamlit Cloud dashboard
- Verify `ui/app_simple.py` exists
- Check deployment logs

**Need to set spending limit?**
```bash
fly orgs billing-limits set
```

---

## 🎉 You're Done!

Students can now access EduMate at your Streamlit URL.

Enjoy! 🎓
