param(
    [ValidateSet('register', 'unregister')][string]$Action = 'register',
    [string]$TaskName = 'Battlecode Growth RL'
)
$ErrorActionPreference = 'Stop'

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($Action -eq 'unregister') {
    if ($existing) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Output "Removed scheduled task '$TaskName'."
    } else {
        Write-Output "Scheduled task '$TaskName' is not registered."
    }
    exit 0
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$ensureScript = Join-Path $PSScriptRoot 'Ensure-GrowthRL.ps1'
$powershell = Join-Path $env:WINDIR 'System32/WindowsPowerShell/v1.0/powershell.exe'
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$ensureScript`""
$taskAction = New-ScheduledTaskAction -Execute $powershell -Argument $arguments -WorkingDirectory $repoRoot
$taskTrigger = New-ScheduledTaskTrigger -AtLogOn -User $currentUser
$principal = New-ScheduledTaskPrincipal -UserId $currentUser -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 3)

Register-ScheduledTask -TaskName $TaskName -Action $taskAction -Trigger $taskTrigger `
    -Principal $principal -Settings $settings `
    -Description 'Resume the local Battlecode growth-RL worker at user logon; this worker does not submit or activate bots.' `
    -Force | Out-Null
Write-Output "Registered '$TaskName' for logon by $currentUser."
