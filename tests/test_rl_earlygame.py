import unittest

from tools.rl_earlygame import context_names, legal_actions, vector
from tools.rl_runtime import EarlyGameQPolicy


class EarlyGamePolicyTest(unittest.TestCase):
    def test_legal_actions_remove_kelp_and_allow_opening_split(self):
        row = {
            "length": 6,
            "units": 4,
            "unit_limit": 64,
            "cF_block": 0,
            "cR_block": 1,
            "cB_block": 0,
            "cL_block": 0,
        }
        actions = legal_actions(row)
        self.assertNotIn("R", actions)
        self.assertIn("split", actions)

    def test_training_and_runtime_vectors_have_same_width(self):
        row = {
            "round": 25,
            "length": 6,
            "units": 4,
            "unit_limit": 64,
            "vis_portal": 1,
            "cF_block": 0,
            "cR_block": 0,
            "cB_block": 0,
            "cL_block": 0,
            "y_split": 0,
        }
        names = context_names(__import__("pandas").DataFrame([row]))
        training = vector(row, "split", names)
        feature_names = (
            names + ["action_" + a for a in ("F", "R", "B", "L", "split")]
            + ["candidate_" + a for a in (
                "block", "portal", "pearl", "cd", "eh_adj", "area", "pdist",
                "pmass", "pc3", "bedsoon", "unvisited", "allyh2", "eseg2",
                "run", "mem_bed", "mem_bed_n", "mem_pearl",
            )] + ["split_size"]
        )
        model = {
            "context_features": names,
            "actions": ["F", "R", "B", "L", "split"],
            "candidate_attributes": [name.removeprefix("candidate_") for name in feature_names if name.startswith("candidate_")],
            "feature_names": feature_names,
            "mean": [0.0] * len(feature_names),
            "scale": [1.0] * len(feature_names),
            "coef": [0.0] * len(feature_names),
            "intercept": 0.0,
        }
        runtime = EarlyGameQPolicy(model)
        self.assertEqual(len(training), len(runtime.vector(row, "split")))


if __name__ == "__main__":
    unittest.main()

