# Discord quota-control bot

`tools.hub.discord_bot` is a small optional Discord client for the automatic
quota filler. It controls the same external `hub.toml` and SQLite event log as
`hubctl quota`, so an existing hub actuator picks up a toggle on its next
executor cycle without being restarted.

The bot exposes only these slash commands:

- `/quota status`
- `/quota on`
- `/quota off`
- `/quota reserve games:<number>`

The current laptop configuration makes all four commands visible and usable
to every member of the configured server. Set
`JKS_DISCORD_ALLOW_ALL_USERS=false` to return to allowlisted control. The bot
accepts no shell commands and always requires a guild boundary.

`/quota reserve games:20` leaves 20 games in both the field and dev rolling
hour pools for manual testing. Use `games:0` to remove the reserve. The
setting is persisted in the hub configuration and takes effect on the next
executor cycle. Automatic filler is paced at 10 games per pool per
ten-minute executor cycle, rather than draining all available quota in one
cycle.

## Setup

1. Create a Discord application and bot in the Discord Developer Portal. Enable
   the `bot` and `applications.commands` scopes when inviting it to the team
   server. No privileged gateway intents are needed.
2. Install the optional dependency in the environment that runs the hub:

       python3 -m pip install -r tools/requirements-discord.txt

3. Export the token and access policy in the service environment. Do not put
   the token in `hub.toml`, a checked-in file, or a command pasted into shared
   logs:

       export DISCORD_BOT_TOKEN='...'
       export JKS_DISCORD_ALLOWED_USER_IDS='123456789012345678'
       export JKS_DISCORD_ALLOWED_GUILD_IDS='234567890123456789'
       export JKS_DISCORD_ALLOWED_CHANNEL_IDS='345678901234567890'

   `JKS_DISCORD_ALLOWED_USER_IDS` is required. Guild and channel allowlists
   are optional, but setting both is recommended. Multiple IDs are comma
   separated. Direct messages are always rejected.

4. If the hub is not at the platform default, set its root explicitly:

       export JKS_HUB_ROOT='/path/to/battlecode-hub'

   On this Linux checkout, the default is the ignored `hub-state/` directory;
   the Mac deployment keeps its historical external hub path.

5. Validate the environment without connecting to Discord, then run the bot:

       python3 -m tools.hub.discord_bot --check-config
       python3 -m tools.hub.discord_bot

When a guild allowlist is configured, slash commands are synced to those
guilds immediately. Without one, Discord global-command propagation can take
up to about an hour.

## Keeping it running

Run the module under the same supervisor as the hub actuator (systemd,
launchd, or a container supervisor). Give it the same `JKS_HUB_ROOT` and
allowlist variables, but keep `DISCORD_BOT_TOKEN` in the supervisor's secret
environment. A Linux systemd starting point is
`tools/hub/jks-hub-discord.service.example`; it is already set for this
checkout and Anaconda path. Keep the referenced environment file outside the
repository. A bot restart
reconnects to Discord; it does not change the quota setting.

The Discord bot only controls the quota toggle; the hub actuator must also be
running for matches to be dispatched. On this laptop, use
`tools/hub/jks-hub-actuator.service.example` for the actuator service.
The actuator also requires a valid Battlecode API key in the repository's
`.battlecode-api-key`; keep that file local and never send it through Discord.

For this laptop, after installing `discord.py` into the Anaconda environment,
the service can be enabled with:

    mkdir -p ~/.config/jkshub ~/.config/systemd/user
    cp tools/hub/discord.env.example ~/.config/jkshub/discord.env
    chmod 600 ~/.config/jkshub/discord.env
    $EDITOR ~/.config/jkshub/discord.env
    cp tools/hub/jks-hub-discord.service.example ~/.config/systemd/user/jks-hub-discord.service
    cp tools/hub/jks-hub-actuator.service.example ~/.config/systemd/user/jks-hub-actuator.service
    systemctl --user daemon-reload
    systemctl --user enable --now jks-hub-actuator.service
    systemctl --user enable --now jks-hub-discord.service

Install the optional package first if needed:

    /home/rory/anaconda3/bin/python -m pip install -r tools/requirements-discord.txt

To stop automatic match filling, use `/quota off` or the local equivalent:

    python3 -m tools.hub.hubctl quota off

The toggle is recorded in `events.jsonl` and the `events` SQLite table with a
`discord/<user-id>` actor.
