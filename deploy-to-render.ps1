# Render.com Deployment Script
# This script helps automate Render deployment using Render API
# You'll need a Render API key from: https://dashboard.render.com/account/api-keys

param(
    [Parameter(Mandatory=$true)]
    [string]$RenderApiKey,
    
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "form-automation-agent"
)

$GitHubRepo = "GokulanandM/AgenticFiller"
$Region = "oregon"
$Plan = "free"

Write-Host "Deploying to Render.com..." -ForegroundColor Green
Write-Host "Service Name: $ServiceName" -ForegroundColor Cyan
Write-Host "GitHub Repo: $GitHubRepo" -ForegroundColor Cyan

# Render API endpoint
$apiBase = "https://api.render.com/v1"

# Headers for API requests
$headers = @{
    "Authorization" = "Bearer $RenderApiKey"
    "Accept" = "application/json"
    "Content-Type" = "application/json"
}

# Check if service already exists
Write-Host "`nChecking for existing service..." -ForegroundColor Yellow
try {
    $services = Invoke-RestMethod -Uri "$apiBase/services" -Headers $headers -Method Get
    $existingService = $services | Where-Object { $_.service.name -eq $ServiceName }
    
    if ($existingService) {
        Write-Host "Service already exists: $($existingService.service.serviceDetails.url)" -ForegroundColor Green
        Write-Host "You can update it in Render dashboard or delete and recreate." -ForegroundColor Yellow
        exit 0
    }
} catch {
    Write-Host "Could not check existing services. Continuing..." -ForegroundColor Yellow
}

# Create new service
Write-Host "`nCreating new Render service..." -ForegroundColor Yellow

$serviceConfig = @{
    type = "web_service"
    name = $ServiceName
    ownerId = ""  # Will be set by API
    repo = "https://github.com/$GitHubRepo"
    branch = "main"
    region = $Region
    planId = "starter"  # Free plan
    envVars = @(
        @{ key = "PYTHON_VERSION"; value = "3.11.9" }
        @{ key = "PORT"; value = "8000" }
        @{ key = "HOST"; value = "0.0.0.0" }
        @{ key = "LOG_LEVEL"; value = "INFO" }
        @{ key = "DEBUG"; value = "false" }
        @{ key = "REQUIRE_APPROVAL"; value = "true" }
        @{ key = "AZURE_DEPLOYMENT_ID"; value = "gpt-4o-mini" }
        # These should be set in Render dashboard for security
        # @{ key = "AZURE_API_KEY"; value = "YOUR_KEY" }
        # @{ key = "AZURE_ENDPOINT"; value = "YOUR_ENDPOINT" }
    )
    buildCommand = "pip install --upgrade pip && pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium"
    startCommand = "uvicorn main:app --host 0.0.0.0 --port `$PORT"
} | ConvertTo-Json -Depth 10

try {
    Write-Host "Sending deployment request to Render..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "$apiBase/services" `
        -Headers $headers `
        -Method Post `
        -Body $serviceConfig `
        -ContentType "application/json"
    
    Write-Host "`n✅ Service created successfully!" -ForegroundColor Green
    Write-Host "Service URL: $($response.service.serviceDetails.url)" -ForegroundColor Cyan
    Write-Host "`n⚠️  IMPORTANT: Set these environment variables in Render dashboard:" -ForegroundColor Yellow
    Write-Host "   - AZURE_API_KEY" -ForegroundColor White
    Write-Host "   - AZURE_ENDPOINT" -ForegroundColor White
    Write-Host "`nGo to: https://dashboard.render.com" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Error creating service: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "`nAuthentication failed. Please check your Render API key." -ForegroundColor Red
        Write-Host "Get your API key from: https://dashboard.render.com/account/api-keys" -ForegroundColor Yellow
    } elseif ($_.Exception.Response.StatusCode -eq 403) {
        Write-Host "`nPermission denied. Your API key might not have the right permissions." -ForegroundColor Red
    } else {
        $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($errorResponse) {
            Write-Host "Error details: $($errorResponse.message)" -ForegroundColor Red
        }
    }
    
    Write-Host "`n💡 Alternative: Deploy manually via Render dashboard:" -ForegroundColor Yellow
    Write-Host "   1. Go to https://render.com" -ForegroundColor White
    Write-Host "   2. Click 'New +' → 'Web Service'" -ForegroundColor White
    Write-Host "   3. Connect GitHub repository: $GitHubRepo" -ForegroundColor White
    Write-Host "   4. Render will auto-detect render.yaml" -ForegroundColor White
    Write-Host "   5. Set environment variables" -ForegroundColor White
    Write-Host "   6. Deploy!" -ForegroundColor White
    
    exit 1
}
