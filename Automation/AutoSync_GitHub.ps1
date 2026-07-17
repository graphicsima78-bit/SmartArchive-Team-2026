# ArchivePro automatic GitHub backup. Checks saved changes at a configurable interval.
param([int]$IntervalSeconds = 600)

$ErrorActionPreference = "Continue"
$RepoPath = Split-Path -Parent $PSScriptRoot
$LogDirectory = Join-Path $env:LOCALAPPDATA "SmartArchive"
$LogFile = Join-Path $LogDirectory "AutoSync.log"
New-Item -ItemType Directory -Path $LogDirectory -Force | Out-Null

function Write-Log([string]$Message) {
    Add-Content -LiteralPath $LogFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $Message" -Encoding UTF8
}
function Find-GitExe {
    $fromPath = Get-Command git.exe -ErrorAction SilentlyContinue
    if ($fromPath) { return $fromPath.Source }
    $root = Join-Path $env:LOCALAPPDATA "GitHubDesktop"
    if (Test-Path $root) {
        $apps = Get-ChildItem -Path $root -Directory -Filter "app-*" | Sort-Object LastWriteTime -Descending
        foreach ($app in $apps) {
            foreach ($candidate in @((Join-Path $app.FullName "resources\app\git\cmd\git.exe"), (Join-Path $app.FullName "resources\app\git\bin\git.exe"))) {
                if (Test-Path $candidate) { return $candidate }
            }
        }
    }
    throw "Git was not found. Install GitHub Desktop first."
}

$mutex = New-Object System.Threading.Mutex($false, "Global\SmartArchiveAutoSync")
if (-not $mutex.WaitOne(0)) { exit 0 }
try {
    $GitExe = Find-GitExe
    $inside = & $GitExe -C $RepoPath rev-parse --is-inside-work-tree 2>&1
    if ($LASTEXITCODE -ne 0 -or ($inside -join "").Trim() -ne "true") { throw "Automation must be inside the Git project folder." }
    $remote = & $GitExe -C $RepoPath remote get-url origin 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Git remote origin was not found." }
    Write-Log "AutoSync started. Interval: $IntervalSeconds seconds."
    while ($true) {
        $status = @(& $GitExe -C $RepoPath status --porcelain --branch 2>&1)
        if ($LASTEXITCODE -ne 0) { Write-Log "ERROR: Cannot read Git status."; Start-Sleep -Seconds $IntervalSeconds; continue }
        $branch = if ($status.Count -gt 0) { [string]$status[0] } else { "" }
        $changes = @($status | Select-Object -Skip 1)
        $committed = $false
        if ($changes.Count -gt 0) {
            & $GitExe -C $RepoPath add -A 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                & $GitExe -C $RepoPath commit -m "Auto backup: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) { $committed = $true; Write-Log "Automatic commit completed." }
            }
        }
        if ($committed -or $branch -match "\[ahead ") {
            & $GitExe -C $RepoPath push origin main 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) { Write-Log "Automatic push completed." }
            else { Write-Log "Push failed; it will be retried at the next interval." }
        }
        Start-Sleep -Seconds $IntervalSeconds
    }
}
catch { Write-Log "FATAL: $($_.Exception.Message)" }
finally { if ($mutex) { $mutex.ReleaseMutex() | Out-Null; $mutex.Dispose() } }
