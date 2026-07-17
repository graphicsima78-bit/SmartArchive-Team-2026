# Save all current project changes to GitHub immediately.
$ErrorActionPreference = "Continue"
$RepoPath = Split-Path -Parent $PSScriptRoot

function Find-GitExe {
    $fromPath = Get-Command git.exe -ErrorAction SilentlyContinue
    if ($fromPath) { return $fromPath.Source }
    $root = Join-Path $env:LOCALAPPDATA "GitHubDesktop"
    if (Test-Path $root) {
        foreach ($app in (Get-ChildItem -Path $root -Directory -Filter "app-*" | Sort-Object LastWriteTime -Descending)) {
            foreach ($candidate in @((Join-Path $app.FullName "resources\app\git\cmd\git.exe"), (Join-Path $app.FullName "resources\app\git\bin\git.exe"))) {
                if (Test-Path $candidate) { return $candidate }
            }
        }
    }
    throw "Git was not found."
}

try {
    $git = Find-GitExe
    $status = @(& $git -C $RepoPath status --porcelain 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "This folder is not a Git repository." }
    if ($status.Count -eq 0) {
        Write-Host "No saved changes to sync." -ForegroundColor Yellow
        exit 0
    }
    & $git -C $RepoPath add -A 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Could not stage changes." }
    & $git -C $RepoPath commit -m "Manual save: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Could not create commit." }
    & $git -C $RepoPath push origin main 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Commit was created, but push failed." }
    Write-Host "Saved and pushed to GitHub successfully." -ForegroundColor Green
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
pause
