# push-repo.ps1
# Run this script from the root of the repository.

param(
    [string]$Message = "auto commit"
)

Write-Host ""
Write-Host "=== KL Repo Push Script ===" -ForegroundColor Cyan
Write-Host ""

try {
    # Check if this directory is a git repository
    if (-not (Test-Path ".git")) {
        Write-Host "This directory has no .git folder. Initialising new repository..." -ForegroundColor Yellow
        git init
    }

    # Show current path
    Write-Host "Repository root: $(Get-Location)" -ForegroundColor Cyan

    # Stage all changes
    Write-Host "Adding all changes (git add -A)..." -ForegroundColor Cyan
    git add -A

    # Commit
    Write-Host "Committing..." -ForegroundColor Cyan
    git commit -m $Message

    # Determine current branch
    $branch = git rev-parse --abbrev-ref HEAD
    Write-Host "Current branch: $branch" -ForegroundColor Cyan

    # Push to origin
    Write-Host "Pushing to origin/$branch ..." -ForegroundColor Cyan
    git push -u origin $branch

    Write-Host ""
    Write-Host "Push completed successfully." -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "An error occurred during push:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Yellow
[void][System.Console]::ReadLine()
