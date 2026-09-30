$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location -LiteralPath $repo
$python = Join-Path $repo 'build/discord-venv/Scripts/python.exe'
$root = Join-Path $repo 'hub-state'
$env:JKS_HUB_ROOT = $root
& $python -u -m tools.hub.quota_runner --live --root $root >> (Join-Path $root 'quota-runner.log') 2>&1
exit $LASTEXITCODE
