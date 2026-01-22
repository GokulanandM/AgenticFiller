# 🚀 Render Deployment - Quick Start

## What I Need From You

**Nothing!** Everything is ready. Just follow these steps:

## 5-Minute Deployment

### 1. Create Render Account (1 minute)
- Go to: https://render.com
- Click "Get Started for Free"
- Sign up with GitHub (recommended) - it will use your existing GitHub account

### 2. Connect Repository (1 minute)
- Click "New +" → "Web Service"
- Click "Connect GitHub"
- Authorize Render
- Select: **GokulanandM/AgenticFiller**
- Render will auto-detect `render.yaml` ✅

### 3. Set Environment Variables (2 minutes)
In the "Environment" section, add these 3 variables:

```
AZURE_API_KEY = d2d05917a33d4c8e8ffb00ea56d47be3
AZURE_ENDPOINT = https://elsai-dev.openai.azure.com/
AZURE_DEPLOYMENT_ID = gpt-4o-mini
```

### 4. Deploy (1 minute)
- Click "Create Web Service"
- Wait 10-15 minutes for first build
- Done! 🎉

## Your App Will Be Live At:
`https://form-automation-agent.onrender.com`

(Or whatever name you choose)

## That's It!

No code changes needed. Everything is configured in `render.yaml`.

## Need Help?

See `RENDER_DEPLOYMENT.md` for detailed instructions.
