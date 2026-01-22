# Render.com Deployment Guide

## Quick Deployment Steps

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (recommended) or email
3. Verify your email

### Step 2: Connect GitHub Repository
1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Click "Connect GitHub"
4. Authorize Render to access your repositories
5. Select repository: **GokulanandM/AgenticFiller**

### Step 3: Configure Service
Render will auto-detect `render.yaml` and pre-fill settings:
- **Name**: form-automation-agent (or your choice)
- **Region**: Oregon (or closest to you)
- **Branch**: main
- **Root Directory**: (leave empty)
- **Runtime**: Python 3
- **Build Command**: (auto-filled from render.yaml)
- **Start Command**: (auto-filled from render.yaml)
- **Plan**: Free

### Step 4: Set Environment Variables
In the "Environment" section, add these variables:

#### Required Azure OpenAI Variables:
```
AZURE_API_KEY=d2d05917a33d4c8e8ffb00ea56d47be3
AZURE_ENDPOINT=https://elsai-dev.openai.azure.com/
AZURE_DEPLOYMENT_ID=gpt-4o-mini
```

#### Optional (but recommended):
```
AZURE_OPENAI_API_KEY=d2d05917a33d4c8e8ffb00ea56d47be3
AZURE_OPENAI_ENDPOINT=https://elsai-dev.openai.azure.com/
AZURE_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

#### Application Settings (already in render.yaml, but can override):
```
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
DEBUG=false
REQUIRE_APPROVAL=true
```

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for build (first build takes 10-15 minutes)
3. Your app will be live at: `https://form-automation-agent.onrender.com`

## Post-Deployment

### Verify Deployment
1. Health Check: `https://your-app.onrender.com/health`
2. Web UI: `https://your-app.onrender.com/`
3. API Docs: `https://your-app.onrender.com/docs`

### Keep App Awake (Free Tier)
Free tier apps sleep after 15 minutes. Use a ping service:
- **UptimeRobot**: https://uptimerobot.com (free)
  - Monitor URL every 5 minutes
- **Cron-job.org**: https://cron-job.org (free)
  - Ping URL every 10 minutes

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure all dependencies are in requirements.txt
- Playwright installation may take time (be patient)

### App Crashes
- Check logs in Render dashboard
- Verify all environment variables are set
- Check PORT is correctly configured

### Slow First Request
- Normal on free tier (app wakes from sleep)
- Use ping service to keep it awake

## Environment Variables Reference

| Variable | Required | Value | Notes |
|----------|----------|-------|------|
| AZURE_API_KEY | Yes | Your Azure OpenAI key | Main API key |
| AZURE_ENDPOINT | Yes | https://elsai-dev.openai.azure.com/ | Your endpoint |
| AZURE_DEPLOYMENT_ID | Yes | gpt-4o-mini | Model deployment |
| PORT | Auto | 8000 | Set by Render |
| HOST | Auto | 0.0.0.0 | Set by Render |
| LOG_LEVEL | No | INFO | Logging level |
| DEBUG | No | false | Debug mode |
| REQUIRE_APPROVAL | No | true | Safety feature |

## Support

If you encounter issues:
1. Check Render logs
2. Verify environment variables
3. Check GitHub repository is connected
4. Ensure render.yaml is in root directory
