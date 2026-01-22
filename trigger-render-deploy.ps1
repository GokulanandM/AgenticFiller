# Trigger Render Deployment via API
param(
    [Parameter(Mandatory=$true)]
    [string]$RenderApiKey,
    
    [Parameter(Mandatory=$false)]
    [string]$ServiceId = ""
)

Write-Host "Triggering Render deployment..." -ForegroundColor Green

$apiBase = "https://api.render.com/v1"
$headers = @{
    "Authorization" = "Bearer $RenderApiKey"
    "Accept" = "application/json"
}

# If service ID not provided, try to find it
if (-not $ServiceId) {
    Write-Host "Finding service..." -ForegroundColor Yellow
    try {
        $user = Invoke-RestMethod -Uri "$apiBase/owners" -Headers $headers -Method Get
        $ownerId = $user[0].owner.id
        
        $services = Invoke-RestMethod -Uri "$apiBase/services?ownerId=$ownerId" -Headers $headers -Method Get
        $service = $services | Where-Object { $_.service.name -eq "form-automation-agent" } | Select-Object -First 1
        
        if ($service) {
            $ServiceId = $service.service.id
            Write-Host "Found service: $ServiceId" -ForegroundColor Green
        } else {
            Write-Host "Service not found. Please provide ServiceId or deploy via dashboard." -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "Error finding service: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "`nPlease deploy manually via Render dashboard:" -ForegroundColor Yellow
        Write-Host "1. Go to https://dashboard.render.com" -ForegroundColor White
        Write-Host "2. Find your service" -ForegroundColor White
        Write-Host "3. Click 'Manual Deploy' → 'Deploy latest commit'" -ForegroundColor White
        exit 1
    }
}

# Trigger manual deploy
Write-Host "`nTriggering deployment for service: $ServiceId" -ForegroundColor Yellow
try {
    $deployConfig = @{
        clearBuildCache = $false
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$apiBase/services/$ServiceId/deploys" `
        -Headers $headers `
        -Method Post `
        -Body $deployConfig `
        -ContentType "application/json"
    
    Write-Host "`n✅ Deployment triggered successfully!" -ForegroundColor Green
    Write-Host "Deploy ID: $($response.deploy.id)" -ForegroundColor Cyan
    Write-Host "Status: $($response.deploy.status)" -ForegroundColor Cyan
    Write-Host "`nCheck deployment status in Render dashboard" -ForegroundColor Yellow
    Write-Host "Dashboard: https://dashboard.render.com" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Error triggering deployment: $($_.Exception.Message)" -ForegroundColor Red
    
    Write-Host "`n💡 Manual deployment method:" -ForegroundColor Yellow
    Write-Host "1. Go to https://dashboard.render.com" -ForegroundColor White
    Write-Host "2. Select your service: form-automation-agent" -ForegroundColor White
    Write-Host "3. Click 'Manual Deploy' → 'Deploy latest commit'" -ForegroundColor White
    Write-Host "4. Wait for build to complete" -ForegroundColor White
}
