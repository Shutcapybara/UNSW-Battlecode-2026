import tempfile
import unittest
from pathlib import Path

from tools.hub.discord_bot import (
    AccessPolicy,
    ConfigurationError,
    QuotaController,
    load_policy,
    parse_id_list,
)


class DiscordBotConfigTests(unittest.TestCase):
    def test_parse_ids_deduplicates_and_ignores_empty_items(self):
        self.assertEqual(parse_id_list("12, 34,12,,", name="ids"), frozenset({12, 34}))

    def test_parse_ids_rejects_non_numeric_values(self):
        with self.assertRaises(ConfigurationError):
            parse_id_list("12,not-an-id", name="ids")

    def test_policy_requires_a_user_allowlist(self):
        with self.assertRaises(ConfigurationError):
            load_policy({})

    def test_policy_is_scoped_to_user_guild_and_optional_channel(self):
        policy = AccessPolicy(user_ids=frozenset({10}), guild_ids=frozenset({20}), channel_ids=frozenset({30}))
        self.assertTrue(policy.allows(user_id=10, guild_id=20, channel_id=30))
        self.assertFalse(policy.allows(user_id=11, guild_id=20, channel_id=30))
        self.assertFalse(policy.allows(user_id=10, guild_id=21, channel_id=30))
        self.assertFalse(policy.allows(user_id=10, guild_id=20, channel_id=31))
        self.assertFalse(policy.allows(user_id=10, guild_id=None, channel_id=None))

    def test_policy_can_allow_all_channels_in_one_guild(self):
        policy = AccessPolicy(user_ids=frozenset({10}), guild_ids=frozenset({20}))
        self.assertTrue(policy.in_scope(guild_id=20, channel_id=999))
        self.assertTrue(policy.allows(user_id=10, guild_id=20, channel_id=999))
        self.assertFalse(policy.allows(user_id=11, guild_id=20, channel_id=999))

    def test_policy_can_allow_everyone_in_one_guild(self):
        policy = AccessPolicy(user_ids=frozenset(), guild_ids=frozenset({20}), allow_all_users=True)
        self.assertTrue(policy.allows(user_id=11, guild_id=20, channel_id=999))
        self.assertFalse(policy.allows(user_id=11, guild_id=21, channel_id=999))

    def test_allow_all_users_can_replace_user_allowlist(self):
        policy = load_policy({
            "JKS_DISCORD_ALLOW_ALL_USERS": "true",
            "JKS_DISCORD_ALLOWED_GUILD_IDS": "20",
        })
        self.assertTrue(policy.allow_all_users)

    def test_controller_toggles_the_same_config_used_by_hubctl(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            controller = QuotaController(root, agent="discord/10")
            self.assertFalse(controller.status()["enabled"])
            self.assertTrue(controller.set_enabled(True)["enabled"])
            self.assertTrue(controller.status()["enabled"])
            self.assertFalse(controller.set_enabled(False)["enabled"])
            self.assertEqual(
                controller.status()["enabled"],
                False,
            )

    def test_controller_sets_a_shared_manual_reserve(self):
        with tempfile.TemporaryDirectory() as tmp:
            controller = QuotaController(Path(tmp), agent="discord/10")
            status = controller.set_reserve(20)
            self.assertEqual(status["settings"]["reserve_games"], {"field": 20, "dev": 20})


if __name__ == "__main__":
    unittest.main()
