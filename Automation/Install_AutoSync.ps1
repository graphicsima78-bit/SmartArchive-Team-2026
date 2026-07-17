param([ValidateRange(1, 1440)][int]$IntervalMinutes = 10)

$ErrorActionPreference = "Stop"
$taskName = "SmartArchive-AutoSync"
$scriptPath = Join-Path $PSScriptRoot "AutoSync_GitHub.ps1"
if (-not (Test-Path $scriptPath)) { throw "AutoSync_GitHub.ps1 was not found." }

$seconds = $IntervalMinutes * 60
$arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`" -IntervalSeconds $seconds"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arguments
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "ArchivePro automatic GitHub sync." -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Write-Host "AutoSync is active. Interval: $IntervalMinutes minute(s)." -ForegroundColor Green
Write-Host "Manual save: run Save_And_Sync_Now.bat" -ForegroundColor Cyan
