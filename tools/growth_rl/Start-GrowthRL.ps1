param(
    [ValidateSet('start', 'status', 'stop')][string]$Action = 'status',
    [string]$Config = 'configs/growth-rl-3060.json'
)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$configPath = if ([IO.Path]::IsPathRooted($Config)) { $Config } else { Join-Path $repoRoot $Config }
$settings = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$runRoot = if ([IO.Path]::IsPathRooted($settings.output)) { $settings.output } else { Join-Path $repoRoot $settings.output }
$pythonPath = Join-Path $repoRoot 'build/rl-venv/Scripts/python.exe'
New-Item -ItemType Directory -Path $runRoot -Force | Out-Null
$stopFile = Join-Path $runRoot 'STOP'
$statusFile = Join-Path $runRoot 'status.json'
if ($Action -eq 'stop') {
    Set-Content -LiteralPath $stopFile -Value 'Stop after the current bounded stage.'
    Write-Output 'Stop requested. Check status.json for stopped.'
    exit
}
if ($Action -eq 'status') {
    if (Test-Path -LiteralPath $statusFile) {
        Get-Content -LiteralPath $statusFile
        $status = Get-Content -LiteralPath $statusFile -Raw | ConvertFrom-Json
        $alive = Get-Process -Id $status.pid -ErrorAction SilentlyContinue
        Write-Output ('Process alive: ' + [bool]$alive)
    } else { Write-Output 'Not started.' }
    exit
}
if (Test-Path -LiteralPath $statusFile) {
    $status = Get-Content -LiteralPath $statusFile -Raw | ConvertFrom-Json
    if (Get-Process -Id $status.pid -ErrorAction SilentlyContinue) {
        throw 'Recorded worker process is still running; use status or stop first.'
    }
}
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Missing build/rl-venv environment. See docs/growth-rl.md.' }
if (Test-Path -LiteralPath $stopFile) { Remove-Item -LiteralPath $stopFile }
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$arguments = @('-u', '-m', 'tools.growth_rl', 'run', '--config', ('"' + $configPath + '"'))
$worker = Start-Process -FilePath $pythonPath -ArgumentList $arguments -WorkingDirectory $repoRoot -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $runRoot "worker-$stamp.log") `
    -RedirectStandardError (Join-Path $runRoot "worker-$stamp.err.log")
Write-Output ('Started RL worker PID ' + $worker.Id + '. Logs: ' + $runRoot)
