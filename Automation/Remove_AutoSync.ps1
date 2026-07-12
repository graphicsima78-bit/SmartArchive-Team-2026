$taskName = "SmartArchive-AutoSync"
Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "AutoSync was stopped and removed." -ForegroundColor Yellow
