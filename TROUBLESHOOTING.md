# Troubleshooting Guide

## Common 404 Errors

### Error: "Failed to load resource: the server responded with a status of 404"

This error typically occurs for these reasons:

#### 1. Favicon Request (Most Common)
**Symptom**: Browser console shows 404 for `/favicon.ico`

**Solution**: ✅ Fixed! Added favicon handler in `main.py`
- The app now returns 204 (No Content) for favicon requests
- This prevents the 404 error in console

#### 2. Static Files Not Found
**Symptom**: 404 errors for files in `/static/` directory

**Solution**: 
- Ensure `static/` directory exists in your project
- Check that files are committed to git
- Verify static files are mounted correctly in `main.py`

#### 3. API Endpoints Not Found
**Symptom**: 404 when calling API endpoints

**Check**:
- Verify the endpoint URL is correct
- Check if the server is running
- Ensure the route is defined in `main.py`

**Common Endpoints**:
- `/health` - Health check
- `/test-connection` - Test Azure OpenAI
- `/analyze-form` - Analyze form structure
- `/fill-form` - Fill and submit form
- `/docs` - API documentation

#### 4. Template Not Found
**Symptom**: 404 when accessing root URL `/`

**Solution**:
- Ensure `templates/index.html` exists
- Check templates directory is properly configured
- Verify Jinja2 is installed

## Debugging Steps

### 1. Check Server Logs
```bash
# Local development
python run.py

# Check logs for errors
tail -f logs/audit.log
```

### 2. Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Test API
curl http://localhost:8000/docs
```

### 3. Check Browser Console
- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for failed requests

### 4. Verify File Structure
```
AgenticForm/
├── static/          # Must exist
│   └── test-form.html
├── templates/       # Must exist
│   └── index.html
├── main.py
└── ...
```

## Render Deployment Issues

### Build Fails
- Check build logs in Render dashboard
- Verify all dependencies in `requirements.txt`
- Playwright installation may take time

### App Crashes
- Check application logs
- Verify environment variables are set
- Check PORT is correctly configured

### 404 on Deployed App
- Verify static files are in repository
- Check Render build logs
- Ensure directories exist in deployment

## Quick Fixes

### Fix Favicon 404
✅ Already fixed in latest code

### Fix Static Files 404
```python
# In main.py - already implemented
app.mount("/static", StaticFiles(directory="static"), name="static")
```

### Fix Template 404
```python
# In main.py - already implemented
templates = Jinja2Templates(directory="templates")
```

## Still Having Issues?

1. Check the latest code is deployed
2. Verify all files are in git repository
3. Check Render build logs
4. Test locally first: `python run.py`
5. Check browser console for specific errors

## Common Solutions

### Clear Browser Cache
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Clear browser cache
- Try incognito/private mode

### Restart Server
```bash
# Stop server (Ctrl+C)
# Start again
python run.py
```

### Rebuild on Render
- Go to Render dashboard
- Click "Manual Deploy" → "Clear build cache & deploy"
