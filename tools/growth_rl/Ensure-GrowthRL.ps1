$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$configPath = Join-Path $repoRoot 'configs/growth-rl-3060.json'
$settings = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$runRoot = if ([IO.Path]::IsPathRooted($settings.output)) { $settings.output } else { Join-Path $repoRoot $settings.output }
$statusPath = Join-Path $runRoot 'status.json'

if (Test-Path -LiteralPath $statusPath) {
    $status = Get-Content -LiteralPath $statusPath -Raw | ConvertFrom-Json
    if ($status.pid) {
        $worker = Get-CimInstance Win32_Process -Filter "ProcessId = $([int]$status.pid)" -ErrorAction SilentlyContinue
        if ($worker -and $worker.CommandLine -like '*tools.growth_rl*') {
            Write-Output "Growth-RL worker already running (PID $($status.pid))."
            exit 0
        }
    }
}

& (Join-Path $PSScriptRoot 'Start-GrowthRL.ps1') -Action start
