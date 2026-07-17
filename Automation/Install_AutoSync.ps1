# Installs SmartArchive AutoSync as a background task for the current Windows user.

$ErrorActionPreference = "Stop"
$taskName = "SmartArchive-AutoSync"
$scriptPath = Join-Path $PSScriptRoot "AutoSync_GitHub.ps1"

if (-not (Test-Path $scriptPath)) {
    throw "AutoSync_GitHub.ps1 was not found. Keep all Automation files together."
}

$arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`""
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arguments
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Automatically commits and pushes SmartArchive saved changes." -Force | Out-Null
Start-ScheduledTask -TaskName $taskName

Write-Host "AutoSync is installed and running." -ForegroundColor Green
Write-Host "It checks for saved changes every 60 seconds." -ForegroundColor Green
Write-Host "Log file: $env:LOCALAPPDATA\SmartArchive\AutoSync.log" -ForegroundColor Cyan
