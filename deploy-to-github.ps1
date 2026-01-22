# GitHub Repository Creation and Push Script
# Usage: .\deploy-to-github.ps1 -Token "YOUR_GITHUB_TOKEN"

param(
    [Parameter(Mandatory=$true)]
    [string]$Token
)

$GitHubUsername = "GokulanandM"
$RepoName = "AgenticFiller"
$IsPrivate = $false  # Public repository

Write-Host "Creating GitHub repository: $RepoName" -ForegroundColor Green

# Create repository via GitHub API
$headers = @{
    "Authorization" = "Bearer $Token"
    "Accept" = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
    "User-Agent" = "PowerShell"
}

$body = @{
    name = $RepoName
    private = $IsPrivate
    auto_init = $false
    description = "Form Automation Agent with Azure OpenAI integration"
} | ConvertTo-Json

try {
    Write-Host "Attempting to create repository via GitHub API..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -ContentType "application/json"
    
    Write-Host "Repository created successfully!" -ForegroundColor Green
    Write-Host "Repository URL: $($response.html_url)" -ForegroundColor Cyan
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 422) {
        Write-Host "Repository might already exist. Continuing with push..." -ForegroundColor Yellow
    } elseif ($statusCode -eq 403) {
        Write-Host "Permission denied. The token might not have 'repo' scope." -ForegroundColor Red
        Write-Host "Please ensure your token has 'repo' permissions." -ForegroundColor Yellow
        Write-Host "Skipping repository creation. If it doesn't exist, create it manually at:" -ForegroundColor Yellow
        Write-Host "https://github.com/new" -ForegroundColor Cyan
        Write-Host "Then continue with push..." -ForegroundColor Yellow
    } else {
        Write-Host "Error creating repository: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Status Code: $statusCode" -ForegroundColor Red
        Write-Host "Continuing with push anyway..." -ForegroundColor Yellow
    }
}

# Navigate to project directory
Set-Location $PSScriptRoot

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "Initializing git repository..." -ForegroundColor Green
    git init
}

# Add remote (remove if exists)
git remote remove origin 2>$null
# Use token in URL for authentication
$remoteUrl = "https://${GitHubUsername}:${Token}@github.com/${GitHubUsername}/${RepoName}.git"
git remote add origin $remoteUrl

# Add all files
Write-Host "Adding files..." -ForegroundColor Green
git add .

# Commit if there are changes
$status = git status --porcelain
if ($status) {
    Write-Host "Committing changes..." -ForegroundColor Green
    git commit -m "Initial commit: Form Automation Agent with Azure OpenAI integration"
} else {
    Write-Host "No changes to commit." -ForegroundColor Yellow
}

# Set branch to main
git branch -M main

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Green
try {
    git push -u origin main
    Write-Host "`nSuccess! Repository pushed to GitHub!" -ForegroundColor Green
    Write-Host "Repository URL: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Cyan
} catch {
    Write-Host "Error pushing: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
