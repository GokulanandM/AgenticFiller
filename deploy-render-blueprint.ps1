# Render.com Deployment using Blueprint API (works with render.yaml)
param(
    [Parameter(Mandatory=$true)]
    [string]$RenderApiKey
)

$GitHubRepo = "GokulanandM/AgenticFiller"

Write-Host "Deploying to Render.com using Blueprint API..." -ForegroundColor Green
Write-Host "GitHub Repo: $GitHubRepo" -ForegroundColor Cyan

$apiBase = "https://api.render.com/v1"
$headers = @{
    "Authorization" = "Bearer $RenderApiKey"
    "Accept" = "application/json"
    "Content-Type" = "application/json"
}

# Get owner ID
Write-Host "`nGetting account information..." -ForegroundColor Yellow
try {
    $user = Invoke-RestMethod -Uri "$apiBase/owners" -Headers $headers -Method Get
    $ownerId = $user[0].owner.id
    Write-Host "Owner ID: $ownerId" -ForegroundColor Green
} catch {
    Write-Host "Error getting owner ID: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Create blueprint (uses render.yaml from repo)
Write-Host "`nCreating service from render.yaml..." -ForegroundColor Yellow

$blueprintConfig = @{
    ownerId = $ownerId
    repo = "https://github.com/$GitHubRepo"
    branch = "main"
    envVars = @(
        @{ key = "AZURE_API_KEY"; value = "d2d05917a33d4c8e8ffb00ea56d47be3" }
        @{ key = "AZURE_ENDPOINT"; value = "https://elsai-dev.openai.azure.com/" }
        @{ key = "AZURE_DEPLOYMENT_ID"; value = "gpt-4o-mini" }
    )
} | ConvertTo-Json -Depth 10

try {
    Write-Host "Sending blueprint deployment request..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "$apiBase/blueprints" `
        -Headers $headers `
        -Method Post `
        -Body $blueprintConfig `
        -ContentType "application/json"
    
    Write-Host "`n✅ Blueprint created successfully!" -ForegroundColor Green
    Write-Host "Blueprint ID: $($response.blueprint.id)" -ForegroundColor Cyan
    Write-Host "`nThe service will be created from render.yaml" -ForegroundColor Yellow
    Write-Host "Check your Render dashboard for deployment status" -ForegroundColor Cyan
    Write-Host "Dashboard: https://dashboard.render.com" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    
    $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
    if ($errorResponse) {
        Write-Host "Details: $($errorResponse.message)" -ForegroundColor Red
    }
    
    Write-Host "`n💡 Since API deployment is complex, let's use the dashboard:" -ForegroundColor Yellow
    Write-Host "   1. Go to https://render.com" -ForegroundColor White
    Write-Host "   2. Click 'New +' → 'Web Service'" -ForegroundColor White
    Write-Host "   3. Connect: $GitHubRepo" -ForegroundColor White
    Write-Host "   4. Render will auto-detect render.yaml ✅" -ForegroundColor Green
    Write-Host "   5. Add environment variables:" -ForegroundColor White
    Write-Host "      - AZURE_API_KEY = d2d05917a33d4c8e8ffb00ea56d47be3" -ForegroundColor Gray
    Write-Host "      - AZURE_ENDPOINT = https://elsai-dev.openai.azure.com/" -ForegroundColor Gray
    Write-Host "      - AZURE_DEPLOYMENT_ID = gpt-4o-mini" -ForegroundColor Gray
    Write-Host "   6. Click 'Create Web Service'" -ForegroundColor White
    
    exit 1
}
