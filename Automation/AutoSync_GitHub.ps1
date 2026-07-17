# SmartArchive automatic GitHub backup
# Watches the project every 60 seconds and commits/pushes any saved changes.
# Logs are written outside the project folder:
# %LOCALAPPDATA%\SmartArchive\AutoSync.log

param(
    [int]$IntervalSeconds = 60
)

# Git can print harmless line-ending warnings on stderr. We check Git exit codes
# ourselves, so those warnings must not stop automatic backup.
$ErrorActionPreference = "Continue"
$RepoPath = Split-Path -Parent $PSScriptRoot
$LogDirectory = Join-Path $env:LOCALAPPDATA "SmartArchive"
$LogFile = Join-Path $LogDirectory "AutoSync.log"
$TaskMutexName = "Global\SmartArchiveAutoSync"

New-Item -ItemType Directory -Path $LogDirectory -Force | Out-Null

function Write-Log {
    param([string]$Message)
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $Message"
    Add-Content -LiteralPath $LogFile -Value $line -Encoding UTF8
}

function Find-GitExe {
    $fromPath = Get-Command git.exe -ErrorAction SilentlyContinue
    if ($fromPath) {
        return $fromPath.Source
    }

    $githubDesktopRoot = Join-Path $env:LOCALAPPDATA "GitHubDesktop"
    if (Test-Path $githubDesktopRoot) {
        $apps = Get-ChildItem -Path $githubDesktopRoot -Directory -Filter "app-*" |
            Sort-Object LastWriteTime -Descending

        foreach ($app in $apps) {
            $candidates = @(
                (Join-Path $app.FullName "resources\app\git\cmd\git.exe"),
                (Join-Path $app.FullName "resources\app\git\bin\git.exe")
            )
            foreach ($candidate in $candidates) {
                if (Test-Path $candidate) {
                    return $candidate
                }
            }
        }
    }

    throw "Git was not found. Install Git for Windows or reinstall GitHub Desktop."
}

$mutex = New-Object System.Threading.Mutex($false, $TaskMutexName)
if (-not $mutex.WaitOne(0)) {
    # Another automatic backup process is already running.
    exit 0
}

try {
    $GitExe = Find-GitExe

    $insideRepository = & $GitExe -C $RepoPath rev-parse --is-inside-work-tree 2>&1
    if ($LASTEXITCODE -ne 0 -or ($insideRepository -join "").Trim() -ne "true") {
        throw "The Automation folder must be inside the SmartArchive Git repository."
    }

    $remote = & $GitExe -C $RepoPath remote get-url origin 2>&1
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($remote -join "").Trim())) {
        throw "No GitHub remote named 'origin' is configured for this project."
    }

    Write-Log "AutoSync started. Repository: $RepoPath | Remote: $(($remote -join '').Trim())"

    while ($true) {
        try {
            $status = @(& $GitExe -C $RepoPath status --porcelain --branch 2>&1)
            if ($LASTEXITCODE -ne 0) {
                throw "Could not read Git status: $($status -join ' ')"
            }

            $branchLine = if ($status.Count -gt 0) { [string]$status[0] } else { "" }
            $workingChanges = @($status | Select-Object -Skip 1)
            $madeCommit = $false

            if ($workingChanges.Count -gt 0) {
                & $GitExe -C $RepoPath add -A 2>&1 | Out-Null
                if ($LASTEXITCODE -ne 0) {
                    throw "git add failed."
                }

                $message = "Auto backup: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
                $commitOutput = @(& $GitExe -C $RepoPath commit -m $message 2>&1)
                if ($LASTEXITCODE -ne 0) {
                    throw "git commit failed: $($commitOutput -join ' ')"
                }

                $madeCommit = $true
                Write-Log "Committed saved changes."
                $branchLine = "## main...origin/main [ahead 1]"
            }

            # Retry a push if an earlier automatic push failed and local commits are ahead.
            if ($madeCommit -or $branchLine -match "\[ahead ") {
                $pushOutput = @(& $GitExe -C $RepoPath push origin main 2>&1)
                if ($LASTEXITCODE -eq 0) {
                    Write-Log "Push completed successfully."
                }
                else {
                    Write-Log "Push failed; it will be retried later. Details: $($pushOutput -join ' ')"
                }
            }
        }
        catch {
            Write-Log "ERROR: $($_.Exception.Message)"
        }

        Start-Sleep -Seconds $IntervalSeconds
    }
}
catch {
    Write-Log "FATAL: $($_.Exception.Message)"
}
finally {
    if ($mutex) {
        $mutex.ReleaseMutex() | Out-Null
        $mutex.Dispose()
    }
}
