# Deploy to GitHub - Instructions

## Quick Deploy (Automated)

### Step 1: Get GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name it: `AgenticFiller-Deploy`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `public_repo` (Access public repositories)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

### Step 2: Run the Deployment Script

Open PowerShell in the project directory and run:

```powershell
cd e:\AgenticForm
.\deploy-to-github.ps1 -Token "YOUR_TOKEN_HERE"
```

Replace `YOUR_TOKEN_HERE` with your actual GitHub token.

---

## Manual Deploy (Alternative)

### Step 1: Create Repository on GitHub

1. Go to: https://github.com/new
2. Repository name: `AgenticFiller`
3. Description: "Form Automation Agent with Azure OpenAI integration"
4. Visibility: **Public** ✅
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

### Step 2: Push Code

```powershell
cd e:\AgenticForm

# Remove old remote if exists
git remote remove origin 2>$null

# Add new remote
git remote add origin https://github.com/GokulanandM/AgenticFiller.git

# Push to GitHub
git push -u origin main
```

When prompted:
- Username: `GokulanandM`
- Password: **Paste your Personal Access Token** (not your GitHub password)

---

## Verify Deployment

After pushing, verify at:
https://github.com/GokulanandM/AgenticFiller

You should see all your files including:
- ✅ README.md
- ✅ render.yaml
- ✅ All source code files

---

## Next Steps

After successful push:

1. **Deploy to Render.com:**
   - Go to https://render.com
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Set environment variables
   - Deploy!

2. **Your repository will be live at:**
   - GitHub: https://github.com/GokulanandM/AgenticFiller
   - Render: https://your-app.onrender.com (after deployment)
