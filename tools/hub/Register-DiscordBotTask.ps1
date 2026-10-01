$ErrorActionPreference = 'Stop'
$startScript = (Resolve-Path (Join-Path $PSScriptRoot 'Run-DiscordBot.ps1')).Path

# Refuse to create an autostart task until its secret and fail-closed policy
# are present and the bot's local configuration check succeeds.
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $startScript -ValidateOnly
if ($LASTEXITCODE -ne 0) { throw 'Discord bot setup is incomplete; no task was registered.' }

$taskName = 'JKS Discord Quota Bot'
$user = "$env:USERDOMAIN\$env:USERNAME"
$workingDirectory = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$powershell = Join-Path $env:SystemRoot 'System32/WindowsPowerShell/v1.0/powershell.exe'
$arguments = "-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$startScript`""
$action = New-ScheduledTaskAction -Execute $powershell -Argument $arguments -WorkingDirectory $workingDirectory
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $user
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Write-Output "Registered and started '$taskName' for $user."
