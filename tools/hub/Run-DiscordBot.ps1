param([switch]$ValidateOnly)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$pythonPath = Join-Path $repoRoot 'build/discord-venv/Scripts/python.exe'
$envFile = Join-Path $env:LOCALAPPDATA 'JKS/discord.env'

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'The Discord virtual environment is missing. Install tools/requirements-discord.txt first.'
}
if (-not (Test-Path -LiteralPath $envFile)) {
    throw "The local Discord settings file is missing: $envFile"
}

$allowedNames = @(
    'DISCORD_BOT_TOKEN',
    'JKS_DISCORD_ALLOWED_USER_IDS',
    'JKS_DISCORD_ALLOWED_GUILD_IDS',
    'JKS_DISCORD_ALLOWED_CHANNEL_IDS',
    'JKS_DISCORD_ALLOW_ALL_USERS'
)
foreach ($line in [IO.File]::ReadAllLines($envFile)) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith('#')) { continue }
    $separator = $line.IndexOf('=')
    if ($separator -lt 1) { throw 'Invalid line in the local Discord settings file.' }
    $name = $line.Substring(0, $separator).Trim()
    $value = $line.Substring($separator + 1).Trim()
    if ($name -notin $allowedNames) { throw "Unsupported Discord setting: $name" }
    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
}

$env:JKS_HUB_ROOT = Join-Path $repoRoot 'hub-state'
if (-not $env:DISCORD_BOT_TOKEN) {
    throw "Set DISCORD_BOT_TOKEN in $envFile before starting the bot."
}
if (-not $env:JKS_DISCORD_ALLOWED_USER_IDS -and $env:JKS_DISCORD_ALLOW_ALL_USERS -ne 'true') {
    throw "Set your Discord user ID in JKS_DISCORD_ALLOWED_USER_IDS in $envFile."
}

& $pythonPath -m tools.hub.discord_bot --check-config
if ($LASTEXITCODE -ne 0) { throw "Discord config check failed ($LASTEXITCODE)." }
if ($ValidateOnly) {
    Write-Output 'Discord bot configuration is valid; no Discord connection was made.'
    exit 0
}

& $pythonPath -u -m tools.hub.discord_bot
exit $LASTEXITCODE
