# push-repo.ps1
# Run this script from the repository root.

param(
    [string]$Message = "auto commit"
)

Write-Host ""
Write-Host "=== KL Repo Push Script ===" -ForegroundColor Cyan
Write-Host ""

# Ensure .git/info/exclude exists and contains this script
try {
    $excludeFile = ".git/info/exclude"
    $scriptName = "push-repo.ps1"

    if (-not (Test-Path $excludeFile)) {
        New-Item -ItemType File -Path $excludeFile -Force | Out-Null
    }

    $excludeContent = Get-Content $excludeFile -Raw

    if ($excludeContent -notmatch [regex]::Escape($scriptName)) {
        Add-Content $excludeFile "`npush-repo.ps1"
        Write-Host "Added push-repo.ps1 to .git/info/exclude (local ignore)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Warning: Could not update .git/info/exclude" -ForegroundColor Red
}

try {
    if (-not (Test-Path ".git")) {
        Write-Host "This directory has no .git folder. Initialising new repository..." -ForegroundColor Yellow
        git init
    }

    Write-Host "Repository root: $(Get-Location)" -ForegroundColor Cyan

    Write-Host "Adding all changes except push-repo.ps1 ..." -ForegroundColor Cyan
    git add -A

    Write-Host "Committing..." -ForegroundColor Cyan
    git commit -m $Message

    $branch = git rev-parse --abbrev-ref HEAD
    Write-Host "Current branch: $branch" -ForegroundColor Cyan

    Write-Host "Pushing to origin/$branch ..." -ForegroundColor Cyan
    git push -u origin $branch

    Write-Host ""
    Write-Host "Push completed successfully." -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "An error occurred:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Yellow
[void][System.Console]::ReadLine()
