"""Discord control bot for the hub quota filler.

The bot deliberately exposes a very small command surface:

    /quota status
    /quota on
    /quota off

The Discord token and access policy are supplied through environment
variables.  No arbitrary shell commands are accepted, and the bot refuses to
start when its user allowlist is missing.
"""
import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from . import db
from .config import hub_root, load_config, set_quota_filler_enabled, set_quota_filler_reserve

try:  # Keep the controller and its tests usable without the optional package.
    import discord
    from discord import app_commands
except ImportError:  # pragma: no cover - exercised by environments without discord.py
    discord = None
    app_commands = None


LOG = logging.getLogger("jks.hub.discord")


class ConfigurationError(ValueError):
    """Raised when the bot's environment configuration is unsafe or invalid."""


def parse_id_list(value, *, name):
    """Parse a comma-separated Discord snowflake allowlist.

    Empty values are accepted for optional guild/channel lists.  User IDs are
    validated separately by :func:`load_policy` and must not be empty.
    """
    result = []
    for raw in (value or "").split(","):
        raw = raw.strip()
        if not raw:
            continue
        if not raw.isdigit() or int(raw) <= 0:
            raise ConfigurationError(f"{name} contains an invalid Discord ID: {raw!r}")
        result.append(int(raw))
    return frozenset(result)


@dataclass(frozen=True)
class AccessPolicy:
    """Allow Discord interactions only from explicitly configured scopes."""

    user_ids: frozenset
    guild_ids: frozenset = frozenset()
    channel_ids: frozenset = frozenset()
    allow_all_users: bool = False

    def in_scope(self, *, guild_id, channel_id):
        """Return whether an interaction came from an approved server/channel."""
        # DMs are intentionally not a control channel.  A guild allowlist is
        # optional, but when present it is an additional required boundary.
        if guild_id is None:
            return False
        if self.guild_ids and guild_id not in self.guild_ids:
            return False
        if self.channel_ids and channel_id not in self.channel_ids:
            return False
        return True

    def allows(self, *, user_id, guild_id, channel_id):
        return self.in_scope(guild_id=guild_id, channel_id=channel_id) and (
            self.allow_all_users or user_id in self.user_ids
        )


def load_policy(environ=None):
    """Load and validate the fail-closed Discord access policy."""
    environ = os.environ if environ is None else environ
    user_ids = parse_id_list(environ.get("JKS_DISCORD_ALLOWED_USER_IDS"), name="JKS_DISCORD_ALLOWED_USER_IDS")
    allow_all_users = environ.get("JKS_DISCORD_ALLOW_ALL_USERS", "").strip().lower() in {
        "1", "true", "yes", "on"
    }
    if not user_ids and not allow_all_users:
        raise ConfigurationError(
            "set JKS_DISCORD_ALLOWED_USER_IDS or JKS_DISCORD_ALLOW_ALL_USERS=true"
        )
    return AccessPolicy(
        user_ids=user_ids,
        guild_ids=parse_id_list(environ.get("JKS_DISCORD_ALLOWED_GUILD_IDS"), name="JKS_DISCORD_ALLOWED_GUILD_IDS"),
        channel_ids=parse_id_list(environ.get("JKS_DISCORD_ALLOWED_CHANNEL_IDS"), name="JKS_DISCORD_ALLOWED_CHANNEL_IDS"),
        allow_all_users=allow_all_users,
    )


def _json_or_none(value, max_chars=700):
    if value is None:
        return "none"
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return rendered if len(rendered) <= max_chars else rendered[: max_chars - 3] + "..."


class QuotaController:
    """Small Python API around the same operation used by ``hubctl quota``."""

    def __init__(self, root=None, *, agent="discord/quota-bot"):
        self.root = Path(root) if root else hub_root()
        self.agent = agent

    def status(self):
        cfg = load_config(self.root)
        conn = db.connect(self.root)
        try:
            last = db.kv_get(conn, "executor_last", {}) or {}
            return {
                "root": str(self.root),
                "enabled": bool((cfg.get("quota_filler") or {}).get("enabled", False)),
                "settings": cfg.get("quota_filler") or {},
                "last": last.get("quota_filler"),
                "quota": last.get("quota"),
            }
        finally:
            conn.close()

    def set_enabled(self, enabled, *, agent=None):
        enabled = bool(enabled)
        # set_quota_filler_enabled creates the config if this is a fresh hub.
        set_quota_filler_enabled(self.root, enabled)
        conn = db.connect(self.root)
        try:
            db.event(conn, self.root, agent or self.agent, "quota_filler_toggled", {"enabled": enabled})
        finally:
            conn.close()
        return self.status()

    def set_reserve(self, games, *, agent=None):
        reserve = set_quota_filler_reserve(self.root, games)
        conn = db.connect(self.root)
        try:
            db.event(
                conn,
                self.root,
                agent or self.agent,
                "quota_filler_reserve_changed",
                {"reserve_games": reserve},
            )
        finally:
            conn.close()
        return self.status()


def format_status(status):
    """Render a bounded, human-readable response for Discord."""
    state = "ON" if status["enabled"] else "OFF"
    lines = [f"Quota filler: **{state}**", "Takes effect on the next executor cycle."]
    reserve = status.get("settings", {}).get("reserve_games") or {}
    lines.append(f"Reserved per rolling hour: field {reserve.get('field', 0)}, dev {reserve.get('dev', 0)}")
    if status.get("last") is not None:
        lines.append(f"Last filler run: `{_json_or_none(status['last'])}`")
    if status.get("quota") is not None:
        lines.append(f"Last quota accounting: `{_json_or_none(status['quota'])}`")
    return "\n".join(lines)


if discord is not None:

    class QuotaGroup(app_commands.Group):
        """The only command group registered by this bot."""

        def __init__(self, controller, policy):
            super().__init__(name="quota", description="Control the automatic match quota filler")
            self.controller = controller
            self.policy = policy

        async def _reply(self, interaction, enabled=None, reserve=None):
            user_id = getattr(interaction.user, "id", None)
            guild_id = getattr(interaction.guild, "id", None)
            channel_id = getattr(interaction.channel, "id", None)
            if (enabled is not None or reserve is not None) and not self.policy.allows(
                user_id=user_id, guild_id=guild_id, channel_id=channel_id
            ):
                await interaction.response.send_message(
                    "You are not authorized to change quota filling.",
                    ephemeral=False,
                )
                return
            await interaction.response.defer(ephemeral=False, thinking=True)
            try:
                if enabled is None:
                    status = self.controller.set_reserve(reserve, agent=f"discord/{user_id}") if reserve is not None else self.controller.status()
                else:
                    status = self.controller.set_enabled(enabled, agent=f"discord/{user_id}")
                await interaction.followup.send(format_status(status), ephemeral=False)
            except Exception:
                LOG.exception("Discord quota command failed")
                await interaction.followup.send(
                    "The hub operation failed. Check the hub daemon logs.", ephemeral=False
                )

        @app_commands.command(name="status", description="Show quota filler status")
        async def status(self, interaction):
            await self._reply(interaction)

        @app_commands.command(name="on", description="Enable automatic quota filling")
        async def on(self, interaction):
            await self._reply(interaction, True)

        @app_commands.command(name="off", description="Disable automatic quota filling")
        async def off(self, interaction):
            await self._reply(interaction, False)

        @app_commands.command(name="reserve", description="Reserve games for manual testing in both pools")
        async def reserve(self, interaction, games: app_commands.Range[int, 0, 60]):
            await self._reply(interaction, reserve=int(games))


    class QuotaCommandTree(app_commands.CommandTree):
        """Apply authorization and safe error responses to every command."""

        def __init__(self, client, policy):
            super().__init__(client)
            self.policy = policy

        async def interaction_check(self, interaction):
            user_id = getattr(interaction.user, "id", None)
            guild_id = getattr(interaction.guild, "id", None)
            channel_id = getattr(interaction.channel, "id", None)
            allowed = self.policy.in_scope(guild_id=guild_id, channel_id=channel_id)
            if not allowed and not interaction.response.is_done():
                await interaction.response.send_message(
                    "This bot is not enabled in this server/channel.",
                    ephemeral=False,
                )
            return allowed

        async def on_error(self, interaction, error):
            if isinstance(error, app_commands.CheckFailure):
                message = "You are not authorized to control this hub."
            else:
                LOG.error(
                    "Discord command dispatch failed: %r",
                    error,
                    exc_info=(type(error), error, error.__traceback__),
                )
                message = "The command could not be completed. Check the bot logs."
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)


    class QuotaBot(discord.Client):
        def __init__(self, controller, policy):
            super().__init__(intents=discord.Intents.none())
            self.tree = QuotaCommandTree(self, policy)
            self.tree.add_command(QuotaGroup(controller, policy))
            self.policy = policy

        async def setup_hook(self):
            if self.policy.guild_ids:
                # Guild sync is immediate and also keeps commands out of
                # unrelated servers if a guild allowlist was configured.
                for guild_id in self.policy.guild_ids:
                    guild = discord.Object(id=guild_id)
                    self.tree.copy_global_to(guild=guild)
                    await self.tree.sync(guild=guild)
            else:
                # Global commands can take up to an hour to appear in Discord.
                await self.tree.sync()

        async def on_ready(self):
            LOG.info("Discord quota bot connected as %s", self.user)


def _check_config_payload(policy):
    return {
        "hub_root": str(hub_root()),
        "allowed_users": len(policy.user_ids),
        "allowed_guilds": len(policy.guild_ids),
        "allowed_channels": len(policy.channel_ids),
        "allow_all_users": policy.allow_all_users,
        "token_configured": bool(os.environ.get("DISCORD_BOT_TOKEN", "").strip()),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="validate environment configuration without connecting to Discord",
    )
    args = parser.parse_args(argv)

    try:
        policy = load_policy()
    except ConfigurationError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2

    if args.check_config:
        print(json.dumps(_check_config_payload(policy), indent=2, sort_keys=True))
        return 0

    if discord is None:
        print(
            "discord.py is not installed; install tools/requirements-discord.txt first",
            file=sys.stderr,
        )
        return 2

    token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    if not token:
        print("configuration error: DISCORD_BOT_TOKEN is required", file=sys.stderr)
        return 2

    logging.basicConfig(level=os.environ.get("JKS_DISCORD_LOG_LEVEL", "INFO"))
    controller = QuotaController(agent="discord/quota-bot")
    bot = QuotaBot(controller, policy)
    bot.run(token)
    return 0


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
